#!/usr/bin/env python3
"""
Test Local DeepSeek Model Integration
Verify that the local DeepSeek R1 model works with NearGravity RAG
"""
import os
import sys
import requests
import json

# Fix tokenizer warning
os.environ['TOKENIZERS_PARALLELISM'] = 'false'
os.environ['USE_LOCAL_MODEL'] = 'true'

# Add project paths
project_root = os.path.join(os.path.dirname(__file__), '../..')
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'src'))

from rag.model_config import get_model_name, print_model_info


class DeepSeekLocalTest:
    """Test local DeepSeek model integration"""
    
    def __init__(self):
        self.local_url = "http://127.0.0.1:1234"
        self.model_name = get_model_name()
    
    def test_server_connectivity(self):
        """Test if local DeepSeek server is accessible"""
        print("🔌 Testing local server connectivity...")
        try:
            response = requests.get(f"{self.local_url}/v1/models", timeout=5)
            if response.status_code == 200:
                models = response.json()
                print(f"✅ Server accessible, found {len(models.get('data', []))} models")
                return True
            else:
                print(f"⚠️ Server responded with status: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Server not accessible: {e}")
            return False
    
    def test_basic_completion(self):
        """Test basic text completion"""
        print("\n💬 Testing basic completion...")
        
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Say hello and explain what you are in one sentence."}
        ]
        
        try:
            response = requests.post(
                f"{self.local_url}/v1/chat/completions",
                headers={"Content-Type": "application/json"},
                json={
                    "model": self.model_name,
                    "messages": messages,
                    "max_tokens": 100,
                    "temperature": 0.7
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                
                # Handle DeepSeek R1 reasoning tokens
                if "<think>" in content:
                    if "</think>" in content:
                        content = content.split("</think>")[-1].strip()
                    else:
                        content = content.split("<think>")[0].strip()
                
                print(f"✅ Completion successful:")
                print(f"📝 Response: {content[:200]}...")
                return True
            else:
                print(f"❌ Completion failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Completion error: {e}")
            return False
    
    def test_rag_integration(self):
        """Test RAG processor with local model"""
        print("\n🧠 Testing RAG integration...")
        
        try:
            from backend.agentic.agent_model import AgentConfig
            from backend.agentic.agent_llm_wrapper import LLMWrapper
            
            # Test LLM wrapper with local model
            config = AgentConfig(agent_id='test', name='test_local', model=self.model_name)
            llm = LLMWrapper()
            
            messages = [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "What is 2+2? Answer briefly."}
            ]
            
            result = llm.generate(
                model=self.model_name,
                messages=messages,
                temperature=0.1,
                max_tokens=50
            )
            
            print(f"✅ RAG integration successful:")
            print(f"📝 LLM Response: {result}")
            return True
            
        except Exception as e:
            print(f"❌ RAG integration failed: {e}")
            return False
    
    def test_reasoning_cleanup(self):
        """Test that DeepSeek reasoning tokens are properly filtered"""
        print("\n🤔 Testing reasoning token cleanup...")
        
        messages = [
            {"role": "system", "content": "Think step by step about this problem."},
            {"role": "user", "content": "What's the capital of France?"}
        ]
        
        try:
            response = requests.post(
                f"{self.local_url}/v1/chat/completions",
                headers={"Content-Type": "application/json"},
                json={
                    "model": self.model_name,
                    "messages": messages,
                    "max_tokens": 200,
                    "temperature": 0.7
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                raw_content = result['choices'][0]['message']['content']
                
                # Check if reasoning tokens are present
                has_reasoning = "<think>" in raw_content
                
                # Clean up reasoning tokens (same logic as in LLM wrapper)
                if has_reasoning:
                    if "</think>" in raw_content:
                        clean_content = raw_content.split("</think>")[-1].strip()
                    else:
                        clean_content = raw_content.split("<think>")[0].strip()
                else:
                    clean_content = raw_content
                
                print(f"✅ Reasoning test completed:")
                print(f"🧠 Has reasoning tokens: {has_reasoning}")
                print(f"📝 Clean response: {clean_content[:100]}...")
                
                return True
            else:
                print(f"❌ Reasoning test failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Reasoning test error: {e}")
            return False
    
    def run_all_tests(self):
        """Run all DeepSeek local tests"""
        print("🤖 DEEPSEEK LOCAL MODEL TESTS")
        print("=" * 40)
        print_model_info()
        print()
        
        tests = [
            ("Server Connectivity", self.test_server_connectivity),
            ("Basic Completion", self.test_basic_completion),
            ("RAG Integration", self.test_rag_integration),
            ("Reasoning Cleanup", self.test_reasoning_cleanup)
        ]
        
        results = []
        for test_name, test_func in tests:
            try:
                result = test_func()
                results.append((test_name, result))
            except Exception as e:
                print(f"❌ {test_name} crashed: {e}")
                results.append((test_name, False))
        
        # Summary
        print("\n📊 TEST SUMMARY")
        print("-" * 30)
        passed = 0
        for test_name, result in results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{test_name}: {status}")
            if result:
                passed += 1
        
        print(f"\n🎯 Overall: {passed}/{len(results)} tests passed")
        
        if passed == len(results):
            print("🎉 All tests passed! DeepSeek local model is working correctly.")
        else:
            print("⚠️ Some tests failed. Check DeepSeek server and configuration.")
        
        return passed == len(results)


def main():
    """Run DeepSeek local model tests"""
    tester = DeepSeekLocalTest()
    success = tester.run_all_tests()
    return 0 if success else 1


if __name__ == "__main__":
    exit(main())