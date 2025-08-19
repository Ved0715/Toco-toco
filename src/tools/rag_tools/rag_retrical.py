from mcp.server.fastmcp import FastMCP
from pinecone.grpc import PineconeGRPC as Pinecone
import os
import dotenv
import asyncio
import json
from openai import OpenAI
from config import Config


dotenv.load_dotenv()


def rag_retrival(mcp: FastMCP) -> None:
    """Retrieve documents from Pinecone"""
    config = Config()
    openai_client = OpenAI(api_key=config.openai_api_key)
    pc = Pinecone(api_key=config.pinecone_api_key)
    embedding_dimension = int(config.embedding_dimension) if config.embedding_dimension else 3072
    embedding_model = config.embedding_model or "text-embedding-3-large"
    
    @mcp.tool()
    async def pinecone_retrieve(index_name: str, namespace: str, query: str, top_k: int = 5) -> dict:
        """Retrieve documents from Pinecone using vector similarity search
        Args:
            index_name: The name of the index to search in
            namespace: The namespace to search in (use "" for default namespace)
            query: The query text to search for (will be converted to embedding)
            top_k: The number of documents to retrieve (default: 5)
        Returns:
            A dictionary containing the retrieved content with proper structure:
            - success: Boolean indicating if the operation was successful
            - content: List of retrieved documents with scores and metadata
            - total_results: Number of results returned
            - query_info: Information about the search query
        """
        try:
            # Validate inputs
            if not index_name or not query:
                return {
                    "success": False,
                    "error": "Index name and query are required",
                    "content": [],
                    "total_results": 0
                }
            
            # Check if index exists
            if not await asyncio.to_thread(pc.has_index, index_name):
                return {
                    "success": False,
                    "error": f"Index '{index_name}' does not exist",
                    "content": [],
                    "total_results": 0
                }
            
            # Convert query to embedding using OpenAI
            try:
                embedding_response = await asyncio.to_thread(
                    openai_client.embeddings.create,
                    input=query,
                    model=embedding_model
                )
                embedding_vector = embedding_response.data[0].embedding
            except Exception as embedding_error:
                return {
                    "success": False,
                    "error": f"Failed to create embedding: {str(embedding_error)}",
                    "content": [],
                    "total_results": 0
                }
            
            # Get the index
            index = await asyncio.to_thread(pc.Index, index_name)
            
            # Search Pinecone
            response = await asyncio.to_thread(
                index.query,
                vector=embedding_vector,
                top_k=top_k,
                namespace=namespace if namespace else "",
                include_metadata=True,
                include_values=False
            )

            # Process resultsc
            content = []
            for match in response.matches:
                result = {
                    "id": match.id,
                    "score": float(match.score),
                    "content": "",
                    "metadata": {}
                }
                
                # Extract content and metadata
                if hasattr(match, 'metadata') and match.metadata:
                    # Extract text content from metadata
                    result["content"] = match.metadata.get("text", "")
                    result["metadata"] = {
                        "source": match.metadata.get("source", ""),
                        "chunk_id": match.metadata.get("chunk_id", ""),
                        "document_id": match.metadata.get("document_id", ""),
                        "page_number": match.metadata.get("page_number", ""),
                        "section": match.metadata.get("section", ""),
                        "timestamp": match.metadata.get("timestamp", ""),
                        "author": match.metadata.get("author", ""),
                        "title": match.metadata.get("title", "")
                    }
                
                content.append(result)

            return {
                "success": True,
                "content": content,
                "total_results": len(content),
                "query_info": {
                    "original_query": query,
                    "index_name": index_name,
                    "namespace": namespace if namespace else "default",
                    "top_k_requested": top_k,
                    "embedding_model": embedding_model,
                    "embedding_dimension": len(embedding_vector)
                },
                "search_metadata": {
                    "index_status": "ready",
                    "namespace_count": len(content),
                    "average_score": sum(r["score"] for r in content) / len(content) if content else 0
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error retrieving documents: {str(e)}",
                "content": [],
                "total_results": 0,
                "query_info": {
                    "original_query": query,
                    "index_name": index_name,
                    "namespace": namespace if namespace else "default"
                }
            }


   