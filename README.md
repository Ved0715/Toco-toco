# FastMCP Server

A comprehensive Model Context Protocol (MCP) server implementation with Pinecone vector database integration, OpenAI embeddings, and RAG (Retrieval-Augmented Generation) capabilities.

## What is MCP (Model Context Protocol)?

The Model Context Protocol (MCP) is an open standard that enables AI assistants to connect to external data sources and tools through a standardized interface. It allows AI models like Claude to:

- **Access External Data**: Connect to databases, APIs, and file systems
- **Execute Tools**: Run custom functions and scripts
- **Maintain Context**: Keep track of conversations and data across sessions
- **Extend Capabilities**: Add new functionality without retraining the model

MCP works through a client-server architecture where:
- **MCP Client**: AI assistants (Claude, Cursor, etc.)
- **MCP Server**: Your custom server that provides tools and data access
- **Transport Layer**: Communication protocol (stdio, HTTP, WebSocket)

## Project Overview

This FastMCP server provides:

- **Pinecone Vector Database Integration**: Create, manage, and query vector indexes
- **OpenAI Embeddings**: Convert text to high-dimensional vectors
- **RAG Operations**: Store and retrieve documents with semantic search
- **Multiple Transport Protocols**: Support for stdio, HTTP, and streamable-HTTP
- **Async Operations**: Non-blocking operations for better performance

## Project Structure

```
mcp-server/
├── main.py                 # Server entry point
├── config.py              # Configuration management
├── pyproject.toml         # Project dependencies
├── src/
│   ├── server.py          # Main server setup
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── math_tools.py  # Basic math operations
│   │   ├── pinecone_tools/
│   │   │   └── pinecone_config.py  # Pinecone index management
│   │   └── rag_tools/
│   │       ├── rag_retrical.py     # Document retrieval
│   │       └── rag_store.py        # Document storage
│   ├── prompts/           # System prompts
│   └── resources/         # Static resources
└── test/                  # Test files
```

## Features

### 🗄️ Pinecone Vector Database Tools
- **create_index**: Create new vector indexes
- **delete_index**: Remove indexes
- **list_indexes**: View all available indexes
- **list_namespaces**: List namespaces within indexes

### 📚 RAG (Retrieval-Augmented Generation) Tools
- **pinecone_store**: Store documents with embeddings
- **pinecone_retrieve**: Semantic search and document retrieval

### 🔢 Math Tools
- **add**: Add two numbers
- **multiply**: Multiply two numbers

## Installation & Setup

### Prerequisites
- Python 3.8+
- OpenAI API key
- Pinecone API key

### 1. Clone and Setup
```bash
git clone <repository-url>
cd mcp-server
```

### 2. Install Dependencies
```bash
# Using uv (recommended)
uv sync

# Or using pip
pip install -r requirements.txt
```

### 3. Environment Configuration
Create a `.env` file or set environment variables:
```bash
OPENAI_API_KEY=your-openai-api-key
PINECONE_API_KEY=your-pinecone-api-key
EMBEDDING_DIMENSIONS=3072
EMBEDDING_MODEL=text-embedding-3-large
```

### 4. Run the Server

#### Development Mode (with Inspector)
```bash
uv run mcp dev main.py
```

#### Production Mode
```bash
uv run mcp run main.py
```

#### Direct Python Execution
```bash
uv run python main.py
```

## Integration with AI Assistants

### Claude Desktop Integration

1. **Locate Claude Desktop Config**
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`
   - Linux: `~/.config/Claude/claude_desktop_config.json`

2. **Add MCP Server Configuration**
```json
{
  "mcpServers": {
    "fastmcp-server": {
      "command": "/path/to/your/project/.venv/bin/python3",
      "args": ["/path/to/your/project/main.py"],
      "env": {
        "PINECONE_API_KEY": "your-pinecone-api-key",
        "OPENAI_API_KEY": "your-openai-api-key",
        "EMBEDDING_DIMENSIONS": "3072",
        "EMBEDDING_MODEL": "text-embedding-3-large"
      }
    }
  }
}
```

3. **Restart Claude Desktop**

### Cursor Integration

1. **Open Cursor Settings**
2. **Navigate to MCP Configuration**
3. **Add Server Configuration**
```json
{
  "name": "fastmcp-server",
  "command": "/path/to/your/project/.venv/bin/python3",
  "args": ["/path/to/your/project/main.py"],
  "env": {
    "PINECONE_API_KEY": "your-pinecone-api-key",
    "OPENAI_API_KEY": "your-openai-api-key"
  }
}
```

## Transport Protocols

### 1. stdio (Default)
- **Use Case**: Direct integration with AI assistants
- **Configuration**: `mcp.run()` (default)
- **Pros**: Simple, reliable, no network setup
- **Cons**: Single client connection

### 2. HTTP
- **Use Case**: Web applications, multiple clients
- **Configuration**: `mcp.run(transport="http")`
- **Pros**: Multiple clients, web integration
- **Cons**: Network configuration required

### 3. Streamable-HTTP
- **Use Case**: Real-time streaming applications
- **Configuration**: `mcp.run(transport="streamable-http")`
- **Pros**: Real-time updates, streaming responses
- **Cons**: More complex setup

### 4. WebSocket
- **Use Case**: Bidirectional communication
- **Configuration**: `mcp.run(transport="websocket")`
- **Pros**: Full duplex communication
- **Cons**: Connection management complexity

## Usage Examples

### Creating and Managing Indexes
```python
# Create a new index
await create_index("my-documents")

# List all indexes
await list_indexes()

# Delete an index
await delete_index("old-index")
```

### Storing Documents
```python
documents = [
    {
        "id": "doc_001",
        "content": "This is a sample document about machine learning.",
        "metadata": {
            "source": "ml_guide.pdf",
            "title": "Machine Learning Basics",
            "author": "John Doe"
        }
    }
]

await pinecone_store(
    index_name="my-documents",
    namespace="",
    documents=documents
)
```

### Retrieving Documents
```python
results = await pinecone_retrieve(
    index_name="my-documents",
    namespace="",
    query="machine learning algorithms",
    top_k=5
)
```

## Configuration Options

### Embedding Models
- **text-embedding-3-small**: 1536 dimensions, faster, cheaper
- **text-embedding-3-large**: 3072 dimensions, more accurate, higher cost

### Pinecone Index Settings
- **Dimension**: Must match embedding model output
- **Metric**: cosine, euclidean, dotproduct
- **Cloud**: AWS, GCP, Azure

## Troubleshooting

### Common Issues

1. **ModuleNotFoundError: No module named 'mcp'**
   - Solution: Install dependencies with `uv sync`
   - Ensure you're using the virtual environment

2. **Dimension Mismatch**
   - Solution: Ensure index dimension matches embedding model
   - Use `text-embedding-3-large` for 3072 dimensions

3. **Connection Issues**
   - Check API keys are correct
   - Verify network connectivity
   - Restart the MCP server

4. **Transport Errors**
   - For stdio: Ensure no other process is using the transport
   - For HTTP: Check port availability
   - For WebSocket: Verify WebSocket server is running

### Debug Mode
```bash
# Enable debug logging
DEBUG=1 uv run python main.py
```

## Development

### Adding New Tools
1. Create a new tool file in `src/tools/`
2. Define the tool function with `@mcp.tool()` decorator
3. Import and register in `src/server.py`

### Testing
```bash
# Run tests
uv run pytest

# Run specific test
uv run pytest test/test_rag_tools.py
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

[Add your license information here]

## Support

For issues and questions:
- Create an issue on GitHub
- Check the troubleshooting section
- Review MCP documentation at https://modelcontextprotocol.io

---

**Note**: This server is designed for development and production use with proper error handling, async operations, and comprehensive logging.