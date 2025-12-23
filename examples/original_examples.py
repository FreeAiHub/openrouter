#!/usr/bin/env python3
"""
OpenRouter API - Practical Examples for Cost-Effective Development
Demonstrates real-world usage patterns with free and cheap models
"""

import os
import json
import requests
from typing import Optional, List, Dict, Any
from datetime import datetime

API_KEY = os.getenv("OPENROUTER_API_KEY")
BASE_URL = "https://openrouter.ai/api/v1"

# ============================================================================
# EXAMPLE 1: Simple Wrapper Function
# ============================================================================

def simple_query(prompt: str, model: str = "xiaomi/mimo-v2-flash:free") -> str:
    """
    Simplest way to use OpenRouter API
    Perfect for quick tests and prototypes
    """
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }
    
    response = requests.post(
        f"{BASE_URL}/chat/completions",
        headers=headers,
        json={
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
        }
    )
    
    return response.json()["choices"][0]["message"]["content"]


# ============================================================================
# EXAMPLE 2: Conversation Manager with History
# ============================================================================

class ConversationManager:
    """Manage multi-turn conversations with context"""
    
    def __init__(self, model: str = "xiaomi/mimo-v2-flash:free"):
        self.model = model
        self.messages = []
        self.headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
        }
    
    def add_system_prompt(self, system_prompt: str):
        """Add system context"""
        self.messages = [{"role": "system", "content": system_prompt}]
    
    def ask(self, question: str) -> str:
        """Ask a question and maintain context"""
        self.messages.append({"role": "user", "content": question})
        
        response = requests.post(
            f"{BASE_URL}/chat/completions",
            headers=self.headers,
            json={
                "model": self.model,
                "messages": self.messages,
                "max_tokens": 500,
            }
        )
        
        answer = response.json()["choices"][0]["message"]["content"]
        self.messages.append({"role": "assistant", "content": answer})
        
        return answer
    
    def clear(self):
        """Clear conversation history"""
        self.messages = []
    
    def get_history(self) -> List[Dict]:
        """Get conversation history"""
        return self.messages.copy()


# ============================================================================
# EXAMPLE 3: Batch Processing with Cost Tracking
# ============================================================================

class BatchProcessor:
    """Process multiple requests and track costs"""
    
    def __init__(self, model: str = "xiaomi/mimo-v2-flash:free"):
        self.model = model
        self.headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
        }
        self.results = []
        self.total_tokens = {"input": 0, "output": 0}
    
    def process_batch(self, prompts: List[str]) -> List[Dict]:
        """Process multiple prompts"""
        for i, prompt in enumerate(prompts, 1):
            print(f"Processing {i}/{len(prompts)}...", end=" ")
            
            response = requests.post(
                f"{BASE_URL}/chat/completions",
                headers=self.headers,
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                }
            )
            
            data = response.json()
            result = {
                "prompt": prompt,
                "response": data["choices"][0]["message"]["content"],
                "usage": data.get("usage", {}),
            }
            
            self.results.append(result)
            
            # Track tokens
            if "usage" in data:
                self.total_tokens["input"] += data["usage"].get("prompt_tokens", 0)
                self.total_tokens["output"] += data["usage"].get("completion_tokens", 0)
            
            print("✓")
        
        return self.results
    
    def get_cost_summary(self) -> Dict:
        """Calculate total cost (free models = $0)"""
        return {
            "model": self.model,
            "total_requests": len(self.results),
            "total_input_tokens": self.total_tokens["input"],
            "total_output_tokens": self.total_tokens["output"],
            "cost": "$0.00" if "free" in self.model else "Calculate based on pricing",
        }


# ============================================================================
# EXAMPLE 4: Streaming Response Handler
# ============================================================================

class StreamingHandler:
    """Handle streaming responses efficiently"""
    
    def __init__(self, model: str = "xiaomi/mimo-v2-flash:free"):
        self.model = model
        self.headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
        }
    
    def stream_response(self, prompt: str, callback=None):
        """Stream response with optional callback"""
        response = requests.post(
            f"{BASE_URL}/chat/completions",
            headers=self.headers,
            json={
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "stream": True,
            },
            stream=True,
        )
        
        full_response = ""
        
        for line in response.iter_lines():
            if line:
                line = line.decode("utf-8")
                if line.startswith("data: "):
                    data_str = line[6:]
                    if data_str != "[DONE]":
                        try:
                            data = json.loads(data_str)
                            delta = data["choices"][0].get("delta", {})
                            content = delta.get("content", "")
                            
                            if content:
                                full_response += content
                                if callback:
                                    callback(content)
                                else:
                                    print(content, end="", flush=True)
                        except json.JSONDecodeError:
                            pass
        
        print()  # Newline after streaming
        return full_response


# ============================================================================
# EXAMPLE 5: Model Comparison
# ============================================================================

def compare_models(prompt: str, models: List[str]) -> Dict:
    """Compare responses from different models"""
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }
    
    results = {}
    
    for model in models:
        print(f"\nTesting {model}...")
        
        try:
            response = requests.post(
                f"{BASE_URL}/chat/completions",
                headers=headers,
                json={
                    "model": model,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 200,
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                results[model] = {
                    "response": data["choices"][0]["message"]["content"],
                    "tokens": data.get("usage", {}),
                    "status": "success",
                }
            else:
                results[model] = {
                    "error": response.text,
                    "status": "error",
                }
        except Exception as e:
            results[model] = {
                "error": str(e),
                "status": "exception",
            }
    
    return results


# ============================================================================
# EXAMPLE 6: Error Handling and Retry Logic
# ============================================================================

def robust_api_call(
    prompt: str,
    model: str = "xiaomi/mimo-v2-flash:free",
    max_retries: int = 3,
    timeout: int = 30
) -> Optional[str]:
    """Make API call with retry logic and error handling"""
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }
    
    for attempt in range(max_retries):
        try:
            print(f"Attempt {attempt + 1}/{max_retries}...", end=" ")
            
            response = requests.post(
                f"{BASE_URL}/chat/completions",
                headers=headers,
                json={
                    "model": model,
                    "messages": [{"role": "user", "content": prompt}],
                },
                timeout=timeout,
            )
            
            if response.status_code == 200:
                print("✓")
                return response.json()["choices"][0]["message"]["content"]
            
            elif response.status_code == 429:
                print("Rate limited, retrying...")
                import time
                time.sleep(2 ** attempt)  # Exponential backoff
            
            elif response.status_code == 400:
                print("Bad request")
                print(f"Error: {response.json()}")
                return None
            
            else:
                print(f"Error {response.status_code}")
        
        except requests.Timeout:
            print("Timeout, retrying...")
        except Exception as e:
            print(f"Error: {e}")
    
    print("Failed after all retries")
    return None


# ============================================================================
# EXAMPLE 7: Using with OpenAI SDK
# ============================================================================

def example_with_openai_sdk():
    """Use OpenRouter with OpenAI Python SDK"""
    
    try:
        from openai import OpenAI
        
        client = OpenAI(
            api_key=API_KEY,
            base_url=BASE_URL,
        )
        
        # Simple completion
        response = client.chat.completions.create(
            model="xiaomi/mimo-v2-flash:free",
            messages=[
                {"role": "user", "content": "What is 2+2?"}
            ]
        )
        
        print("OpenAI SDK Response:", response.choices[0].message.content)
        
        # Streaming with SDK
        stream = client.chat.completions.create(
            model="xiaomi/mimo-v2-flash:free",
            messages=[
                {"role": "user", "content": "Count to 5"}
            ],
            stream=True,
        )
        
        print("\nStreaming with SDK:")
        for chunk in stream:
            if chunk.choices[0].delta.content:
                print(chunk.choices[0].delta.content, end="", flush=True)
        print()
        
    except ImportError:
        print("OpenAI SDK not installed. Install with: pip install openai")


# ============================================================================
# MAIN: Run Examples
# ============================================================================

def main():
    """Run all examples"""
    
    if not API_KEY:
        print("❌ OPENROUTER_API_KEY not set")
        return
    
    print("=" * 70)
    print("OpenRouter API - Practical Examples")
    print("=" * 70)
    
    # Example 1: Simple Query
    print("\n📝 Example 1: Simple Query")
    print("-" * 70)
    result = simple_query("What is the capital of France?")
    print(f"Response: {result}")
    
    # Example 2: Conversation Manager
    print("\n💬 Example 2: Multi-turn Conversation")
    print("-" * 70)
    conv = ConversationManager()
    conv.add_system_prompt("You are a helpful assistant.")
    print("Q: What is Python?")
    print(f"A: {conv.ask('What is Python?')}")
    print("Q: What are its main uses?")
    print(f"A: {conv.ask('What are its main uses?')}")
    
    # Example 3: Batch Processing
    print("\n📦 Example 3: Batch Processing")
    print("-" * 70)
    processor = BatchProcessor()
    prompts = [
        "What is machine learning?",
        "Explain neural networks",
        "What is deep learning?"
    ]
    processor.process_batch(prompts)
    print(f"Cost Summary: {processor.get_cost_summary()}")
    
    # Example 4: Streaming
    print("\n🌊 Example 4: Streaming Response")
    print("-" * 70)
    streamer = StreamingHandler()
    print("Streaming response: ", end="")
    streamer.stream_response("Count from 1 to 3")
    
    # Example 5: Model Comparison
    print("\n⚖️ Example 5: Model Comparison")
    print("-" * 70)
    models_to_compare = [
        "xiaomi/mimo-v2-flash:free",
        "kwaipilot/kat-coder-pro-v1:free",
    ]
    comparison = compare_models("What is AI?", models_to_compare)
    for model, result in comparison.items():
        print(f"\n{model}:")
        if result["status"] == "success":
            print(f"  Response: {result['response'][:100]}...")
        else:
            print(f"  Error: {result['error']}")
    
    # Example 6: Robust API Call
    print("\n🛡️ Example 6: Robust API Call with Retries")
    print("-" * 70)
    result = robust_api_call("Hello!")
    print(f"Result: {result}")
    
    # Example 7: OpenAI SDK
    print("\n🔌 Example 7: Using OpenAI SDK")
    print("-" * 70)
    example_with_openai_sdk()
    
    print("\n" + "=" * 70)
    print("Examples completed!")
    print("=" * 70)


if __name__ == "__main__":
    main()
