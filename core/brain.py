"""Central Brain - Query routing and command orchestration"""

import re
from typing import Dict, Any, Optional
from openai import OpenAI

class Brain:
    def __init__(self, openai_api_key: str):
        self.client = OpenAI(api_key=openai_api_key)
        self.command_registry = {}
        self.command_patterns = []
        
    def register_module(self, module_name: str, patterns: list, handler):
        """Register a module with its trigger patterns and handler function"""
        self.command_registry[module_name] = {
            'patterns': patterns,
            'handler': handler
        }
        # Compile regex patterns for faster matching
        for pattern in patterns:
            self.command_patterns.append((re.compile(pattern, re.IGNORECASE), handler))
    
    def process_query(self, query: str) -> Dict[str, Any]:
        """Main routing function - determines if query should go to handler or LLM"""
        # First check if query matches any predefined command patterns
        for pattern, handler in self.command_patterns:
            if pattern.search(query):
                return {
                    'type': 'command',
                    'handler': handler,
                    'response': handler(query)
                }
        
        # If no pattern matches, route to LLM
        return self._route_to_llm(query)
    
    def _route_to_llm(self, query: str) -> Dict[str, Any]:
        """Send query to OpenAI API for complex natural language understanding"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are Jarvis, a helpful AI assistant. Respond concisely and accurately."},
                    {"role": "user", "content": query}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            return {
                'type': 'llm',
                'response': response.choices[0].message.content
            }
        except Exception as e:
            return {
                'type': 'error',
                'response': f"Error communicating with LLM: {str(e)}"
            }
    
    def function_call_to_llm(self, query: str, available_functions: list) -> Dict[str, Any]:
        """Use OpenAI function calling to determine which module to invoke"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": query}],
                functions=available_functions,
                function_call="auto"
            )
            
            message = response.choices[0].message
            
            if message.function_call:
                return {
                    'type': 'function_call',
                    'function': message.function_call.name,
                    'arguments': message.function_call.arguments
                }
            else:
                return {
                    'type': 'llm',
                    'response': message.content
                }
        except Exception as e:
            return {
                'type': 'error',
                'response': f"Error with function calling: {str(e)}"
            }
