# Deep Agent Trading Research System - Usage Guide

## 🚀 Quick Start

### 1. Installation

Dependencies are already installed. If you need to reinstall:

```bash
pip install -r requirements.txt
```

### 2. Configuration

Your `.env` file should contain:

```env
# OpenAI API Configuration
OPENAI_API_KEY=your_actual_api_key_here
OPENAI_MODEL=gpt-4

# Trading Configuration
ENABLE_REAL_TRADING=false  # Set to true to enable real trading

# Agent Configuration
MAX_ITERATIONS=20
WORKSPACE_DIR=./workspace
MEMORY_DIR=./workspace/memory

# Risk Configuration
MAX_POSITION_RISK_PERCENT=2.0
DEFAULT_RISK_TOLERANCE=medium
```

### 3. Run the Agent

```bash
python3 -m src.main
```

## 📋 Example Requests

### Market Data Analysis
```
Analyze AAPL stock and show me the current price and volatility
```

### Options Risk Analysis
```
What's the risk of buying one AAPL call option at $180 strike expiring next month?
```

### Portfolio Analysis
```
Show me my current portfolio and identify any concentration risks
```

### Paper Trading
```
Create a paper trade for 10 shares of MSFT
```

### Real Trading (if enabled)
```
Buy 1 AAPL call option at $180 strike - I want to execute this trade
```
**Note**: Real trades require explicit approval with safety checks.

## 🎯 Features

### 1. Market Data Analysis
- Current stock prices
- Historical price trends
- Volatility calculations
- Support/resistance levels
- 52-week highs/lows

### 2. Options Risk Analysis
- Max loss calculations
- Breakeven price
- Greeks (delta, gamma, theta, vega)
- Time decay analysis
- Risk level assessment

### 3. Portfolio Research
- Current holdings and exposures
- Concentration risk analysis
- Sector allocation
- Unrealized P&L
- Position sizing recommendations

### 4. Trade Execution

#### Paper Trading (Simulation)
- No real money involved
- Track simulated trades
- Test strategies safely
- No approval required

#### Real Trading (With Safety Controls)
- **Mandatory human approval** for every trade
- Position size limits (default 2% of portfolio)
- Daily loss limits (default 5% of portfolio)
- Maximum trade value limits (default $10,000)
- Concentration risk checks
- 5-minute approval timeout
- Comprehensive audit trail

### 5. Memory Management
- Remembers user preferences
- Stores prior research
- Tracks rejected trade ideas
- Maintains watchlist

### 6. Safety Features
- Automatic risk assessment
- Required disclaimers
- Data source labeling
- Uncertainty acknowledgment
- Safety review before execution

## 🔒 Safety Controls (Real Trading)

When real trading is enabled, every trade goes through:

### 1. Safety Checks
```
✓ Position size within limit (0.7% < 2.0%)
✓ Daily loss limit OK
✓ Trade value within maximum
✓ Concentration acceptable
```

### 2. Approval Request
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

⚠️  THIS IS A REAL TRADE - REAL MONEY WILL BE USED
⚠️  This approval expires in 5 minutes

Do you approve this trade? [YES/NO]
```

### 3. Execution Confirmation
```
✓ Trade RT-0001 executed
✓ Broker order ID: RH-ABC123
✓ Filled at $3.45
✓ Total cost: $345.00
```

## 📊 Workspace Structure

After running the agent, you'll find:

```
workspace/
  runs/
    run-12345678/
      plan.json              # Task plan
      observations.md        # Agent observations
      market_data.json       # Market data fetched
      options_analysis.json  # Options analysis
      risk_review.md         # Safety review
      final_report.md        # Final report
  memory/
    user_preferences.json    # Your preferences
    prior_research.json      # Past analyses
    rejected_ideas.json      # Rejected trades
  paper_trades.json          # Paper trade proposals
  trade_audit.json           # Real trade audit log
```

## 🛠️ Advanced Usage

### Enable Real Trading

1. Update `.env`:
```env
ENABLE_REAL_TRADING=true
```

2. Restart the agent

3. All real trades will require approval

### Configure Risk Limits

Update `.env`:
```env
MAX_POSITION_RISK_PERCENT=1.0    # More conservative
DAILY_LOSS_LIMIT_PERCENT=3.0     # Lower daily limit
MAX_TRADE_VALUE=5000             # Lower max trade
```

### Change AI Model

Update `.env`:
```env
OPENAI_MODEL=gpt-3.5-turbo  # Faster, cheaper
# or
OPENAI_MODEL=gpt-4          # More capable (recommended)
```

## 🔍 Understanding Agent Output

### Plan
The agent creates a task plan:
```
Current Plan:
[x] Fetch market data for AAPL
[x] Analyze volatility and trends
[-] Calculate option risk metrics
[ ] Generate final report
```

### Observations
The agent logs its thinking:
```
[2024-01-15T10:30:00Z]
Fetching market data for AAPL...
Current price: $175.50
90-day return: +12.5%
Volatility: 28.3% (medium)
```

### Final Report
Structured analysis with:
- Key findings
- Risk metrics
- Recommendations
- Disclaimers

## ⚠️ Important Notes

### Data Sources
- **Mock Data**: Used by default for testing
- **Live Data**: Requires API configuration (not implemented yet)
- **Robinhood MCP**: Optional integration for portfolio data

### Disclaimers
All outputs include:
- "This is not financial advice"
- "Trading involves risk"
- "Past performance does not guarantee future results"
- Data source labels (mock/live)

### Real Trading Risks
- Real trades use real money
- Losses can occur
- Always review trades carefully
- Use paper trading to test first
- Understand the risks before enabling

## 🐛 Troubleshooting

### "OpenAI API key not set"
- Check `.env` file exists
- Verify `OPENAI_API_KEY` is set
- Make sure it's not `your_openai_api_key_here`

### "Import errors"
- Run: `pip install -r requirements.txt`
- Check Python version (3.9+ required)

### "Agent not responding"
- Check internet connection
- Verify OpenAI API key is valid
- Check OpenAI API status

### "Trade approval timeout"
- Approvals expire after 5 minutes
- Create a new trade request
- Respond faster to approval prompts

## 📚 Example Session

```
You: Analyze AAPL and tell me if it's a good time to buy a call option

🤖 Agent is thinking...

📊 AGENT RESPONSE
================================================================================

# AAPL Market Analysis and Options Assessment

## Current Market Data
- **Price**: $175.50 (+0.75% today)
- **90-Day Return**: +12.5%
- **Volatility**: 28.3% (Medium)
- **Trend**: Uptrend with consolidation near $175

## Options Analysis
For a $180 call expiring in 30 days:
- **Premium**: $3.50
- **Max Loss**: $350 (premium paid)
- **Breakeven**: $183.50
- **Risk Level**: Medium
- **Time Decay**: -$8/day

## Key Risks
1. Need stock above $183.50 to profit
2. Losing $8/day to theta decay
3. 30 days until expiration - moderate time risk
4. IV at 32% - volatility risk present

## Assessment
The option provides leveraged exposure with defined risk. However:
- Stock needs to move 4.6% to breakeven
- Time decay is significant
- Consider your risk tolerance

⚠️ **Disclaimers**
- This is not financial advice
- Options trading involves significant risk
- Past performance does not guarantee future results
- Data source: mock (for demonstration)

✅ Run completed successfully (Run ID: run-12345678)
📁 Artifacts saved to: workspace/runs/run-12345678/
```

## 🎓 Learning Resources

- Review `TECHNICAL_SPECIFICATION.md` for architecture details
- Check `IMPLEMENTATION_STATUS.md` for current progress
- Explore `skills/` directory for skill definitions
- Read `workspace/runs/` for example outputs

## 🤝 Support

For issues or questions:
1. Check this guide
2. Review error messages
3. Check workspace logs
4. Verify configuration

## 🔐 Security

- Never commit `.env` with real API keys
- Keep trade audit logs secure
- Review all real trades before approval
- Use paper trading for testing