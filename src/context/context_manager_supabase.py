"""
Context Manager with Supabase Persistence
Implements framework Layer 5: Context Management
Version: 1.0.0
Date: January 9, 2026
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum
from dataclasses import dataclass
import json
import hashlib

class ContextStrategy(str, Enum):
    """Context optimization strategies."""
    SLIDING_WINDOW = "sliding_window"
    PRIORITY_BASED = "priority_based"
    FORECAST_ENGINE_BASED = "forecast_engine_based"
    HYBRID = "hybrid"

@dataclass
class ContextCheckpoint:
    """Checkpoint of workflow context state."""
    id: str
    workflow_id: str
    stage: str
    timestamp: datetime
    state_data: Dict[str, Any]
    token_count: int
    message_count: int

class BidDeedContextManager:
    """Manages context lifecycle with Supabase persistence."""
    
    def __init__(
        self,
        supabase_client,
        max_tokens: int = 100000,
        strategy: ContextStrategy = ContextStrategy.FORECAST_ENGINE_BASED
    ):
        self.supabase = supabase_client
        self.max_tokens = max_tokens
        self.strategy = strategy
        self._current_context: Dict[str, Any] = {}
        self._checkpoints: List[ContextCheckpoint] = []
    
    async def create_checkpoint(
        self,
        workflow_id: str,
        stage: str,
        state_data: Dict[str, Any]
    ) -> ContextCheckpoint:
        """Create checkpoint and persist to Supabase."""
        checkpoint_id = f"{workflow_id}_{stage}_{datetime.utcnow().isoformat()}"
        
        checkpoint = ContextCheckpoint(
            id=checkpoint_id,
            workflow_id=workflow_id,
            stage=stage,
            timestamp=datetime.utcnow(),
            state_data=state_data,
            token_count=self._estimate_tokens(state_data),
            message_count=len(state_data.get("messages", []))
        )
        
        # Persist to Supabase
        try:
            self.supabase.table("workflow_checkpoints").insert({
                "id": checkpoint.id,
                "workflow_id": checkpoint.workflow_id,
                "stage": checkpoint.stage,
                "timestamp": checkpoint.timestamp.isoformat(),
                "state_data": json.dumps(checkpoint.state_data),
                "token_count": checkpoint.token_count,
                "message_count": checkpoint.message_count
            }).execute()
        except Exception as e:
            print(f"Warning: Failed to persist checkpoint to Supabase: {e}")
        
        self._checkpoints.append(checkpoint)
        return checkpoint
    
    async def restore_checkpoint(self, checkpoint_id: str) -> Dict[str, Any]:
        """Restore context from checkpoint."""
        try:
            response = self.supabase.table("workflow_checkpoints").select("*").eq(
                "id", checkpoint_id
            ).execute()
            
            if response.data:
                data = response.data[0]
                return json.loads(data["state_data"])
        except Exception as e:
            print(f"Error restoring checkpoint: {e}")
        
        raise ValueError(f"Checkpoint not found: {checkpoint_id}")
    
    async def restore_latest_checkpoint(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Restore the most recent checkpoint for a workflow."""
        try:
            response = self.supabase.table("workflow_checkpoints").select("*").eq(
                "workflow_id", workflow_id
            ).order("timestamp", desc=True).limit(1).execute()
            
            if response.data:
                data = response.data[0]
                return json.loads(data["state_data"])
        except Exception as e:
            print(f"Error restoring latest checkpoint: {e}")
        
        return None
    
    async def optimize_context(self, state_data: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize context based on strategy."""
        if self.strategy == ContextStrategy.FORECAST_ENGINE_BASED:
            return self._optimize_forecast_engine_context(state_data)
        elif self.strategy == ContextStrategy.SLIDING_WINDOW:
            return self._optimize_sliding_window(state_data)
        elif self.strategy == ContextStrategy.PRIORITY_BASED:
            return self._optimize_priority_based(state_data)
        elif self.strategy == ContextStrategy.HYBRID:
            return self._optimize_hybrid(state_data)
        
        return state_data
    
    def _optimize_forecast_engine_context(self, state_data: Dict[str, Any]) -> Dict[str, Any]:
        """Keep only ForecastEngine inputs/outputs + critical property data."""
        optimized = {
            "property": state_data.get("property", {}),
            "forecast_engine_results": state_data.get("forecast_engine_results", {}),
            "decision_log": state_data.get("decision_log", []),
            "final_recommendation": state_data.get("final_recommendation"),
            "max_bid": state_data.get("max_bid"),
            "risk_score": state_data.get("risk_score")
        }
        
        # Add condensed version of messages
        messages = state_data.get("messages", [])
        if len(messages) > 10:
            optimized["messages"] = [
                messages[0],  # System prompt
                *messages[-9:]  # Last 9 messages
            ]
        else:
            optimized["messages"] = messages
        
        return optimized
    
    def _optimize_sliding_window(self, state_data: Dict[str, Any], window_size: int = 20) -> Dict[str, Any]:
        """Keep only the last N messages."""
        optimized = state_data.copy()
        messages = state_data.get("messages", [])
        
        if len(messages) > window_size:
            optimized["messages"] = [
                messages[0],  # Keep system prompt
                *messages[-window_size+1:]  # Keep last N-1 messages
            ]
        
        return optimized
    
    def _optimize_priority_based(self, state_data: Dict[str, Any]) -> Dict[str, Any]:
        """Keep high-priority messages and key data."""
        optimized = {
            "property": state_data.get("property", {}),
            "final_recommendation": state_data.get("final_recommendation")
        }
        
        # Keep only messages marked as priority
        messages = state_data.get("messages", [])
        priority_messages = [
            msg for msg in messages 
            if isinstance(msg, dict) and msg.get("priority") == "high"
        ]
        
        # Always include system prompt if present
        if messages and messages[0].get("role") == "system":
            priority_messages.insert(0, messages[0])
        
        optimized["messages"] = priority_messages
        return optimized
    
    def _optimize_hybrid(self, state_data: Dict[str, Any]) -> Dict[str, Any]:
        """Combine multiple strategies."""
        # First apply ForecastEngine optimization
        optimized = self._optimize_forecast_engine_context(state_data)
        
        # Then apply sliding window to messages
        optimized = self._optimize_sliding_window(optimized, window_size=15)
        
        return optimized
    
    def _estimate_tokens(self, data: Dict[str, Any]) -> int:
        """Estimate token count for data."""
        text = json.dumps(data)
        # Rough estimate: 4 chars ≈ 1 token
        return len(text) // 4
    
    def _hash_state(self, state_data: Dict[str, Any]) -> str:
        """Generate hash of state data for deduplication."""
        state_str = json.dumps(state_data, sort_keys=True)
        return hashlib.md5(state_str.encode()).hexdigest()
    
    async def get_checkpoint_history(
        self, 
        workflow_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get checkpoint history for a workflow."""
        try:
            response = self.supabase.table("workflow_checkpoints").select("*").eq(
                "workflow_id", workflow_id
            ).order("timestamp", desc=True).limit(limit).execute()
            
            return response.data if response.data else []
        except Exception as e:
            print(f"Error getting checkpoint history: {e}")
            return []
    
    async def delete_old_checkpoints(
        self, 
        workflow_id: str,
        keep_last: int = 5
    ) -> int:
        """Delete old checkpoints, keeping only the most recent N."""
        try:
            history = await self.get_checkpoint_history(workflow_id, limit=1000)
            
            if len(history) <= keep_last:
                return 0
            
            to_delete = history[keep_last:]
            deleted_count = 0
            
            for checkpoint in to_delete:
                self.supabase.table("workflow_checkpoints").delete().eq(
                    "id", checkpoint["id"]
                ).execute()
                deleted_count += 1
            
            return deleted_count
        except Exception as e:
            print(f"Error deleting old checkpoints: {e}")
            return 0
    
    def get_context_stats(self) -> Dict[str, Any]:
        """Get current context statistics."""
        return {
            "checkpoints_cached": len(self._checkpoints),
            "current_context_keys": list(self._current_context.keys()),
            "strategy": self.strategy.value,
            "max_tokens": self.max_tokens
        }


class SupabaseCheckpointSaver:
    """LangGraph-compatible checkpoint saver using Supabase."""
    
    def __init__(self, supabase_client):
        self.supabase = supabase_client
        self.context_manager = BidDeedContextManager(supabase_client)
    
    def put(self, config: Dict, checkpoint: Dict) -> None:
        """Save checkpoint (sync wrapper for async method)."""
        import asyncio
        
        workflow_id = config.get("configurable", {}).get("thread_id", "unknown")
        stage = checkpoint.get("stage", "unknown")
        
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        loop.run_until_complete(
            self.context_manager.create_checkpoint(workflow_id, stage, checkpoint)
        )
    
    def get(self, config: Dict) -> Optional[Dict]:
        """Retrieve latest checkpoint (sync wrapper for async method)."""
        import asyncio
        
        workflow_id = config.get("configurable", {}).get("thread_id")
        if not workflow_id:
            return None
        
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(
            self.context_manager.restore_latest_checkpoint(workflow_id)
        )
    
    def list(self, config: Dict) -> List[Dict]:
        """List checkpoints for a workflow."""
        import asyncio
        
        workflow_id = config.get("configurable", {}).get("thread_id")
        if not workflow_id:
            return []
        
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(
            self.context_manager.get_checkpoint_history(workflow_id)
        )
