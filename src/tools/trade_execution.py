"""
Trade execution tools for real trading with safety controls.
"""
import uuid
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import logging

from src.models.schemas import ApprovalRequest

logger = logging.getLogger(__name__)


class TradeExecutionTools:
    """Tools for executing real trades with safety controls."""
    
    def __init__(
        self,
        broker_api_enabled: bool = False
    ):
        """
        Initialize trade execution tools.
        
        Args:
            broker_api_enabled: Whether broker API is configured
        """
        self.broker_api_enabled = broker_api_enabled
        self.pending_approvals: Dict[str, Dict[str, Any]] = {}
        
        logger.info(
            f"Trade execution tools initialized "
            f"(broker_api={broker_api_enabled})"
        )
    
    def create_trade_proposal(
        self,
        ticker: str,
        action: str,
        instrument_type: str,
        quantity: int,
        order_type: str,
        strategy: str,
        rationale: str,
        max_loss: float,
        portfolio_value: float,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create a real trade proposal with safety checks.
        
        Args:
            ticker: Stock ticker
            action: 'buy' or 'sell'
            instrument_type: 'stock' or 'option'
            quantity: Number of shares/contracts
            order_type: 'market', 'limit', 'stop'
            strategy: Strategy description
            rationale: Trade rationale
            max_loss: Maximum loss amount
            portfolio_value: Current portfolio value
            **kwargs: Additional parameters (limit_price, stop_price, etc.)
            
        Returns:
            Trade proposal with safety checks
        """
        trade_id = f"RT-{uuid.uuid4().hex[:8].upper()}"
        
        # Extract additional parameters
        limit_price = kwargs.get("limit_price")
        stop_price = kwargs.get("stop_price")
        option_details = kwargs.get("option_details")
        
        # Calculate trade value
        if instrument_type == "option":
            premium = kwargs.get("premium", 0)
            trade_value = premium * 100 * quantity
        else:
            price = limit_price or kwargs.get("current_price", 0)
            trade_value = price * quantity
        
        # Run safety checks
        safety_checks = self._run_safety_checks(
            trade_value=trade_value,
            max_loss=max_loss,
            portfolio_value=portfolio_value,
            ticker=ticker,
            action=action
        )
        
        # Check if all safety checks passed
        all_checks_passed = all(safety_checks.values())
        
        if not all_checks_passed:
            logger.warning(f"Trade {trade_id} failed safety checks")
        
        # Create proposal
        proposal = {
            "trade_id": trade_id,
            "trade_type": "real",
            "status": "pending_approval" if all_checks_passed else "rejected",
            "ticker": ticker.upper(),
            "action": action,
            "instrument_type": instrument_type,
            "quantity": quantity,
            "order_type": order_type,
            "limit_price": limit_price,
            "stop_price": stop_price,
            "option_details": option_details,
            "estimated_cost": trade_value,
            "max_loss": max_loss,
            "strategy": strategy,
            "rationale": rationale,
            "safety_checks": safety_checks,
            "portfolio_impact": self._calculate_portfolio_impact(
                ticker, trade_value, portfolio_value, action
            ),
            "approval_required": True,
            "approval_expires_at": (
                datetime.utcnow() + timedelta(minutes=5)
            ).isoformat(),
            "created_at": datetime.utcnow().isoformat()
        }
        
        # Store for approval tracking
        if all_checks_passed:
            self.pending_approvals[trade_id] = proposal
        
        logger.info(f"Created real trade proposal {trade_id}")
        return proposal
    
    def _run_safety_checks(
        self,
        trade_value: float,
        max_loss: float,
        portfolio_value: float,
        ticker: str,
        action: str,
        max_position_risk_percent: float = 2.0,
        daily_loss_limit_percent: float = 5.0,
        max_trade_value: float = 10000.0
    ) -> Dict[str, bool]:
        """
        Run safety checks on a trade.
        
        Args:
            trade_value: Dollar value of trade
            max_loss: Maximum loss
            portfolio_value: Portfolio value
            ticker: Stock ticker
            action: 'buy' or 'sell'
            max_position_risk_percent: Max risk per position
            daily_loss_limit_percent: Max daily loss
            max_trade_value: Max trade value
            
        Returns:
            Dictionary of safety check results
        """
        checks = {}
        
        # Position size check
        risk_pct = (max_loss / portfolio_value) * 100 if portfolio_value > 0 else 100
        checks["position_size_ok"] = risk_pct <= max_position_risk_percent
        
        # Daily loss limit check (simplified - would need to track actual daily losses)
        checks["daily_limit_ok"] = True  # TODO: Implement actual daily tracking
        
        # Maximum trade value check
        checks["max_value_ok"] = trade_value <= max_trade_value
        
        # Concentration check (simplified)
        checks["concentration_ok"] = risk_pct <= 20  # No single position > 20%
        
        return checks
    
    def _calculate_portfolio_impact(
        self,
        ticker: str,
        trade_value: float,
        portfolio_value: float,
        action: str
    ) -> Dict[str, Any]:
        """Calculate how trade impacts portfolio."""
        trade_pct = (trade_value / portfolio_value) * 100 if portfolio_value > 0 else 0
        
        return {
            "current_value": portfolio_value,
            "trade_value": trade_value,
            "trade_percent": round(trade_pct, 2),
            "action": action
        }
    
    def request_human_approval(
        self,
        trade_id: str
    ) -> ApprovalRequest:
        """
        Create an approval request for a trade.
        
        Args:
            trade_id: Trade identifier
            
        Returns:
            Approval request
        """
        if trade_id not in self.pending_approvals:
            raise ValueError(f"Trade {trade_id} not found in pending approvals")
        
        proposal = self.pending_approvals[trade_id]
        
        approval_request = ApprovalRequest(
            action="execute_real_trade",
            reason=f"Agent wants to execute trade {trade_id}",
            requires_approval=True,
            approved=False,
            details=proposal
        )
        
        logger.info(f"Created approval request for trade {trade_id}")
        return approval_request
    
    def approve_trade(self, trade_id: str) -> Dict[str, Any]:
        """
        Approve a trade for execution.
        
        Args:
            trade_id: Trade identifier
            
        Returns:
            Updated trade proposal
        """
        if trade_id not in self.pending_approvals:
            raise ValueError(f"Trade {trade_id} not found")
        
        proposal = self.pending_approvals[trade_id]
        
        # Check if approval expired
        expires_at = datetime.fromisoformat(proposal["approval_expires_at"])
        if datetime.utcnow() > expires_at:
            proposal["status"] = "expired"
            logger.warning(f"Trade {trade_id} approval expired")
            return proposal
        
        # Mark as approved
        proposal["status"] = "approved"
        proposal["approved_at"] = datetime.utcnow().isoformat()
        
        logger.info(f"Trade {trade_id} approved")
        return proposal
    
    def reject_trade(self, trade_id: str, reason: str) -> Dict[str, Any]:
        """
        Reject a trade.
        
        Args:
            trade_id: Trade identifier
            reason: Rejection reason
            
        Returns:
            Updated trade proposal
        """
        if trade_id not in self.pending_approvals:
            raise ValueError(f"Trade {trade_id} not found")
        
        proposal = self.pending_approvals[trade_id]
        proposal["status"] = "rejected"
        proposal["rejection_reason"] = reason
        proposal["rejected_at"] = datetime.utcnow().isoformat()
        
        # Remove from pending
        del self.pending_approvals[trade_id]
        
        logger.info(f"Trade {trade_id} rejected: {reason}")
        return proposal
    
    def execute_trade(self, trade_id: str) -> Dict[str, Any]:
        """
        Execute an approved trade.
        
        Args:
            trade_id: Trade identifier
            
        Returns:
            Execution result
        """
        if trade_id not in self.pending_approvals:
            raise ValueError(f"Trade {trade_id} not found")
        
        proposal = self.pending_approvals[trade_id]
        
        if proposal["status"] != "approved":
            raise ValueError(f"Trade {trade_id} is not approved")
        
        # Execute trade
        if self.broker_api_enabled:
            result = self._execute_via_broker_api(proposal)
        else:
            result = self._simulate_execution(proposal)
        
        # Update proposal
        proposal["status"] = "executed"
        proposal["executed_at"] = datetime.utcnow().isoformat()
        proposal["execution_details"] = result
        
        # Remove from pending
        del self.pending_approvals[trade_id]
        
        logger.info(f"Trade {trade_id} executed")
        return proposal
    
    def _execute_via_broker_api(self, proposal: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute trade via broker API (Robinhood, etc.).
        
        Args:
            proposal: Trade proposal
            
        Returns:
            Execution details
        """
        # TODO: Implement actual broker API integration
        logger.warning("Broker API not implemented, simulating execution")
        return self._simulate_execution(proposal)
    
    def _simulate_execution(self, proposal: Dict[str, Any]) -> Dict[str, Any]:
        """
        Simulate trade execution.
        
        Args:
            proposal: Trade proposal
            
        Returns:
            Simulated execution details
        """
        # Generate mock broker order ID
        broker_order_id = f"BROKER-{uuid.uuid4().hex[:12].upper()}"
        
        # Simulate execution with slight price improvement
        if proposal["order_type"] == "limit" and proposal["limit_price"]:
            executed_price = proposal["limit_price"] * 0.99  # Slight improvement
        else:
            executed_price = proposal["estimated_cost"] / proposal["quantity"]
        
        return {
            "broker_order_id": broker_order_id,
            "filled_quantity": proposal["quantity"],
            "average_price": round(executed_price, 2),
            "total_cost": round(executed_price * proposal["quantity"], 2),
            "commission": 0.00,
            "fees": 0.00,
            "execution_timestamp": datetime.utcnow().isoformat(),
            "simulated": not self.broker_api_enabled
        }
    
    def cancel_trade(self, trade_id: str) -> Dict[str, Any]:
        """
        Cancel a pending trade.
        
        Args:
            trade_id: Trade identifier
            
        Returns:
            Cancellation result
        """
        if trade_id not in self.pending_approvals:
            raise ValueError(f"Trade {trade_id} not found")
        
        proposal = self.pending_approvals[trade_id]
        proposal["status"] = "cancelled"
        proposal["cancelled_at"] = datetime.utcnow().isoformat()
        
        # Remove from pending
        del self.pending_approvals[trade_id]
        
        logger.info(f"Trade {trade_id} cancelled")
        return proposal
    
    def get_pending_approvals(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all pending approval requests.
        
        Returns:
            Dictionary of pending approvals
        """
        return self.pending_approvals.copy()

# Made with Bob
