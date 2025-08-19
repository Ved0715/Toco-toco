from src.server import mcp

def main():
    mcp.run(transport="streamable-http") #for streamable HTTP port
    # mcp.run(transport="http") #for streamable HTTP port
    # mcp.run()  # Use default stdio transport for Claude Desktop

if __name__ == "__main__":
    main()





