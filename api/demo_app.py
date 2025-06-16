#!/usr/bin/env python3
import json
import time
import random
import hashlib
from typing import Dict, Any, List
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins=['http://localhost:3000', 'http://127.0.0.1:3000'])

class MockSearchService:
    
    def get_scenario_data(self, query: str) -> Dict[str, Any]:
        query_lower = query.lower()
        
        if "climate change" in query_lower or "renewable energy" in query_lower:
            return {
                "scenario": "high_trust",
                "results": [
                    {
                        "title": "IPCC Report: Global Warming Accelerating Beyond Previous Projections",
                        "snippet": "The latest Intergovernmental Panel on Climate Change assessment reveals that global temperatures are rising 15% faster than earlier models predicted. Arctic ice loss and sea level rise show clear acceleration patterns across multiple measurement systems.",
                        "url": "https://ipcc.ch/reports/ar6-synthesis-update-2024",
                        "source_type": "scientific"
                    },
                    {
                        "title": "NASA Satellite Data Confirms Record-Breaking Ocean Temperatures",
                        "snippet": "Advanced satellite measurements document unprecedented ocean warming in 2024. Marine heat waves now occur 20 times more frequently than in the 1980s, affecting global weather patterns and marine ecosystems worldwide.",
                        "url": "https://climate.nasa.gov/ocean-temperature-analysis-2024",
                        "source_type": "scientific"
                    },
                    {
                        "title": "Renewable Energy Infrastructure Outpaces Fossil Fuels Globally",
                        "snippet": "International Energy Agency data shows clean energy installations exceeded 500 GW in 2024, representing 85% of all new power generation capacity. Solar costs dropped another 12% while wind efficiency improved significantly.",
                        "url": "https://iea.org/reports/renewable-energy-outlook-2024",
                        "source_type": "institutional"
                    },
                    {
                        "title": "G20 Nations Announce Binding Carbon Reduction Commitments",
                        "snippet": "Major economies pledge legally binding emissions cuts of 45% by 2030. The agreement includes enforcement mechanisms and financial penalties for non-compliance, marking strongest climate action to date.",
                        "url": "https://unfccc.int/news/g20-climate-commitments-2024",
                        "source_type": "institutional"
                    },
                    {
                        "title": "Climate Investment Reaches Historic $2.8 Trillion Milestone",
                        "snippet": "Bloomberg Clean Energy Finance tracking shows venture capital, government funding, and corporate investments in climate solutions hit record levels. Electric vehicle sales doubled while battery storage costs plummeted 30%.",
                        "url": "https://bloomberg.com/professional/climate-finance-trends-2024",
                        "source_type": "financial"
                    }
                ]
            }
        
        elif "vaccine" in query_lower or "covid" in query_lower or "election" in query_lower:
            return {
                "scenario": "misinformation_detected",
                "results": [
                    {
                        "title": "CDC Analysis: COVID-19 Vaccines Maintain 89% Efficacy Against Severe Disease",
                        "snippet": "Comprehensive analysis of 47 million vaccinated individuals shows sustained protection against hospitalization and death. Updated bivalent formulations demonstrate improved effectiveness against Omicron variants, with breakthrough infections remaining mild in 94% of cases.",
                        "url": "https://cdc.gov/mmwr/volumes/73/wr/mm7315a1.htm",
                        "source_type": "health_authority"
                    },
                    {
                        "title": "World Health Organization Publishes Global Vaccine Safety Database Findings",
                        "snippet": "WHO analysis of 13.25 billion vaccine doses administered worldwide confirms excellent safety profile. Adverse event rates remain consistent with pre-pandemic vaccine standards, with serious events occurring in 0.003% of recipients across all age groups.",
                        "url": "https://who.int/news/item/15-03-2024-global-vaccine-safety-report",
                        "source_type": "health_authority"
                    },
                    {
                        "title": "Peer-Reviewed Meta-Analysis Validates Long-Term Vaccine Safety",
                        "snippet": "Nature Medicine publishes systematic review of 384 independent studies covering 180 million participants. No evidence found for increased cancer, autoimmune, or fertility risks. Myocarditis rates remain 8x lower than COVID infection risks.",
                        "url": "https://nature.com/articles/s41591-024-02857-3",
                        "source_type": "medical"
                    },
                    {
                        "title": "BREAKING: Secret Government Documents PROVE Vaccines Are Weapons!",
                        "snippet": "LEAKED FILES show vaccines contain GRAPHENE OXIDE and DNA-altering nanotechnology! Government whistleblower exposes the DEPOPULATION AGENDA behind mandatory injections. Share before THEY DELETE this truth!",
                        "url": "https://truthexpose247.net/vaccine-weapon-documents-leaked",
                        "source_type": "conspiracy"
                    },
                    {
                        "title": "Regional Medical Centers Report Continued COVID Protection Benefits",
                        "snippet": "Multi-hospital consortium data shows vaccinated patients experience 91% fewer ICU admissions. Emergency departments report minimal vaccine-related visits, with most cases resolved within 24 hours of observation.",
                        "url": "https://medicalnews.org/regional-covid-outcomes-2024",
                        "source_type": "local_news"
                    }
                ]
            }
        
        elif "artificial intelligence" in query_lower or "ai" in query_lower:
            return {
                "scenario": "mixed_signals",
                "results": [
                    {
                        "title": "Revolutionary AI System Achieves 99.7% Accuracy in Early Cancer Detection",
                        "snippet": "DeepMind's latest diagnostic AI identifies malignant tumors 18 months earlier than traditional screening methods. The system analyzed 2.8 million medical images and detected stage-1 cancers missed by radiologists in 23% of cases, potentially saving 100,000 lives annually.",
                        "url": "https://nature.com/articles/s41586-2024-07234-1",
                        "source_type": "scientific"
                    },
                    {
                        "title": "Silicon Valley Announces $127 Billion AI Safety Initiative",
                        "snippet": "Coalition of 47 tech companies commits unprecedented funding to prevent AI catastrophic risks. The initiative includes red team testing, constitutional AI development, and mandatory safety audits for frontier models exceeding 10^25 FLOPs.",
                        "url": "https://techcrunch.com/2024/03/15/ai-safety-mega-initiative",
                        "source_type": "tech_news"
                    },
                    {
                        "title": "Oxford Economics: 47% of Current Jobs Face Automation Risk by 2035",
                        "snippet": "Comprehensive labor market analysis predicts massive displacement across white-collar professions. Legal research, financial analysis, and content creation show highest vulnerability. However, 31 million new AI-adjacent jobs expected to emerge simultaneously.",
                        "url": "https://oxfordeconomics.com/resource/future-work-ai-automation-2024",
                        "source_type": "economic"
                    },
                    {
                        "title": "EU AI Act Enforcement Begins as US Maintains Voluntary Standards",
                        "snippet": "European Union's comprehensive AI regulation framework enters effect with €35M maximum fines for violations. Meanwhile, American tech leaders argue regulatory constraints could surrender AI leadership to China, creating global governance tensions.",
                        "url": "https://politico.eu/article/ai-act-implementation-us-china-competition",
                        "source_type": "policy"
                    },
                    {
                        "title": "Universities Report 340% Increase in AI-Assisted Academic Work",
                        "snippet": "Stanford research documents widespread adoption of AI writing and coding tools among students. While 89% report improved productivity, concerns mount over academic integrity and diminished critical thinking skills development.",
                        "url": "https://stanford.edu/news/2024/education-ai-integration-study",
                        "source_type": "education"
                    }
                ]
            }
        
        elif "inflation" in query_lower or "economy" in query_lower or "recession" in query_lower:
            return {
                "scenario": "economic_uncertainty",
                "results": [
                    {
                        "title": "Federal Reserve Maintains 5.25% Interest Rate Amid Economic Uncertainty",
                        "snippet": "Chair Powell emphasizes data-dependent approach as core inflation persists at 3.8%. Fed officials express measured optimism about disinflation progress while acknowledging labor market tightness and geopolitical risks affecting monetary policy decisions.",
                        "url": "https://federalreserve.gov/newsevents/pressreleases/monetary20240320a.htm",
                        "source_type": "central_bank"
                    },
                    {
                        "title": "Consumer Price Index Declines to 3.1% as Housing Costs Moderate",
                        "snippet": "Bureau of Labor Statistics reports continued disinflation driven by declining shelter costs and stable energy prices. Core goods deflation persists while services inflation remains elevated at 4.8%, creating mixed signals for policymakers.",
                        "url": "https://bls.gov/news.release/cpi.nr0.htm",
                        "source_type": "government"
                    },
                    {
                        "title": "Employment Report: 180,000 Jobs Added Despite Manufacturing Contraction",
                        "snippet": "Labor Department data shows continued job growth concentrated in services sectors. Manufacturing employment declined for third consecutive month while professional services and healthcare drove overall gains. Wage growth slowed to 3.9% annually.",
                        "url": "https://bls.gov/news.release/empsit.nr0.htm",
                        "source_type": "government"
                    },
                    {
                        "title": "URGENT: Secret Banking Crisis Signals TOTAL ECONOMIC MELTDOWN!",
                        "snippet": "INSIDERS reveal commercial real estate collapse will trigger MASSIVE bank failures! Government hiding $8 TRILLION in losses! Stock market manipulation exposed - crash coming within 60 days! Download survival guide before it's BANNED!",
                        "url": "https://economiccollapsenews.net/secret-banking-crisis-exposed",
                        "source_type": "alarmist"
                    },
                    {
                        "title": "Q1 Corporate Earnings Exceed Forecasts as Margins Stabilize",
                        "snippet": "FactSet analysis reveals 78% of S&P 500 companies beat earnings estimates despite revenue headwinds. Technology and healthcare sectors outperformed while energy and real estate faced pressure. Forward guidance suggests cautious optimism for remainder of year.",
                        "url": "https://wsj.com/articles/q1-earnings-analysis-corporate-america-2024",
                        "source_type": "financial"
                    }
                ]
            }
        
        else:
            return {
                "scenario": "balanced",
                "results": [
                    {
                        "title": f"Breaking: {query} - Latest Updates",
                        "snippet": f"Recent developments regarding {query}. This comprehensive report covers all the latest information and analysis from reliable sources.",
                        "url": f"https://news-source-1.com/breaking-{query.replace(' ', '-')}",
                        "source_type": "news"
                    },
                    {
                        "title": f"{query} Analysis and Expert Commentary", 
                        "snippet": f"In-depth analysis of {query} by leading experts. This detailed examination provides context and implications for stakeholders.",
                        "url": f"https://analysis-site.com/expert-view-{query.replace(' ', '-')}",
                        "source_type": "expert"
                    },
                    {
                        "title": f"Complete Guide to {query}",
                        "snippet": f"A comprehensive guide covering everything you need to know about {query}. Includes background, current status, and future outlook.",
                        "url": f"https://guide-portal.com/complete-guide-{query.replace(' ', '-')}",
                        "source_type": "guide"
                    },
                    {
                        "title": f"{query}: What You Need to Know",
                        "snippet": f"Essential information about {query} including key facts, timeline, and impact assessment from authoritative sources.",
                        "url": f"https://info-hub.com/essential-info-{query.replace(' ', '-')}",
                        "source_type": "informational"
                    },
                    {
                        "title": f"Controversial Perspectives on {query}",
                        "snippet": f"Alternative viewpoints and controversial opinions regarding {query}. This piece presents contrarian analysis that may differ from mainstream coverage.",
                        "url": f"https://alternative-views.com/contrarian-{query.replace(' ', '-')}",
                        "source_type": "opinion"
                    }
                ]
            }
    
    def search(self, query: str, count: int = 5, prefer_mock: bool = True) -> List[Dict[str, Any]]:
        scenario_data = self.get_scenario_data(query)
        results = []
        
        for i, mock_result in enumerate(scenario_data["results"][:count]):
            result_id = chr(65 + i)
            results.append({
                "id": result_id,
                "title": mock_result["title"],
                "snippet": mock_result["snippet"],
                "url": mock_result["url"],
                "rank": i + 1,
                "provider_used": "mock",
                "source_type": mock_result["source_type"],
                "scenario": scenario_data["scenario"]
            })
            
        return results

class MockSemanticService:
    
    def analyze_search_results(self, query: str, search_results: List[Dict], 
                             semantic_threshold: float = 0.75, user_id: str = "demo") -> Dict[str, Any]:
        start_time = time.time()
        time.sleep(2)
        
        scenario = search_results[0].get("scenario", "balanced") if search_results else "balanced"
        embeddings = []
        for result in search_results:
            content = f"{result['title']} {result['snippet']}"
            semantic_hash = hashlib.md5(content.encode()).hexdigest()
            
            embeddings.append({
                "result_id": result["id"],
                "semantic_hash": semantic_hash,
                "embedding_vector": [random.random() for _ in range(8)]
            })
        distance_matrix = {}
        result_ids = [r["id"] for r in search_results]
        
        if scenario == "high_trust":
            for i, id1 in enumerate(result_ids):
                for j, id2 in enumerate(result_ids):
                    if i != j:
                        result1 = search_results[i]
                        result2 = search_results[j]
                        
                        base_distance = 0.15 + random.random() * 0.3
                        
                        if result1.get("source_type") == result2.get("source_type"):
                            base_distance *= 0.8
                        
                        if abs(i - j) == 1:
                            base_distance *= 0.9
                        
                        distance_matrix[f"{id1}->{id2}"] = {
                            "distance": base_distance,
                            "similarity_score": 1.0 - base_distance
                        }
        
        elif scenario == "misinformation_detected":
            for i, id1 in enumerate(result_ids):
                for j, id2 in enumerate(result_ids):
                    if i != j:
                        result1 = search_results[i]
                        result2 = search_results[j]
                        
                        if (result1.get("source_type") == "conspiracy" or 
                            result2.get("source_type") == "conspiracy"):
                            base_distance = 0.85 + random.random() * 0.25
                        else:
                            base_distance = 0.25 + random.random() * 0.25
                            
                            if (result1.get("source_type") == result2.get("source_type") and 
                                result1.get("source_type") in ["health_authority", "medical"]):
                                base_distance *= 0.7
                        
                        distance_matrix[f"{id1}->{id2}"] = {
                            "distance": base_distance,
                            "similarity_score": 1.0 - base_distance
                        }
        
        elif scenario == "mixed_signals":
            for i, id1 in enumerate(result_ids):
                for j, id2 in enumerate(result_ids):
                    if i != j:
                        result1 = search_results[i]
                        result2 = search_results[j]
                        
                        base_distance = 0.45 + random.random() * 0.35
                        
                        source1, source2 = result1.get("source_type"), result2.get("source_type")
                        if (source1 == "economic" and source2 == "scientific") or \
                           (source1 == "scientific" and source2 == "economic"):
                            base_distance = 0.65 + random.random() * 0.2
                        elif (source1 == "policy" and source2 != "policy") or \
                             (source2 == "policy" and source1 != "policy"):
                            base_distance = 0.55 + random.random() * 0.25
                        elif source1 == source2:
                            base_distance *= 0.8
                        
                        distance_matrix[f"{id1}->{id2}"] = {
                            "distance": base_distance,
                            "similarity_score": 1.0 - base_distance
                        }
        
        elif scenario == "economic_uncertainty":
            for i, id1 in enumerate(result_ids):
                for j, id2 in enumerate(result_ids):
                    if i != j:
                        result1 = search_results[i]
                        result2 = search_results[j]
                        
                        if (result1.get("source_type") == "alarmist" or 
                            result2.get("source_type") == "alarmist"):
                            base_distance = 0.78 + random.random() * 0.22
                        else:
                            base_distance = 0.35 + random.random() * 0.3
                            
                            if ({result1.get("source_type"), result2.get("source_type")} == 
                                {"government", "central_bank"}):
                                base_distance *= 0.75
                            elif result1.get("source_type") == result2.get("source_type"):
                                base_distance *= 0.8
                        
                        distance_matrix[f"{id1}->{id2}"] = {
                            "distance": base_distance,
                            "similarity_score": 1.0 - base_distance
                        }
        
        else:
            for i, id1 in enumerate(result_ids):
                for j, id2 in enumerate(result_ids):
                    if i != j:
                        base_distance = 0.4 + random.random() * 0.35
                        if abs(i - j) == 1:
                            base_distance *= 0.9
                        if abs(i - j) >= 3:
                            base_distance *= 1.1
                        
                        distance_matrix[f"{id1}->{id2}"] = {
                            "distance": base_distance,
                            "similarity_score": 1.0 - base_distance
                        }
        
        avg_distances = {}
        for result_id in result_ids:
            distances = [
                distance_matrix[f"{result_id}->{other_id}"]["distance"]
                for other_id in result_ids if other_id != result_id
            ]
            avg_distances[result_id] = sum(distances) / len(distances)
        
        center_of_gravity = min(avg_distances, key=avg_distances.get)
        outliers = []
        for i, result_id in enumerate(result_ids):
            result = search_results[i]
            outlier_distances = []
            max_distance = 0
            
            for other_id in result_ids:
                if other_id != result_id:
                    distance = distance_matrix[f"{result_id}->{other_id}"]["distance"]
                    max_distance = max(max_distance, distance)
                    
                    if distance > semantic_threshold:
                        outlier_distances.append({
                            "to_result": other_id,
                            "distance": distance,
                            "threshold_exceeded_by": distance - semantic_threshold
                        })
            
            if outlier_distances:
                max_exceeded = max(d["threshold_exceeded_by"] for d in outlier_distances)
                source_type = result.get("source_type", "unknown")
                
                if source_type == "conspiracy":
                    severity = "high"
                    reason = "Potential misinformation detected - source promotes conspiracy theories"
                elif source_type == "alarmist":
                    severity = "medium"
                    reason = "Alarmist content detected - may contain sensationalized claims"
                elif max_exceeded > 0.3:
                    severity = "high"
                    reason = f"Significant semantic deviation from consensus (>{semantic_threshold + 0.3:.1f})"
                elif max_exceeded > 0.15:
                    severity = "medium"
                    reason = f"Moderate semantic deviation from consensus (>{semantic_threshold + 0.15:.1f})"
                else:
                    severity = "low"
                    reason = f"Minor semantic deviation from consensus (>{semantic_threshold:.1f})"
                
                outliers.append({
                    "result_id": result_id,
                    "reason": reason,
                    "severity": severity,
                    "threshold": semantic_threshold,
                    "max_distance": max_distance,
                    "outlier_distances": outlier_distances,
                    "source_type": source_type
                })
        
        processing_time_ms = int((time.time() - start_time) * 1000)
        
        return {
            "center_of_gravity": center_of_gravity,
            "outliers": outliers,
            "distance_matrix": distance_matrix,
            "embeddings": embeddings,
            "threshold_used": semantic_threshold,
            "processing_time_ms": processing_time_ms,
            "scenario": scenario
        }

class MockNEARService:
    """Mock NEAR contracts service"""
    
    def health_check(self) -> bool:
        return True
    
    def submit_semantic_analysis(self, prefix: str, identifier: str, analysis_data: Dict) -> Dict:
        storage_key = f"{prefix}_{identifier}_{int(time.time())}"
        return {"storage_key": storage_key, "status": "stored"}

# Initialize mock services
search_service = MockSearchService()
semantic_service = MockSemanticService()
near_service = MockNEARService()

@app.route('/near/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "service": "semantic_guard_demo",
        "status": "healthy",
        "timestamp": int(time.time()),
        "components": {
            "search_service": True,
            "semantic_service": True,
            "near_service": True
        }
    })

@app.route('/near/semantic-guard', methods=['POST'])
def analyze_semantic_guard():
    """Main semantic guard analysis endpoint"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        query = data.get('query')
        if not query:
            return jsonify({"error": "Query parameter required"}), 400
        
        max_results = data.get('max_results', 5)
        semantic_threshold = data.get('semantic_threshold', 0.75)
        
        if not isinstance(max_results, int) or max_results < 1 or max_results > 10:
            return jsonify({"error": "max_results must be between 1 and 10"}), 400
        
        if not isinstance(semantic_threshold, (int, float)) or semantic_threshold < 0 or semantic_threshold > 2:
            return jsonify({"error": "semantic_threshold must be between 0 and 2"}), 400
        
        search_results = search_service.search(query, max_results)
        
        analysis_result = semantic_service.analyze_search_results(
            query=query,
            search_results=search_results,
            semantic_threshold=semantic_threshold
        )
        
        processed_results = []
        for result in search_results:
            embedding = next(
                (e for e in analysis_result["embeddings"] if e["result_id"] == result["id"]),
                None
            )
            
            is_outlier = any(o["result_id"] == result["id"] for o in analysis_result["outliers"])
            
            center_distance_key = f"{analysis_result['center_of_gravity']}->{result['id']}"
            gravity_score = 0.0
            if center_distance_key in analysis_result["distance_matrix"]:
                gravity_score = analysis_result["distance_matrix"][center_distance_key]["distance"]
            
            processed_results.append({
                "id": result["id"],
                "title": result["title"],
                "snippet": result["snippet"], 
                "url": result["url"],
                "rank": result["rank"],
                "is_center_of_gravity": result["id"] == analysis_result["center_of_gravity"],
                "is_outlier": is_outlier,
                "gravity_score": gravity_score,
                "semantic_hash": embedding["semantic_hash"] if embedding else None,
                "source_type": result.get("source_type", "unknown"),
                "scenario": result.get("scenario", "balanced")
            })
        
        distance_matrix_simple = {}
        for key, distance_obj in analysis_result["distance_matrix"].items():
            distance_matrix_simple[key] = distance_obj["distance"]
        
        semantic_analysis = {
            "center_of_gravity": {
                "result_id": analysis_result["center_of_gravity"],
                "gravity_score": 0.0,
                "reason": "Result with minimum average semantic distance"
            },
            "outliers": analysis_result["outliers"],
            "distance_matrix": distance_matrix_simple,
            "threshold_used": analysis_result["threshold_used"],
            "total_comparisons": len(analysis_result["distance_matrix"]) // 2,
            "processing_time_ms": analysis_result["processing_time_ms"],
            "embeddings_generated": len(analysis_result["embeddings"])
        }
        
        analysis_id = None
        if near_service.health_check():
            try:
                storage_result = near_service.submit_semantic_analysis(
                    prefix="semantic_guard_demo",
                    identifier=f"query_{int(time.time())}",
                    analysis_data={
                        "query": query,
                        "results": processed_results,
                        "semantic_analysis": semantic_analysis
                    }
                )
                analysis_id = storage_result.get("storage_key")
            except Exception as e:
                print(f"Error storing on NEAR: {e}")
        
        response = {
            "query": query,
            "results": processed_results,
            "semantic_analysis": semantic_analysis,
            "metadata": {
                "analysis_id": analysis_id,
                "near_storage": analysis_id is not None,
                "service_status": "demo_mode",
                "search_provider": "mock",
                "timestamp": int(time.time())
            }
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        print(f"Error in semantic guard analysis: {e}")
        return jsonify({
            "error": "Internal server error",
            "message": str(e)
        }), 500

if __name__ == '__main__':
    print("Starting NEAR Semantic Guard Demo Server...")
    print("UI available at: http://localhost:3000/semantic-guard")
    print("API health check: http://localhost:5000/near/health")
    app.run(host='127.0.0.1', port=5000, debug=True)