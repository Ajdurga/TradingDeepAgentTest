"""
Pydantic models for the Deep Agent system.
"""
from typing import List, Dict, Any, Optional, Literal
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum


class TaskStatus(str, Enum):
    """Task status enumeration."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class RiskLevel(str, Enum):
    """Risk level enumeration."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class RiskTolerance(str, Enum):
    """User risk tolerance enumeration."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class DataSource(str, Enum):
    """Data source enumeration."""
    MOCK = "mock"
    ROBINHOOD_MCP = "robinhood_mcp"
    LIVE_API = "live_api"


class InstrumentType(str, Enum):
    """Financial instrument type."""
    STOCK = "stock"
    OPTION = "option"
    ETF = "etf"


class OptionType(str, Enum):
    """Option type."""
    CALL = "call"
    PUT = "put"


class ApprovalStatus(str, Enum):
    """Approval status for sensitive actions."""
    PENDING = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"


# Task and Planning Models
class Task(BaseModel):
    """Individual task in the agent's plan."""
    id: str
    description: str
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None


class Plan(BaseModel):
    """Agent execution plan."""
    tasks: List[Task] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# Portfolio Models
class Position(BaseModel):
    """Portfolio position."""
    ticker: str
    quantity: float
    average_cost: float
    current_price: float
    market_value: float
    unrealized_pnl: float
    unrealized_pnl_percent: float


class PortfolioSummary(BaseModel):
    """Portfolio summary."""
    total_equity: float
    cash: float
    num_positions: int
    positions: List[Position] = Field(default_factory=list)
    data_source: DataSource


class PortfolioResearchOutput(BaseModel):
    """Output from portfolio research skill."""
    portfolio_summary: PortfolioSummary
    top_exposures: List[Dict[str, Any]] = Field(default_factory=list)
    risk_notes: List[str] = Field(default_factory=list)
    data_source: DataSource


# Market Data Models
class Quote(BaseModel):
    """Stock quote."""
    ticker: str
    current_price: float
    previous_close: float
    change: float
    change_percent: float
    volume: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class MarketDataOutput(BaseModel):
    """Output from market data skill."""
    ticker: str
    current_price: float
    lookback_days: int
    return_percent: float
    annualized_volatility: float
    trend_summary: str
    support_resistance_notes: List[str] = Field(default_factory=list)
    data_quality_notes: List[str] = Field(default_factory=list)


# Options Models
class OptionContract(BaseModel):
    """Option contract details."""
    ticker: str
    option_type: OptionType
    strike: float
    expiration: str  # YYYY-MM-DD
    premium: float
    implied_volatility: Optional[float] = None
    delta: Optional[float] = None
    gamma: Optional[float] = None
    theta: Optional[float] = None
    vega: Optional[float] = None


class OptionsRiskOutput(BaseModel):
    """Output from options risk skill."""
    ticker: str
    strategy: str
    expiration: str
    strike: float
    premium: float
    max_loss: float
    breakeven: float
    estimated_risk_level: RiskLevel
    key_risks: List[str] = Field(default_factory=list)
    invalidating_conditions: List[str] = Field(default_factory=list)


# Paper Trade Models
class PaperTradeProposal(BaseModel):
    """Paper trade proposal."""
    proposal_id: str
    status: ApprovalStatus = ApprovalStatus.PENDING
    ticker: str
    instrument_type: InstrumentType
    strategy: str
    rationale: str
    max_loss: float
    approval_required: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    approved_at: Optional[datetime] = None


# Safety Review Models
class SafetyReviewOutput(BaseModel):
    """Output from safety review skill."""
    passed: bool
    issues: List[str] = Field(default_factory=list)
    required_fixes: List[str] = Field(default_factory=list)
    final_disclaimer_present: bool


# Memory Models
class UserPreferences(BaseModel):
    """User preferences stored in memory."""
    risk_tolerance: RiskTolerance = RiskTolerance.MEDIUM
    max_position_risk_percent: float = 2.0
    watchlist: List[str] = Field(default_factory=list)


class MemoryEntry(BaseModel):
    """Generic memory entry."""
    key: str
    value: Dict[str, Any]
    confidence: Literal["low", "medium", "high"] = "medium"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# Tool Result Models
class ToolResult(BaseModel):
    """Result from tool execution."""
    tool_name: str
    success: bool
    result: Any
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# Agent Run Models
class AgentRunResult(BaseModel):
    """Final result from agent run."""
    run_id: str
    user_prompt: str
    plan: Plan
    skills_used: List[str] = Field(default_factory=list)
    tools_called: List[str] = Field(default_factory=list)
    final_report: str
    workspace_artifacts: List[str] = Field(default_factory=list)
    safety_review_passed: bool
    approval_required: bool = False
    approval_status: Optional[ApprovalStatus] = None
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    success: bool = True
    error: Optional[str] = None


# Skill Models
class Skill(BaseModel):
    """Skill definition."""
    name: str
    description: str
    skill_path: str
    content: str


# Approval Request Models
class ApprovalRequest(BaseModel):
    """Request for human approval."""
    action: str
    reason: str
    requires_approval: bool = True
    approved: bool = False
    details: Dict[str, Any] = Field(default_factory=dict)


# Subagent Models
class SubagentResult(BaseModel):
    """Result from subagent execution."""
    subagent_name: str
    success: bool
    output: Dict[str, Any]
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class MarketResearchSubagentOutput(BaseModel):
    """Output from market research subagent."""
    ticker: str
    market_context_summary: str
    bullish_points: List[str] = Field(default_factory=list)
    bearish_points: List[str] = Field(default_factory=list)
    uncertainties: List[str] = Field(default_factory=list)


class OptionsAnalystSubagentOutput(BaseModel):
    """Output from options analyst subagent."""
    strategy: str
    risk_reward_summary: str
    max_loss: float
    breakeven: float
    key_option_risks: List[str] = Field(default_factory=list)


class RiskReviewerSubagentOutput(BaseModel):
    """Output from risk reviewer subagent."""
    approved: bool
    issues: List[str] = Field(default_factory=list)
    fixes_required: List[str] = Field(default_factory=list)

# Made with Bob
