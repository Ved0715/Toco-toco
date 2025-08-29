from mcp.server.fastmcp import FastMCP




def schema_managment_tools(mcp: FastMCP) -> None:

    @mcp.tool()
    async def list_tables():
        """Get all tables in database"""
  
    @mcp.tool()
    async def describe_table(table_name: str):
        """Get table structure, columns, types, constraints"""
  
    @mcp.tool()
    async def get_table_relationships():
        """Show foreign key relationships"""
  
    @mcp.tool()
    async def table_statistics(table_name: str):
        """Row count, size, indexes"""

