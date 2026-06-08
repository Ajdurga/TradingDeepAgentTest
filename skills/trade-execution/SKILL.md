---
name: trade-execution
description: Create and execute real trade proposals with mandatory approval gates and safety limits. Use when the user wants to execute a trade, buy or sell stocks or options.
---

# Trade Execution Skill

## Overview

This skill enables the agent to create and execute real trade proposals with comprehensive safety controls. All trades require mandatory human approval and are subject to safety limits.

## When to Use This Skill

Activate this skill when the user:
- Explicitly asks to execute a trade
- Wants to buy or sell stocks or options
- Asks to place an order
- Requests trade execution

## Required Inputs

- Trade type (paper or real)
- Ticker symbol
- Instrument type (stock or option)
- Action (buy or sell)
- Quantity
- Order type (market, limit, stop)
- Optional: Limit price, stop price
- Strategy description and rationale

## Safety Limits (Real Trades Only)

All real trades must pass these checks:

1. **Position Size Limit**
   - Single trade cannot exceed user's max_position_risk_percent
   - Default: 2% of portfolio value
   - Configurable in user preferences

2. **Daily Loss Limit**
   - Total losses for the day cannot exceed daily limit
   - Default: 5% of portfolio value
   - Prevents catastrophic daily losses

3. **Maximum Trade Value**
   - Single trade cannot exceed maximum dollar amount
   - Default: $10,000 per trade
   - Configurable in user preferences

4. **Risk Assessment**
   - Options with undefined risk require explicit acknowledgment
   - High-risk trades flagged for extra scrutiny
   - Concentration limits enforced

5. **Approval Timeout**
   - Approval requests expire after 5 minutes
   - Prevents stale orders from executing
   - User must re-approve if expired

## Step-by-Step Procedure

1. **Validate Prerequisites**
   - Verify risk analysis completed
   - Check safety limits
   - Validate account has sufficient funds
   - Ensure market is open (for market orders)

2. **Safety Checks**
   - Check position size limit
   - Check daily loss limit
   - Check maximum trade value
   - Verify no duplicate orders
   - Check concentration risk

3. **Create Trade Proposal**
   - Generate unique trade ID (RT-XXXX)
   - Set status to "pending_approval"
   - Calculate all risk metrics
   - Prepare approval request

4. **Request Human Approval**
   - Display full trade details
   - Show risk metrics and limits
   - Show current portfolio impact
   - Require explicit YES/NO response
   - Set 5-minute timeout

5. **Execute if Approved**
   - Submit order to broker API
   - Log order ID and timestamp
   - Monitor order status
   - Update portfolio tracking
   - Save execution details

6. **Handle Rejection**
   - Log rejection reason
   - Add to rejected_ideas
   - Do not execute trade
   - Provide feedback to user

## Tools This Skill May Call
- `validate_trade_safety`: Check safety limits
- `check_account_balance`: Verify sufficient funds
- `request_human_approval`: Get user approval
- `place_order`: Execute real trade (Robinhood/broker API)
- `get_order_status`: Check order execution
- `cancel_order`: Cancel pending order
- `write_trade_log`: Log all trade activity

### Common Tools
- `calculate_position_size`: Determine safe quantity
- `calculate_max_loss`: Determine risk
- `read_memory`: Check user preferences and limits
- `write_memory`: Update trade history

## Output Format

### Trade Proposal (Pending Approval)
```json
{
  "trade_id": "RT-0001",
  "trade_type": "real",
  "status": "pending_approval",
  "ticker": "AAPL",
  "action": "buy",
  "instrument_type": "option",
  "option_details": {
    "option_type": "call",
    "strike": 180.00,
    "expiration": "2024-02-16"
  },
  "quantity": 1,
  "order_type": "limit",
  "limit_price": 3.50,
  "estimated_cost": 350.00,
  "max_loss": 350.00,
  "risk_level": "medium",
  "safety_checks": {
    "position_size_ok": true,
    "daily_limit_ok": true,
    "max_value_ok": true,
    "concentration_ok": true
  },
  "portfolio_impact": {
    "current_value": 50000.00,
    "trade_percent": 0.7,
    "new_aapl_exposure": 17.7
  },
  "approval_required": true,
  "approval_expires_at": "2024-01-15T10:35:00Z",
  "created_at": "2024-01-15T10:30:00Z"
}
```

### Trade (Executed)
```json
{
  "trade_id": "RT-0001",
  "trade_type": "real",
  "status": "executed",
  "ticker": "AAPL",
  "action": "buy",
  "quantity": 1,
  "order_type": "limit",
  "limit_price": 3.50,
  "executed_price": 3.45,
  "total_cost": 345.00,
  "broker_order_id": "RH-ABC123",
  "approved_at": "2024-01-15T10:32:00Z",
  "executed_at": "2024-01-15T10:32:15Z",
  "execution_details": {
    "filled_quantity": 1,
    "average_price": 3.45,
    "commission": 0.00,
    "fees": 0.00
  }
}
```

## Approval Request Format
```
⚠️  REAL TRADE APPROVAL REQUIRED ⚠️

Trade ID: RT-0001
Type: BUY
Ticker: AAPL
Instrument: Call Option ($180 strike, expires 2024-02-16)
Quantity: 1 contract
Order Type: Limit @ $3.50
Estimated Cost: $350.00

Risk Analysis:
• Max Loss: $350.00
• Risk Level: Medium
• Portfolio Impact: 0.7%
• Current AAPL Exposure: 17.0% → 17.7%

Safety Checks:
✓ Position size within limit (0.7% < 2.0%)
✓ Daily loss limit OK
✓ Trade value within maximum
✓ Concentration acceptable

Rationale:
AAPL showing uptrend with support at $175. Moderate volatility at 28%.
Call option provides leveraged exposure with defined risk.

⚠️  THIS IS A REAL TRADE - REAL MONEY WILL BE USED
⚠️  This approval expires in 5 minutes

Do you approve this trade? [YES/NO]
```

## Safety Constraints

**MANDATORY for All Trades:**
- Human approval required for EVERY trade
- Safety limits must pass
- Sufficient funds verified
- Risk metrics calculated
- Full audit trail logged
- Approval timeout enforced
- No duplicate orders
- Emergency stop available

**MUST NOT:**
- Execute without approval
- Bypass safety limits
- Execute after approval expires
- Place orders when market closed (market orders)
- Exceed position size limits
- Ignore concentration risk

**MUST:**
- Log every trade attempt
- Log approval/rejection
- Log execution details
- Save to audit trail
- Update portfolio tracking
- Notify user of execution
- Provide order confirmation

## Error Handling

### Safety Limit Violations
```
❌ Trade Rejected - Safety Limit Exceeded

Trade ID: RT-0001
Reason: Position size exceeds limit

Details:
• Requested: 5.5% of portfolio
• Limit: 2.0% of portfolio
• Recommendation: Reduce quantity to 2 contracts

The trade was not submitted for approval.
```

### Approval Timeout
```
⏱️  Trade Approval Expired

Trade ID: RT-0001
Status: Expired (not executed)

The approval request expired after 5 minutes.
To execute this trade, please create a new trade request.
```

### Execution Failure
```
❌ Trade Execution Failed

Trade ID: RT-0001
Broker Order ID: RH-ABC123
Error: Insufficient buying power

The order was submitted but rejected by the broker.
No trade was executed. Your account was not charged.
```

## Emergency Stop

User can say "STOP ALL TRADES" or "CANCEL ALL ORDERS" to:
- Cancel all pending approvals
- Cancel all pending orders with broker
- Prevent new trade submissions
- Require explicit re-enable

## Audit Trail

All real trades logged to `workspace/trade_audit.json`:

```json
{
  "trades": [
    {
      "trade_id": "RT-0001",
      "timestamp": "2024-01-15T10:30:00Z",
      "action": "approval_requested",
      "details": {...}
    },
    {
      "trade_id": "RT-0001",
      "timestamp": "2024-01-15T10:32:00Z",
      "action": "approved",
      "approved_by": "user"
    },
    {
      "trade_id": "RT-0001",
      "timestamp": "2024-01-15T10:32:15Z",
      "action": "executed",
      "broker_order_id": "RH-ABC123",
      "execution_price": 3.45
    }
  ]
}
```

## Example Usage
**User:** "Buy 1 AAPL call option, $180 strike, next month expiration"

**Agent:**
1. Activate trade-execution skill
2. Run safety checks
3. Create trade proposal RT-0001
4. Request approval with full details
5. Wait for user response
6. If approved: execute trade
7. Confirm execution with order ID

**Output:** "✓ Trade RT-0001 executed. Broker order ID: RH-ABC123. Filled at $3.45."

## Integration with Other Skills

- **Options Risk**: Must complete before option trades
- **Market Data**: Verify current prices
- **Portfolio Research**: Check portfolio impact
- **Safety Review**: Validate before approval request
- **Memory Management**: Log to trade history

## Configuration

User can configure in preferences:
- `max_position_risk_percent`: Default 2.0%
- `daily_loss_limit_percent`: Default 5.0%
- `max_trade_value`: Default $10,000
- `approval_timeout_minutes`: Default 5