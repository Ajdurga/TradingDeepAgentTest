"""
Market data tools for fetching stock quotes, price history, and volatility.
"""
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging
import numpy as np

from src.models.schemas import Quote, MarketDataOutput, DataSource

logger = logging.getLogger(__name__)


class MarketDataTools:
    """Tools for fetching and analyzing market data."""
    
    def __init__(self, use_mock: bool = True):
        """
        Initialize market data tools.
        
        Args:
            use_mock: Whether to use mock data (True) or live API (False)
        """
        self.use_mock = use_mock
        logger.info(f"Market data tools initialized (mock={use_mock})")
    
    def get_quote(self, ticker: str) -> Dict[str, Any]:
        """
        Get current quote for a ticker.
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Quote data
        """
        if self.use_mock:
            return self._get_mock_quote(ticker)
        else:
            # TODO: Implement live API integration
            logger.warning("Live API not implemented, using mock data")
            return self._get_mock_quote(ticker)
    
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
            List of price data points
        """
        if self.use_mock:
            return self._get_mock_price_history(ticker, days)
        else:
            logger.warning("Live API not implemented, using mock data")
            return self._get_mock_price_history(ticker, days)
    
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
        
        return summary
    
    def get_market_data_analysis(
        self, 
        ticker: str, 
        lookback_days: int = 90
    ) -> MarketDataOutput:
        """
        Get complete market data analysis.
        
        Args:
            ticker: Stock ticker symbol
            lookback_days: Days of history to analyze
            
        Returns:
            Market data output
        """
        logger.info(f"Analyzing market data for {ticker}")
        
        # Get current quote
        quote = self.get_quote(ticker)
        
        # Get price history
        history = self.get_price_history(ticker, lookback_days)
        
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
        
        # Data quality notes
        data_quality = [
            f"Data current as of {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}",
        ]
        
        if self.use_mock:
            data_quality.append("Using mock data - live API not configured")
        
        return MarketDataOutput(
            ticker=ticker.upper(),
            current_price=quote["current_price"],
            lookback_days=lookback_days,
            return_percent=return_pct,
            annualized_volatility=volatility,
            trend_summary=trend,
            support_resistance_notes=support_resistance,
            data_quality_notes=data_quality
        )

# Made with Bob
