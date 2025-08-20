
"""
  Web Search Tools using DuckDuckGo + Content Scraping
  Provides ChatGPT-style web search functionality
"""



from mcp.server.fastmcp import FastMCP

import asyncio
import aiohttp
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS
from typing import List, Dict, Optional
import logging
import re
from urllib.parse import urljoin


logger = logging.getLogger(__name__)



def web_search_tools(mcp: FastMCP) -> None:
    """Register the web search tool with the MCP server."""

    @mcp.tool()
    async def web_search(query: str, max_results: int = 5):
        """Search the web for information
        Args:
            query: The query to search for
            max_results: The maximum number of results to return
        """
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=max_results))
        
            formatted_results = []
            for result in results:
                # Debug: log the result structure
                logger.info(f"DuckDuckGo result keys: {result.keys() if isinstance(result, dict) else 'Not a dict'}")
                
                formatted_results.append({
                    "title": result.get("title", "") or result.get("t", ""),
                    "url": result.get("href", "") or result.get("u", "") or result.get("link", ""),
                    "snippet": result.get("body", "") or result.get("a", "") or result.get("snippet", ""),
                    "raw_result": str(result)  # Debug info
                })
        
            return {
                "query": query,
                "results": formatted_results,
                "total_found": len(formatted_results),
            }
        except Exception as e:
            logger.error(f"Web search error: {e}")
            return {
                "query": query,
                "results": [],
                "total_found": 0,
                "error": str(e)
            }

    @mcp.tool()
    async def web_search_with_content(query: str, max_results: int = 3):
        """Search web, scrape content, and provide detailed results
        Args:
            query: The query to search for
            max_results: The maximum number of results to return
        """
        try:
            with DDGS() as ddgs:
                search_results = []
                for result in ddgs.text(query, max_results=max_results):
                    search_results.append({
                        "title": result.get("title",""),
                        "url": result.get("href",""),
                        "snippet": result.get("body",""),
                    })

                # 2. Scrape content from URLs
                scraped_content = await scrape_multiple_urls([r["url"] for r in search_results])
                
                enhanced_results = []
                for result in search_results:
                    url = result["url"]
                    content = scraped_content.get(url, "")
    
                    enhanced_results.append({
                        "title": result["title"],
                        "url": url,
                        "snippet": result["snippet"],
                        "content": content[:2000] if content else "",  # Limit content length
                        "content_available": bool(content)
                    })
                
                all_content = "\n\n".join([
                    f"{r['content']}\nSource: {r['url']}" 
                    for r in enhanced_results 
                    if r["content"]
                ])

                # summary = create_summary(all_content, query) if all_content else "No content could be scraped."

                return {
                    "query": query,
                    "results": enhanced_results,
                    "summary": all_content,
                    "total_found": len(enhanced_results),
                }
        except Exception as e:
            logger.error(f"Error in web_search_with_content: {e}")
            return {
                "query": query,
                "results": [],
                "summary": "No content could be scraped.",
                "total_found": 0,
                "error": str(e)
            }


    @mcp.tool()
    async def debug_search(query: str = "test"):
        """Debug tool to check DuckDuckGo response format"""
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=1))
                
            if results:
                first_result = results[0]
                return {
                    "raw_result": str(first_result),
                    "result_type": str(type(first_result)),
                    "keys": list(first_result.keys()) if isinstance(first_result, dict) else "Not a dict",
                    "sample_values": {k: str(v)[:100] for k, v in first_result.items()} if isinstance(first_result, dict) else "Not a dict"
                }
            else:
                return {"error": "No results found"}
        except Exception as e:
            return {"error": str(e)}

    @mcp.tool()
    async def scrape_url(url: str) -> Dict:
        """ 
        Scrape the content of a URL
        Args:
            url: The URL to scrape
        """
        try:
            content = await scrape_single_url(url)
            return {
                "url": url,
                "content": content,
                "success": bool(content)
            }
        except Exception as e:
            logger.error(f"Error in scrape_url: {e}")
            return {
              "url": url,
              "error": str(e),
              "success": False
          }


# Helper Functions
async def scrape_single_url(url: str) -> Optional[str]:
    """Scrape content from a single URL"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status != 200:
                    return None
                html = await response.text()
                soup = BeautifulSoup(html, 'lxml')
                # Remove unwanted elements
                for element in soup(['script', 'style', 'nav', 'footer', 'aside', 'header', 'form']):
                    element.decompose()
                # Find main content
                main_content = (
                    soup.find('main') or
                    soup.find('article') or
                    soup.find('div', class_=re.compile(r'content|article|main', re.I)) or
                    soup.find('div', id=re.compile(r'content|article|main', re.I)) or
                    soup.find('body')
                )
                if main_content:
                    # Extract text
                    text = main_content.get_text(separator=' ', strip=True)
                    # Clean whitespace
                    text = re.sub(r'\s+', ' ', text)
                    # Limit length
                    return text[:5000] if len(text) > 5000 else text
                return None
    except Exception as e:
        logger.error(f"Failed to scrape {url}: {e}")
        return None
        
        
async def scrape_multiple_urls(urls: List[str]) -> Dict[str, Optional[str]]:
    """Scrape content from multiple URLs concurrently"""
    tasks = [scrape_single_url(url) for url in urls]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    scraped_content = {}
    for url, result in zip(urls, results):
        if isinstance(result, Exception):
            scraped_content[url] = None
        else:
            scraped_content[url] = result
    return scraped_content                       


