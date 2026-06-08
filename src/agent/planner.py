"""
Planning and task management for the Deep Agent.
"""
import uuid
from typing import List, Optional
from datetime import datetime
import logging

from src.models.schemas import Task, Plan, TaskStatus

logger = logging.getLogger(__name__)


class Planner:
    """Manages agent planning and task tracking."""
    
    def __init__(self):
        """Initialize planner."""
        self.current_plan: Optional[Plan] = None
        logger.info("Planner initialized")
    
    def create_plan(self, user_prompt: str, initial_tasks: Optional[List[str]] = None) -> Plan:
        """
        Create a new plan based on user prompt.
        
        Args:
            user_prompt: User's request
            initial_tasks: Optional list of initial task descriptions
            
        Returns:
            New plan
        """
        tasks = []
        
        if initial_tasks:
            for desc in initial_tasks:
                task = Task(
                    id=f"task-{uuid.uuid4().hex[:8]}",
                    description=desc,
                    status=TaskStatus.PENDING
                )
                tasks.append(task)
        
        self.current_plan = Plan(tasks=tasks)
        logger.info(f"Created plan with {len(tasks)} tasks")
        return self.current_plan
    
    def add_task(self, description: str) -> Task:
        """
        Add a new task to the current plan.
        
        Args:
            description: Task description
            
        Returns:
            New task
        """
        if not self.current_plan:
            self.current_plan = Plan()
        
        task = Task(
            id=f"task-{uuid.uuid4().hex[:8]}",
            description=description,
            status=TaskStatus.PENDING
        )
        
        self.current_plan.tasks.append(task)
        self.current_plan.updated_at = datetime.utcnow()
        
        logger.info(f"Added task: {description}")
        return task
    
    def update_task_status(self, task_id: str, status: TaskStatus) -> None:
        """
        Update the status of a task.
        
        Args:
            task_id: Task identifier
            status: New status
        """
        if not self.current_plan:
            logger.warning("No current plan to update")
            return
        
        for task in self.current_plan.tasks:
            if task.id == task_id:
                task.status = status
                if status == TaskStatus.COMPLETED:
                    task.completed_at = datetime.utcnow()
                self.current_plan.updated_at = datetime.utcnow()
                logger.info(f"Updated task {task_id} to {status}")
                return
        
        logger.warning(f"Task {task_id} not found in plan")
    
    def get_next_pending_task(self) -> Optional[Task]:
        """
        Get the next pending task.
        
        Returns:
            Next pending task or None
        """
        if not self.current_plan:
            return None
        
        for task in self.current_plan.tasks:
            if task.status == TaskStatus.PENDING:
                return task
        
        return None
    
    def get_in_progress_tasks(self) -> List[Task]:
        """
        Get all in-progress tasks.
        
        Returns:
            List of in-progress tasks
        """
        if not self.current_plan:
            return []
        
        return [t for t in self.current_plan.tasks if t.status == TaskStatus.IN_PROGRESS]
    
    def get_completed_tasks(self) -> List[Task]:
        """
        Get all completed tasks.
        
        Returns:
            List of completed tasks
        """
        if not self.current_plan:
            return []
        
        return [t for t in self.current_plan.tasks if t.status == TaskStatus.COMPLETED]
    
    def is_plan_complete(self) -> bool:
        """
        Check if all tasks in the plan are completed.
        
        Returns:
            True if plan is complete
        """
        if not self.current_plan or not self.current_plan.tasks:
            return False
        
        return all(t.status == TaskStatus.COMPLETED for t in self.current_plan.tasks)
    
    def get_plan_summary(self) -> str:
        """
        Get a text summary of the current plan.
        
        Returns:
            Plan summary
        """
        if not self.current_plan:
            return "No active plan"
        
        lines = ["Current Plan:"]
        for task in self.current_plan.tasks:
            status_symbol = {
                TaskStatus.PENDING: "[ ]",
                TaskStatus.IN_PROGRESS: "[-]",
                TaskStatus.COMPLETED: "[x]",
                TaskStatus.FAILED: "[!]"
            }.get(task.status, "[ ]")
            
            lines.append(f"{status_symbol} {task.description}")
        
        return "\n".join(lines)
    
    def get_plan_dict(self) -> dict:
        """
        Get plan as dictionary.
        
        Returns:
            Plan dictionary
        """
        if not self.current_plan:
            return {"tasks": []}
        
        return self.current_plan.model_dump()
    
    def mark_task_in_progress(self, task_id: str) -> None:
        """
        Mark a task as in progress.
        
        Args:
            task_id: Task identifier
        """
        self.update_task_status(task_id, TaskStatus.IN_PROGRESS)
    
    def mark_task_completed(self, task_id: str) -> None:
        """
        Mark a task as completed.
        
        Args:
            task_id: Task identifier
        """
        self.update_task_status(task_id, TaskStatus.COMPLETED)
    
    def mark_task_failed(self, task_id: str) -> None:
        """
        Mark a task as failed.
        
        Args:
            task_id: Task identifier
        """
        self.update_task_status(task_id, TaskStatus.FAILED)

# Made with Bob
