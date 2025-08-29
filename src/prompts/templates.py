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

# Intelligent RAG Prompts for Automatic Retrieval
INTELLIGENT_RAG_PROMPTS = {
    "auto_retrieval_agent": """
    **Intelligent Document Retrieval Agent**
    
    **Role**: You are an intelligent document retrieval agent that automatically determines when to fetch relevant information from vector databases.
    
    **Automatic Triggers**: Detect and respond to these query types:
    - Questions asking for specific information: "What is X?", "How does Y work?", "Tell me about Z"
    - Research queries: "Find information about...", "Show me data on...", "Research..."
    - Comparison requests: "Compare A and B", "What's the difference between..."
    - Explanation requests: "Explain how...", "Why does...", "What causes..."
    - Analysis requests: "Analyze...", "Summarize...", "Review..."
    - Code-related queries: "Show me examples of...", "How to implement..."
    
    **Decision Logic**:
    1. If query contains knowledge-seeking words → Use pinecone_retrieve
    2. If query asks for recent/specific data → Use pinecone_retrieve with targeted search
    3. If query is conversational/greeting → Respond directly without retrieval
    4. If query asks to store/save → Use pinecone_store
    
    **Default Settings**:
    - index_name: "main-knowledge" (or user-specified)
    - namespace: "" (default namespace)
    - top_k: 5 (adjust based on query complexity)
    
    **Response Format**: Always provide sources and confidence scores from retrieval results.
    """,
    
    "context_aware_search": """
    **Context-Aware Search Strategy**
    
    **Query Enhancement**: Before searching, enhance user queries:
    - Extract key entities and concepts
    - Identify search intent (factual, procedural, comparative, etc.)
    - Add relevant synonyms and related terms
    - Consider conversation context for disambiguation
    
    **Search Optimization**:
    - Use multiple search strategies for complex queries
    - Combine semantic and keyword approaches
    - Adjust retrieval parameters based on query type:
      * Simple facts: top_k=3, focused search
      * Complex topics: top_k=10, broad search
      * Comparisons: top_k=8, balanced coverage
    
    **Result Processing**:
    - Filter results by relevance score (>0.7 for high confidence)
    - Deduplicate similar content
    - Rank by context relevance
    - Synthesize information from multiple sources
    """,
    
    "adaptive_retrieval": """
    **Adaptive Retrieval System**
    
    **Smart Namespace Selection**:
    - Analyze query to determine domain (technical, business, general, etc.)
    - Route to appropriate namespace automatically:
      * Technical queries → "technical" namespace
      * Business questions → "business" namespace  
      * General knowledge → "" (default) namespace
      * Code examples → "code" namespace
    
    **Dynamic Parameter Adjustment**:
    - Query complexity detection:
      * Simple: top_k=3, single namespace
      * Medium: top_k=5-7, consider multiple namespaces
      * Complex: top_k=10, multi-namespace search with ranking
    
    **Follow-up Strategy**:
    - If initial results are insufficient (low scores), try:
      1. Broader search terms
      2. Different namespace
      3. Increased top_k
      4. Alternative query formulations
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
    
    # Intelligent RAG Prompts for Automatic Retrieval
    @mcp.prompt("auto_retrieval", description="Automatically trigger RAG retrieval based on user intent")
    def auto_retrieval_prompt(query: str, index_name: str = "main-knowledge") -> str:
        """
        Intelligent Auto-Retrieval Prompt
        
        This prompt automatically analyzes user queries and determines whether to trigger
        document retrieval from Pinecone. It uses intent detection to decide when RAG
        is needed and configures retrieval parameters automatically.
        
        Args:
            query: The user's input query to analyze
            index_name: Target Pinecone index (default: "main-knowledge")
            
        Returns:
            str: Instructions for automatic retrieval workflow
        """
        return f"""
        **AUTOMATIC RAG RETRIEVAL WORKFLOW**
        
        **User Query**: "{query}"
        **Target Index**: "{index_name}"
        
        **INSTRUCTIONS**:
        
        1. **INTENT ANALYSIS** - Analyze this query for retrieval triggers:
           - Knowledge Questions: "what is", "how does", "tell me about", "explain"
           - Research Requests: "find", "search", "lookup", "get information"  
           - Specific Data: "show me", "give me details", "provide data"
           - Analysis: "analyze", "compare", "review", "summarize"
           - Examples: "show examples", "give me samples", "demonstrate"
        
        2. **AUTOMATIC DECISION**:
           IF query matches ANY trigger patterns:
           → **RETRIEVE DOCUMENTS** using pinecone_retrieve with these parameters:
             - index_name: "{index_name}"
             - namespace: "" (auto-detect from query domain)
             - query: "{query}"  
             - top_k: 5-10 (based on complexity)
           
           IF query is conversational/greeting/simple:
           → **RESPOND DIRECTLY** without retrieval
        
        3. **ENHANCEMENT LOGIC**:
           - Extract key terms from: "{query}"
           - Add relevant synonyms and context
           - Consider conversation history for disambiguation
           
        4. **RESPONSE SYNTHESIS**:
           - Use retrieved documents as primary source
           - Cite sources with confidence scores
           - Provide comprehensive answers
           - Suggest related topics if relevant
        
        **EXECUTE NOW**: Apply this workflow to the current query automatically.
        """
    
    @mcp.prompt("smart_search", description="Context-aware search with automatic parameter optimization")
    def smart_search_prompt(query: str, domain_hint: str = "general") -> str:
        """
        Smart Search Optimization Prompt
        
        Automatically optimizes search parameters and strategies based on query
        characteristics and domain context.
        
        Args:
            query: User's search query
            domain_hint: Domain context (technical, business, code, general)
            
        Returns:
            str: Optimized search instructions
        """
        
        # Analyze query complexity
        word_count = len(query.split())
        has_technical_terms = any(term in query.lower() for term in 
                                ['api', 'function', 'class', 'algorithm', 'code', 'implementation'])
        
        if word_count <= 3:
            complexity = "simple"
            top_k = 3
        elif word_count <= 8:
            complexity = "medium" 
            top_k = 5
        else:
            complexity = "complex"
            top_k = 10
            
        return f"""
        **SMART SEARCH OPTIMIZATION**
        
        **Query Analysis**:
        - Original: "{query}"
        - Domain: {domain_hint}
        - Complexity: {complexity} ({word_count} words)
        - Technical: {has_technical_terms}
        
        **Optimized Parameters**:
        - top_k: {top_k}
        - namespace: {"technical" if has_technical_terms else ""}
        - search_strategy: {"focused" if complexity == "simple" else "comprehensive"}
        
        **Search Enhancement**:
        1. Extract key entities from query
        2. Add domain-specific context
        3. Include relevant synonyms
        4. Optimize for {domain_hint} domain
        
        **Execute Search**: Use pinecone_retrieve with optimized parameters automatically.
        """
    
    @mcp.prompt("conversational_rag", description="Maintain conversation context while performing retrieval")  
    def conversational_rag_prompt(current_query: str, conversation_context: str = "") -> str:
        """
        Conversational RAG Prompt
        
        Maintains conversation context and flow while performing intelligent retrieval
        to provide contextually relevant responses.
        
        Args:
            current_query: Current user question
            conversation_context: Previous conversation messages
            
        Returns:
            str: Contextual retrieval instructions
        """
        return f"""
        **CONVERSATIONAL RAG WORKFLOW**
        
        **Current Query**: "{current_query}"
        **Context**: {conversation_context[:200]}{"..." if len(conversation_context) > 200 else ""}
        
        **CONTEXTUAL ANALYSIS**:
        1. **Reference Resolution**: Check if query refers to previous topics
        2. **Intent Continuity**: Determine if this extends previous discussion
        3. **Context Integration**: Use conversation history to enhance search
        
        **RETRIEVAL STRATEGY**:
        - If query references "that", "it", "this" → Use conversation context
        - If query is follow-up question → Combine with previous topics  
        - If query is new topic → Fresh retrieval with full query
        
        **RESPONSE INTEGRATION**:
        - Maintain conversation flow and tone
        - Reference previous exchanges when relevant
        - Provide context-aware explanations
        - Build upon established knowledge
        
        **AUTOMATIC EXECUTION**: Apply contextual retrieval strategy now.
        """
    


