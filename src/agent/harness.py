"""
Deep Agent Harness - Main execution loop using LangChain.
"""
import os
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import AgentExecutor, create_structured_chat_agent
from langchain.tools import Tool
from langchain_core.messages import SystemMessage, HumanMessage

from src.agent.planner import Planner
from src.agent.skill_registry import SkillRegistry
from src.agent.workspace import Workspace
from src.agent.memory import MemoryManager
from src.tools.market_data import MarketDataTools
from src.tools.options_data import OptionsDataTools
from src.tools.portfolio import PortfolioTools
from src.tools.trade_execution import TradeExecutionTools
from src.models.schemas import AgentRunResult, TaskStatus

logger = logging.getLogger(__name__)


class DeepAgentHarness:
    """Main agent harness for orchestrating the Deep Agent system."""
    
    def __init__(
        self,
        google_api_key: Optional[str] = None,
        model: str = "gemini-pro",
        workspace_dir: str = "./workspace",
        skills_dir: str = "./skills",
        max_iterations: int = 20
    ):
        """
        Initialize the Deep Agent Harness.
        
        Args:
            google_api_key: Google API key for Gemini
            model: Model to use (gemini-pro, gemini-1.5-pro, etc.)
            workspace_dir: Workspace directory
            skills_dir: Skills directory
            max_iterations: Maximum agent iterations
        """
        # Get API key from env if not provided
        self.api_key = google_api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("Google API key not provided")
        
        self.model = model
        self.max_iterations = max_iterations
        
        # Initialize components
        self.workspace = Workspace(workspace_dir)
        self.memory_manager = MemoryManager(f"{workspace_dir}/memory")
        self.planner = Planner()
        self.skill_registry = SkillRegistry(skills_dir)
        
        # Initialize tools (Yahoo Finance for market data, mock for others)
        self.market_data_tools = MarketDataTools(use_mock=False)  # Use Yahoo Finance
        self.options_tools = OptionsDataTools(use_mock=True)  # Mock options data
        self.portfolio_tools = PortfolioTools(use_mock=True)  # Mock portfolio
        self.trade_tools = TradeExecutionTools(
            broker_api_enabled=False
        )
        
        # Initialize LLM with Gemini
        self.llm = ChatGoogleGenerativeAI(
            model=model,
            temperature=0.1,
            google_api_key=self.api_key,
            convert_system_message_to_human=True
        )
        
        # Create agent tools
        self.tools = self._create_tools()
        
        # Create agent
        self.agent = self._create_agent()
        
        logger.info(
            f"Deep Agent Harness initialized (model={model})"
        )
    
    def _create_tools(self) -> List[Tool]:
        """Create LangChain tools from our tool classes."""
        tools = []
        
        # Market data tools
        tools.append(Tool(
            name="get_market_data",
            func=lambda ticker: self.market_data_tools.get_market_data_analysis(ticker),
            description="Get market data analysis for a stock ticker including price, volatility, and trend"
        ))
        
        # Options tools
        tools.append(Tool(
            name="analyze_option_risk",
            func=lambda params: self.options_tools.analyze_option_risk(**params),
            description="Analyze risk for an option contract. Requires ticker, option_type, strike, expiration"
        ))
        
        # Portfolio tools
        tools.append(Tool(
            name="analyze_portfolio",
            func=lambda: self.portfolio_tools.analyze_portfolio(),
            description="Analyze current portfolio for exposures and concentration risks"
        ))
        
        # Memory tools
        tools.append(Tool(
            name="read_memory",
            func=lambda key: self.memory_manager.read(key),
            description="Read from persistent memory. Keys: user_preferences, prior_research, rejected_ideas"
        ))
        
        tools.append(Tool(
            name="write_memory",
            func=lambda params: self.memory_manager.write(params["key"], params["value"]),
            description="Write to persistent memory"
        ))
        
        # Workspace tools
        tools.append(Tool(
            name="write_workspace_file",
            func=lambda params: self.workspace.write_json(
                params["path"], params["data"], params.get("run_id")
            ),
            description="Write JSON data to workspace"
        ))
        
        tools.append(Tool(
            name="read_workspace_file",
            func=lambda params: self.workspace.read_json(
                params["path"], params.get("run_id")
            ),
            description="Read JSON data from workspace"
        ))
        
        return tools
    
    def _create_agent(self) -> AgentExecutor:
        """Create the LangChain agent."""
        # Create system prompt
        system_prompt = """You are a Deep Agent for portfolio research and options risk analysis.

Your capabilities:
- Analyze stock market data and trends
- Evaluate options risk with Greeks and breakeven calculations
- Review portfolio exposures and concentration risks
- Create paper trade proposals or real trade proposals (with approval)
- Maintain memory of prior research and user preferences
- Use specialized skills for different tasks

Available skills:
{skills}

Safety rules:
- Always calculate max loss for options
- Always calculate breakeven for options
- Include disclaimers in final reports
- For real trades: require human approval and check safety limits
- Label mock data clearly
- Acknowledge uncertainty

Your workflow:
1. Understand the user's request
2. Create a plan with specific tasks
3. Select appropriate skills
4. Execute tools to gather data
5. Analyze and synthesize findings
6. Run safety review
7. Present final report

Current user preferences:
{user_preferences}
"""
        
        # Get skills description
        skills_desc = "\n".join([
            f"- {name}: {desc}"
            for name, desc in self.skill_registry.get_skill_descriptions().items()
        ])
        
        # Get user preferences
        user_prefs = self.memory_manager.get_user_preferences()
        prefs_str = f"Risk Tolerance: {user_prefs.risk_tolerance}, Max Position Risk: {user_prefs.max_position_risk_percent}%"
        
        # Create prompt template
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt.format(skills=skills_desc, user_preferences=prefs_str)),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        # Create agent (using structured chat for Gemini compatibility)
        agent = create_structured_chat_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt
        )
        
        # Create executor
        executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,
            max_iterations=self.max_iterations,
            handle_parsing_errors=True
        )
        
        return executor
    
    def run(self, user_prompt: str) -> AgentRunResult:
        """
        Run the agent on a user prompt.
        
        Args:
            user_prompt: User's request
            
        Returns:
            Agent run result
        """
        run_id = f"run-{uuid.uuid4().hex[:8]}"
        started_at = datetime.utcnow()
        
        logger.info(f"Starting agent run {run_id}")
        logger.info(f"User prompt: {user_prompt}")
        
        # Create run directory
        self.workspace.create_run_directory(run_id)
        
        # Create initial plan
        initial_tasks = self._generate_initial_tasks(user_prompt)
        plan = self.planner.create_plan(user_prompt, initial_tasks)
        
        # Save plan
        self.workspace.save_plan(run_id, plan.model_dump())
        
        # Log observation
        self.workspace.create_observation_log(
            run_id,
            f"Starting analysis: {user_prompt}"
        )
        
        try:
            # Run agent
            result = self.agent.invoke({
                "input": user_prompt,
                "chat_history": []
            })
            
            # Extract output
            final_output = result.get("output", "No output generated")
            
            # Mark plan as complete
            for task in self.planner.current_plan.tasks:
                if task.status != TaskStatus.COMPLETED:
                    self.planner.mark_task_completed(task.id)
            
            # Save final report
            self.workspace.save_final_report(run_id, final_output)
            
            # Create result
            agent_result = AgentRunResult(
                run_id=run_id,
                user_prompt=user_prompt,
                plan=self.planner.current_plan,
                skills_used=self._extract_skills_used(result),
                tools_called=self._extract_tools_called(result),
                final_report=final_output,
                workspace_artifacts=self.workspace.get_run_artifacts(run_id),
                safety_review_passed=True,  # TODO: Implement actual safety review
                started_at=started_at,
                completed_at=datetime.utcnow(),
                success=True
            )
            
            logger.info(f"Agent run {run_id} completed successfully")
            return agent_result
            
        except Exception as e:
            logger.error(f"Agent run {run_id} failed: {e}")
            
            # Create error result
            agent_result = AgentRunResult(
                run_id=run_id,
                user_prompt=user_prompt,
                plan=self.planner.current_plan,
                skills_used=[],
                tools_called=[],
                final_report=f"Error: {str(e)}",
                workspace_artifacts=[],
                safety_review_passed=False,
                started_at=started_at,
                completed_at=datetime.utcnow(),
                success=False,
                error=str(e)
            )
            
            return agent_result
    
    def _generate_initial_tasks(self, user_prompt: str) -> List[str]:
        """Generate initial tasks based on user prompt."""
        prompt_lower = user_prompt.lower()
        tasks = []
        
        if "portfolio" in prompt_lower or "holdings" in prompt_lower:
            tasks.append("Fetch and analyze portfolio data")
        
        if "option" in prompt_lower or "call" in prompt_lower or "put" in prompt_lower:
            tasks.append("Analyze option risk and Greeks")
        
        if any(word in prompt_lower for word in ["price", "stock", "market", "ticker"]):
            tasks.append("Fetch market data and analyze trends")
        
        if "trade" in prompt_lower or "buy" in prompt_lower or "sell" in prompt_lower:
            tasks.append("Create trade proposal with risk analysis")
            tasks.append("Request human approval if real trade")
        
        tasks.append("Run safety review")
        tasks.append("Generate final report")
        
        return tasks
    
    def _extract_skills_used(self, result: Dict[str, Any]) -> List[str]:
        """Extract skills used from agent result."""
        # TODO: Implement skill tracking
        return []
    
    def _extract_tools_called(self, result: Dict[str, Any]) -> List[str]:
        """Extract tools called from agent result."""
        # TODO: Implement tool tracking
        return []

# Made with Bob
