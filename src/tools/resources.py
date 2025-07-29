"""Resource definitions for FastMCP server."""

from mcp.server.fastmcp import FastMCP

def register_resources(mcp: FastMCP) -> None:
    """Register all resources with the MCP server."""
    
    @mcp.resource("math://operation/{operation}")
    def get_math_info(operation: str) -> str:
        """Get information about math operations.
        
        Args:
            operation: Name of the math operation
            
        Returns:
            Description of the operation
        """
        operations = {
            "add": "Addition combines two numbers to get their sum",
            "multiply": "Multiplication combines two numbers to get their product"
        }
        return operations.get(operation, f"Unknown operation: {operation}") 

    @mcp.resource("pinecone://{operation}")
    def get_rag_info(operation: str) -> str:
        """Get information about Pinecone operations.
        
        Args:
            operation: Name of the Pinecone operation
            
        Returns:
            Description of the operation
        """
        operations = {
            "create_index": "Create a new Pinecone index",
            "delete_index": "Delete a Pinecone index",
            "list_indexes": "List all Pinecone indexes",
            "create_namespace": "Create a new Pinecone namespace"
        }
        return operations.get(operation, f"Unknown operation: {operation}")