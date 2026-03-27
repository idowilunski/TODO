"""
Agent service - Abstraction layer for different LLM providers doing agent research.
Switch providers by changing LLM_PROVIDER in config.
"""
import os
import json
import logging
from abc import ABC, abstractmethod
from openai import OpenAI
import ollama
try:
    import requests
except ImportError:
    requests = None


def search_shopping_serpapi(query: str, max_price: float = None) -> dict:
    """
    Real shopping search using SerpAPI.
    Requires SERPAPI_API_KEY in environment.
    Free tier: 100 searches/month at https://serpapi.com
    
    Args:
        query: Product search query
        max_price: Optional maximum price filter
        
    Returns:
        Dict with search results
    """
    api_key = os.getenv('SERPAPI_API_KEY')
    if not api_key:
        logging.warning("SERPAPI_API_KEY not set, falling back to mock data")
        return mock_search_shopping(query, max_price)
    
    if not requests:
        logging.warning("requests library not installed, falling back to mock data")
        return mock_search_shopping(query, max_price)
    
    try:
        response = requests.get('https://serpapi.com/search', params={
            'engine': 'google_shopping',
            'q': query,
            'api_key': api_key,
            'num': 10
        }, timeout=10)
        
        response.raise_for_status()
        data = response.json()
        
        results = []
        for item in data.get('shopping_results', [])[:10]:
            price_str = item.get('price', '').replace('$', '').replace(',', '')
            try:
                price = float(price_str)
            except:
                price = 0
            
            # Filter by max_price
            if max_price and price > max_price:
                continue
            
            results.append({
                'name': item.get('title', 'Unknown'),
                'price': price,
                'url': item.get('link', ''),
                'rating': item.get('rating', 0),
                'source': item.get('source', 'Unknown')
            })
        
        return {
            'query': query,
            'results': results[:3],
            'source': 'serpapi'
        }
    
    except Exception as e:
        logging.error(f"SerpAPI error: {e}, falling back to mock data")
        return mock_search_shopping(query, max_price)


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


# Tool definition (shared by all providers)
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


class AgentProvider(ABC):
    """Abstract base class for agent services."""
    
    @abstractmethod
    def research_task(self, task_title: str, task_description: str) -> dict:
        """
        Use LLM agent to research a task.
        
        Args:
            task_title: Task title
            task_description: Task description with requirements
            
        Returns:
            Dict with recommendation and iterations
        """
        pass


class OpenAIAgentProvider(AgentProvider):
    """OpenAI implementation of agent service."""
    
    def research_task(self, task_title: str, task_description: str) -> dict:
        client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        user_prompt = f"""I need help finding the best product for this task:

Title: {task_title}
Requirements: {task_description}

Please search for options and recommend the best one based on price, ratings, and value."""
        
        messages = [{"role": "user", "content": user_prompt}]
        
        # Agent loop (max 5 iterations)
        for iteration in range(5):
            logging.info(f"[OpenAI] Agent iteration {iteration + 1}")
            
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                tools=TOOLS,
                tool_choice="auto"
            )
            
            assistant_message = response.choices[0].message
            messages.append(assistant_message)
            
            # Check if agent wants to call a function
            if assistant_message.tool_calls:
                for tool_call in assistant_message.tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)
                    
                    logging.info(f"[OpenAI] Agent calling: {function_name}({function_args})")
                    
                    # Execute the function
                    if function_name == "search_shopping":
                        function_result = search_shopping_serpapi(**function_args)
                    else:
                        function_result = {"error": "Unknown function"}
                    
                    # Add function result to conversation
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(function_result)
                    })
                
                continue
            
            # Agent finished
            if assistant_message.content:
                logging.info(f"[OpenAI] Agent final response: {assistant_message.content[:200]}")
                return {
                    "recommendation": assistant_message.content,
                    "iterations": iteration + 1
                }
        
        return {
            "recommendation": "Unable to complete research (max iterations reached)",
            "error": "timeout"
        }


class OllamaAgentProvider(AgentProvider):
    """Ollama implementation of agent service."""
    
    def __init__(self, model: str = "llama3.2"):
        self.model = model
    
    def research_task(self, task_title: str, task_description: str) -> dict:
        user_prompt = f"""I need help finding the best product for this task:

Title: {task_title}
Requirements: {task_description}

Please search for options and recommend the best one based on price, ratings, and value."""
        
        messages = [{"role": "user", "content": user_prompt}]
        
        # Agent loop (max 5 iterations)
        for iteration in range(5):
            logging.info(f"[Ollama] Agent iteration {iteration + 1}")
            
            try:
                response = ollama.chat(
                    model=self.model,
                    messages=messages,
                    tools=TOOLS,
                )
                
                assistant_message = response['message']
                messages.append(assistant_message)
                
                # Check if agent wants to call a function
                if assistant_message.get('tool_calls'):
                    for tool_call in assistant_message['tool_calls']:
                        function_name = tool_call['function']['name']
                        function_args = tool_call['function']['arguments']
                        
                        logging.info(f"[Ollama] Agent calling: {function_name}({function_args})")
                        
                        # Execute the function
                        if function_name == "search_shopping":
                            function_result = search_shopping_serpapi(**function_args)
                        else:
                            function_result = {"error": "Unknown function"}
                        
                        # Add function result to conversation
                        messages.append({
                            "role": "tool",
                            "content": json.dumps(function_result)
                        })
                    
                    continue
                
                # Agent finished
                if assistant_message.get('content'):
                    logging.info(f"[Ollama] Agent final response: {assistant_message['content'][:200]}")
                    return {
                        "recommendation": assistant_message['content'],
                        "iterations": iteration + 1
                    }
            
            except Exception as e:
                logging.error(f"[Ollama] Error in iteration {iteration + 1}: {e}")
                return {
                    "recommendation": f"Error communicating with Ollama: {str(e)}",
                    "error": "ollama_error"
                }
        
        return {
            "recommendation": "Unable to complete research (max iterations reached)",
            "error": "timeout"
        }


class AgentServiceFactory:
    """Factory to get the appropriate agent provider based on config."""
    
    @staticmethod
    def get_agent() -> AgentProvider:
        """Get agent provider based on LLM_PROVIDER environment variable."""
        provider = os.getenv('LLM_PROVIDER', 'openai').lower()
        
        if provider == 'openai':
            return OpenAIAgentProvider()
        elif provider == 'ollama':
            model = os.getenv('OLLAMA_MODEL', 'llama3.2')
            return OllamaAgentProvider(model=model)
        else:
            raise ValueError(f"Unknown LLM provider: {provider}")
