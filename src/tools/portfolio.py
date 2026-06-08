"""
Portfolio tools for fetching and analyzing portfolio data.
"""
import random
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

from src.models.schemas import (
    Position, PortfolioSummary, PortfolioResearchOutput, 
    DataSource, RiskLevel
)

logger = logging.getLogger(__name__)


class PortfolioTools:
    """Tools for portfolio data and analysis."""
    
    def __init__(self, use_mock: bool = True, mcp_enabled: bool = False):
        """
        Initialize portfolio tools.
        
        Args:
            use_mock: Whether to use mock data
            mcp_enabled: Whether Robinhood MCP is enabled
        """
        self.use_mock = use_mock
        self.mcp_enabled = mcp_enabled
        logger.info(f"Portfolio tools initialized (mock={use_mock}, mcp={mcp_enabled})")
    
    def get_portfolio_snapshot(self) -> Dict[str, Any]:
        """
        Get current portfolio snapshot.
        
        Returns:
            Portfolio data
        """
        if self.mcp_enabled and not self.use_mock:
            return self._get_mcp_portfolio()
        else:
            return self._get_mock_portfolio()
    
    def _get_mock_portfolio(self) -> Dict[str, Any]:
        """Generate mock portfolio data."""
        positions = [
            {
                "ticker": "AAPL",
                "quantity": 50,
                "average_cost": 170.00,
                "current_price": 175.50,
                "market_value": 8775.00,
                "unrealized_pnl": 275.00,
                "unrealized_pnl_percent": 3.24
            },
            {
                "ticker": "MSFT",
                "quantity": 20,
                "average_cost": 375.00,
                "current_price": 380.00,
                "market_value": 7600.00,
                "unrealized_pnl": 100.00,
                "unrealized_pnl_percent": 1.33
            },
            {
                "ticker": "GOOGL",
                "quantity": 30,
                "average_cost": 138.00,
                "current_price": 140.50,
                "market_value": 4215.00,
                "unrealized_pnl": 75.00,
                "unrealized_pnl_percent": 1.81
            },
            {
                "ticker": "NVDA",
                "quantity": 10,
                "average_cost": 480.00,
                "current_price": 495.00,
                "market_value": 4950.00,
                "unrealized_pnl": 150.00,
                "unrealized_pnl_percent": 3.13
            },
        ]
        
        total_market_value = sum(p["market_value"] for p in positions)
        cash = 5000.00
        total_equity = total_market_value + cash
        
        return {
            "total_equity": total_equity,
            "cash": cash,
            "positions": positions,
            "num_positions": len(positions),
            "data_source": "mock",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _get_mcp_portfolio(self) -> Dict[str, Any]:
        """Get portfolio from Robinhood MCP."""
        # TODO: Implement actual MCP integration
        logger.warning("MCP integration not implemented, using mock data")
        return self._get_mock_portfolio()
    
    def get_positions(self) -> List[Position]:
        """
        Get list of positions.
        
        Returns:
            List of Position objects
        """
        snapshot = self.get_portfolio_snapshot()
        positions = []
        
        for pos_data in snapshot["positions"]:
            position = Position(**pos_data)
            positions.append(position)
        
        return positions
    
    def get_account_summary(self) -> Dict[str, Any]:
        """
        Get account summary.
        
        Returns:
            Account summary data
        """
        snapshot = self.get_portfolio_snapshot()
        
        return {
            "total_equity": snapshot["total_equity"],
            "cash": snapshot["cash"],
            "buying_power": snapshot["cash"],  # Simplified
            "num_positions": snapshot["num_positions"],
            "data_source": snapshot["data_source"],
            "timestamp": snapshot["timestamp"]
        }
    
    def analyze_portfolio(self) -> PortfolioResearchOutput:
        """
        Analyze portfolio for risks and exposures.
        
        Returns:
            Portfolio research output
        """
        logger.info("Analyzing portfolio")
        
        snapshot = self.get_portfolio_snapshot()
        
        # Create portfolio summary
        positions = [Position(**p) for p in snapshot["positions"]]
        
        portfolio_summary = PortfolioSummary(
            total_equity=snapshot["total_equity"],
            cash=snapshot["cash"],
            num_positions=snapshot["num_positions"],
            positions=positions,
            data_source=DataSource.MOCK if snapshot["data_source"] == "mock" else DataSource.ROBINHOOD_MCP
        )
        
        # Calculate top exposures
        total_equity = snapshot["total_equity"]
        top_exposures = []
        
        for pos in snapshot["positions"]:
            exposure_pct = (pos["market_value"] / total_equity) * 100
            
            # Determine risk level based on concentration
            if exposure_pct > 20:
                risk_level = RiskLevel.HIGH
            elif exposure_pct > 10:
                risk_level = RiskLevel.MEDIUM
            else:
                risk_level = RiskLevel.LOW
            
            top_exposures.append({
                "ticker": pos["ticker"],
                "percent": round(exposure_pct, 1),
                "market_value": pos["market_value"],
                "risk_level": risk_level.value
            })
        
        # Sort by exposure
        top_exposures.sort(key=lambda x: x["percent"], reverse=True)
        
        # Generate risk notes
        risk_notes = []
        
        for exp in top_exposures:
            if exp["percent"] > 20:
                risk_notes.append(
                    f"{exp['ticker']} represents {exp['percent']}% of portfolio - "
                    f"HIGH concentration risk (>20% threshold)"
                )
            elif exp["percent"] > 10:
                risk_notes.append(
                    f"{exp['ticker']} represents {exp['percent']}% of portfolio - "
                    f"above 10% concentration threshold"
                )
        
        # Check for sector concentration (simplified - assume tech)
        tech_tickers = ["AAPL", "MSFT", "GOOGL", "NVDA", "META", "AMZN"]
        tech_exposure = sum(
            exp["percent"] for exp in top_exposures 
            if exp["ticker"] in tech_tickers
        )
        
        if tech_exposure > 50:
            risk_notes.append(
                f"Tech sector represents {tech_exposure:.1f}% of portfolio - "
                f"high sector concentration"
            )
        
        # Check for unrealized losses
        for pos in snapshot["positions"]:
            if pos["unrealized_pnl_percent"] < -10:
                risk_notes.append(
                    f"{pos['ticker']} has {pos['unrealized_pnl_percent']:.1f}% "
                    f"unrealized loss - consider reviewing position"
                )
        
        if not risk_notes:
            risk_notes.append("Portfolio appears well-diversified with no major concentration risks")
        
        return PortfolioResearchOutput(
            portfolio_summary=portfolio_summary,
            top_exposures=top_exposures,
            risk_notes=risk_notes,
            data_source=portfolio_summary.data_source
        )
    
    def check_trade_impact(
        self,
        ticker: str,
        trade_value: float,
        action: str = "buy"
    ) -> Dict[str, Any]:
        """
        Check how a trade would impact portfolio.
        
        Args:
            ticker: Stock ticker
            trade_value: Dollar value of trade
            action: 'buy' or 'sell'
            
        Returns:
            Impact analysis
        """
        snapshot = self.get_portfolio_snapshot()
        total_equity = snapshot["total_equity"]
        
        # Find existing position
        existing_value = 0
        for pos in snapshot["positions"]:
            if pos["ticker"] == ticker:
                existing_value = pos["market_value"]
                break
        
        # Calculate new exposure
        if action == "buy":
            new_value = existing_value + trade_value
        else:  # sell
            new_value = max(0, existing_value - trade_value)
        
        current_pct = (existing_value / total_equity) * 100
        new_pct = (new_value / total_equity) * 100
        
        return {
            "ticker": ticker,
            "action": action,
            "trade_value": trade_value,
            "current_exposure_pct": round(current_pct, 2),
            "new_exposure_pct": round(new_pct, 2),
            "exposure_change": round(new_pct - current_pct, 2),
            "concentration_warning": new_pct > 10,
            "high_concentration_warning": new_pct > 20
        }

# Made with Bob
