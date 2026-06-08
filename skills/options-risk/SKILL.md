---
name: options-risk
description: Analyze option contracts including calls, puts, spreads, Greeks, breakeven, max loss, theta decay, and implied volatility. Use when the user asks about options risk, strategies, or option-specific metrics.
---

# Options Risk Skill

## Overview

This skill enables the agent to analyze option contracts and strategies, calculate risk metrics, determine breakeven points, assess max loss scenarios, and evaluate Greeks and time decay.

## When to Use This Skill

Activate this skill when the user:
- Asks about call or put options
- Wants to analyze an option strategy (spreads, straddles, etc.)
- Inquires about option Greeks (delta, gamma, theta, vega)
- Requests breakeven calculation
- Asks about max loss or max profit
- Wants to understand theta decay or time value
- Inquires about implied volatility
- Asks about option risk assessment

## Required Inputs

- Ticker symbol
- Option type (call or put)
- Strike price
- Expiration date
- Optional: Current premium/price
- Optional: Strategy type (long call, covered call, spread, etc.)
- Optional: Number of contracts

## Step-by-Step Procedure

1. **Validate Option Parameters**
   - Ensure ticker, strike, and expiration are valid
   - Check if expiration is in the future
   - Validate option type

2. **Fetch Option Data**
   - Get options chain if available
   - Find specific contract or use mock data
   - Get current premium and Greeks if available

3. **Calculate Max Loss**
   - For long options: premium paid × 100 × contracts
   - For short options: potentially unlimited (flag high risk)
   - For spreads: calculate based on strategy

4. **Calculate Breakeven**
   - Long call: strike + premium
   - Long put: strike - premium
   - Adjust for spreads and complex strategies

5. **Analyze Time Decay (Theta)**
   - Calculate daily theta if available
   - Estimate time value remaining
   - Flag if expiration is near (<30 days)

6. **Assess Risk Level**
   - Low: Defined risk, small position size
   - Medium: Defined risk, moderate position size
   - High: Undefined risk, large position, or near expiration

7. **Identify Key Risks**
   - Time decay risk
   - Volatility risk
   - Directional risk
   - Liquidity risk

8. **Generate Report**
   - Create structured options risk output
   - Include all key metrics
   - Save to workspace

## Tools This Skill May Call

- `get_options_chain`: Fetch available options
- `get_option_quote`: Get specific option price
- `calculate_option_payoff`: Calculate P&L at various prices
- `calculate_max_loss`: Determine maximum loss
- `calculate_breakeven`: Find breakeven price(s)
- `estimate_position_risk`: Assess overall risk level
- `write_workspace_file`: Save analysis
- `read_memory`: Check user risk tolerance

## Output Format

```json
{
  "ticker": "AAPL",
  "strategy": "long_call",
  "option_type": "call",
  "strike": 180.00,
  "expiration": "2024-02-16",
  "days_to_expiration": 32,
  "premium": 3.50,
  "contracts": 1,
  "max_loss": 350.00,
  "max_profit": "unlimited",
  "breakeven": 183.50,
  "estimated_risk_level": "medium",
  "greeks": {
    "delta": 0.45,
    "gamma": 0.03,
    "theta": -0.08,
    "vega": 0.12,
    "implied_volatility": 0.32
  },
  "key_risks": [
    "Time decay: losing $8/day in theta",
    "Need stock above $183.50 to profit",
    "32 days until expiration - moderate time risk",
    "Implied volatility at 32% - volatility risk present"
  ],
  "invalidating_conditions": [
    "Stock stays below $180 at expiration",
    "Significant drop in implied volatility",
    "Time decay erodes value faster than stock moves"
  ]
}
```

## Failure Handling

- If options chain unavailable, use mock data with realistic values
- If Greeks unavailable, estimate based on standard models
- If unable to calculate exact metrics, provide ranges
- Never recommend undefined risk strategies without explicit warnings

## Safety Constraints

**MUST NOT:**
- Recommend selling naked options without severe warnings
- Ignore undefined risk scenarios
- Downplay time decay risk
- Make guarantees about option profitability

**MUST:**
- Always calculate and display max loss
- Always calculate breakeven point(s)
- Warn about time decay for long options
- Flag high-risk strategies explicitly
- Include disclaimer about option risk
- Check against user risk tolerance
- Warn if position size exceeds risk limits

## Risk Level Assessment

**Low Risk:**
- Defined max loss <2% of portfolio
- Long options with >60 days to expiration
- Spreads with limited risk

**Medium Risk:**
- Defined max loss 2-5% of portfolio
- Long options with 30-60 days to expiration
- Moderate position size

**High Risk:**
- Max loss >5% of portfolio
- Short options with undefined risk
- Options with <30 days to expiration
- Large position size relative to account

## Common Strategies

### Long Call
- Max Loss: Premium paid
- Max Profit: Unlimited
- Breakeven: Strike + Premium
- Risk: Time decay, need significant upward movement

### Long Put
- Max Loss: Premium paid
- Max Profit: Strike - Premium (down to $0)
- Breakeven: Strike - Premium
- Risk: Time decay, need significant downward movement

### Covered Call
- Max Loss: Stock loss - premium received
- Max Profit: (Strike - Stock Price) + Premium
- Risk: Capped upside, full downside exposure

### Bull Call Spread
- Max Loss: Net premium paid
- Max Profit: (Higher Strike - Lower Strike) - Net Premium
- Risk: Limited profit potential, time decay

## Example Usage

**User Prompt:** "Analyze the risk of buying one AAPL $180 call expiring next month"

**Agent Actions:**
1. Activate options-risk skill
2. Fetch AAPL options chain
3. Find $180 call for next month
4. Calculate max loss (premium × 100)
5. Calculate breakeven (strike + premium)
6. Assess theta decay
7. Determine risk level
8. Generate structured output
9. Save to workspace

**Output:** Max loss $350, breakeven $183.50, medium risk, losing $8/day to theta, need stock above breakeven to profit.

## Integration with Other Skills

- **Market Data**: Get underlying stock price and volatility
- **Portfolio Research**: Check if strategy fits portfolio risk profile
- **Safety Review**: Validate risk calculations and warnings
- **Paper Trade Proposal**: Include full risk analysis in proposal