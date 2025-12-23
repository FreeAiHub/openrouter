#!/usr/bin/env python3
"""
OpenRouter API Test Suite
Tests free and cheap models for cost-effective development
"""

import os
import json
import requests
from typing import Optional, Dict, Any

# Configuration
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
API_BASE_URL = "https://openrouter.ai/api/v1"

# Free models to test
FREE_MODELS = [
    "xiaomi/mimo-v2-flash:free",
    "mistralai/devstral-2-2512:free",
    "kwaipilot/kat-coder-pro-v1:free",
    "z-ai/glm-4.5-air:free",
    "nvidia/nemotron-3-nano-30b:free",
]

# Cheap models (under $0.001 per 1M tokens)
CHEAP_MODELS = [
    "deepseek/deepseek-chat",
    "qwen/qwen-2.5-7b-instruct",
    "meta-llama/llama-3.2-3b-instruct",
]


def test_model(model_id: str, prompt: str = "What is the capital of France?") -> Dict[str, Any]:
    """
    Test a single model with OpenRouter API
    
    Args:
        model_id: Model identifier
        prompt: Test prompt
        
    Returns:
        Dictionary with test results
    """
    
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/test",
        "X-Title": "OpenRouter API Test",
    }
    
    payload = {
        "model": model_id,
        "messages": [
            {
                "role": "user",
                "content": prompt,
            }
        ],
        "max_tokens": 100,
        "temperature": 0.7,
    }
    
    result = {
        "model": model_id,
        "status": "unknown",
        "response": None,
        "error": None,
        "usage": None,
    }
    
    try:
        print(f"\n🔄 Testing: {model_id}")
        response = requests.post(
            f"{API_BASE_URL}/chat/completions",
            headers=headers,
            json=payload,
            timeout=30,
        )
        
        if response.status_code == 200:
            data = response.json()
            result["status"] = "success"
            result["response"] = data["choices"][0]["message"]["content"]
            result["usage"] = data.get("usage", {})
            print(f"✅ Success: {result['response'][:100]}...")
        else:
            result["status"] = "error"
            result["error"] = f"HTTP {response.status_code}: {response.text}"
            print(f"❌ Error: {result['error']}")
            
    except Exception as e:
        result["status"] = "exception"
        result["error"] = str(e)
        print(f"❌ Exception: {result['error']}")
    
    return result


def test_streaming(model_id: str, prompt: str = "Count from 1 to 5") -> Dict[str, Any]:
    """
    Test streaming capability with a model
    
    Args:
        model_id: Model identifier
        prompt: Test prompt
        
    Returns:
        Dictionary with streaming test results
    """
    
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    
    payload = {
        "model": model_id,
        "messages": [
            {
                "role": "user",
                "content": prompt,
            }
        ],
        "stream": True,
        "max_tokens": 50,
    }
    
    result = {
        "model": model_id,
        "status": "unknown",
        "chunks": [],
        "error": None,
    }
    
    try:
        print(f"\n🌊 Testing streaming: {model_id}")
        response = requests.post(
            f"{API_BASE_URL}/chat/completions",
            headers=headers,
            json=payload,
            stream=True,
            timeout=30,
        )
        
        if response.status_code == 200:
            result["status"] = "success"
            chunk_count = 0
            
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
                                    result["chunks"].append(content)
                                    chunk_count += 1
                            except json.JSONDecodeError:
                                pass
            
            print(f"✅ Streaming success: {chunk_count} chunks received")
            print(f"   Content: {''.join(result['chunks'])[:100]}...")
        else:
            result["status"] = "error"
            result["error"] = f"HTTP {response.status_code}"
            print(f"❌ Error: {result['error']}")
            
    except Exception as e:
        result["status"] = "exception"
        result["error"] = str(e)
        print(f"❌ Exception: {result['error']}")
    
    return result


def get_models_list() -> Dict[str, Any]:
    """
    Fetch available models from OpenRouter
    
    Returns:
        Dictionary with models information
    """
    
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    }
    
    try:
        print("\n📋 Fetching models list...")
        response = requests.get(
            f"{API_BASE_URL}/models",
            headers=headers,
            timeout=10,
        )
        
        if response.status_code == 200:
            data = response.json()
            free_models = [m for m in data["data"] if m.get("pricing", {}).get("prompt") == 0]
            print(f"✅ Found {len(free_models)} free models")
            return {
                "status": "success",
                "total_models": len(data["data"]),
                "free_models_count": len(free_models),
                "models": data["data"][:10],  # First 10 for preview
            }
        else:
            print(f"❌ Error: HTTP {response.status_code}")
            return {"status": "error", "error": f"HTTP {response.status_code}"}
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return {"status": "exception", "error": str(e)}


def main():
    """Run all tests"""
    
    if not OPENROUTER_API_KEY:
        print("❌ Error: OPENROUTER_API_KEY environment variable not set")
        return
    
    print("=" * 60)
    print("OpenRouter API Test Suite")
    print("=" * 60)
    
    # Test 1: Get models list
    models_result = get_models_list()
    
    # Test 2: Test free models
    print("\n" + "=" * 60)
    print("Testing Free Models")
    print("=" * 60)
    
    free_results = []
    for model in FREE_MODELS[:3]:  # Test first 3 to avoid rate limits
        result = test_model(model)
        free_results.append(result)
    
    # Test 3: Test streaming
    print("\n" + "=" * 60)
    print("Testing Streaming Capability")
    print("=" * 60)
    
    if free_results and free_results[0]["status"] == "success":
        streaming_result = test_streaming(FREE_MODELS[0])
    
    # Test 4: Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    successful = sum(1 for r in free_results if r["status"] == "success")
    print(f"\n✅ Successful tests: {successful}/{len(free_results)}")
    
    print("\n📊 Results:")
    for result in free_results:
        status_icon = "✅" if result["status"] == "success" else "❌"
        print(f"{status_icon} {result['model']}: {result['status']}")
        if result["usage"]:
            print(f"   Tokens - Input: {result['usage'].get('prompt_tokens', 0)}, "
                  f"Output: {result['usage'].get('completion_tokens', 0)}")
    
    print("\n" + "=" * 60)
    print("Test completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
