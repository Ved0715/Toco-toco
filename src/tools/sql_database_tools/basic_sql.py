from mcp.server.fastmcp import FastMCP
import aiosqlite
import asyncio
import os
import logging
from typing import List, Dict, Any, Optional
import json
from pathlib import Path

logger = logging.getLogger(__name__)

# Database configuration
DB_PATH = os.getenv("SQL_DATABASE_PATH", "./data/fastmcp.db")

class DatabaseManager:
    """Manages SQLite database connections and operations"""
    
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        # Create directory if it doesn't exist
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    
    async def get_connection(self):
        """Get database connection"""
        return aiosqlite.connect(self.db_path)
    
    async def execute_query(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """Execute SELECT query and return results"""
        async with await self.get_connection() as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(query, params) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
    
    async def execute_modification(self, query: str, params: tuple = ()) -> Dict[str, Any]:
        """Execute INSERT, UPDATE, DELETE queries"""
        async with await self.get_connection() as db:
            cursor = await db.execute(query, params)
            await db.commit()
            return {
                "rows_affected": cursor.rowcount,
                "last_row_id": cursor.lastrowid
            }
    
    async def get_tables(self) -> List[str]:
        """Get list of all tables in database"""
        query = "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
        result = await self.execute_query(query)
        return [row['name'] for row in result]
    
    async def get_table_schema(self, table_name: str) -> List[Dict[str, str]]:
        """Get table schema information"""
        query = f"PRAGMA table_info({table_name})"
        return await self.execute_query(query)

# Global database manager instance
db_manager = DatabaseManager()

def basic_mcp(mcp: FastMCP) -> None:
    """Register basic SQL tools with the MCP server"""

    @mcp.tool()
    async def sql_query(table: str, limit: int = 100) -> Dict[str, Any]:
        """
        Get all data from a table or execute SELECT query
        Args:
            table: Table name OR full SELECT query
            limit: Maximum number of rows to return (default: 100)
        """
        try:
            table_lower = table.lower().strip()
            
            # If it's just a table name (no spaces, no SQL keywords), convert to SELECT *
            if ' ' not in table_lower and not any(keyword in table_lower for keyword in ['select', 'from', 'where', 'order', 'group']):
                # It's likely just a table name
                query = f"SELECT * FROM {table}"
            else:
                # It's a full query
                query = table
            
            query_lower = query.lower()
            
            # Validate query is SELECT only
            if not query_lower.startswith('select'):
                return {
                    "error": "Only SELECT queries are allowed, or provide a table name to get all data",
                    "success": False
                }
            
            # Add LIMIT if not present
            if 'limit' not in query_lower:
                query = f"{query.rstrip(';')} LIMIT {limit}"
            
            # Execute query
            results = await db_manager.execute_query(query)
            
            return {
                "success": True,
                "table_or_query": table,
                "executed_query": query,
                "results": results,
                "row_count": len(results),
                "columns": list(results[0].keys()) if results else []
            }
            
        except Exception as e:
            logger.error(f"SQL query error: {e}")
            return {
                "error": str(e),
                "success": False,
                "table_or_query": table
            }


    @mcp.tool()
    async def sql_insert(table: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Insert new record into table
        Args:
            table: Target table name
            data: Dictionary of column-value pairs to insert
        """
        try:
            if not data:
                return {
                    "error": "No data provided for insertion",
                    "success": False
                }
            
            # Build INSERT query
            columns = list(data.keys())
            placeholders = ','.join(['?' for _ in columns])
            values = tuple(data.values())
            
            query = f"INSERT INTO {table} ({','.join(columns)}) VALUES ({placeholders})"
            
            # Execute insertion
            result = await db_manager.execute_modification(query, values)
            
            return {
                "success": True,
                "table": table,
                "inserted_data": data,
                "rows_affected": result['rows_affected'],
                "last_row_id": result['last_row_id']
            }
            
        except Exception as e:
            logger.error(f"SQL insert error: {e}")
            return {
                "error": str(e),
                "success": False,
                "table": table,
                "data": data
            }


    @mcp.tool()
    async def sql_update(table: str, data: Dict[str, Any], conditions: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update existing records in table
        Args:
            table: Target table name
            data: Dictionary of column-value pairs to update
            conditions: Dictionary of WHERE conditions
        """
        try:
            if not data:
                return {
                    "error": "No data provided for update",
                    "success": False
                }
            
            if not conditions:
                return {
                    "error": "No conditions provided - this would update all rows!",
                    "success": False
                }
            
            # Build UPDATE query
            set_clause = ','.join([f"{col} = ?" for col in data.keys()])
            where_clause = ' AND '.join([f"{col} = ?" for col in conditions.keys()])
            
            query = f"UPDATE {table} SET {set_clause} WHERE {where_clause}"
            params = tuple(list(data.values()) + list(conditions.values()))
            
            # Execute update
            result = await db_manager.execute_modification(query, params)
            
            return {
                "success": True,
                "table": table,
                "updated_data": data,
                "conditions": conditions,
                "rows_affected": result['rows_affected']
            }
            
        except Exception as e:
            logger.error(f"SQL update error: {e}")
            return {
                "error": str(e),
                "success": False,
                "table": table,
                "data": data,
                "conditions": conditions
            }


    @mcp.tool()
    async def sql_delete(table: str, conditions: Dict[str, Any], confirm_delete: bool = False) -> Dict[str, Any]:
        """
        Delete records with safety checks
        Args:
            table: Target table name
            conditions: Dictionary of WHERE conditions
            confirm_delete: Must be True to actually delete (safety measure)
        """
        try:
            if not conditions:
                return {
                    "error": "No conditions provided - this would delete all rows! Use sql_truncate_table for that.",
                    "success": False
                }
            
            if not confirm_delete:
                # First, show what would be deleted
                where_clause = ' AND '.join([f"{col} = ?" for col in conditions.keys()])
                preview_query = f"SELECT COUNT(*) as count FROM {table} WHERE {where_clause}"
                params = tuple(conditions.values())
                
                count_result = await db_manager.execute_query(preview_query, params)
                rows_to_delete = count_result[0]['count'] if count_result else 0
                
                return {
                    "success": False,
                    "preview": True,
                    "table": table,
                    "conditions": conditions,
                    "rows_that_would_be_deleted": rows_to_delete,
                    "message": f"This would delete {rows_to_delete} rows. Set confirm_delete=True to proceed."
                }
            
            # Build DELETE query
            where_clause = ' AND '.join([f"{col} = ?" for col in conditions.keys()])
            query = f"DELETE FROM {table} WHERE {where_clause}"
            params = tuple(conditions.values())
            
            # Execute deletion
            result = await db_manager.execute_modification(query, params)
            
            return {
                "success": True,
                "table": table,
                "conditions": conditions,
                "rows_deleted": result['rows_affected']
            }
            
        except Exception as e:
            logger.error(f"SQL delete error: {e}")
            return {
                "error": str(e),
                "success": False,
                "table": table,
                "conditions": conditions
            }

    @mcp.tool()
    async def list_tables() -> Dict[str, Any]:
        """
        List all tables in the database
        """
        try:
            tables = await db_manager.get_tables()
            return {
                "success": True,
                "tables": tables,
                "table_count": len(tables)
            }
        except Exception as e:
            logger.error(f"List tables error: {e}")
            return {
                "error": str(e),
                "success": False
            }
    
    @mcp.tool()
    async def describe_table(table_name: str) -> Dict[str, Any]:
        """
        Get detailed information about a table's structure
        Args:
            table_name: Name of the table to describe
        """
        try:
            schema = await db_manager.get_table_schema(table_name)
            
            # Get row count
            count_query = f"SELECT COUNT(*) as count FROM {table_name}"
            count_result = await db_manager.execute_query(count_query)
            row_count = count_result[0]['count'] if count_result else 0
            
            return {
                "success": True,
                "table_name": table_name,
                "columns": schema,
                "column_count": len(schema),
                "row_count": row_count
            }
        except Exception as e:
            logger.error(f"Describe table error: {e}")
            return {
                "error": str(e),
                "success": False,
                "table_name": table_name
            }
    
    @mcp.tool()
    async def create_table(table_name: str, columns: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Create a new table
        Args:
            table_name: Name of the new table
            columns: List of column definitions [{'name': 'id', 'type': 'INTEGER PRIMARY KEY'}, ...]
        """
        try:
            if not columns:
                return {
                    "error": "No columns provided",
                    "success": False
                }
            
            # Build CREATE TABLE query
            column_definitions = []
            for col in columns:
                if 'name' not in col or 'type' not in col:
                    return {
                        "error": "Each column must have 'name' and 'type' fields",
                        "success": False
                    }
                column_definitions.append(f"{col['name']} {col['type']}")
            
            query = f"CREATE TABLE {table_name} ({', '.join(column_definitions)})"
            
            await db_manager.execute_modification(query)
            
            return {
                "success": True,
                "table_name": table_name,
                "columns": columns,
                "query": query
            }
            
        except Exception as e:
            logger.error(f"Create table error: {e}")
            return {
                "error": str(e),
                "success": False,
                "table_name": table_name
            }
    
    @mcp.tool()
    async def sample_data(table_name: str, limit: int = 5) -> Dict[str, Any]:
        """
        Get a sample of data from a table
        Args:
            table_name: Name of the table
            limit: Number of sample rows to return (default: 5)
        """
        try:
            query = f"SELECT * FROM {table_name} LIMIT {limit}"
            results = await db_manager.execute_query(query)
            
            return {
                "success": True,
                "table_name": table_name,
                "sample_data": results,
                "sample_count": len(results)
            }
            
        except Exception as e:
            logger.error(f"Sample data error: {e}")
            return {
                "error": str(e),
                "success": False,
                "table_name": table_name
            }