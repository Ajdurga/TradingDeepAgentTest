"""
Options data tools for fetching options chains and calculating Greeks.
"""
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging
import math

from src.models.schemas import OptionContract, OptionType, OptionsRiskOutput, RiskLevel

logger = logging.getLogger(__name__)


class OptionsDataTools:
    """Tools for options data and analysis."""
    
    def __init__(self, use_mock: bool = True):
        """
        Initialize options data tools.
        
        Args:
            use_mock: Whether to use mock data
        """
        self.use_mock = use_mock
        logger.info(f"Options data tools initialized (mock={use_mock})")
    
    def get_options_chain(
        self, 
        ticker: str,
        expiration: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get options chain for a ticker.
        
        Args:
            ticker: Stock ticker
            expiration: Optional expiration date filter
            
        Returns:
            List of option contracts
        """
        if self.use_mock:
            return self._get_mock_options_chain(ticker, expiration)
        else:
            logger.warning("Live API not implemented, using mock data")
            return self._get_mock_options_chain(ticker, expiration)
    
    def _get_mock_options_chain(
        self, 
        ticker: str,
        expiration: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Generate mock options chain."""
        # Mock stock price
        base_prices = {
            "AAPL": 175.50,
            "MSFT": 380.00,
            "GOOGL": 140.50,
            "TSLA": 245.00,
        }
        stock_price = base_prices.get(ticker.upper(), 100.00)
        
        # Generate expirations
        if expiration:
            expirations = [expiration]
        else:
            expirations = [
                (datetime.utcnow() + timedelta(days=30)).strftime("%Y-%m-%d"),
                (datetime.utcnow() + timedelta(days=60)).strftime("%Y-%m-%d"),
            ]
        
        options = []
        
        for exp in expirations:
            # Generate strikes around current price
            strikes = [
                stock_price * 0.90,
                stock_price * 0.95,
                stock_price,
                stock_price * 1.05,
                stock_price * 1.10,
            ]
            
            for strike in strikes:
                # Calculate days to expiration
                exp_date = datetime.strptime(exp, "%Y-%m-%d")
                days_to_exp = (exp_date - datetime.utcnow()).days
                
                # Mock Greeks and pricing
                moneyness = stock_price / strike
                
                # Call option
                call_premium = max(stock_price - strike, 0) + random.uniform(1, 5)
                options.append({
                    "ticker": ticker.upper(),
                    "option_type": "call",
                    "strike": round(strike, 2),
                    "expiration": exp,
                    "days_to_expiration": days_to_exp,
                    "premium": round(call_premium, 2),
                    "implied_volatility": round(random.uniform(0.25, 0.40), 2),
                    "delta": round(0.5 * moneyness, 2),
                    "gamma": round(random.uniform(0.01, 0.05), 3),
                    "theta": round(-random.uniform(0.05, 0.15), 3),
                    "vega": round(random.uniform(0.08, 0.15), 2),
                })
                
                # Put option
                put_premium = max(strike - stock_price, 0) + random.uniform(1, 5)
                options.append({
                    "ticker": ticker.upper(),
                    "option_type": "put",
                    "strike": round(strike, 2),
                    "expiration": exp,
                    "days_to_expiration": days_to_exp,
                    "premium": round(put_premium, 2),
                    "implied_volatility": round(random.uniform(0.25, 0.40), 2),
                    "delta": round(-0.5 * (2 - moneyness), 2),
                    "gamma": round(random.uniform(0.01, 0.05), 3),
                    "theta": round(-random.uniform(0.05, 0.15), 3),
                    "vega": round(random.uniform(0.08, 0.15), 2),
                })
        
        return options
    
    def get_option_quote(
        self,
        ticker: str,
        option_type: str,
        strike: float,
        expiration: str
    ) -> Dict[str, Any]:
        """
        Get quote for a specific option.
        
        Args:
            ticker: Stock ticker
            option_type: 'call' or 'put'
            strike: Strike price
            expiration: Expiration date
            
        Returns:
            Option quote
        """
        chain = self.get_options_chain(ticker, expiration)
        
        for option in chain:
            if (option["option_type"] == option_type and 
                abs(option["strike"] - strike) < 0.01):
                return option
        
        # If not found, generate one
        logger.warning(f"Option not found in chain, generating mock data")
        return self._generate_mock_option(ticker, option_type, strike, expiration)
    
    def _generate_mock_option(
        self,
        ticker: str,
        option_type: str,
        strike: float,
        expiration: str
    ) -> Dict[str, Any]:
        """Generate a single mock option."""
        exp_date = datetime.strptime(expiration, "%Y-%m-%d")
        days_to_exp = (exp_date - datetime.utcnow()).days
        
        premium = random.uniform(2, 8)
        
        return {
            "ticker": ticker.upper(),
            "option_type": option_type,
            "strike": strike,
            "expiration": expiration,
            "days_to_expiration": days_to_exp,
            "premium": round(premium, 2),
            "implied_volatility": round(random.uniform(0.25, 0.40), 2),
            "delta": round(random.uniform(0.3, 0.7), 2) if option_type == "call" else round(random.uniform(-0.7, -0.3), 2),
            "gamma": round(random.uniform(0.01, 0.05), 3),
            "theta": round(-random.uniform(0.05, 0.15), 3),
            "vega": round(random.uniform(0.08, 0.15), 2),
        }
    
    def calculate_option_payoff(
        self,
        option_type: str,
        strike: float,
        premium: float,
        stock_price: float,
        quantity: int = 1
    ) -> float:
        """
        Calculate option payoff at a given stock price.
        
        Args:
            option_type: 'call' or 'put'
            strike: Strike price
            premium: Premium paid
            stock_price: Stock price at expiration
            quantity: Number of contracts
            
        Returns:
            Profit/loss
        """
        if option_type == "call":
            intrinsic = max(stock_price - strike, 0)
        else:  # put
            intrinsic = max(strike - stock_price, 0)
        
        payoff = (intrinsic - premium) * 100 * quantity
        return round(payoff, 2)
    
    def calculate_max_loss(
        self,
        strategy: str,
        option_type: str,
        premium: float,
        quantity: int = 1,
        **kwargs
    ) -> float:
        """
        Calculate maximum loss for an option strategy.
        
        Args:
            strategy: Strategy name (long_call, long_put, etc.)
            option_type: 'call' or 'put'
            premium: Premium paid/received
            quantity: Number of contracts
            **kwargs: Additional strategy parameters
            
        Returns:
            Maximum loss (positive number)
        """
        if strategy in ["long_call", "long_put"]:
            # Max loss is premium paid
            return round(premium * 100 * quantity, 2)
        
        elif strategy in ["short_call", "short_put"]:
            # Undefined risk for naked shorts
            return float('inf')
        
        elif strategy == "covered_call":
            # Max loss is stock loss minus premium received
            stock_price = kwargs.get("stock_price", 0)
            return round((stock_price - premium) * 100 * quantity, 2)
        
        elif strategy == "bull_call_spread":
            # Max loss is net premium paid
            long_premium = premium
            short_premium = kwargs.get("short_premium", 0)
            net_premium = long_premium - short_premium
            return round(net_premium * 100 * quantity, 2)
        
        else:
            logger.warning(f"Unknown strategy: {strategy}")
            return round(premium * 100 * quantity, 2)
    
    def calculate_breakeven(
        self,
        option_type: str,
        strike: float,
        premium: float
    ) -> float:
        """
        Calculate breakeven price.
        
        Args:
            option_type: 'call' or 'put'
            strike: Strike price
            premium: Premium paid
            
        Returns:
            Breakeven price
        """
        if option_type == "call":
            return round(strike + premium, 2)
        else:  # put
            return round(strike - premium, 2)
    
    def estimate_position_risk(
        self,
        max_loss: float,
        portfolio_value: float,
        days_to_expiration: int,
        implied_volatility: float
    ) -> RiskLevel:
        """
        Estimate risk level for an option position.
        
        Args:
            max_loss: Maximum loss amount
            portfolio_value: Total portfolio value
            days_to_expiration: Days until expiration
            implied_volatility: IV of the option
            
        Returns:
            Risk level
        """
        # Calculate risk as percentage of portfolio
        risk_pct = (max_loss / portfolio_value) * 100 if portfolio_value > 0 else 100
        
        # Adjust for time and volatility
        if days_to_expiration < 30:
            risk_pct *= 1.2  # Higher risk near expiration
        
        if implied_volatility > 0.40:
            risk_pct *= 1.1  # Higher risk with high IV
        
        # Determine risk level
        if risk_pct < 1.0:
            return RiskLevel.LOW
        elif risk_pct < 3.0:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.HIGH
    
    def analyze_option_risk(
        self,
        ticker: str,
        option_type: str,
        strike: float,
        expiration: str,
        quantity: int = 1,
        portfolio_value: float = 50000.0
    ) -> OptionsRiskOutput:
        """
        Complete option risk analysis.
        
        Args:
            ticker: Stock ticker
            option_type: 'call' or 'put'
            strike: Strike price
            expiration: Expiration date
            quantity: Number of contracts
            portfolio_value: Portfolio value for risk assessment
            
        Returns:
            Options risk output
        """
        logger.info(f"Analyzing option risk for {ticker} {option_type} ${strike}")
        
        # Get option quote
        option = self.get_option_quote(ticker, option_type, strike, expiration)
        
        premium = option["premium"]
        days_to_exp = option["days_to_expiration"]
        iv = option["implied_volatility"]
        theta = option["theta"]
        
        # Calculate metrics
        strategy = f"long_{option_type}"
        max_loss = self.calculate_max_loss(strategy, option_type, premium, quantity)
        breakeven = self.calculate_breakeven(option_type, strike, premium)
        risk_level = self.estimate_position_risk(max_loss, portfolio_value, days_to_exp, iv)
        
        # Identify key risks
        key_risks = []
        
        # Time decay risk
        daily_theta_loss = abs(theta) * 100 * quantity
        key_risks.append(f"Time decay: losing ${daily_theta_loss:.2f}/day in theta")
        
        # Directional risk
        if option_type == "call":
            key_risks.append(f"Need stock above ${breakeven:.2f} to profit")
        else:
            key_risks.append(f"Need stock below ${breakeven:.2f} to profit")
        
        # Time risk
        if days_to_exp < 30:
            key_risks.append(f"{days_to_exp} days until expiration - high time risk")
        else:
            key_risks.append(f"{days_to_exp} days until expiration - moderate time risk")
        
        # Volatility risk
        if iv > 0.35:
            key_risks.append(f"Implied volatility at {iv*100:.0f}% - volatility risk present")
        
        # Invalidating conditions
        invalidating = []
        if option_type == "call":
            invalidating.append(f"Stock stays below ${strike:.2f} at expiration")
        else:
            invalidating.append(f"Stock stays above ${strike:.2f} at expiration")
        
        invalidating.append("Significant drop in implied volatility")
        invalidating.append("Time decay erodes value faster than stock moves")
        
        return OptionsRiskOutput(
            ticker=ticker.upper(),
            strategy=strategy,
            expiration=expiration,
            strike=strike,
            premium=premium,
            max_loss=max_loss,
            breakeven=breakeven,
            estimated_risk_level=risk_level,
            key_risks=key_risks,
            invalidating_conditions=invalidating
        )

# Made with Bob
