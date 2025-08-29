from mcp.server.fastmcp import FastMCP



def data_insights_tools(mcp: FastMCP) -> None:

    @mcp.tool()
    async def data_profiler(table_name: str):
        """Analyze data quality, null counts, unique values"""
  
    @mcp.tool()
    async def find_duplicates(table_name: str, columns: list):
        """Identify duplicate records"""
  
    @mcp.tool()
    async def column_statistics(table_name: str, column_name: str):
        """Min, max, avg, distribution for numeric columns"""
  
    @mcp.tool()
    async def data_sampling(table_name: str, sample_size: int = 10):
        """Get random sample of data"""


    

    
    
    
    
    
    