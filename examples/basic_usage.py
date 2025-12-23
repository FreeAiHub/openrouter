#!/usr/bin/env python3
"""
Basic Usage Examples for OpenRouter API Client

This demonstrates fundamental patterns for using the OpenRouter client.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.openrouter import OpenRouterClient, Message
from config.settings import get_settings


def example_1_simple_query():
    """Example 1: Simple question-answer."""
    print("\n" + "="*70)
    print("Example 1: Simple Query")
    print("="*70)
    
    with OpenRouterClient() as client:
        messages = [
            Message(role="user", content="What is the capital of France?")
        ]
        
        response = client.chat_completion(messages)
        print(f"Question: {messages[0].content}")
        print(f"Answer: {response.choices[0].message.content}")
        
        if response.usage:
            print(f"\nTokens used: {response.usage.total_tokens}")


def example_2_conversation():
    """Example 2: Multi-turn conversation."""
    print("\n" + "="*70)
    print("Example 2: Multi-turn Conversation")
    print("="*70)
    
    with OpenRouterClient() as client:
        messages = []
        
        # Turn 1
        messages.append(Message(role="user", content="What is Python?"))
        response = client.chat_completion(messages)
        assistant_msg = response.choices[0].message.content
        messages.append(Message(role="assistant", content=assistant_msg))
        print(f"\nUser: What is Python?")
        print(f"Assistant: {assistant_msg}\n")
        
        # Turn 2
        messages.append(Message(
            role="user",
            content="What are its main applications?"
        ))
        response = client.chat_completion(messages)
        assistant_msg = response.choices[0].message.content
        print(f"User: What are its main applications?")
        print(f"Assistant: {assistant_msg}")


def example_3_streaming():
    """Example 3: Streaming responses."""
    print("\n" + "="*70)
    print("Example 3: Streaming Response")
    print("="*70)
    
    with OpenRouterClient() as client:
        messages = [
            Message(
                role="user",
                content="Write a short poem about programming"
            )
        ]
        
        print("\nStreaming response:\n")
        for chunk in client.stream_chat_completion(messages):
            print(chunk, end="", flush=True)
        print("\n")


def example_4_with_system_prompt():
    """Example 4: Using system prompt."""
    print("\n" + "="*70)
    print("Example 4: System Prompt")
    print("="*70)
    
    with OpenRouterClient() as client:
        messages = [
            Message(
                role="system",
                content="You are a helpful assistant that explains concepts simply."
            ),
            Message(
                role="user",
                content="Explain quantum computing"
            )
        ]
        
        response = client.chat_completion(messages, max_tokens=200)
        print(f"Response: {response.choices[0].message.content}")


def example_5_different_models():
    """Example 5: Testing different models."""
    print("\n" + "="*70)
    print("Example 5: Model Comparison")
    print("="*70)
    
    models = [
        "xiaomi/mimo-v2-flash:free",
        "kwaipilot/kat-coder-pro-v1:free",
    ]
    
    question = Message(role="user", content="What is machine learning?")
    
    with OpenRouterClient() as client:
        for model in models:
            try:
                print(f"\n--- Testing {model} ---")
                response = client.chat_completion([question], model=model)
                answer = response.choices[0].message.content
                print(f"Answer: {answer[:150]}...")
                
                if response.usage:
                    print(f"Tokens: {response.usage.total_tokens}")
            except Exception as e:
                print(f"Error: {e}")


def example_6_cost_tracking():
    """Example 6: Cost tracking."""
    print("\n" + "="*70)
    print("Example 6: Cost Tracking")
    print("="*70)
    
    with OpenRouterClient() as client:
        # Make several requests
        questions = [
            "What is AI?",
            "What is machine learning?",
            "What is deep learning?"
        ]
        
        for q in questions:
            messages = [Message(role="user", content=q)]
            response = client.chat_completion(messages)
            print(f"Q: {q}")
            print(f"A: {response.choices[0].message.content[:80]}...")
            print()
        
        # Get metrics summary
        summary = client.get_metrics_summary()
        print("\n--- Metrics Summary ---")
        for key, value in summary.items():
            print(f"{key}: {value}")


def example_7_error_handling():
    """Example 7: Error handling."""
    print("\n" + "="*70)
    print("Example 7: Error Handling")
    print("="*70)
    
    from src.openrouter.exceptions import (
        InvalidRequestError,
        ModelNotFoundError,
        AuthenticationError
    )
    
    with OpenRouterClient() as client:
        # Test with invalid model
        try:
            messages = [Message(role="user", content="Hello")]
            client.chat_completion(messages, model="invalid/model:free")
        except ModelNotFoundError as e:
            print(f"✓ Caught ModelNotFoundError: {e.message}")
        except InvalidRequestError as e:
            print(f"✓ Caught InvalidRequestError: {e.message}")
        
        # Test with empty messages
        try:
            client.chat_completion([])
        except Exception as e:
            print(f"✓ Caught validation error: {e}")


def main():
    """Run all examples."""
    settings = get_settings()
    
    print("="*70)
    print("OpenRouter API - Basic Usage Examples")
    print("="*70)
    print(f"Environment: {settings.environment}")
    print(f"Default Model: {settings.default_model}")
    print("="*70)
    
    try:
        example_1_simple_query()
        example_2_conversation()
        example_3_streaming()
        example_4_with_system_prompt()
        example_5_different_models()
        example_6_cost_tracking()
        example_7_error_handling()
        
        print("\n" + "="*70)
        print("All examples completed successfully!")
        print("="*70)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
