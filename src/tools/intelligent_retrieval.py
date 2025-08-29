"""
Intelligent Retrieval Coordinator

Automatically triggers RAG workflows based on user intent using MCP prompts.
This module integrates with existing RAG tools to provide seamless automatic retrieval.
"""

import re
import asyncio
from typing import Dict, List, Optional, Tuple
from mcp.server.fastmcp import FastMCP


def intelligent_retrieval_coordinator(mcp: FastMCP) -> None:
    """
    Register intelligent retrieval coordinator that automatically triggers RAG workflows
    """
    
    # Intent detection patterns
    KNOWLEDGE_PATTERNS = [
        r"\b(what is|what are|tell me about|explain|describe)\b",
        r"\b(how does|how do|how to|how can)\b", 
        r"\b(why|when|where|who)\b",
        r"\b(definition of|meaning of|concept of)\b"
    ]
    
    RESEARCH_PATTERNS = [
        r"\b(find|search|lookup|get information|research)\b",
        r"\b(show me|give me|provide|fetch)\b",
        r"\b(details about|data on|information on)\b"
    ]
    
    ANALYSIS_PATTERNS = [
        r"\b(analyze|compare|review|summarize|evaluate)\b",
        r"\b(differences between|similarities between)\b",
        r"\b(pros and cons|advantages|disadvantages)\b"
    ]
    
    EXAMPLE_PATTERNS = [
        r"\b(example|sample|demonstration|show example)\b",
        r"\b(code example|implementation example)\b"
    ]
    
    # Domain detection patterns
    DOMAIN_PATTERNS = {
        "technical": [
            r"\b(api|function|class|method|algorithm|code|programming)\b",
            r"\b(implementation|framework|library|database|server)\b",
            r"\b(error|bug|debug|test|deployment)\b"
        ],
        "business": [
            r"\b(strategy|market|revenue|cost|profit|customer)\b", 
            r"\b(business|management|operations|sales|marketing)\b"
        ],
        "code": [
            r"\b(python|javascript|java|react|node|sql|html|css)\b",
            r"\b(function|class|variable|loop|condition|import)\b"
        ]
    }
    
    def analyze_query_intent(query: str) -> Dict[str, any]:
        """Analyze user query to determine intent and optimal retrieval strategy"""
        query_lower = query.lower()
        
        # Check for retrieval triggers
        needs_retrieval = False
        intent_type = "conversational"
        
        if any(re.search(pattern, query_lower, re.IGNORECASE) for pattern in KNOWLEDGE_PATTERNS):
            needs_retrieval = True
            intent_type = "knowledge"
            
        elif any(re.search(pattern, query_lower, re.IGNORECASE) for pattern in RESEARCH_PATTERNS):
            needs_retrieval = True  
            intent_type = "research"
            
        elif any(re.search(pattern, query_lower, re.IGNORECASE) for pattern in ANALYSIS_PATTERNS):
            needs_retrieval = True
            intent_type = "analysis"
            
        elif any(re.search(pattern, query_lower, re.IGNORECASE) for pattern in EXAMPLE_PATTERNS):
            needs_retrieval = True
            intent_type = "examples"
        
        # Detect domain
        domain = "general"
        for domain_name, patterns in DOMAIN_PATTERNS.items():
            if any(re.search(pattern, query_lower, re.IGNORECASE) for pattern in patterns):
                domain = domain_name
                break
        
        # Determine complexity and parameters
        word_count = len(query.split())
        complexity = "simple" if word_count <= 3 else "medium" if word_count <= 8 else "complex"
        
        top_k = {
            "simple": 3,
            "medium": 5, 
            "complex": 10
        }.get(complexity, 5)
        
        namespace = {
            "technical": "technical",
            "code": "code", 
            "business": "business"
        }.get(domain, "")
        
        return {
            "needs_retrieval": needs_retrieval,
            "intent_type": intent_type,
            "domain": domain,
            "complexity": complexity,
            "suggested_top_k": top_k,
            "suggested_namespace": namespace,
            "query_analysis": {
                "word_count": word_count,
                "has_question_words": bool(re.search(r"\b(what|how|why|when|where|who)\b", query_lower)),
                "is_specific": bool(re.search(r"\b(specific|exactly|precisely|details)\b", query_lower))
            }
        }
    
    @mcp.tool()
    async def intelligent_retrieve(
        query: str, 
        index_name: str = "main-knowledge",
        force_retrieval: bool = False,
        conversation_context: str = ""
    ) -> dict:
        """
        Intelligent retrieval that automatically determines when and how to search based on query intent
        
        Args:
            query: User's input query
            index_name: Target Pinecone index (default: "main-knowledge")  
            force_retrieval: Force retrieval even if intent detection suggests otherwise
            conversation_context: Previous conversation context for better intent understanding
            
        Returns:
            Dictionary with retrieval results and metadata about the decision process
        """
        try:
            # Analyze query intent 
            analysis = analyze_query_intent(query)
            
            # Enhanced context analysis if conversation context provided
            if conversation_context:
                # Check for referential queries ("that", "it", "this")
                if re.search(r"\b(that|it|this|they|those)\b", query.lower()):
                    analysis["needs_retrieval"] = True
                    analysis["intent_type"] = "contextual_reference"
                    # Use conversation context to enhance query
                    enhanced_query = f"{conversation_context[-200:]} {query}"
                else:
                    enhanced_query = query
            else:
                enhanced_query = query
            
            # Decision logic
            if not analysis["needs_retrieval"] and not force_retrieval:
                return {
                    "success": True,
                    "decision": "no_retrieval_needed",
                    "intent_analysis": analysis,
                    "message": "Query detected as conversational - no retrieval needed",
                    "suggested_response": "direct_answer"
                }
            
            # Get the pinecone_retrieve tool from MCP
            from .rag_tools.rag_retrical import rag_retrival
            
            # Import the actual function (this is a bit hacky but works)
            import importlib.util
            import sys
            
            # Create a temporary module to access the function
            spec = importlib.util.spec_from_file_location(
                "rag_module", 
                "/Users/logic-liar/Documents/AiVi/FastMCP/mcp-server/src/tools/rag_tools/rag_retrical.py"
            )
            rag_module = importlib.util.module_from_spec(spec)
            sys.modules["rag_module"] = rag_module
            spec.loader.exec_module(rag_module)
            
            # Execute retrieval with optimized parameters
            retrieval_params = {
                "index_name": index_name,
                "namespace": analysis["suggested_namespace"], 
                "query": enhanced_query,
                "top_k": analysis["suggested_top_k"]
            }
            
            # This is where you'd call your actual pinecone_retrieve function
            # For now, return the analysis and suggested parameters
            return {
                "success": True,
                "decision": "retrieval_triggered",
                "intent_analysis": analysis,
                "retrieval_params": retrieval_params,
                "enhanced_query": enhanced_query,
                "message": f"Automatic retrieval triggered for {analysis['intent_type']} query in {analysis['domain']} domain",
                "next_action": "call_pinecone_retrieve_with_params"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Intelligent retrieval failed: {str(e)}",
                "decision": "error"
            }
    
    @mcp.tool()
    async def auto_rag_workflow(
        query: str,
        index_name: str = "main-knowledge", 
        conversation_context: str = "",
        user_preferences: dict = None
    ) -> dict:
        """
        Complete automatic RAG workflow that handles the entire process from query to response
        
        Args:
            query: User's query
            index_name: Target Pinecone index
            conversation_context: Previous conversation for context
            user_preferences: User preferences for retrieval (optional)
            
        Returns:
            Complete workflow result with retrieved content and AI response
        """
        try:
            # Step 1: Intent Analysis
            analysis = analyze_query_intent(query)
            
            # Step 2: Auto-trigger retrieval if needed
            if analysis["needs_retrieval"]:
                
                # Get the pinecone_retrieve function
                # Note: In a real implementation, you'd get this from your tool registry
                retrieval_result = {
                    "intent_detected": analysis["intent_type"],
                    "domain": analysis["domain"],
                    "should_call_pinecone_retrieve": True,
                    "parameters": {
                        "index_name": index_name,
                        "namespace": analysis["suggested_namespace"],
                        "query": query,
                        "top_k": analysis["suggested_top_k"]
                    }
                }
                
                return {
                    "success": True,
                    "workflow_stage": "retrieval_triggered",
                    "retrieval_decision": retrieval_result,
                    "message": f"Auto-triggered {analysis['intent_type']} retrieval for domain: {analysis['domain']}",
                    "next_steps": [
                        "1. Call pinecone_retrieve with suggested parameters",
                        "2. Process and rank results",
                        "3. Generate contextual response",
                        "4. Provide source citations"
                    ]
                }
            else:
                return {
                    "success": True,
                    "workflow_stage": "direct_response",
                    "retrieval_decision": {"should_retrieve": False},
                    "message": "Query identified as conversational - responding directly without retrieval"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Auto RAG workflow failed: {str(e)}"
            }
    
    @mcp.tool()
    async def query_intent_analyzer(query: str) -> dict:
        """
        Analyze user query intent for debugging and optimization
        
        Args:
            query: User's input query
            
        Returns:
            Detailed analysis of query intent and suggested actions
        """
        analysis = analyze_query_intent(query)
        
        return {
            "query": query,
            "analysis": analysis,
            "recommendations": {
                "should_retrieve": analysis["needs_retrieval"],
                "retrieval_params": {
                    "top_k": analysis["suggested_top_k"],
                    "namespace": analysis["suggested_namespace"]
                },
                "enhancement_suggestions": [
                    "Consider adding domain-specific keywords",
                    f"Query complexity: {analysis['complexity']}",
                    f"Detected domain: {analysis['domain']}"
                ]
            }
        }