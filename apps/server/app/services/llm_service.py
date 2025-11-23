"""
LLM Service - Abstraction layer for different LLM providers.
Switch providers by changing LLM_PROVIDER in config.
"""
import os
import json
from abc import ABC, abstractmethod
from typing import Dict, List
import difflib
import logging
import random
import time


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    @abstractmethod
    def cluster_tasks(self, task_descriptions: List[str], task_titles: List[str]) -> Dict[str, List[str]]:
        """
        Cluster task titles into categories based on descriptions.
        
        Args:
            task_descriptions: List of task descriptions
            task_titles: List of corresponding task titles
            
        Returns:
            Dict mapping category names to lists of task titles
        """
        pass
    
    @abstractmethod
    def generate_tasks(self, n: int) -> List[Dict[str, str]]:
        """Generate `n` mock tasks using the provider. Returns list of {title, description}."""
        pass


class OpenAIProvider(LLMProvider):
    """OpenAI GPT clustering provider."""
    
    def __init__(self):
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError("openai package not installed. Run: pip install openai")
        
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        
        self.client = OpenAI(api_key=api_key)
        self.model = "gpt-3.5-turbo"
    
    def cluster_tasks(self, task_descriptions: List[str], task_titles: List[str]) -> Dict[str, List[str]]:
        """Call OpenAI API to cluster tasks."""
        task_text = "\n".join([
            f"- {title}: {desc}"
            for title, desc in zip(task_titles, task_descriptions)
        ])
        
        prompt = f"""You are a task organizer. Categorize the following tasks into logical groups/categories.
Return ONLY a valid JSON object with categories as keys and lists of task titles as values.
Categories should be general (Work, Home, Shopping, Health, Personal, Finance, Social, Other).
Ensure every task title is included in exactly one category.

Example output format:
{{"Work": ["Fix login bug", "Code review PR"], "Home": ["Buy groceries", "Clean kitchen"]}}

Tasks to categorize:
{task_text}

Respond with ONLY the JSON object, no markdown, no extra text:"""
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=1024,
        )
        
        llm_response = response.choices[0].message.content.strip()
        
        # Remove markdown code blocks if present
        if llm_response.startswith("```"):
            llm_response = llm_response.split("```")[1]
            if llm_response.startswith("json"):
                llm_response = llm_response[4:]
        
        clusters = json.loads(llm_response)
        return clusters

    def generate_tasks(self, n: int) -> List[Dict[str, str]]:
        """Ask OpenAI to generate `n` realistic task objects as JSON list.

        Returns:
            List of dicts: [{"title": "...", "description": "..."}, ...]
        """
        seed = random.randint(0, 10**9)
        prompt = f"""You are a task generator. Produce {n} realistic, concise todo tasks.
    Return a JSON array of objects, each with fields `title` and `description`.
    Titles should be short (3-6 words) and unique. Descriptions should be 5-20 words.
    Do not include the seed shown below in the output; it is only to encourage variance between calls.

    Seed: {seed}

    Return ONLY the JSON array, no markdown or explanatory text.

    Example:
    [{{"title": "Buy groceries", "description": "Milk, eggs, bread"}}, {{"title": "Fix login bug", "description": "Users cannot reset password"}}]
    """

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.9,
            max_tokens=800,
        )

        llm_response = response.choices[0].message.content.strip()
        if llm_response.startswith("```"):
            llm_response = llm_response.split("```")[1]
            if llm_response.startswith("json"):
                llm_response = llm_response[4:]

        logging.info("Raw LLM response for generate_tasks: %r", llm_response)
        try:
            tasks = json.loads(llm_response)
        except Exception as e:
            logging.exception("Failed to parse LLM response for generate_tasks: %s", llm_response)
            raise
        # Basic validation: ensure list of objects with title/description
        out = []
        for t in tasks:
            if isinstance(t, dict) and 'title' in t and 'description' in t:
                out.append({'title': str(t['title']).strip(), 'description': str(t['description']).strip()})
        # Log a short sample for debugging (do not log secrets)
        try:
            sample = [x['title'] for x in out[:5]]
        except Exception:
            sample = []
        logging.info('OpenAIProvider.generate_tasks seed=%s generated=%s sample=%s', seed, len(out), sample)
        return out


class OllamaProvider(LLMProvider):
    """Ollama local LLM clustering provider."""
    
    def __init__(self):
        import requests
        self.requests = requests
        self.base_url = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
        self.model = os.getenv('OLLAMA_MODEL', 'llama2')
        
        # Test connection
        try:
            self.requests.get(f"{self.base_url}/api/tags", timeout=5)
        except Exception as e:
            raise ConnectionError(f"Cannot connect to Ollama at {self.base_url}. Is it running? Error: {e}")
    
    def cluster_tasks(self, task_descriptions: List[str], task_titles: List[str]) -> Dict[str, List[str]]:
        """Call Ollama API to cluster tasks."""
        task_text = "\n".join([
            f"- {title}: {desc}"
            for title, desc in zip(task_titles, task_descriptions)
        ])
        
        prompt = f"""You are a task organizer. Categorize the following tasks into logical groups/categories.
Return ONLY a valid JSON object with categories as keys and lists of task titles as values.
Categories should be general (Work, Home, Shopping, Health, Personal, Finance, Social, Other).
Ensure every task title is included in exactly one category.

Example output format:
{{"Work": ["Fix login bug", "Code review PR"], "Home": ["Buy groceries", "Clean kitchen"]}}

Tasks to categorize:
{task_text}

Respond with ONLY the JSON object, no markdown, no extra text:"""
        
        response = self.requests.post(
            f"{self.base_url}/api/generate",
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "temperature": 0.5,
            },
            timeout=60,
        )
        
        response.raise_for_status()
        result = response.json()
        llm_response = result.get('response', '').strip()
        
        # Remove markdown code blocks if present
        if llm_response.startswith("```"):
            llm_response = llm_response.split("```")[1]
            if llm_response.startswith("json"):
                llm_response = llm_response[4:]
        
        clusters = json.loads(llm_response)
        return clusters

    def generate_tasks(self, n: int) -> List[Dict[str, str]]:
        """Ask Ollama to generate `n` mock tasks and parse JSON array response."""
        seed = random.randint(0, 10**9)
        prompt = f"""You are a task generator. Produce {n} realistic, concise todo tasks.
Return a JSON array of objects, each with fields `title` and `description`.
Titles should be short (3-6 words) and unique. Descriptions should be 5-20 words.
Do not include the seed shown below in the output; it is only to encourage variance between calls.

Seed: {seed}

Return ONLY the JSON array, no markdown or explanatory text.

Example:
[{{"title": "Buy groceries", "description": "Milk, eggs, bread"}}, {{"title": "Fix login bug", "description": "Users cannot reset password"}}]
"""

        response = self.requests.post(
            f"{self.base_url}/api/generate",
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "temperature": 0.9,
            },
            timeout=60,
        )

        response.raise_for_status()
        result = response.json()
        llm_response = result.get('response', '').strip()
        if llm_response.startswith("```"):
            llm_response = llm_response.split("```")[1]
            if llm_response.startswith("json"):
                llm_response = llm_response[4:]

        try:
            tasks = json.loads(llm_response)
        except Exception as e:
            logging.exception("Failed to parse Ollama response for generate_tasks: %s", llm_response)
            raise
        out = []
        for t in tasks:
            if isinstance(t, dict) and 'title' in t and 'description' in t:
                out.append({'title': str(t['title']).strip(), 'description': str(t['description']).strip()})
        try:
            sample = [x['title'] for x in out[:5]]
        except Exception:
            sample = []
        logging.info('OllamaProvider.generate_tasks seed=%s generated=%s sample=%s', seed, len(out), sample)
        return out


class LLMServiceFactory:
    """Factory to create LLM provider based on configuration."""
    
    _provider_cache = None
    
    @classmethod
    def get_provider(cls) -> LLMProvider:
        """Get the configured LLM provider."""
        if cls._provider_cache is not None:
            return cls._provider_cache
        
        provider_name = os.getenv('LLM_PROVIDER', 'openai').lower()
        
        if provider_name == 'openai':
            cls._provider_cache = OpenAIProvider()
        elif provider_name == 'ollama':
            cls._provider_cache = OllamaProvider()
        else:
            raise ValueError(f"Unknown LLM provider: {provider_name}. Use 'openai' or 'ollama'")
        
        return cls._provider_cache


class TaskClusteringService:
    """High-level service for task clustering."""
    
    @staticmethod
    def cluster_tasks(tasks: List) -> Dict[str, List[dict]]:
        """
        Cluster tasks using the configured LLM provider.
        
        Args:
            tasks: List of Task model objects
            
        Returns:
            Dict mapping category names to lists of task dicts
        """
        if not tasks:
            raise ValueError("No tasks to cluster")
        
        # Extract titles and descriptions
        task_titles = [t.title for t in tasks]
        task_descriptions = [t.description for t in tasks]
        
        # Get LLM provider and cluster
        provider = LLMServiceFactory.get_provider()
        clustered_titles = provider.cluster_tasks(task_descriptions, task_titles)
        
        # Map titles back to task objects
        task_map = {t.title: t for t in tasks}

        # also prepare a lowercase map for case-insensitive checks
        lower_map = {k.lower(): v for k, v in task_map.items()}

        # Build result with task dicts, using fuzzy matching when needed
        result = {}
        unmatched = []
        for category, titles in clustered_titles.items():
            result[category] = []
            for title in titles:
                # direct match
                if title in task_map:
                    result[category].append(task_map[title].to_dict())
                    continue

                # case-insensitive exact
                t_lower = title.lower()
                if t_lower in lower_map:
                    result[category].append(lower_map[t_lower].to_dict())
                    continue

                # substring match (title appears inside task title or vice-versa)
                found = None
                for k, task_obj in task_map.items():
                    if t_lower in k.lower() or k.lower() in t_lower:
                        found = task_obj
                        break
                if found:
                    result[category].append(found.to_dict())
                    continue

                # fuzzy match using difflib
                candidates = difflib.get_close_matches(title, list(task_map.keys()), n=1, cutoff=0.6)
                if candidates:
                    match = task_map[candidates[0]]
                    result[category].append(match.to_dict())
                    continue

                # nothing matched; record it for debugging
                unmatched.append(title)

        if unmatched:
            logging.warning('Unmatched clustered titles (no corresponding task found): %s', unmatched)

        return result
