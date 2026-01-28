"""Database connection management for OpenRouter Phase 2."""

import os
import asyncpg
from typing import Optional
from contextlib import asynccontextmanager


class DatabaseConnection:
    """Manages PostgreSQL database connections using asyncpg."""
    
    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None
        self.database_url = os.getenv(
            'DATABASE_URL',
            'postgresql://localhost:5432/openrouter'
        )
    
    async def initialize(self, min_size: int = 10, max_size: int = 20):
        """Initialize connection pool.
        
        Args:
            min_size: Minimum number of connections in the pool
            max_size: Maximum number of connections in the pool
        """
        if self.pool is None:
            self.pool = await asyncpg.create_pool(
                self.database_url,
                min_size=min_size,
                max_size=max_size,
                command_timeout=60
            )
    
    async def close(self):
        """Close the connection pool."""
        if self.pool:
            await self.pool.close()
            self.pool = None
    
    @asynccontextmanager
    async def acquire(self):
        """Acquire a connection from the pool.
        
        Usage:
            async with db.acquire() as conn:
                result = await conn.fetch('SELECT * FROM models')
        """
        if self.pool is None:
            raise RuntimeError('Database pool not initialized')
        
        async with self.pool.acquire() as connection:
            yield connection


# Global database instance
db = DatabaseConnection()
