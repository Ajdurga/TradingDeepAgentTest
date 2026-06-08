---
name: memory-management
description: Manage persistent memory including user preferences, prior research, rejected trade ideas, and watchlists. Use when the agent needs to remember context, store findings, or recall previous analyses.
---

# Memory Management Skill

## Overview

This skill enables the agent to store and retrieve persistent information across sessions, including user preferences, prior research findings, rejected trade ideas, and watchlists. It helps maintain context and avoid repeating work.

## When to Use This Skill

Activate this skill when:
- User asks to remember something
- User sets preferences (risk tolerance, position limits)
- Storing completed research for future reference
- Recording rejected trade ideas
- Managing watchlist
- Retrieving prior analysis
- Searching for previous research
- User asks "what did we analyze before?"

## Required Inputs

- Action type (read, write, search, update)
- Memory category (user_preferences, prior_research, rejected_ideas, watchlist)
- Data to store or search query
- Optional: Confidence level (low, medium, high)

## Step-by-Step Procedure

1. **Determine Memory Action**
   - Read: Retrieve existing memory
   - Write: Store new information
   - Search: Find relevant past entries
   - Update: Modify existing memory
   - Delete: Remove memory (with user confirmation)

2. **Validate Memory Category**
   - user_preferences: Risk tolerance, limits, settings
   - prior_research: Past analyses and findings
   - rejected_ideas: Trades that were rejected and why
   - watchlist: Tickers of interest

3. **Execute Memory Operation**
   - For read: Load and return data
   - For write: Validate and store data
   - For search: Query and return matches
   - For update: Modify and save

4. **Maintain Privacy**
   - Never store sensitive credentials
   - Never store full account numbers
   - Store summaries, not raw private data
   - Allow user to delete memory

5. **Track Confidence**
   - Mark memory confidence level
   - Update confidence based on new information
   - Flag low-confidence memories

## Tools This Skill May Call

- `read_memory`: Read memory by key
- `write_memory`: Write memory by key
- `search_memory`: Search across memory
- `summarize_memory`: Generate memory summary
- `update_user_preferences`: Update preferences
- `add_to_watchlist`: Add ticker to watchlist
- `remove_from_watchlist`: Remove ticker

## Memory Categories

### User Preferences

```json
{
  "risk_tolerance": "medium",
  "max_position_risk_percent": 2.0,
  "preferred_strategies": ["long_calls", "spreads"],
  "avoid_strategies": ["naked_puts"],
  "watchlist": ["AAPL", "MSFT", "GOOGL"],
  "notification_preferences": {
    "email_reports": false,
    "approval_required": true
  }
}
```

### Prior Research

```json
[
  {
    "ticker": "AAPL",
    "summary": "Analyzed long call strategy, medium risk, approved paper trade PT-0001",
    "analysis": {
      "date": "2024-01-15",
      "price": 175.50,
      "volatility": 28.3,
      "recommendation": "Moderate bullish outlook"
    },
    "timestamp": "2024-01-15T10:30:00Z",
    "confidence": "high"
  }
]
```

### Rejected Ideas

```json
[
  {
    "ticker": "TSLA",
    "strategy": "Short put",
    "reason": "Undefined risk exceeds user tolerance",
    "details": {
      "proposed_strike": 200,
      "max_loss": "unlimited",
      "rejection_reason": "User risk tolerance is medium, strategy has undefined risk"
    },
    "timestamp": "2024-01-14T15:20:00Z"
  }
]
```

## Output Format

### Read Operation
```json
{
  "action": "read",
  "category": "user_preferences",
  "data": {
    "risk_tolerance": "medium",
    "max_position_risk_percent": 2.0,
    "watchlist": ["AAPL", "MSFT"]
  },
  "success": true
}
```

### Write Operation
```json
{
  "action": "write",
  "category": "prior_research",
  "success": true,
  "message": "Research entry added for AAPL"
}
```

### Search Operation
```json
{
  "action": "search",
  "query": "AAPL",
  "results": [
    {
      "category": "prior_research",
      "data": {
        "ticker": "AAPL",
        "summary": "Analyzed long call strategy...",
        "timestamp": "2024-01-15T10:30:00Z"
      }
    },
    {
      "category": "watchlist",
      "data": ["AAPL", "MSFT", "GOOGL"]
    }
  ],
  "count": 2
}
```

## Safety Constraints

**MUST NOT:**
- Store sensitive credentials or API keys
- Store full account numbers
- Store personally identifiable information
- Store raw private data without user consent
- Make memory permanent without user awareness

**MUST:**
- Store summaries, not raw data
- Mark confidence levels
- Allow user to view all memory
- Allow user to delete memory
- Encrypt sensitive data if stored
- Respect privacy

## Memory Confidence Levels

- **High**: Verified information, recent data, user-confirmed
- **Medium**: Reasonable inference, somewhat dated, not verified
- **Low**: Speculation, old data, uncertain

## Example Usage Scenarios

### Scenario 1: Store Research

**User Prompt:** "Remember this AAPL analysis for future reference"

**Agent Actions:**
1. Activate memory-management skill
2. Extract key findings from analysis
3. Create research entry
4. Store in prior_research
5. Confirm storage

**Output:**
```
✓ Stored AAPL analysis in memory
✓ Summary: Long call strategy, medium risk, breakeven $183.50
✓ Confidence: High
✓ You can recall this with "what did we analyze for AAPL?"
```

### Scenario 2: Update Preferences

**User Prompt:** "Set my risk tolerance to low and max position risk to 1%"

**Agent Actions:**
1. Activate memory-management skill
2. Read current preferences
3. Update risk_tolerance to "low"
4. Update max_position_risk_percent to 1.0
5. Save preferences
6. Confirm update

**Output:**
```
✓ Updated user preferences
  • Risk tolerance: medium → low
  • Max position risk: 2.0% → 1.0%
✓ Future analyses will use these settings
```

### Scenario 3: Search Prior Research

**User Prompt:** "What have we analyzed before?"

**Agent Actions:**
1. Activate memory-management skill
2. Read prior_research
3. Summarize findings
4. Present to user

**Output:**
```
Prior Research Summary:

1. AAPL (2024-01-15)
   - Long call strategy analyzed
   - Risk: Medium, Max loss: $350
   - Status: Paper trade approved (PT-0001)

2. MSFT (2024-01-10)
   - Market data research
   - Trend: Uptrend, Volatility: 25%
   - Status: Research only, no trade

Total: 2 research entries
```

### Scenario 4: Add to Watchlist

**User Prompt:** "Add NVDA to my watchlist"

**Agent Actions:**
1. Activate memory-management skill
2. Read current watchlist
3. Add NVDA if not present
4. Save updated watchlist
5. Confirm addition

**Output:**
```
✓ Added NVDA to watchlist
Current watchlist: AAPL, MSFT, GOOGL, NVDA
```

### Scenario 5: Record Rejected Idea

**User Prompt:** "I don't want to do that TSLA trade"

**Agent Actions:**
1. Activate memory-management skill
2. Create rejected idea entry
3. Store reason and details
4. Save to rejected_ideas
5. Confirm recording

**Output:**
```
✓ Recorded rejected trade idea for TSLA
✓ Reason: User declined
✓ This will help avoid similar suggestions in the future
```

## Memory Search Capabilities

The skill should support:
- **Ticker search**: Find all entries for a specific ticker
- **Date range search**: Find entries within date range
- **Strategy search**: Find entries by strategy type
- **Keyword search**: Search across all text fields
- **Category filter**: Search within specific category

## Memory Summarization

When user asks for summary, provide:
- Total number of entries per category
- Most recent entries
- Key patterns or trends
- Watchlist contents
- Current preferences

## Memory Maintenance

Periodically:
- Archive old entries (>90 days)
- Update confidence levels
- Remove duplicates
- Compress large entries

## Integration with Other Skills

- **Portfolio Research**: Check preferences before analysis
- **Options Risk**: Compare against rejected ideas
- **Paper Trade Proposal**: Verify against user preferences
- **Market Data**: Check if ticker in watchlist
- **Safety Review**: Validate against user risk tolerance

## Privacy and Security

- Store memory locally in workspace/memory/
- Use JSON format for easy inspection
- Allow user to export all memory
- Allow user to delete specific entries
- Never transmit memory to external services
- Encrypt if storing sensitive summaries

## Memory File Structure

```
workspace/memory/
  user_preferences.json
  prior_research.json
  rejected_ideas.json
  watchlist.json
  archive/
    2024-01/
      prior_research.json
```

## User Commands

Support these memory-related commands:
- "Remember this..."
- "What did we analyze for [ticker]?"
- "Show my watchlist"
- "Update my risk tolerance to [level]"
- "Add [ticker] to watchlist"
- "Remove [ticker] from watchlist"
- "Show my preferences"
- "What trades did we reject?"
- "Clear my memory" (with confirmation)
- "Export my memory"