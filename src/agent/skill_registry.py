"""
Skill discovery and management for the Deep Agent.
"""
import os
import re
from pathlib import Path
from typing import List, Dict, Optional
import logging

from src.models.schemas import Skill

logger = logging.getLogger(__name__)


class SkillRegistry:
    """Discovers and manages agent skills."""
    
    def __init__(self, skills_dir: str = "./skills"):
        """
        Initialize skill registry.
        
        Args:
            skills_dir: Directory containing skill folders
        """
        self.skills_dir = Path(skills_dir)
        self.skills: Dict[str, Skill] = {}
        
        if self.skills_dir.exists():
            self.discover_skills()
        else:
            logger.warning(f"Skills directory not found: {self.skills_dir}")
    
    def discover_skills(self) -> List[Skill]:
        """
        Discover all skills in the skills directory.
        
        Returns:
            List of discovered skills
        """
        self.skills.clear()
        
        if not self.skills_dir.exists():
            logger.warning(f"Skills directory does not exist: {self.skills_dir}")
            return []
        
        for skill_dir in self.skills_dir.iterdir():
            if not skill_dir.is_dir():
                continue
            
            skill_file = skill_dir / "SKILL.md"
            if not skill_file.exists():
                logger.warning(f"No SKILL.md found in {skill_dir}")
                continue
            
            try:
                skill = self._load_skill(skill_file)
                self.skills[skill.name] = skill
                logger.info(f"Loaded skill: {skill.name}")
            except Exception as e:
                logger.error(f"Error loading skill from {skill_file}: {e}")
        
        logger.info(f"Discovered {len(self.skills)} skills")
        return list(self.skills.values())
    
    def _load_skill(self, skill_file: Path) -> Skill:
        """
        Load a skill from a SKILL.md file.
        
        Args:
            skill_file: Path to SKILL.md file
            
        Returns:
            Skill object
        """
        with open(skill_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse YAML frontmatter
        frontmatter_match = re.match(r'^---\s*\n(.*?)\n---\s*\n(.*)$', content, re.DOTALL)
        
        if not frontmatter_match:
            raise ValueError(f"Invalid SKILL.md format in {skill_file}")
        
        frontmatter = frontmatter_match.group(1)
        body = frontmatter_match.group(2)
        
        # Parse frontmatter fields
        name = self._extract_yaml_field(frontmatter, 'name')
        description = self._extract_yaml_field(frontmatter, 'description')
        
        if not name or not description:
            raise ValueError(f"Missing required fields (name, description) in {skill_file}")
        
        return Skill(
            name=name,
            description=description,
            skill_path=str(skill_file),
            content=body.strip()
        )
    
    def _extract_yaml_field(self, yaml_text: str, field: str) -> Optional[str]:
        """
        Extract a field from YAML frontmatter.
        
        Args:
            yaml_text: YAML text
            field: Field name
            
        Returns:
            Field value or None
        """
        pattern = rf'^{field}:\s*(.+?)$'
        match = re.search(pattern, yaml_text, re.MULTILINE)
        
        if match:
            value = match.group(1).strip()
            # Remove quotes if present
            value = value.strip('"\'')
            return value
        
        return None
    
    def get_skill(self, name: str) -> Optional[Skill]:
        """
        Get a skill by name.
        
        Args:
            name: Skill name
            
        Returns:
            Skill object or None
        """
        return self.skills.get(name)
    
    def list_skills(self) -> List[str]:
        """
        List all available skill names.
        
        Returns:
            List of skill names
        """
        return list(self.skills.keys())
    
    def get_skill_descriptions(self) -> Dict[str, str]:
        """
        Get all skill names and descriptions.
        
        Returns:
            Dictionary mapping skill names to descriptions
        """
        return {name: skill.description for name, skill in self.skills.items()}
    
    def select_skill(self, user_prompt: str, context: Optional[str] = None) -> Optional[str]:
        """
        Select the most appropriate skill for a user prompt.
        This is a simple keyword-based selector. In production, this would use
        an LLM to make the selection.
        
        Args:
            user_prompt: User's request
            context: Optional context
            
        Returns:
            Selected skill name or None
        """
        prompt_lower = user_prompt.lower()
        
        # Keyword-based skill selection
        skill_keywords = {
            'portfolio-research': ['portfolio', 'holdings', 'positions', 'exposure', 'account'],
            'market-data': ['price', 'ticker', 'stock', 'market', 'quote', 'volatility', 'trend'],
            'options-risk': ['option', 'call', 'put', 'strike', 'expiration', 'greek', 'breakeven'],
            'paper-trade-proposal': ['paper trade', 'simulate', 'proposal', 'trade idea'],
            'safety-review': ['review', 'safety', 'check', 'validate'],
            'memory-management': ['remember', 'memory', 'preference', 'watchlist', 'prior']
        }
        
        # Score each skill
        scores = {}
        for skill_name, keywords in skill_keywords.items():
            score = sum(1 for keyword in keywords if keyword in prompt_lower)
            if score > 0:
                scores[skill_name] = score
        
        if not scores:
            logger.warning("No skill matched the prompt")
            return None
        
        # Return skill with highest score
        selected_skill = max(scores.items(), key=lambda x: x[1])[0]
        logger.info(f"Selected skill: {selected_skill}")
        return selected_skill
    
    def get_skill_content(self, name: str) -> Optional[str]:
        """
        Get the full content of a skill.
        
        Args:
            name: Skill name
            
        Returns:
            Skill content or None
        """
        skill = self.get_skill(name)
        return skill.content if skill else None
    
    def reload_skills(self) -> List[Skill]:
        """
        Reload all skills from disk.
        
        Returns:
            List of reloaded skills
        """
        logger.info("Reloading skills...")
        return self.discover_skills()

# Made with Bob
