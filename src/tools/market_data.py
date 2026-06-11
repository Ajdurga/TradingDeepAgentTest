"""
Market data tools for fetching stock quotes, price history, and volatility.
"""
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging
import numpy as np
import os
import time

from src.models.schemas import Quote, MarketDataOutput, DataSource

logger = logging.getLogger(__name__)

try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False
    logger.warning("yfinance not installed")

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    logger.warning("requests not installed")


class MarketDataTools:
    """Tools for fetching and analyzing market data."""
    
    def __init__(self, use_mock: bool = False, alpha_vantage_key: Optional[str] = None):
        """
        Initialize market data tools.
        
        Args:
            use_mock: Whether to use mock data only
            alpha_vantage_key: Alpha Vantage API key (optional, from env if not provided)
        """
        self.use_mock = use_mock
        self.alpha_vantage_key = alpha_vantage_key or os.getenv("ALPHA_VANTAGE_API_KEY")
        self.yfinance_available = YFINANCE_AVAILABLE and not use_mock
        self.alpha_vantage_available = REQUESTS_AVAILABLE and self.alpha_vantage_key and not use_mock
        
        # Track rate limit state
        self.yfinance_rate_limited = False
        self.last_yfinance_attempt = 0
        
        logger.info(
            f"Market data tools initialized - "
            f"yfinance: {self.yfinance_available}, "
            f"alpha_vantage: {self.alpha_vantage_available}, "
            f"mock: {self.use_mock}"
        )
    
    def get_quote(self, ticker: str) -> Dict[str, Any]:
        """
        Get current quote for a ticker.
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Quote data with error information if data unavailable
        """
        if self.use_mock:
            return self._get_mock_quote(ticker)
        
        # Try Alpha Vantage first (better rate limits)
        if self.alpha_vantage_available:
            try:
                result = self._get_alpha_vantage_quote(ticker)
                if result and "error" not in result:
                    return result
            except Exception as e:
                logger.warning(f"Alpha Vantage failed for {ticker}: {e}")
        
        # Try yfinance if not rate limited
        if self.yfinance_available and not self.yfinance_rate_limited:
            result = self._get_yfinance_quote(ticker)
            if result and "error" not in result:
                return result
        
        # Return error response instead of mock data
        return {
            "ticker": ticker.upper(),
            "error": "DATA_UNAVAILABLE",
            "message": "Unable to fetch real-time data. yfinance may be rate-limited. Please try again later or configure Alpha Vantage API key.",
            "timestamp": datetime.utcnow().isoformat(),
            "data_source": "error"
        }
    
    def _get_alpha_vantage_quote(self, ticker: str) -> Dict[str, Any]:
        """Get quote data from Alpha Vantage API."""
        if not self.alpha_vantage_key or not REQUESTS_AVAILABLE:
            return {"error": "Alpha Vantage not configured"}
        
        try:
            url = f"https://www.alphavantage.co/query"
            params = {
                "function": "GLOBAL_QUOTE",
                "symbol": ticker,
                "apikey": self.alpha_vantage_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Check for Alpha Vantage error responses
            if "Error Message" in data:
                logger.error(f"Alpha Vantage error: {data['Error Message']}")
                return {"error": f"Alpha Vantage error: {data['Error Message']}"}
            
            if "Note" in data:
                logger.warning(f"Alpha Vantage rate limit: {data['Note']}")
                return {"error": f"Alpha Vantage rate limit: {data['Note']}"}
            
            if "Information" in data:
                logger.warning(f"Alpha Vantage info: {data['Information']}")
                return {"error": f"Alpha Vantage info: {data['Information']}"}
            
            if "Global Quote" not in data or not data["Global Quote"]:
                logger.warning(f"No Global Quote from Alpha Vantage for {ticker}. Raw response: {data}")
                return {"error": f"No Global Quote returned. Raw response: {data}"}
            
            quote = data["Global Quote"]
            current_price = float(quote.get("05. price", 0))
            previous_close = float(quote.get("08. previous close", 0))
            change = float(quote.get("09. change", 0))
            change_percent = float(quote.get("10. change percent", "0").rstrip('%'))
            volume = int(quote.get("06. volume", 0))
            
            return {
                "ticker": ticker.upper(),
                "current_price": round(current_price, 2),
                "previous_close": round(previous_close, 2),
                "change": round(change, 2),
                "change_percent": round(change_percent, 2),
                "volume": volume,
                "timestamp": datetime.utcnow().isoformat(),
                "data_source": "alpha_vantage"
            }
        except Exception as e:
            logger.error(f"Alpha Vantage error for {ticker}: {e}")
            return {"error": str(e)}
    
    def _get_alpha_vantage_history(self, ticker: str, days: int) -> List[Dict[str, Any]]:
        """Get historical price data from Alpha Vantage API."""
        if not self.alpha_vantage_key or not REQUESTS_AVAILABLE:
            return []
        
        try:
            url = f"https://www.alphavantage.co/query"
            # Use TIME_SERIES_DAILY for up to 100 days of data
            params = {
                "function": "TIME_SERIES_DAILY",
                "symbol": ticker,
                "apikey": self.alpha_vantage_key,
                "outputsize": "compact" if days <= 100 else "full"
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Check for errors
            if "Error Message" in data:
                logger.error(f"Alpha Vantage error: {data['Error Message']}")
                return []
            
            if "Note" in data:
                logger.warning(f"Alpha Vantage rate limit: {data['Note']}")
                return []
            
            if "Information" in data:
                logger.warning(f"Alpha Vantage info: {data['Information']}")
                return []
            
            if "Time Series (Daily)" not in data:
                logger.warning(f"No time series data from Alpha Vantage for {ticker}")
                return []
            
            time_series = data["Time Series (Daily)"]
            history = []
            
            # Convert to our format and limit to requested days
            for date_str in sorted(time_series.keys(), reverse=True)[:days]:
                day_data = time_series[date_str]
                history.append({
                    "date": date_str,
                    "close": round(float(day_data["4. close"]), 2),
                    "volume": int(day_data["5. volume"])
                })
            
            # Reverse to get chronological order
            history.reverse()
            return history
            
        except Exception as e:
            logger.error(f"Alpha Vantage history error for {ticker}: {e}")
            return []
    
    def _get_yfinance_quote(self, ticker: str) -> Dict[str, Any]:
        """Get real quote data from Yahoo Finance."""
        if not YFINANCE_AVAILABLE:
            return {"error": "yfinance not available"}
        
        # Check if we're rate limited (wait 60 seconds between attempts)
        current_time = time.time()
        if self.yfinance_rate_limited and (current_time - self.last_yfinance_attempt) < 60:
            return {"error": "Rate limited"}
        
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="2d")
            
            if hist.empty:
                logger.warning(f"No price data found for {ticker}")
                return {"error": "No price data found, symbol may be delisted"}
            
            current_price = hist['Close'].iloc[-1]
            previous_close = hist['Close'].iloc[-2] if len(hist) > 1 else current_price
            change = current_price - previous_close
            change_percent = (change / previous_close) * 100 if previous_close > 0 else 0
            
            # Reset rate limit flag on success
            self.yfinance_rate_limited = False
            
            return {
                "ticker": ticker.upper(),
                "current_price": round(float(current_price), 2),
                "previous_close": round(float(previous_close), 2),
                "change": round(float(change), 2),
                "change_percent": round(float(change_percent), 2),
                "volume": int(hist['Volume'].iloc[-1]) if 'Volume' in hist else 0,
                "timestamp": datetime.utcnow().isoformat(),
                "data_source": "yahoo_finance"
            }
        except Exception as e:
            error_str = str(e)
            logger.error(f"Error fetching Yahoo Finance data for {ticker}: {error_str}")
            
            # Detect rate limiting
            if "429" in error_str or "Too Many Requests" in error_str:
                self.yfinance_rate_limited = True
                self.last_yfinance_attempt = time.time()
                logger.warning("yfinance rate limited - will retry after cooldown")
            
            return {"error": error_str}
    
    def _get_mock_quote(self, ticker: str) -> Dict[str, Any]:
        """Generate mock quote data."""
        # Base prices for common tickers
        base_prices = {
            "AAPL": 175.50,
            "MSFT": 380.00,
            "GOOGL": 140.50,
            "TSLA": 245.00,
            "NVDA": 495.00,
            "AMZN": 155.00,
            "META": 350.00,
            "SPY": 450.00,
        }
        
        base_price = base_prices.get(ticker.upper(), 100.00)
        
        # Add some random variation
        current_price = base_price * (1 + random.uniform(-0.02, 0.02))
        previous_close = base_price
        change = current_price - previous_close
        change_percent = (change / previous_close) * 100
        
        volume = random.randint(10_000_000, 100_000_000)
        
        return {
            "ticker": ticker.upper(),
            "current_price": round(current_price, 2),
            "previous_close": round(previous_close, 2),
            "change": round(change, 2),
            "change_percent": round(change_percent, 2),
            "volume": volume,
            "timestamp": datetime.utcnow().isoformat(),
            "data_source": "mock"
        }
    
    def get_price_history(
        self,
        ticker: str,
        days: int = 90
    ) -> List[Dict[str, Any]]:
        """
        Get historical price data.
        
        Args:
            ticker: Stock ticker symbol
            days: Number of days of history
            
        Returns:
            List of price data points or empty list if unavailable
        """
        if self.use_mock:
            return self._get_mock_price_history(ticker, days)
        
        # Try Alpha Vantage first (better for daily data)
        if self.alpha_vantage_available:
            result = self._get_alpha_vantage_history(ticker, days)
            if result:
                logger.info(f"Got {len(result)} days of history from Alpha Vantage for {ticker}")
                return result
        
        # Fallback to yfinance
        if self.yfinance_available and not self.yfinance_rate_limited:
            result = self._get_yfinance_history(ticker, days)
            if result:
                logger.info(f"Got {len(result)} days of history from yfinance for {ticker}")
                return result
        
        # Return empty list instead of mock data
        logger.warning(f"Unable to fetch price history for {ticker} from any source")
        return []
    
    def _get_yfinance_history(self, ticker: str, days: int) -> List[Dict[str, Any]]:
        """Get historical price data from Yahoo Finance."""
        if not YFINANCE_AVAILABLE:
            return []
        
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period=f"{days}d")
            
            if hist.empty:
                logger.warning(f"No history for {ticker}")
                return []
            
            history = []
            for date, row in hist.iterrows():
                history.append({
                    "date": date.strftime("%Y-%m-%d"),
                    "close": round(float(row['Close']), 2),
                    "volume": int(row['Volume']) if 'Volume' in row else 0
                })
            
            return history
        except Exception as e:
            error_str = str(e)
            logger.error(f"Error fetching Yahoo Finance history for {ticker}: {error_str}")
            
            # Detect rate limiting
            if "429" in error_str or "Too Many Requests" in error_str:
                self.yfinance_rate_limited = True
                self.last_yfinance_attempt = time.time()
            
            return []
    
    def _get_mock_price_history(
        self, 
        ticker: str, 
        days: int
    ) -> List[Dict[str, Any]]:
        """Generate mock price history."""
        quote = self._get_mock_quote(ticker)
        current_price = quote["current_price"]
        
        history = []
        price = current_price
        
        # Generate realistic price movement
        for i in range(days, 0, -1):
            date = datetime.utcnow() - timedelta(days=i)
            
            # Random walk with slight upward bias
            daily_return = random.gauss(0.001, 0.02)  # 0.1% mean, 2% std
            price = price * (1 + daily_return)
            
            history.append({
                "date": date.strftime("%Y-%m-%d"),
                "close": round(price, 2),
                "volume": random.randint(10_000_000, 100_000_000)
            })
        
        return history
    
    def calculate_returns(
        self, 
        price_history: List[Dict[str, Any]]
    ) -> float:
        """
        Calculate total return over the period.
        
        Args:
            price_history: List of price data
            
        Returns:
            Return percentage
        """
        if not price_history or len(price_history) < 2:
            return 0.0
        
        start_price = price_history[0]["close"]
        end_price = price_history[-1]["close"]
        
        return_pct = ((end_price - start_price) / start_price) * 100
        return round(return_pct, 2)
    
    def calculate_volatility(
        self, 
        price_history: List[Dict[str, Any]]
    ) -> float:
        """
        Calculate annualized volatility.
        
        Args:
            price_history: List of price data
            
        Returns:
            Annualized volatility percentage
        """
        if not price_history or len(price_history) < 2:
            return 0.0
        
        # Calculate daily returns
        returns = []
        for i in range(1, len(price_history)):
            prev_price = price_history[i-1]["close"]
            curr_price = price_history[i]["close"]
            daily_return = (curr_price - prev_price) / prev_price
            returns.append(daily_return)
        
        # Calculate standard deviation
        std_dev = np.std(returns)
        
        # Annualize (assuming 252 trading days)
        annualized_vol = std_dev * np.sqrt(252) * 100
        
        return round(annualized_vol, 2)
    
    def analyze_trend(
        self, 
        price_history: List[Dict[str, Any]]
    ) -> str:
        """
        Analyze price trend.
        
        Args:
            price_history: List of price data
            
        Returns:
            Trend summary
        """
        if not price_history or len(price_history) < 10:
            return "Insufficient data for trend analysis"
        
        # Calculate moving averages
        recent_prices = [p["close"] for p in price_history[-20:]]
        older_prices = [p["close"] for p in price_history[-40:-20]]
        
        recent_avg = np.mean(recent_prices)
        older_avg = np.mean(older_prices)
        
        current_price = price_history[-1]["close"]
        start_price = price_history[0]["close"]
        
        total_change = ((current_price - start_price) / start_price) * 100
        
        # Determine trend
        if recent_avg > older_avg * 1.05:
            trend = "Strong uptrend"
        elif recent_avg > older_avg * 1.02:
            trend = "Moderate uptrend"
        elif recent_avg < older_avg * 0.95:
            trend = "Strong downtrend"
        elif recent_avg < older_avg * 0.98:
            trend = "Moderate downtrend"
        else:
            trend = "Sideways/consolidation"
        
        # Find support and resistance
        prices = [p["close"] for p in price_history]
        high = max(prices)
        low = min(prices)
        
        summary = f"{trend}. "
        summary += f"Total change: {total_change:+.1f}%. "
        summary += f"Range: ${low:.2f} - ${high:.2f}"
        
    
    def _normalize_ticker(self, ticker: Any) -> str:
        """Normalize ticker input to uppercase string."""
        if isinstance(ticker, dict):
            ticker = ticker.get("ticker") or ticker.get("TICKER") or ticker.get("symbol")
        return str(ticker).upper().strip()
    
    def get_current_price(self, ticker: str) -> str:
        """
        Get only the current stock price (quote-only, no historical analysis).
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Formatted current price string or error message
        """
        ticker = self._normalize_ticker(ticker)
        logger.info(f"Fetching current price for {ticker}")
        
        quote = self.get_quote(ticker)
        
        if "error" in quote:
            error_msg = quote.get("message", quote.get("error", "Unknown error"))
            return f"❌ Unable to fetch current price for {ticker}: {error_msg}"
        
        return (
            f"Current price for {ticker}: ${quote['current_price']:.2f}\n"
            f"Change: {quote['change']:+.2f} ({quote['change_percent']:+.2f}%)\n"
            f"Volume: {quote['volume']:,}\n"
            f"Source: {quote.get('data_source', 'unknown')}\n"
            f"Timestamp: {quote['timestamp']}"
        )
        return summary
    
    def get_market_data_analysis(
        self,
        ticker: str,
        lookback_days: int = 90
    ) -> str:
        """
        Get complete market data analysis.
        
        Args:
            ticker: Stock ticker symbol
            lookback_days: Days of history to analyze
            
        Returns:
            Market data analysis as formatted string or error message
        """
        logger.info(f"Analyzing market data for {ticker}")
        
        # Get current quote
        quote = self.get_quote(ticker)
        
        # Check if quote has error
        if "error" in quote:
            error_msg = quote.get("message", quote.get("error", "Unknown error"))
            return f"❌ Unable to fetch data for {ticker}: {error_msg}"
        
        # Get price history
        history = self.get_price_history(ticker, lookback_days)
        
        # Check if we have sufficient data
        if not history or len(history) < 10:
            return f"❌ Insufficient price history for {ticker}. Data may be unavailable due to API rate limits. Please try again later or configure Alpha Vantage API key in .env file."
        
        # Calculate metrics
        return_pct = self.calculate_returns(history)
        volatility = self.calculate_volatility(history)
        trend = self.analyze_trend(history)
        
        # Identify support/resistance
        prices = [p["close"] for p in history]
        high_52w = max(prices)
        low_52w = min(prices)
        current = quote["current_price"]
        
        support_resistance = []
        if current - low_52w < (high_52w - low_52w) * 0.2:
            support_resistance.append(f"Near 52-week low of ${low_52w:.2f}")
        if high_52w - current < (high_52w - low_52w) * 0.2:
            support_resistance.append(f"Near 52-week high of ${high_52w:.2f}")
        
        # Format output
        data_source = quote.get("data_source", "unknown")
        output = f"""📊 Market Data Analysis for {ticker}

Current Price: ${current:.2f}
Change: ${quote['change']:+.2f} ({quote['change_percent']:+.2f}%)
Volume: {quote['volume']:,}

{lookback_days}-Day Performance:
• Return: {return_pct:+.2f}%
• Annualized Volatility: {volatility:.2f}%
• Trend: {trend}

"""
        if support_resistance:
            output += "Key Levels:\n"
            for note in support_resistance:
                output += f"• {note}\n"
            output += "\n"
        
        output += f"Data Source: {data_source}\n"
        output += f"Timestamp: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}"
        
        return output

# Made with Bob
