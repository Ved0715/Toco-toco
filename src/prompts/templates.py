"""
AI prompt templates for enhanced MCP server interactions
"""

# Define prompt dictionaries at module level
SYSTEM_PROMPTS = {
    "main": """
    You are a FastMCP server assistant with access to powerful tools for:
    
    1. **Pinecone Vector Database Operations**
       - Create, manage, and query vector indexes
       - Store and retrieve documents with semantic search
       - Manage namespaces and metadata
    
    2. **RAG (Retrieval-Augmented Generation)**
       - Document storage with embeddings
       - Semantic search and retrieval
       - Content analysis and summarization
    
    3. **Mathematical Operations**
       - Basic arithmetic operations
       - Mathematical computations
    
    **Best Practices:**
    - Always validate inputs before processing
    - Handle errors gracefully with informative messages
    - Use appropriate tools for the task at hand
    - Provide clear, structured responses
    """,
    
    "error_handling": """
    When encountering errors:
    1. Log the error with context
    2. Provide user-friendly error messages
    3. Suggest alternative approaches
    4. Maintain system stability
    """
}

TOOL_PROMPTS = {
    "pinecone_retrieve": """
    **Pinecone Document Retrieval Tool**
    
    **Purpose**: Retrieve documents from Pinecone using semantic search
    
    **Input Format**:
    - index_name: String (required) - Name of the Pinecone index
    - namespace: String (optional) - Namespace to search in (use "" for default)
    - query: String (required) - Search query text
    - top_k: Integer (default: 5) - Number of results to return
    
    **Example Usage**:
    ```python
    await pinecone_retrieve(
        index_name="my-documents",
        namespace="",
        query="machine learning algorithms",
        top_k=10
    )
    ```
    
    **Expected Output**:
    - success: Boolean indicating operation status
    - content: List of retrieved documents with scores
    - total_results: Number of results found
    - query_info: Search metadata
    
    **Best Practices**:
    - Use descriptive, specific queries for better results
    - Start with small top_k values and increase as needed
    - Check index existence before querying
    """,
    
    "pinecone_store": """
    **Pinecone Document Storage Tool**
    
    **Purpose**: Store documents in Pinecone with embeddings
    
    **Input Format**:
    - index_name: String (required) - Target index name
    - namespace: String (optional) - Target namespace
    - documents: List[Dict] (required) - Documents to store
    
    **Document Structure**:
    ```python
    {
        "id": "unique_document_id",
        "content": "document text content",
        "metadata": {
            "source": "document.pdf",
            "title": "Document Title",
            "author": "Author Name",
            "page_number": "1",
            "section": "introduction"
        }
    }
    ```
    
    **Best Practices**:
    - Use unique, descriptive document IDs
    - Include rich metadata for better searchability
    - Ensure content is properly formatted
    - Validate index exists before storing
    """
}

WORKFLOW_PROMPTS = {
    "rag_pipeline": """
    **RAG (Retrieval-Augmented Generation) Pipeline**
    
    **Workflow Steps**:
    1. **Document Ingestion**
       - Validate document format and content
       - Extract text and metadata
       - Generate embeddings using OpenAI
    
    2. **Storage**
       - Store documents in Pinecone index
       - Verify successful storage
       - Update metadata and tracking
    
    3. **Retrieval**
       - Process user query
       - Generate query embeddings
       - Perform semantic search
       - Rank and filter results
    
    4. **Response Generation**
       - Format retrieved content
       - Add context and metadata
       - Provide structured response
    
    **Error Handling**:
    - Handle embedding generation failures
    - Manage Pinecone connection issues
    - Provide fallback responses
    """,
    
    "index_management": """
    **Pinecone Index Management Workflow**
    
    **Index Lifecycle**:
    1. **Creation**: Create index with proper dimensions
    2. **Population**: Store initial documents
    3. **Monitoring**: Track usage and performance
    4. **Maintenance**: Update and optimize
    5. **Cleanup**: Delete when no longer needed
    
    **Best Practices**:
    - Use descriptive index names
    - Monitor index size and performance
    - Implement proper cleanup procedures
    - Document index purposes and contents
    """
}

def register_prompts(mcp):
    """
    Register all MCP prompts with the FastMCP server instance.
    
    This function creates and registers three types of prompts:
    1. System prompts - Define overall AI behavior and capabilities
    2. Tool prompts - Provide guidance for individual tool usage
    3. Workflow prompts - Describe complex multi-step operations
    
    Args:
        mcp: The FastMCP server instance to register prompts with
    """
    
    @mcp.prompt("system_prompt", description="System-level prompts defining server capabilities and behavior")
    def system_prompt() -> str:
        """
        MCP System Prompt Function
        
        This function provides system-level prompts that define the overall behavior and capabilities
        of the FastMCP server. These prompts are used by the AI assistant to understand its role,
        available tools, and best practices for interacting with users.
        
        Returns:
            str: A string containing the main system prompt defining server capabilities and behavior
        
        Usage:
            This prompt is automatically loaded by the MCP server and provides context
            to the AI assistant about its role and responsibilities.
            
        Key Features:
            - Defines server capabilities (Pinecone, RAG, Math operations)
            - Establishes best practices for tool usage
            - Sets guidelines for error handling and user communication
            - Provides structured response expectations
        """
        return SYSTEM_PROMPTS["main"]
    
    @mcp.prompt("tool_prompt", description="Tool-specific prompts with usage guidance and examples")
    def tool_prompt() -> str:
        """
        MCP Tool Prompt Function
        
        This function provides tool-specific prompts that give detailed guidance on how to use
        individual MCP tools. Each tool prompt includes purpose, input format, examples, expected
        output, and best practices for optimal usage.
        
        Returns:
            str: A string containing combined tool prompts for all available tools
        
        Usage:
            These prompts help users understand:
            - When and how to use each tool
            - Required and optional parameters
            - Expected input/output formats
            - Best practices for optimal results
            - Common pitfalls to avoid
            
        Key Features:
            - Parameter descriptions with types and requirements
            - Code examples for practical usage
            - Expected output structure explanations
            - Best practices and optimization tips
            - Error handling recommendations
        """
        return "\n\n".join(TOOL_PROMPTS.values())
    
    @mcp.prompt("workflow_prompt", description="Workflow prompts for complex multi-step operations")
    def workflow_prompt() -> str:
        """
        MCP Workflow Prompt Function
        
        This function provides workflow-level prompts that describe complex, multi-step operations
        and processes. These prompts help users understand how to combine multiple tools and
        operations to achieve specific goals or implement complete workflows.
        
        Returns:
            str: A string containing combined workflow prompts for all available workflows
        
        Usage:
            These prompts guide users through:
            - Complex multi-step operations
            - Best practices for workflow implementation
            - Error handling strategies for workflows
            - Optimization techniques for process efficiency
            
        Key Features:
            - Step-by-step workflow descriptions
            - Process optimization guidelines
            - Error handling and recovery strategies
            - Performance and cost considerations
            - Maintenance and monitoring recommendations
        """
        return "\n\n".join(WORKFLOW_PROMPTS.values())
    


