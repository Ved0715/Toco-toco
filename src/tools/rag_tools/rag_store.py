from config import Config
from pinecone.grpc import PineconeGRPC as Pinecone
from openai import OpenAI
from mcp.server.fastmcp import FastMCP
import asyncio
import os
import dotenv

dotenv.load_dotenv()


def rag_store(mcp: FastMCP) -> None:
    """Store documents in Pinecone"""
    config = Config()
    openai_client = OpenAI(api_key=config.openai_api_key)
    pc = Pinecone(api_key=config.pinecone_api_key)
    embedding_dimension = int(config.embedding_dimension) if config.embedding_dimension else 3072
    embedding_model = config.embedding_model or "text-embedding-3-small"
    
    @mcp.tool()
    async def pinecone_store(index_name: str, namespace: str, documents: list[dict]) -> dict:
        """Store documents in Pinecone with embeddings
        Args:
            index_name: The name of the index to store documents in
            namespace: The namespace to store documents in (use "" for default namespace)
            documents: List of documents with structure:
                [
                    {
                        "id": "unique_document_id",
                        "content": "document text content",
                        "metadata": {
                            "source": "document.pdf",
                            "title": "Document Title",
                            "author": "Author Name",
                            "page_number": "1",
                            "section": "introduction",
                            "timestamp": "2024-01-01"
                        }
                    }
                ]
        Returns:
            A dictionary containing the storage results:
            - success: Boolean indicating if the operation was successful
            - total_documents: Number of documents processed
            - index_info: Information about the target index and namespace
        """
        try:
            # Validate inputs
            if not index_name or not documents:
                return {
                    "success": False,
                    "error": "Index name and documents are required",
                    "total_documents": 0
                }
            
            # Check if index exists
            if not await asyncio.to_thread(pc.has_index, index_name):
                return {
                    "success": False,
                    "error": f"Index '{index_name}' does not exist",
                    "total_documents": 0
                }
            
            # Validate document structure
            valid_documents = []
            for doc in documents:
                if not isinstance(doc, dict) or 'content' not in doc:
                    continue
                if not doc.get('id'):
                    doc['id'] = f"doc_{len(valid_documents)}_{hash(doc['content']) % 10000}"
                valid_documents.append(doc)
            
            if not valid_documents:
                return {
                    "success": False,
                    "error": "No valid documents found. Each document must have 'content' field.",
                    "total_documents": 0
                }
            
            # Convert documents to embeddings using OpenAI
            try:
                embedding_response = await asyncio.to_thread(
                    openai_client.embeddings.create,
                    input=[doc['content'] for doc in valid_documents],
                    model=embedding_model
                )
            except Exception as embedding_error:
                return {
                    "success": False,
                    "error": f"Failed to create embeddings: {str(embedding_error)}",
                    "total_documents": 0
                }
            
            # Get the index
            index = await asyncio.to_thread(pc.Index, index_name)
            
            # Prepare vectors for Pinecone upsert
            vectors = []
            for i, doc in enumerate(valid_documents):
                vector_data = {
                    "id": doc['id'],
                    "values": embedding_response.data[i].embedding,
                    "metadata": {
                        "text": doc['content'],
                        **doc.get('metadata', {})
                    }
                }
                vectors.append(vector_data)
            
            # Store embeddings in Pinecone
            try:
                await asyncio.to_thread(
                    index.upsert,
                    vectors=vectors,
                    namespace=namespace if namespace else ""
                )
            except Exception as upsert_error:
                return {
                    "success": False,
                    "error": f"Failed to upsert to Pinecone: {str(upsert_error)}",
                    "total_documents": 0
                }

            return {
                "success": True,
                "total_documents": len(valid_documents),
                "index_info": {
                    "index_name": index_name,
                    "namespace": namespace if namespace else "default",
                    "embedding_model": embedding_model,
                    "embedding_dimension": len(embedding_response.data[0].embedding)
                },
                "storage_metadata": {
                    "documents_processed": len(valid_documents),
                    "vectors_stored": len(vectors),
                    "namespace_used": namespace if namespace else "default"
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error storing documents: {str(e)}",
                "total_documents": 0
            }



    