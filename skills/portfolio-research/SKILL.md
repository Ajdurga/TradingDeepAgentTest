---
name: portfolio-research
description: Fetch and analyze portfolio holdings, account exposure, concentration risk, and how potential trades affect existing positions. Use when the user asks about portfolio, holdings, positions, or account exposure.
---

# Portfolio Research Skill

## Overview

This skill enables the agent to research and analyze portfolio holdings, understand account exposure, identify concentration risks, and evaluate how potential trades would affect existing positions.

## When to Use This Skill

Activate this skill when the user:
- Asks about their portfolio holdings
- Wants to know their account exposure
- Inquires about concentration risk
- Wants to understand how a trade would affect their positions
- Requests a portfolio summary or snapshot
- Asks about specific positions they hold

## Required Inputs

- User request/prompt
- Optional: Specific ticker to analyze in context of portfolio
- Optional: Trade proposal to evaluate against portfolio

## Step-by-Step Procedure

1. **Fetch Portfolio Data**
   - Check if Robinhood MCP is configured and available
   - If available, use `get_portfolio_snapshot` tool
   - If not available, use mock portfolio data
   - Clearly label the data source

2. **Analyze Holdings**
   - Calculate total equity and cash
   - Count number of positions
   - Identify top exposures by dollar value and percentage
   - Calculate concentration metrics

3. **Assess Risk**
   - Identify over-concentrated positions (>10% of portfolio)
   - Check for sector concentration
   - Note any positions with significant unrealized losses
   - Flag positions that exceed user's risk tolerance

4. **Generate Report**
   - Create structured portfolio summary
   - List top exposures with percentages
   - Document risk notes and concerns
   - Save snapshot to workspace

5. **Context for Trade Analysis**
   - If evaluating a trade, show how it would affect portfolio balance
   - Calculate new concentration percentages
   - Assess if trade increases or decreases risk

## Tools This Skill May Call

- `get_portfolio_snapshot`: Fetch current portfolio data
- `get_positions`: Get detailed position information
- `get_account_summary`: Get account-level summary
- `write_workspace_file`: Save portfolio snapshot
- `read_workspace_file`: Read prior portfolio data
- `read_memory`: Check user preferences and risk tolerance

## Output Format

```json
{
  "portfolio_summary": {
    "total_equity": 50000.00,
    "cash": 5000.00,
    "num_positions": 8,
    "data_source": "mock | robinhood_mcp"
  },
  "positions": [
    {
      "ticker": "AAPL",
      "quantity": 50,
      "market_value": 8500.00,
      "percent_of_portfolio": 17.0,
      "unrealized_pnl": 500.00,
      "unrealized_pnl_percent": 6.25
    }
  ],
  "top_exposures": [
    {
      "ticker": "AAPL",
      "percent": 17.0,
      "risk_level": "medium"
    }
  ],
  "risk_notes": [
    "AAPL represents 17% of portfolio - above 10% concentration threshold",
    "Tech sector represents 45% of portfolio - high sector concentration"
  ],
  "data_source": "mock"
}
```

## Failure Handling

- If MCP is unavailable, fall back to mock data and clearly state this
- If portfolio data is stale, include timestamp and warning
- If unable to fetch data, return error with explanation
- Never fabricate specific position details

## Safety Constraints

**MUST NOT:**
- Execute any trades or modifications to the account
- Access write-enabled MCP tools
- Make guarantees about future performance
- Recommend specific trades without proper analysis

**MUST:**
- Clearly label mock vs. real data
- Include data freshness timestamp
- Respect user privacy (no logging of account numbers)
- Include disclaimer that this is for research only
- Flag when data quality is uncertain

## Risk Assessment Guidelines

- **Low Risk**: Position <5% of portfolio, diversified holdings
- **Medium Risk**: Position 5-10% of portfolio, moderate concentration
- **High Risk**: Position >10% of portfolio, high concentration, or significant unrealized losses

## Example Usage

**User Prompt:** "Show me my current portfolio and identify any concentration risks"

**Agent Actions:**
1. Activate portfolio-research skill
2. Fetch portfolio data (MCP or mock)
3. Calculate exposures and concentrations
4. Generate risk assessment
5. Save snapshot to workspace
6. Return structured summary with risk notes

**Output:** Portfolio summary with top 5 positions, concentration percentages, and specific risk warnings for over-concentrated holdings.