"""
Agent service for OpenAI function calling.
Handles tool execution and multi-turn conversations.
"""
import os
import json
import logging
from openai import OpenAI


def mock_search_shopping(query: str, max_price: float = None) -> dict:
    """
    Mock shopping search function.
    In production, this would call a real API (Google Shopping, SerpAPI, etc.)
    
    Args:
        query: Product search query (e.g., "wireless mouse")
        max_price: Optional maximum price filter
        
    Returns:
        Dict with search results
    """
    # Hardcoded mock results
    mock_products = {
        "wireless mouse": [
            {"name": "Logitech M185", "price": 24.99, "url": "https://amazon.com/logitech-m185", "rating": 4.5},
            {"name": "HP X3000", "price": 19.99, "url": "https://amazon.com/hp-x3000", "rating": 4.2},
            {"name": "Microsoft Bluetooth Mouse", "price": 29.99, "url": "https://amazon.com/microsoft-bt", "rating": 4.6}
        ],
        "wireless keyboard": [
            {"name": "Logitech K380", "price": 39.99, "url": "https://amazon.com/logitech-k380", "rating": 4.6},
            {"name": "Anker Ultra Compact", "price": 24.99, "url": "https://amazon.com/anker-keyboard", "rating": 4.4},
            {"name": "Microsoft Designer", "price": 59.99, "url": "https://amazon.com/ms-designer", "rating": 4.7}
        ],
        "headphones": [
            {"name": "Sony WH-1000XM5", "price": 349.99, "url": "https://amazon.com/sony-xm5", "rating": 4.8},
            {"name": "Bose QC45", "price": 329.99, "url": "https://amazon.com/bose-qc45", "rating": 4.7},
            {"name": "Anker Q30", "price": 79.99, "url": "https://amazon.com/anker-q30", "rating": 4.5}
        ]
    }
    
    # Find matching products (simple keyword match)
    results = []
    query_lower = query.lower()
    for key, products in mock_products.items():
        if key in query_lower or any(word in query_lower for word in key.split()):
            results.extend(products)
    
    # Filter by price if specified
    if max_price:
        results = [p for p in results if p["price"] <= max_price]
    
    # Return top 3
    return {
        "query": query,
        "results": results[:3] if results else [
            {"name": "Generic Product", "price": 29.99, "url": "https://amazon.com/search", "rating": 4.0}
        ]
    }


class AgentService:
    """Service for running OpenAI agents with function calling."""
    
    # Define available tools (functions the agent can call)
    TOOLS = [
        {
            "type": "function",
            "function": {
                "name": "search_shopping",
                "description": "Search for products online. Returns product names, prices, URLs, and ratings.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The product to search for (e.g., 'wireless mouse', 'bluetooth headphones')"
                        },
                        "max_price": {
                            "type": "number",
                            "description": "Optional maximum price in USD"
                        }
                    },
                    "required": ["query"]
                }
            }
        }
    ]
    
    @classmethod
    def research_task(cls, task_title: str, task_description: str) -> dict:
        """
        Use OpenAI agent to research a shopping task.
        
        Args:
            task_title: Task title (e.g., "Buy wireless mouse")
            task_description: Task description with requirements
            
        Returns:
            Dict with recommendation, price, url, reasoning
        """
        client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        # Initial prompt to the agent
        user_prompt = f"""I need help finding the best product for this task:

Title: {task_title}
Requirements: {task_description}

Please search for options and recommend the best one based on price, ratings, and value."""
        
        messages = [{"role": "user", "content": user_prompt}]
        
        # Agent loop (max 5 iterations to prevent infinite loops)
        for iteration in range(5):
            logging.info(f"Agent iteration {iteration + 1}")
            
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                tools=cls.TOOLS,
                tool_choice="auto"  # Let the model decide when to call functions
            )
            
            assistant_message = response.choices[0].message
            messages.append(assistant_message)
            
            # Check if the agent wants to call a function
            if assistant_message.tool_calls:
                # Execute each function call
                for tool_call in assistant_message.tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)
                    
                    logging.info(f"Agent calling: {function_name}({function_args})")
                    
                    # Execute the function
                    if function_name == "search_shopping":
                        function_result = mock_search_shopping(**function_args)
                    else:
                        function_result = {"error": "Unknown function"}
                    
                    # Add function result to conversation
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(function_result)
                    })
                
                # Continue loop to get agent's response to function results
                continue
            
            # Agent has finished and returned a text response
            if assistant_message.content:
                logging.info(f"Agent final response: {assistant_message.content[:200]}")
                
                # Parse the response to extract structured data
                # In a real app, you might ask the agent to return JSON
                return {
                    "recommendation": assistant_message.content,
                    "iterations": iteration + 1
                }
        
        # Max iterations reached
        return {
            "recommendation": "Unable to complete research (max iterations reached)",
            "error": "timeout"
        }
