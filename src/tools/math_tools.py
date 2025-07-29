"""Math operation tools for FastMCP server."""

from mcp.server.fastmcp import FastMCP

def register_math_tools(mcp: FastMCP) -> None:
    """Register all math-related tools with the MCP server."""
    
    @mcp.tool()
    def add(a: int, b: int) -> dict:
        """Add two numbers together.
        
        Args:
            a: First number
            b: Second number
            
        Returns:
            Dictionary containing:
                - result: Sum of the numbers
                - operation: Type of operation
                - operands: List of input numbers
        """
        result = a + b
        return {"result": result, "operation": "addition", "operands": [a, b]}

    @mcp.tool()
    def multiply(a: int, b: int) -> dict:
        """Multiply two numbers.
        
        Args:
            a: First number
            b: Second number
            
        Returns:
            Dictionary containing:
                - result: Product of the numbers
                - operation: Type of operation
                - operands: List of input numbers
        """
        result = a * b
        return {"result": result, "operation": "multiplication", "operands": [a, b]} 

            
            
        
        
        
        
        
        