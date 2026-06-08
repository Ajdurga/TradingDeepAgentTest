---
name: paper-trade-proposal
description: Create and manage simulated paper trade proposals. Use only when the user explicitly asks to simulate, track, or create a paper-trade idea. Always requires human approval before saving.
---

# Paper Trade Proposal Skill

## Overview

This skill enables the agent to create simulated paper trade proposals for research and learning purposes. It is strictly for simulation only and must never connect to real order placement systems.

## When to Use This Skill

Activate this skill ONLY when the user:
- Explicitly asks to create a paper trade
- Requests a simulated trade proposal
- Wants to track a trade idea without executing
- Asks to save a trade concept for later review

**DO NOT** activate this skill for:
- General research or analysis
- Risk assessment without trade intent
- Portfolio review
- Market data queries

## Required Inputs

- Ticker symbol
- Instrument type (stock or option)
- Strategy description
- Rationale for the trade
- Risk analysis (max loss, breakeven)
- Optional: Entry price, target price, stop loss

## Step-by-Step Procedure

1. **Validate Prerequisites**
   - Ensure prior analysis has been completed
   - Verify risk metrics are calculated
   - Confirm safety review has passed

2. **Create Proposal Structure**
   - Generate unique proposal ID (PT-XXXX)
   - Set status to "pending_approval"
   - Include all required fields

3. **Request Human Approval**
   - Present proposal details to user
   - Explain this is simulation only
   - Wait for explicit approval
   - Do not proceed without approval

4. **Save Approved Proposal**
   - If approved, save to workspace/paper_trades.json
   - Include timestamp and approval status
   - Log to observations

5. **Handle Rejection**
   - If rejected, log reason
   - Add to rejected_ideas in memory
   - Do not save proposal

## Tools This Skill May Call

- `create_paper_trade_proposal`: Generate proposal structure
- `request_human_approval`: Request user approval
- `write_workspace_file`: Save approved proposal
- `read_workspace_file`: Read existing proposals
- `write_memory`: Log rejected ideas

## Output Format

```json
{
  "proposal_id": "PT-0001",
  "status": "pending_approval",
  "ticker": "AAPL",
  "instrument_type": "option",
  "strategy": "Long Call - AAPL $180 Call expiring 2024-02-16",
  "rationale": "AAPL showing uptrend with support at $175. Moderate volatility at 28%. Call option provides leveraged exposure with defined risk of $350.",
  "entry_details": {
    "option_type": "call",
    "strike": 180.00,
    "expiration": "2024-02-16",
    "premium": 3.50,
    "contracts": 1
  },
  "risk_analysis": {
    "max_loss": 350.00,
    "breakeven": 183.50,
    "risk_level": "medium",
    "percent_of_portfolio": 0.7
  },
  "approval_required": true,
  "created_at": "2024-01-15T10:30:00Z",
  "approved_at": null,
  "simulation_only": true,
  "disclaimer": "This is a simulated paper trade for research purposes only. No real orders will be placed."
}
```

## Approval Request Format

When requesting approval, present:

```
PAPER TRADE PROPOSAL APPROVAL REQUIRED

Proposal ID: PT-0001
Ticker: AAPL
Strategy: Long Call - $180 strike, expires 2024-02-16
Max Loss: $350.00
Breakeven: $183.50
Risk Level: Medium

Rationale: [Full rationale here]

⚠️  SIMULATION ONLY - No real trades will be executed

Do you approve this paper trade proposal? [Yes/No]
```

## Failure Handling

- If approval denied, log reason and stop
- If unable to save, return error
- If proposal already exists, ask to update or create new
- Never proceed without explicit approval

## Safety Constraints

**MUST NOT:**
- Connect to real trading APIs
- Execute actual orders
- Bypass approval requirement
- Save proposals without approval
- Make guarantees about profitability

**MUST:**
- Always require human approval
- Clearly label as "simulation only"
- Include full risk disclosure
- Save to local file only (paper_trades.json)
- Include max loss in every proposal
- Check against user risk tolerance
- Include disclaimer in output

## Risk Validation

Before creating proposal, verify:
- Max loss is calculated and reasonable
- Risk level is assessed
- Position size is within user limits
- Prior analysis supports the trade
- Safety review has passed

## Proposal Storage

Proposals are stored in `workspace/paper_trades.json`:

```json
{
  "proposals": [
    {
      "proposal_id": "PT-0001",
      "status": "approved",
      "ticker": "AAPL",
      "created_at": "2024-01-15T10:30:00Z",
      "approved_at": "2024-01-15T10:35:00Z"
    }
  ]
}
```

## Status Values

- `pending_approval`: Waiting for user approval
- `approved`: User approved, saved to file
- `rejected`: User rejected, logged to memory
- `expired`: Proposal expired (optional feature)

## Example Usage

**User Prompt:** "Create a paper trade for the AAPL call we analyzed"

**Agent Actions:**
1. Verify prior options-risk analysis exists
2. Activate paper-trade-proposal skill
3. Create proposal structure with all details
4. Request human approval with full disclosure
5. If approved: save to paper_trades.json
6. If rejected: log to rejected_ideas
7. Return confirmation

**Approval Dialog:**
```
PAPER TRADE PROPOSAL APPROVAL REQUIRED

Proposal ID: PT-0001
Ticker: AAPL
Strategy: Long Call - $180 strike, expires 2024-02-16
Max Loss: $350.00
Breakeven: $183.50

⚠️  SIMULATION ONLY - No real trades will be executed

Approve? [Yes/No]
```

**Output (if approved):**
```
✓ Paper trade proposal PT-0001 approved and saved
✓ Simulation only - no real orders placed
✓ Saved to workspace/paper_trades.json
```

## Integration with Other Skills

- **Options Risk**: Must run before creating option proposals
- **Market Data**: Include current market context
- **Portfolio Research**: Verify proposal fits portfolio
- **Safety Review**: Must pass before approval request
- **Memory Management**: Log rejected proposals

## Disclaimers

Every proposal must include:

1. "This is a simulated paper trade for research purposes only."
2. "No real orders will be placed."
3. "Past performance does not guarantee future results."
4. "Options trading involves significant risk."
5. "This is not financial advice."