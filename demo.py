#!/usr/bin/env python3
"""
MARAG System Demo
This script demonstrates how to run the Multi-Agent Retrieval-Augmented Generation system.
"""

import os
import sys
from pathlib import Path

# Add the current directory to the Python path
sys.path.append(str(Path(__file__).parent))

def check_environment():
    """Check if required environment variables are set."""
    required_vars = ['OPENAI_API_KEY']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\n📝 Please create a .env file based on .env.example and set your API keys.")
        return False
    
    print("✅ Environment variables are set correctly.")
    return True

def test_basic_imports():
    """Test if basic dependencies are available."""
    try:
        import langchain
        import openai
        print("✅ Core dependencies are installed.")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please install missing dependencies with:")
        print("pip install langchain langchain-community langchain-openai langgraph openai python-dotenv pydantic")
        return False

def run_simple_test():
    """Run a simple test of the OpenAI connection."""
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        import openai
        client = openai.OpenAI()
        
        # Test with a simple completion
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hello! This is a test message."}],
            max_tokens=50
        )
        
        print("✅ OpenAI API connection successful!")
        print(f"Response: {response.choices[0].message.content}")
        return True
    except Exception as e:
        print(f"❌ OpenAI API test failed: {e}")
        return False

def main():
    """Main demo function."""
    print("🌐 MARAG System Demo")
    print("=" * 50)
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Check environment
    if not check_environment():
        return False
    
    # Test imports
    if not test_basic_imports():
        return False
    
    # Test OpenAI connection
    if not run_simple_test():
        return False
    
    print("\n🎉 All basic tests passed!")
    print("\n📚 Available components in this project:")
    print("   - final_adaptive_rag.py: Advanced RAG system")
    print("   - new_adaptive_rag.py: Alternative RAG implementation")
    print("   - modular_agent.py: Multi-agent framework")
    print("   - financial_markets.py: Financial analysis tools")
    print("   - response_transformation.py: Response processing")
    print("   - report_gen/report_gen.py: Report generation")
    
    print("\n🚀 To run specific components:")
    print("   python final_adaptive_rag.py")
    print("   python modular_agent.py")
    print("   python financial_markets.py")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)