#!/usr/bin/env python3
"""
NearGravity AG-UI Demo Launcher
Automated demo scenarios for showcasing the semantic advertising protocol
"""
import os
import sys
import json
import time
import requests
import threading
from datetime import datetime

# Add parent directories to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

class NearGravityDemo:
    """Automated demo scenarios for NearGravity AG-UI"""
    
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.session_data = {
            "injections": [],
            "queries": [],
            "responses": []
        }
    
    def wait_for_server(self, timeout=30):
        """Wait for server to be ready"""
        print("🔍 Waiting for NearGravity AG-UI server...")
        
        for i in range(timeout):
            try:
                response = requests.get(self.base_url, timeout=2)
                if response.status_code == 200:
                    print("✅ Server is ready!")
                    return True
            except requests.exceptions.RequestException:
                pass
            
            print(f"   Waiting... ({i+1}/{timeout})", end='\r')
            time.sleep(1)
        
        print("❌ Server not responding!")
        return False
    
    def demo_scenario_coffee_shop(self):
        """Demo Scenario 1: Coffee Shop Morning Motivation"""
        print("\n" + "="*60)
        print("☕ DEMO SCENARIO 1: Coffee Shop Morning Motivation")
        print("="*60)
        
        # Add coffee shop injection
        injection_data = {
            "content": "Start your day right with Blue Bottle Coffee's single-origin Ethiopian beans. Hand-roasted daily for maximum freshness and energy!",
            "provider_id": "blue_bottle_coffee",
            "metadata": {
                "bid_amount": 0.003,
                "tags": ["coffee", "morning", "energy", "premium"],
                "category": "beverages",
                "location": "SF Bay Area"
            }
        }
        
        print("💉 Adding coffee shop campaign...")
        self.add_injection(injection_data)
        
        time.sleep(2)
        
        # User query
        query = "I need some morning motivation and energy to start my productive workday. Any tips for staying focused?"
        
        print(f"👤 User query: {query}")
        response = self.generate_content(query, "morning_professional")
        
        print("✅ Scenario complete!")
        return response
    
    def demo_scenario_tech_tools(self):
        """Demo Scenario 2: Developer Tools Discovery"""
        print("\n" + "="*60)
        print("💻 DEMO SCENARIO 2: Developer Tools Discovery")
        print("="*60)
        
        # Add tech tool injection
        injection_data = {
            "content": "JetBrains DataGrip offers advanced database management with intelligent query completion and schema navigation for developers.",
            "provider_id": "jetbrains",
            "metadata": {
                "bid_amount": 0.005,
                "tags": ["database", "developer", "tools", "productivity"],
                "category": "software",
                "target_audience": "developers"
            }
        }
        
        print("💉 Adding developer tools campaign...")
        self.add_injection(injection_data)
        
        time.sleep(2)
        
        # User query
        query = "How can I optimize slow database queries in my Python application? I'm struggling with performance issues."
        
        print(f"👤 User query: {query}")
        response = self.generate_content(query, "python_developer")
        
        print("✅ Scenario complete!")
        return response
    
    def demo_scenario_fitness(self):
        """Demo Scenario 3: Fitness Equipment"""
        print("\n" + "="*60)
        print("🏋️ DEMO SCENARIO 3: Home Fitness Equipment")
        print("="*60)
        
        # Add fitness injection
        injection_data = {
            "content": "Transform your home workouts with Peloton's connected fitness equipment. Live classes, expert instruction, community motivation.",
            "provider_id": "peloton_fitness",
            "metadata": {
                "bid_amount": 0.004,
                "tags": ["fitness", "home", "workout", "equipment"],
                "category": "health",
                "price_range": "premium"
            }
        }
        
        print("💉 Adding fitness equipment campaign...")
        self.add_injection(injection_data)
        
        time.sleep(2)
        
        # User query
        query = "I want to start exercising at home but I'm not motivated. What's the best way to build a consistent workout routine?"
        
        print(f"👤 User query: {query}")
        response = self.generate_content(query, "fitness_beginner")
        
        print("✅ Scenario complete!")
        return response
    
    def demo_scenario_negative_semantic_match(self):
        """Demo Scenario 4: Poor Semantic Match (Should Reject)"""
        print("\n" + "="*60)
        print("❌ DEMO SCENARIO 4: Poor Semantic Match (Rejection Test)")
        print("="*60)
        
        # Add unrelated injection
        injection_data = {
            "content": "Invest in cryptocurrency with our trading platform. High returns, minimal risk, get rich quick!",
            "provider_id": "crypto_trader",
            "metadata": {
                "bid_amount": 0.010,  # High bid but irrelevant
                "tags": ["crypto", "trading", "investment"],
                "category": "finance"
            }
        }
        
        print("💉 Adding crypto trading campaign...")
        self.add_injection(injection_data)
        
        time.sleep(2)
        
        # User query about health
        query = "I'm feeling anxious about my health and need some stress management techniques. What should I do?"
        
        print(f"👤 User query: {query}")
        print("🧠 This should demonstrate semantic integrity protection...")
        
        response = self.generate_content(query, "health_anxiety")
        
        print("✅ Semantic protection test complete!")
        return response
    
    def add_injection(self, injection_data):
        """Add injection to the system"""
        try:
            response = requests.post(
                f"{self.base_url}/api/inject",
                json=injection_data,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 201:
                result = response.json()
                self.session_data["injections"].append({
                    "id": result["injection_id"],
                    "provider": injection_data["provider_id"],
                    "content": injection_data["content"]
                })
                print(f"   ✅ Added: {injection_data['provider_id']}")
            else:
                print(f"   ❌ Failed: {response.json().get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    def generate_content(self, message, user_id):
        """Generate content using RAG"""
        try:
            request_data = {
                "message": message,
                "user_id": user_id,
                "modality": "text"
            }
            
            print("   🔄 Processing through RAG pipeline...")
            
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=request_data,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Store response
                self.session_data["responses"].append({
                    "user_id": user_id,
                    "query": message,
                    "response": result["content"],
                    "semantic_score": result["semantic_delta"]["composite_delta"],
                    "within_bounds": result["semantic_delta"]["is_within_bounds"]
                })
                
                print(f"   ✅ Generated content ({result['processing_time_ms']:.0f}ms)")
                print(f"   🧠 Semantic score: {result['semantic_delta']['composite_delta']:.3f}")
                print(f"   ✅ Within bounds: {result['semantic_delta']['is_within_bounds']}")
                print(f"   📝 Content preview: {result['content'][:100]}...")
                
                return result
            else:
                error = response.json().get('error', 'Unknown error')
                print(f"   ❌ Generation failed: {error}")
                return None
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return None
    
    def get_system_metrics(self):
        """Get system metrics"""
        try:
            response = requests.get(f"{self.base_url}/api/metrics", timeout=10)
            if response.status_code == 200:
                return response.json()
            return None
        except:
            return None
    
    def print_session_summary(self):
        """Print session summary"""
        print("\n" + "="*60)
        print("📊 DEMO SESSION SUMMARY")
        print("="*60)
        
        metrics = self.get_system_metrics()
        
        print(f"Campaigns Added: {len(self.session_data['injections'])}")
        print(f"User Queries: {len(self.session_data['responses'])}")
        
        if metrics:
            proc_metrics = metrics.get("processor_metrics", {})
            print(f"Total Requests: {proc_metrics.get('total_requests', 0)}")
            print(f"Avg Processing Time: {proc_metrics.get('avg_processing_time', 0):.1f}ms")
            print(f"Cache Hit Rate: {proc_metrics.get('cache_hits', 0)}/{proc_metrics.get('cache_hits', 0) + proc_metrics.get('cache_misses', 0)}")
        
        print("\n🎯 Semantic Integrity Results:")
        for i, resp in enumerate(self.session_data["responses"], 1):
            status = "✅ PASSED" if resp["within_bounds"] else "⚠️ FLAGGED"
            print(f"   {i}. Score: {resp['semantic_score']:.3f} - {status}")
        
        # Calculate success rate
        if self.session_data["responses"]:
            passed = sum(1 for r in self.session_data["responses"] if r["within_bounds"])
            rate = passed / len(self.session_data["responses"]) * 100
            print(f"\n🏆 Semantic Integrity Rate: {rate:.1f}%")
        
        print("\n🌟 NearGravity AG-UI Demo Complete!")
        print("   • Real-time event streaming: ✅")
        print("   • Dual-panel interface: ✅") 
        print("   • Semantic verification: ✅")
        print("   • Campaign management: ✅")

def main():
    """Run the demo"""
    print("🌟 NEARGRAVITY AG-UI DEMO LAUNCHER")
    print("World's First Semantic Advertising Protocol")
    print("Powered by AG-UI Protocol")
    print("="*60)
    
    demo = NearGravityDemo()
    
    # Check server
    if not demo.wait_for_server():
        print("\n💡 To start the server, run:")
        print("   python3 src/claude/ag_ui/server.py")
        print("\n🌐 Then open in browser:")
        print("   http://localhost:5000")
        return
    
    print(f"\n🚀 Starting automated demo scenarios...")
    print(f"🌐 Watch the real-time interface at: http://localhost:5000")
    time.sleep(2)
    
    # Run demo scenarios
    scenarios = [
        demo.demo_scenario_coffee_shop,
        demo.demo_scenario_tech_tools,
        demo.demo_scenario_fitness,
        demo.demo_scenario_negative_semantic_match
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n⏱️  Starting scenario {i}/4 in 3 seconds...")
        time.sleep(3)
        scenario()
        time.sleep(2)
    
    # Print summary
    demo.print_session_summary()
    
    print(f"\n🎉 Demo complete! Visit http://localhost:5000 to continue exploring.")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")