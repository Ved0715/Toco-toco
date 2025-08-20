"""FastMCP server implementation."""

from mcp.server.fastmcp import FastMCP
from .tools import register_math_tools, register_resources, pinecone_config, rag_retrival, rag_store
from .prompts.templates import register_prompts
from src.tools import web_search_tools

# Create FastMCP server
mcp = FastMCP("FastMCP Server")

# Register prompts

register_prompts(mcp)

# Register all tools and resources
register_math_tools(mcp)
register_resources(mcp)
pinecone_config(mcp)
rag_retrival(mcp)
rag_store(mcp)
web_search_tools(mcp)

if __name__ == "__main__":
    # print("Starting FastMCP Server on http://localhost:8000/mcp")
    mcp.run(transport="streamable-http")
    # mcp.run()
