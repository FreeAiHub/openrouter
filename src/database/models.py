"""Database models and query functions for OpenRouter."""

from typing import List, Optional, Dict, Any
from datetime import datetime
from .connection import db


class Model:
    """Represents an AI model in the routing system."""
    
    @staticmethod
    async def create(name: str, provider: str, endpoint_url: str, 
                    max_tokens: int = 4096, supports_streaming: bool = True,
                    cost_per_1k_tokens: float = 0.0) -> Dict[str, Any]:
        """Create a new model entry."""
        async with db.acquire() as conn:
            result = await conn.fetchrow(
                """
                INSERT INTO models (name, provider, endpoint_url, max_tokens, 
                                   supports_streaming, cost_per_1k_tokens)
                VALUES ($1, $2, $3, $4, $5, $6)
                RETURNING *
                """,
                name, provider, endpoint_url, max_tokens, 
                supports_streaming, cost_per_1k_tokens
            )
            return dict(result)
    
    @staticmethod
    async def get_by_id(model_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve a model by ID."""
        async with db.acquire() as conn:
            result = await conn.fetchrow(
                "SELECT * FROM models WHERE id = $1", model_id
            )
            return dict(result) if result else None
    
    @staticmethod
    async def get_active_models() -> List[Dict[str, Any]]:
        """Get all active models."""
        async with db.acquire() as conn:
            results = await conn.fetch(
                "SELECT * FROM models WHERE status = 'active' ORDER BY name"
            )
            return [dict(row) for row in results]


class Route:
    """Manages routing configurations."""
    
    @staticmethod
    async def create(route_name: str, model_id: int, priority: int = 0,
                    load_balancing_strategy: str = 'round_robin') -> Dict[str, Any]:
        """Create a new route."""
        async with db.acquire() as conn:
            result = await conn.fetchrow(
                """
                INSERT INTO routes (route_name, model_id, priority, load_balancing_strategy)
                VALUES ($1, $2, $3, $4)
                RETURNING *
                """,
                route_name, model_id, priority, load_balancing_strategy
            )
            return dict(result)
    
    @staticmethod
    async def get_by_name(route_name: str) -> Optional[Dict[str, Any]]:
        """Get route by name."""
        async with db.acquire() as conn:
            result = await conn.fetchrow(
                "SELECT * FROM routes WHERE route_name = $1", route_name
            )
            return dict(result) if result else None
