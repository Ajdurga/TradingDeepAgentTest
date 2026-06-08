---
name: safety-review
description: Review agent outputs for safety, accuracy, and compliance. Use before finalizing any portfolio, options, or paper-trade analysis to ensure proper disclaimers, risk metrics, and uncertainty acknowledgment.
---

# Safety Review Skill

## Overview

This skill performs a comprehensive safety and quality review of agent outputs before they are presented to the user. It ensures proper risk disclosure, accurate calculations, appropriate disclaimers, and compliance with safety constraints.

## When to Use This Skill

Activate this skill:
- Before finalizing any research report
- Before presenting options analysis
- Before requesting approval for paper trades
- Before saving any analysis to workspace
- As the final step in any analysis workflow

**ALWAYS** use this skill before:
- Presenting final reports to user
- Requesting human approval
- Making recommendations
- Discussing specific trades

## Required Inputs

- Draft report or analysis to review
- Type of analysis (portfolio, market, options, paper-trade)
- Workspace files to review
- Context of the user request

## Step-by-Step Procedure

1. **Read Analysis Files**
   - Load all relevant workspace files
   - Read draft reports and observations
   - Gather all analysis outputs

2. **Check Risk Metrics**
   - Verify max loss is calculated (for options)
   - Verify breakeven is calculated (for options)
   - Check that risk levels are assessed
   - Ensure position sizing is addressed

3. **Validate Disclaimers**
   - Check for "not financial advice" disclaimer
   - Verify "simulation only" for paper trades
   - Ensure uncertainty is acknowledged
   - Confirm data source is labeled

4. **Review Language**
   - Flag overconfident statements
   - Check for guarantee language
   - Ensure probabilistic framing
   - Verify no misleading claims

5. **Verify Safety Constraints**
   - Confirm no real trade execution
   - Check no bypass of approval gates
   - Verify read-only data access
   - Ensure privacy protection

6. **Check Data Quality**
   - Verify data sources are labeled
   - Check timestamps are included
   - Ensure mock data is clearly marked
   - Validate calculations are reasonable

7. **Generate Review Report**
   - List all issues found
   - Specify required fixes
   - Determine pass/fail status
   - Provide recommendations

## Tools This Skill May Call

- `read_workspace_file`: Read analysis files
- `write_workspace_file`: Save review report
- `validate_report_safety`: Run automated checks
- `check_disclaimer_presence`: Verify disclaimers
- `validate_risk_metrics`: Check risk calculations

## Output Format

```json
{
  "passed": true,
  "review_timestamp": "2024-01-15T10:45:00Z",
  "analysis_type": "options_risk",
  "issues": [],
  "required_fixes": [],
  "warnings": [
    "Data is mock - ensure user is aware"
  ],
  "final_disclaimer_present": true,
  "risk_metrics_complete": true,
  "uncertainty_acknowledged": true,
  "overconfident_language": false,
  "approval_gate_respected": true,
  "recommendations": [
    "Consider adding more context about market conditions"
  ]
}
```

## Safety Checklist

### Required Elements (MUST be present)

**For All Analysis:**
- [ ] "This is not financial advice" disclaimer
- [ ] Data source clearly labeled (mock/live/MCP)
- [ ] Timestamp of data included
- [ ] Uncertainty acknowledged where appropriate
- [ ] No guarantee language

**For Options Analysis:**
- [ ] Max loss calculated and displayed
- [ ] Breakeven calculated and displayed
- [ ] Time decay (theta) mentioned for long options
- [ ] Risk level assessed (low/medium/high)
- [ ] Expiration date included

**For Paper Trade Proposals:**
- [ ] "Simulation only" disclaimer
- [ ] "No real orders will be placed" statement
- [ ] Human approval required
- [ ] Max loss included
- [ ] Risk analysis complete

**For Portfolio Analysis:**
- [ ] Data source labeled (mock/MCP)
- [ ] No account numbers exposed
- [ ] Concentration risks identified
- [ ] No modification of account

### Forbidden Elements (MUST NOT be present)

- [ ] Guarantees of profit or performance
- [ ] "This will definitely..." language
- [ ] Specific price predictions without uncertainty
- [ ] Recommendations without risk disclosure
- [ ] Real trade execution commands
- [ ] Bypass of approval gates
- [ ] Exposure of sensitive credentials

## Issue Severity Levels

**Critical (Must Fix):**
- Missing max loss for options
- Missing required disclaimers
- Guarantee language present
- Real trade execution attempted
- Approval gate bypassed

**High (Should Fix):**
- Missing breakeven calculation
- Overconfident language
- Insufficient risk disclosure
- Data source not labeled

**Medium (Consider Fixing):**
- Missing uncertainty acknowledgment
- Incomplete context
- Minor calculation issues

**Low (Optional):**
- Formatting improvements
- Additional context suggestions

## Example Review Scenarios

### Scenario 1: Options Analysis - PASS

**Input:** Options risk analysis with max loss $350, breakeven $183.50, disclaimers present

**Review Result:**
```json
{
  "passed": true,
  "issues": [],
  "required_fixes": [],
  "warnings": ["Using mock options data"],
  "final_disclaimer_present": true
}
```

### Scenario 2: Options Analysis - FAIL

**Input:** Options analysis missing max loss calculation

**Review Result:**
```json
{
  "passed": false,
  "issues": [
    "CRITICAL: Max loss not calculated for option strategy",
    "HIGH: Breakeven not specified"
  ],
  "required_fixes": [
    "Calculate and display max loss",
    "Calculate and display breakeven price"
  ],
  "final_disclaimer_present": true
}
```

### Scenario 3: Paper Trade - FAIL

**Input:** Paper trade proposal without approval gate

**Review Result:**
```json
{
  "passed": false,
  "issues": [
    "CRITICAL: Approval gate not implemented",
    "CRITICAL: Missing 'simulation only' disclaimer"
  ],
  "required_fixes": [
    "Add human approval requirement",
    "Include 'simulation only' disclaimer",
    "Add 'no real orders' statement"
  ]
}
```

## Language Review Guidelines

### Forbidden Phrases
- "This will definitely..."
- "Guaranteed profit..."
- "Can't lose..."
- "Sure thing..."
- "100% certain..."

### Acceptable Phrases
- "Based on current data..."
- "If conditions remain..."
- "Potential risk includes..."
- "May result in..."
- "Could potentially..."

### Required Phrases
- "This is not financial advice"
- "Past performance does not guarantee future results"
- "Trading involves risk"
- "Simulation only" (for paper trades)

## Failure Handling

If safety review fails:
1. Return detailed list of issues
2. Specify required fixes
3. Block final report generation
4. Require agent to revise analysis
5. Re-run safety review after fixes

## Integration with Other Skills

- **All Skills**: Must pass safety review before completion
- **Paper Trade Proposal**: Critical safety gate before approval
- **Options Risk**: Verify all risk metrics present
- **Portfolio Research**: Ensure privacy and data labeling

## Example Usage

**Agent Workflow:**
1. Complete options risk analysis
2. Activate safety-review skill
3. Review finds missing breakeven
4. Agent recalculates breakeven
5. Re-run safety review
6. Review passes
7. Present final report to user

**Safety Review Output:**
```
✓ Safety Review PASSED

Checks Completed:
✓ Max loss calculated: $350
✓ Breakeven calculated: $183.50
✓ Risk level assessed: Medium
✓ Disclaimers present
✓ No guarantee language
✓ Data source labeled: mock
✓ Uncertainty acknowledged

Warnings:
⚠ Using mock options data - ensure user is aware

Recommendations:
• Consider adding more market context
• Include historical volatility comparison

Status: APPROVED FOR PRESENTATION
```

## Automated Checks

The safety review should automate these checks:

1. **Regex Patterns**: Scan for forbidden phrases
2. **Required Fields**: Verify all required data present
3. **Calculation Validation**: Check math is reasonable
4. **Disclaimer Detection**: Ensure disclaimers included
5. **Data Source Labeling**: Verify source is marked
6. **Approval Gate**: Confirm approval flow for sensitive actions

## Final Report Requirements

Before passing safety review, final report must include:

```markdown
# [Analysis Title]

[Analysis content...]

## Risk Disclosure

- Maximum Loss: $XXX
- Breakeven: $XXX
- Risk Level: [Low/Medium/High]

## Important Disclaimers

⚠️ This analysis is for research and educational purposes only.
⚠️ This is not financial advice.
⚠️ Trading involves significant risk of loss.
⚠️ Past performance does not guarantee future results.
⚠️ [Data source: mock/live/MCP] - Data current as of [timestamp]

[For paper trades:]
⚠️ SIMULATION ONLY - No real orders will be placed.