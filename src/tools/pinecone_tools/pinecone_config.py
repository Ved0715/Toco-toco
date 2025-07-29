"""RAG tools for FastMCP server."""

from mcp.server.fastmcp import FastMCP
from pinecone.grpc import PineconeGRPC as Pinecone
from pinecone import ServerlessSpec
import os
import dotenv
import asyncio

dotenv.load_dotenv()


def pinecone_config(mcp: FastMCP) -> None:
    """Register all RAG-related tools with the MCP server."""
    
    pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))
    embedding_dimension = int(os.getenv('EMBEDDING_DIMENSION' , 3072))

    @mcp.tool()
    async def create_index(index_name: str) -> dict:
        """Create a new Pinecone index (takes 30-60 seconds)
        Args:
            index_name: The name of the index to create
        """
        spec = ServerlessSpec(
            cloud="aws",
            region="us-east-1"
        )
        print(f"Creating index {index_name}")
        if not await asyncio.to_thread(pc.has_index, index_name):
            try:
                await asyncio.to_thread(pc.create_index, name=index_name, 
                                spec=spec, 
                                dimension=embedding_dimension, 
                                vector_type="dense")
                return {"message": f"Index {index_name} created successfully"}
            except Exception as e:
                return {"message": f"Error creating index: {e}"}

        else:
            return {"message": f"Index {index_name} already exists"}

    @mcp.tool()
    async def delete_index(index_name: str) -> dict:
        """Delete a Pinecone index
        Args:
            index_name: The name of the index to delete
        """
        if await asyncio.to_thread(pc.has_index, index_name):
            try:
                await asyncio.to_thread(pc.delete_index, index_name)
                return {"message": f"Index {index_name} deleted successfully"}
            except Exception as e:
                return {"message": f"Error creating index: {e}"}
        else :
            return {"message": f"No index with name {index_name} found"}

    @mcp.tool()
    async def list_indexes() -> dict:
        """List all Pinecone indexes
        """
        indexes = await asyncio.to_thread(pc.list_indexes)
        # Convert to serializable format
        index_list = []
        if indexes:
            for index in indexes:
                index_list.append({
                    "name": index.name,
                    "dimension": index.dimension,
                    "metric": index.metric,
                    "status": index.status.ready if hasattr(index.status, 'ready') else str(index.status)
                })
        return {"indexes": index_list}
    
    @mcp.tool()
    async def create_namespace(index_name: str, namespace: str) -> dict:
        """Create a new Pinecone namespace (namespaces are created automatically on first upsert)
        Args:
            index_name: The name of the index
            namespace: The name of the namespace to create
        """
        # Check if index exists first
        if not await asyncio.to_thread(pc.has_index, index_name):
            return {"message": f"Index {index_name} does not exist"}
        
        # Namespaces are created automatically when you first upsert data to them
        # This is just a placeholder operation
        return {"message": f"Namespace {namespace} will be created automatically when data is first upserted to it in index {index_name}"}

    @mcp.tool()
    async def list_namespaces(index_name: str) -> dict:
        """List all namespaces in a Pinecone index
        Args:
            index_name: The name of the index
        """
        # Check if index exists first
        if not await asyncio.to_thread(pc.has_index, index_name):
            return {"message": f"Index {index_name} does not exist"}
        
        try:
            # Get the index object
            index = await asyncio.to_thread(pc.Index, index_name)
            
            # List namespaces using the generator function
            namespace_list = []
            for namespace in await asyncio.to_thread(lambda: list(index.list_namespaces())):
                namespace_list.append({
                    "name": namespace.name,
                    "record_count": namespace.record_count
                })
            
            return {"namespaces": namespace_list}
        except Exception as e:
            return {"message": f"Error listing namespaces: {e}"}


    