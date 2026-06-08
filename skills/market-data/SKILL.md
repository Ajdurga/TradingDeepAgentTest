---
name: market-data
description: Fetch and summarize stock price, volatility, and trend data for public equities. Use when the user asks about a ticker, price movement, technical context, or market conditions.
---

# Market Data Skill

## Overview

This skill enables the agent to fetch and analyze market data for stocks, including current prices, historical performance, volatility metrics, and trend analysis.

## When to Use This Skill

Activate this skill when the user:
- Asks about a specific stock ticker
- Wants to know current price or recent price movement
- Inquires about volatility or risk metrics
- Requests technical analysis or trend information
- Asks about support/resistance levels
- Wants market context for a trading decision

## Required Inputs

- Ticker symbol (e.g., "AAPL", "TSLA")
- Optional: Lookback period (default: 90 days)
- Optional: Specific metrics requested (price, volatility, returns)

## Step-by-Step Procedure

1. **Validate Ticker**
   - Ensure ticker symbol is valid format
   - Check if ticker is in watchlist or prior research

2. **Fetch Current Quote**
   - Get current price, volume, and basic metrics
   - Note timestamp of data
   - Use mock data if live API unavailable

3. **Fetch Historical Data**
   - Get price history for lookback period
   - Calculate returns over period
   - Identify high/low points

4. **Calculate Volatility**
   - Compute daily returns
   - Calculate standard deviation
   - Annualize volatility metric

5. **Analyze Trends**
   - Identify trend direction (up, down, sideways)
   - Note significant price movements
   - Identify potential support/resistance levels

6. **Generate Summary**
   - Create structured market data output
   - Include data quality notes
   - Save to workspace for reference

## Tools This Skill May Call

- `get_quote`: Fetch current stock quote
- `get_price_history`: Get historical price data
- `calculate_returns`: Calculate return percentages
- `calculate_volatility`: Compute volatility metrics
- `write_workspace_file`: Save market data
- `read_memory`: Check if ticker in watchlist

## Output Format

```json
{
  "ticker": "AAPL",
  "current_price": 175.50,
  "previous_close": 174.20,
  "change": 1.30,
  "change_percent": 0.75,
  "lookback_days": 90,
  "return_percent": 12.5,
  "annualized_volatility": 28.3,
  "trend_summary": "Uptrend with recent consolidation near $175",
  "support_resistance_notes": [
    "Support around $170",
    "Resistance at $180"
  ],
  "data_quality_notes": [
    "Data current as of 2024-01-15 16:00 EST",
    "Using mock data - live API not configured"
  ],
  "volume": 52000000,
  "52_week_high": 198.23,
  "52_week_low": 124.17
}
```

## Failure Handling

- If ticker not found, return clear error message
- If live data unavailable, use mock data and label it
- If data is stale (>1 day old), include warning
- Never fabricate specific prices - use realistic mock data or state unavailable

## Safety Constraints

**MUST NOT:**
- Make price predictions or guarantees
- Recommend buying or selling without full analysis
- Fabricate exact prices without labeling as mock
- Ignore data quality issues

**MUST:**
- Clearly label mock vs. live data
- Include data timestamp
- Note if data is delayed or stale
- Include disclaimer about market risk
- State uncertainty when present

## Volatility Interpretation

- **Low Volatility**: <20% annualized - relatively stable
- **Medium Volatility**: 20-40% annualized - moderate risk
- **High Volatility**: >40% annualized - high risk, large price swings

## Trend Analysis Guidelines

- **Strong Uptrend**: Price up >10% over period, higher highs and lows
- **Moderate Uptrend**: Price up 5-10% over period
- **Sideways/Consolidation**: Price within 5% range
- **Moderate Downtrend**: Price down 5-10% over period
- **Strong Downtrend**: Price down >10% over period

## Example Usage

**User Prompt:** "What's the current price and volatility of AAPL?"

**Agent Actions:**
1. Activate market-data skill
2. Fetch current quote for AAPL
3. Get 90-day price history
4. Calculate returns and volatility
5. Generate trend summary
6. Save data to workspace
7. Return structured output

**Output:** Current price $175.50 (+0.75%), 90-day return +12.5%, annualized volatility 28.3% (medium), uptrend with consolidation.

## Integration with Other Skills

- **Portfolio Research**: Provide market context for holdings
- **Options Risk**: Supply underlying price and volatility for options analysis
- **Paper Trade Proposal**: Include current market conditions in rationale
- **Memory Management**: Store frequently researched tickers in watchlist