"""
Memory management for the Deep Agent.
Handles persistent storage of user preferences, prior research, and context.
"""
import json
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime
import logging

from src.models.schemas import UserPreferences, MemoryEntry, RiskTolerance

logger = logging.getLogger(__name__)


class MemoryManager:
    """Manages agent memory for persistent context and preferences."""
    
    def __init__(self, memory_dir: str = "./workspace/memory"):
        """
        Initialize memory manager.
        
        Args:
            memory_dir: Directory for memory storage
        """
        self.memory_dir = Path(memory_dir)
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize default memory files
        self._initialize_defaults()
        
        logger.info(f"Memory manager initialized at {self.memory_dir}")
    
    def _initialize_defaults(self) -> None:
        """Initialize default memory files if they don't exist."""
        # User preferences
        if not self._file_exists("user_preferences"):
            default_prefs = UserPreferences(
                risk_tolerance=RiskTolerance.MEDIUM,
                max_position_risk_percent=2.0,
                watchlist=[]
            )
            self.write("user_preferences", default_prefs.model_dump())
        
        # Prior research
        if not self._file_exists("prior_research"):
            self.write("prior_research", [])
        
        # Rejected ideas
        if not self._file_exists("rejected_ideas"):
            self.write("rejected_ideas", [])
    
    def _get_file_path(self, key: str) -> Path:
        """Get the file path for a memory key."""
        return self.memory_dir / f"{key}.json"
    
    def _file_exists(self, key: str) -> bool:
        """Check if a memory file exists."""
        return self._get_file_path(key).exists()
    
    def read(self, key: str) -> Dict[str, Any]:
        """
        Read memory by key.
        
        Args:
            key: Memory key
            
        Returns:
            Memory data
        """
        file_path = self._get_file_path(key)
        
        if not file_path.exists():
            logger.warning(f"Memory key not found: {key}")
            return {}
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            logger.debug(f"Read memory: {key}")
            return data
        except Exception as e:
            logger.error(f"Error reading memory {key}: {e}")
            return {}
    
    def write(self, key: str, value: Any) -> None:
        """
        Write memory by key.
        
        Args:
            key: Memory key
            value: Memory data (can be dict or list)
        """
        file_path = self._get_file_path(key)
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(value, f, indent=2, default=str)
            logger.info(f"Wrote memory: {key}")
        except Exception as e:
            logger.error(f"Error writing memory {key}: {e}")
            raise
    
    def search_memory(self, query: str, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Search memory for entries matching a query.
        
        Args:
            query: Search query
            category: Optional category to search within
            
        Returns:
            List of matching memory entries
        """
        results = []
        query_lower = query.lower()
        
        # Determine which files to search
        if category:
            files_to_search = [category]
        else:
            files_to_search = ["prior_research", "rejected_ideas", "user_preferences"]
        
        for key in files_to_search:
            if not self._file_exists(key):
                continue
            
            data = self.read(key)
            
            # Search in the data
            if isinstance(data, list):
                for item in data:
                    if self._matches_query(item, query_lower):
                        results.append({"category": key, "data": item})
            elif isinstance(data, dict):
                if self._matches_query(data, query_lower):
                    results.append({"category": key, "data": data})
        
        logger.debug(f"Memory search for '{query}' found {len(results)} results")
        return results
    
    def _matches_query(self, data: Any, query: str) -> bool:
        """Check if data matches the search query."""
        data_str = json.dumps(data, default=str).lower()
        return query in data_str
    
    def summarize_memory(self, category: Optional[str] = None) -> str:
        """
        Generate a summary of memory contents.
        
        Args:
            category: Optional category to summarize
            
        Returns:
            Memory summary text
        """
        summary_parts = []
        
        if category:
            categories = [category]
        else:
            categories = ["user_preferences", "prior_research", "rejected_ideas"]
        
        for cat in categories:
            if not self._file_exists(cat):
                continue
            
            data = self.read(cat)
            
            if cat == "user_preferences":
                summary_parts.append(f"User Preferences: {json.dumps(data, indent=2)}")
            elif cat == "prior_research":
                count = len(data) if isinstance(data, list) else 0
                summary_parts.append(f"Prior Research: {count} entries")
            elif cat == "rejected_ideas":
                count = len(data) if isinstance(data, list) else 0
                summary_parts.append(f"Rejected Ideas: {count} entries")
        
        return "\n\n".join(summary_parts)
    
    def add_research_entry(self, ticker: str, summary: str, analysis: Dict[str, Any]) -> None:
        """
        Add a research entry to memory.
        
        Args:
            ticker: Stock ticker
            summary: Research summary
            analysis: Analysis data
        """
        prior_research = self.read("prior_research")
        if not isinstance(prior_research, list):
            prior_research = []
        
        entry = {
            "ticker": ticker,
            "summary": summary,
            "analysis": analysis,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        prior_research.append(entry)
        self.write("prior_research", prior_research)
        logger.info(f"Added research entry for {ticker}")
    
    def add_rejected_idea(self, ticker: str, reason: str, details: Dict[str, Any]) -> None:
        """
        Add a rejected trade idea to memory.
        
        Args:
            ticker: Stock ticker
            reason: Rejection reason
            details: Additional details
        """
        rejected_ideas = self.read("rejected_ideas")
        if not isinstance(rejected_ideas, list):
            rejected_ideas = []
        
        entry = {
            "ticker": ticker,
            "reason": reason,
            "details": details,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        rejected_ideas.append(entry)
        self.write("rejected_ideas", rejected_ideas)
        logger.info(f"Added rejected idea for {ticker}")
    
    def get_user_preferences(self) -> UserPreferences:
        """
        Get user preferences.
        
        Returns:
            User preferences object
        """
        data = self.read("user_preferences")
        return UserPreferences(**data)
    
    def update_user_preferences(self, preferences: UserPreferences) -> None:
        """
        Update user preferences.
        
        Args:
            preferences: Updated preferences
        """
        self.write("user_preferences", preferences.model_dump())
        logger.info("Updated user preferences")
    
    def add_to_watchlist(self, ticker: str) -> None:
        """
        Add a ticker to the watchlist.
        
        Args:
            ticker: Stock ticker
        """
        prefs = self.get_user_preferences()
        if ticker not in prefs.watchlist:
            prefs.watchlist.append(ticker)
            self.update_user_preferences(prefs)
            logger.info(f"Added {ticker} to watchlist")
    
    def remove_from_watchlist(self, ticker: str) -> None:
        """
        Remove a ticker from the watchlist.
        
        Args:
            ticker: Stock ticker
        """
        prefs = self.get_user_preferences()
        if ticker in prefs.watchlist:
            prefs.watchlist.remove(ticker)
            self.update_user_preferences(prefs)
            logger.info(f"Removed {ticker} from watchlist")
    
    def clear_category(self, category: str) -> None:
        """
        Clear all entries in a memory category.
        
        Args:
            category: Category to clear
        """
        if category == "user_preferences":
            logger.warning("Cannot clear user_preferences, resetting to defaults")
            self._initialize_defaults()
        else:
            self.write(category, [])
            logger.info(f"Cleared memory category: {category}")

# Made with Bob
