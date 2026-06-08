"""
Workspace management for the Deep Agent.
Handles file I/O for agent artifacts, observations, and reports.
"""
import os
import json
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class Workspace:
    """Manages the agent's workspace for storing artifacts and intermediate results."""
    
    def __init__(self, base_dir: str = "./workspace"):
        """
        Initialize workspace.
        
        Args:
            base_dir: Base directory for workspace
        """
        self.base_dir = Path(base_dir)
        self.runs_dir = self.base_dir / "runs"
        self.memory_dir = self.base_dir / "memory"
        
        # Create directories if they don't exist
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.runs_dir.mkdir(parents=True, exist_ok=True)
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Workspace initialized at {self.base_dir}")
    
    def create_run_directory(self, run_id: str) -> Path:
        """
        Create a directory for a specific run.
        
        Args:
            run_id: Unique run identifier
            
        Returns:
            Path to the run directory
        """
        run_dir = self.runs_dir / run_id
        run_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Created run directory: {run_dir}")
        return run_dir
    
    def write_file(self, path: str, content: str, run_id: Optional[str] = None) -> str:
        """
        Write content to a file in the workspace.
        
        Args:
            path: Relative path within workspace
            content: Content to write
            run_id: Optional run ID to write to run-specific directory
            
        Returns:
            Absolute path to the written file
        """
        if run_id:
            full_path = self.runs_dir / run_id / path
        else:
            full_path = self.base_dir / path
        
        # Create parent directories if needed
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write content
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"Wrote file: {full_path}")
        return str(full_path)
    
    def write_json(self, path: str, data: Dict[str, Any], run_id: Optional[str] = None) -> str:
        """
        Write JSON data to a file.
        
        Args:
            path: Relative path within workspace
            data: Data to write as JSON
            run_id: Optional run ID
            
        Returns:
            Absolute path to the written file
        """
        content = json.dumps(data, indent=2, default=str)
        return self.write_file(path, content, run_id)
    
    def read_file(self, path: str, run_id: Optional[str] = None) -> str:
        """
        Read content from a file in the workspace.
        
        Args:
            path: Relative path within workspace
            run_id: Optional run ID
            
        Returns:
            File content
        """
        if run_id:
            full_path = self.runs_dir / run_id / path
        else:
            full_path = self.base_dir / path
        
        if not full_path.exists():
            raise FileNotFoundError(f"File not found: {full_path}")
        
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        logger.debug(f"Read file: {full_path}")
        return content
    
    def read_json(self, path: str, run_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Read JSON data from a file.
        
        Args:
            path: Relative path within workspace
            run_id: Optional run ID
            
        Returns:
            Parsed JSON data
        """
        content = self.read_file(path, run_id)
        return json.loads(content)
    
    def file_exists(self, path: str, run_id: Optional[str] = None) -> bool:
        """
        Check if a file exists in the workspace.
        
        Args:
            path: Relative path within workspace
            run_id: Optional run ID
            
        Returns:
            True if file exists
        """
        if run_id:
            full_path = self.runs_dir / run_id / path
        else:
            full_path = self.base_dir / path
        
        return full_path.exists()
    
    def list_files(self, directory: str = "", run_id: Optional[str] = None) -> List[str]:
        """
        List files in a directory.
        
        Args:
            directory: Relative directory path
            run_id: Optional run ID
            
        Returns:
            List of file paths
        """
        if run_id:
            full_path = self.runs_dir / run_id / directory
        else:
            full_path = self.base_dir / directory
        
        if not full_path.exists():
            return []
        
        files = []
        for item in full_path.rglob("*"):
            if item.is_file():
                rel_path = item.relative_to(full_path)
                files.append(str(rel_path))
        
        return files
    
    def get_run_artifacts(self, run_id: str) -> List[str]:
        """
        Get list of all artifacts for a specific run.
        
        Args:
            run_id: Run identifier
            
        Returns:
            List of artifact file paths
        """
        return self.list_files(run_id=run_id)
    
    def append_to_file(self, path: str, content: str, run_id: Optional[str] = None) -> str:
        """
        Append content to a file.
        
        Args:
            path: Relative path within workspace
            content: Content to append
            run_id: Optional run ID
            
        Returns:
            Absolute path to the file
        """
        if run_id:
            full_path = self.runs_dir / run_id / path
        else:
            full_path = self.base_dir / path
        
        # Create parent directories if needed
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Append content
        with open(full_path, 'a', encoding='utf-8') as f:
            f.write(content)
        
        logger.debug(f"Appended to file: {full_path}")
        return str(full_path)
    
    def create_observation_log(self, run_id: str, observation: str) -> None:
        """
        Log an observation to the run's observation file.
        
        Args:
            run_id: Run identifier
            observation: Observation text
        """
        timestamp = datetime.utcnow().isoformat()
        log_entry = f"\n[{timestamp}]\n{observation}\n"
        self.append_to_file("observations.md", log_entry, run_id)
    
    def save_plan(self, run_id: str, plan: Dict[str, Any]) -> None:
        """
        Save the agent's plan to the workspace.
        
        Args:
            run_id: Run identifier
            plan: Plan data
        """
        self.write_json("plan.json", plan, run_id)
    
    def save_final_report(self, run_id: str, report: str) -> None:
        """
        Save the final report to the workspace.
        
        Args:
            run_id: Run identifier
            report: Report content
        """
        self.write_file("final_report.md", report, run_id)
    
    def get_memory_path(self, key: str) -> Path:
        """
        Get the path for a memory file.
        
        Args:
            key: Memory key
            
        Returns:
            Path to memory file
        """
        return self.memory_dir / f"{key}.json"

# Made with Bob
