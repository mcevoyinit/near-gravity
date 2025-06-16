#!/usr/bin/env python3
"""
Search Service for NearGravity NEAR Integration
Provides web search functionality with Brave Search API and DuckDuckGo fallback
"""
import requests
import json
import time
import os
from typing import Dict, Any, List, Optional
from urllib.parse import quote_plus
import hashlib

import sys
from pathlib import Path

# Add src to path for imports
src_path = str(Path(__file__).parent.parent.parent)
if src_path not in sys.path:
    sys.path.insert(0, src_path)


class SearchResult:
    """Standardized search result format"""
    
    def __init__(
        self,
        result_id: str,
        title: str,
        snippet: str,
        url: str,
        rank: int,
        provider: str = "unknown"
    ):
        self.id = result_id
        self.title = title
        self.snippet = snippet
        self.url = url
        self.rank = rank
        self.provider = provider
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "snippet": self.snippet,
            "url": self.url,
            "rank": self.rank,
            "provider": self.provider
        }


class BraveSearchService:
    """Brave Search API client"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('BRAVE_SEARCH_API_KEY')
        self.base_url = "https://api.search.brave.com/res/v1/web/search"
        self.timeout = 10
        
    def search(self, query: str, count: int = 5) -> List[SearchResult]:
        """
        Search using Brave Search API.
        
        Args:
            query: Search query
            count: Number of results to return
            
        Returns:
            list: List of SearchResult objects
        """
        if not self.api_key:
            raise ValueError("Brave Search API key not configured")
        
        headers = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
            "X-Subscription-Token": self.api_key
        }
        
        params = {
            "q": query,
            "count": min(count, 20),  # Brave Search limit
            "offset": 0,
            "mkt": "en-US",
            "safesearch": "moderate",
            "freshness": "pw",  # Past week for recent results
            "text_decorations": False,
            "spellcheck": True
        }
        
        try:
            response = requests.get(
                self.base_url,
                headers=headers,
                params=params,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            data = response.json()
            results = []
            
            # Parse web results
            web_results = data.get("web", {}).get("results", [])
            
            for i, result in enumerate(web_results[:count]):
                # Generate consistent ID based on URL
                result_id = hashlib.md5(result.get("url", "").encode()).hexdigest()[:8]
                
                search_result = SearchResult(
                    result_id=result_id,
                    title=result.get("title", ""),
                    snippet=result.get("description", ""),
                    url=result.get("url", ""),
                    rank=i + 1,
                    provider="brave_search"
                )
                results.append(search_result)
            
            return results
            
        except requests.RequestException as e:
            raise Exception(f"Brave Search API error: {e}")
        except json.JSONDecodeError as e:
            raise Exception(f"Brave Search response parsing error: {e}")
    
    def is_available(self) -> bool:
        """Check if Brave Search service is available"""
        return bool(self.api_key)


class DuckDuckGoSearchService:
    """DuckDuckGo search service (fallback)"""
    
    def __init__(self):
        self.base_url = "https://api.duckduckgo.com/"
        self.timeout = 10
    
    def search(self, query: str, count: int = 5) -> List[SearchResult]:
        """
        Search using DuckDuckGo Instant Answer API.
        Note: DuckDuckGo's free API is limited, so this is a simplified implementation.
        
        Args:
            query: Search query
            count: Number of results to return (limited by API)
            
        Returns:
            list: List of SearchResult objects
        """
        params = {
            "q": query,
            "format": "json",
            "t": "NearGravity_near",  # App identifier
            "no_redirect": "1",
            "no_html": "1",
            "skip_disambig": "1"
        }
        
        try:
            response = requests.get(
                self.base_url,
                params=params,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            data = response.json()
            results = []
            
            # DuckDuckGo API returns different result types
            # Try to extract useful results from RelatedTopics
            related_topics = data.get("RelatedTopics", [])
            
            for i, topic in enumerate(related_topics[:count]):
                if isinstance(topic, dict) and "Text" in topic and "FirstURL" in topic:
                    # Generate consistent ID
                    result_id = hashlib.md5(topic.get("FirstURL", "").encode()).hexdigest()[:8]
                    
                    search_result = SearchResult(
                        result_id=result_id,
                        title=f"DuckDuckGo Result {i+1}",
                        snippet=topic.get("Text", ""),
                        url=topic.get("FirstURL", ""),
                        rank=i + 1,
                        provider="duckduckgo"
                    )
                    results.append(search_result)
            
            # If no related topics, try to use Abstract
            if not results and data.get("Abstract"):
                result_id = hashlib.md5(query.encode()).hexdigest()[:8]
                search_result = SearchResult(
                    result_id=result_id,
                    title=data.get("Heading", "DuckDuckGo Abstract"),
                    snippet=data.get("Abstract", ""),
                    url=data.get("AbstractURL", ""),
                    rank=1,
                    provider="duckduckgo"
                )
                results.append(search_result)
            
            return results
            
        except requests.RequestException as e:
            raise Exception(f"DuckDuckGo API error: {e}")
        except json.JSONDecodeError as e:
            raise Exception(f"DuckDuckGo response parsing error: {e}")
    
    def is_available(self) -> bool:
        """Check if DuckDuckGo service is available"""
        return True  # DuckDuckGo doesn't require API key


class MockSearchService:
    """Mock search service for development and testing"""
    
    def search(self, query: str, count: int = 5) -> List[SearchResult]:
        """
        Generate mock search results for development.
        
        Args:
            query: Search query
            count: Number of results to return
            
        Returns:
            list: List of mock SearchResult objects
        """
        # Generate varied mock results based on query
        mock_data = [
            {
                "title_template": "Breaking: {query} - Latest Updates",
                "snippet_template": "Recent developments regarding {query}. This comprehensive report covers all the latest information and analysis from reliable sources.",
                "url_template": "https://news-source-1.com/breaking-{query_slug}"
            },
            {
                "title_template": "{query} Analysis and Expert Commentary",
                "snippet_template": "In-depth analysis of {query} by leading experts. This detailed examination provides context and implications for stakeholders.",
                "url_template": "https://analysis-site.com/expert-view-{query_slug}"
            },
            {
                "title_template": "Complete Guide to {query}",
                "snippet_template": "A comprehensive guide covering everything you need to know about {query}. Includes background, current status, and future outlook.",
                "url_template": "https://guide-portal.com/complete-guide-{query_slug}"
            },
            {
                "title_template": "{query}: What You Need to Know",
                "snippet_template": "Essential information about {query} including key facts, timeline, and impact assessment from authoritative sources.",
                "url_template": "https://info-hub.com/essential-info-{query_slug}"
            },
            {
                "title_template": "Controversial Perspectives on {query}",
                "snippet_template": "Alternative viewpoints and controversial opinions regarding {query}. This piece presents contrarian analysis that may differ from mainstream coverage.",
                "url_template": "https://alternative-views.com/contrarian-{query_slug}"
            }
        ]
        
        results = []
        query_slug = query.lower().replace(" ", "-").replace("'", "")
        
        for i, template in enumerate(mock_data[:count]):
            result_id = chr(65 + i)  # A, B, C, D, E
            
            search_result = SearchResult(
                result_id=result_id,
                title=template["title_template"].format(query=query),
                snippet=template["snippet_template"].format(query=query),
                url=template["url_template"].format(query_slug=query_slug),
                rank=i + 1,
                provider="mock"
            )
            results.append(search_result)
        
        return results
    
    def is_available(self) -> bool:
        """Mock service is always available"""
        return True


class SearchService:
    """
    Main search service with provider fallback hierarchy.
    Tries Brave Search first, then DuckDuckGo, then mock data.
    """
    
    def __init__(self):
        self.brave_search = BraveSearchService()
        self.duckduckgo_search = DuckDuckGoSearchService()
        self.mock_search = MockSearchService()
        
        # Cache for repeated queries (5 minute TTL)
        self._cache = {}
        self._cache_ttl = 300  # 5 minutes
    
    def search(
        self, 
        query: str, 
        count: int = 5, 
        use_cache: bool = True,
        prefer_mock: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Perform web search with provider fallback.
        
        Args:
            query: Search query
            count: Number of results to return
            use_cache: Whether to use cached results
            prefer_mock: Force use of mock service (for testing)
            
        Returns:
            list: List of search result dictionaries
        """
        # Check cache first
        if use_cache and not prefer_mock:
            cache_key = f"{query}:{count}"
            cached_result = self._get_cached_result(cache_key)
            if cached_result:
                return cached_result
        
        results = []
        provider_used = None
        error_log = []
        
        # Force mock if requested
        if prefer_mock:
            try:
                results = self.mock_search.search(query, count)
                provider_used = "mock"
            except Exception as e:
                error_log.append(f"Mock search error: {e}")
        else:
            # Try providers in order: Brave -> DuckDuckGo -> Mock
            providers = [
                ("brave", self.brave_search),
                ("duckduckgo", self.duckduckgo_search),
                ("mock", self.mock_search)
            ]
            
            for provider_name, provider in providers:
                if not provider.is_available():
                    error_log.append(f"{provider_name} not available")
                    continue
                
                try:
                    results = provider.search(query, count)
                    provider_used = provider_name
                    break
                except Exception as e:
                    error_log.append(f"{provider_name} error: {e}")
                    continue
        
        # Convert to dictionaries and add metadata
        result_dicts = []
        for result in results:
            result_dict = result.to_dict()
            result_dict["provider_used"] = provider_used
            result_dict["search_timestamp"] = int(time.time())
            result_dicts.append(result_dict)
        
        # Cache successful results
        if result_dicts and use_cache and not prefer_mock:
            cache_key = f"{query}:{count}"
            self._cache_result(cache_key, result_dicts)
        
        # Add metadata about search process
        for result in result_dicts:
            result["search_metadata"] = {
                "provider_used": provider_used,
                "error_log": error_log,
                "timestamp": int(time.time())
            }
        
        return result_dicts
    
    def _get_cached_result(self, cache_key: str) -> Optional[List[Dict[str, Any]]]:
        """Get cached search result if still valid"""
        if cache_key in self._cache:
            cached_data, timestamp = self._cache[cache_key]
            if time.time() - timestamp < self._cache_ttl:
                return cached_data
            else:
                # Remove expired cache entry
                del self._cache[cache_key]
        return None
    
    def _cache_result(self, cache_key: str, results: List[Dict[str, Any]]):
        """Cache search results"""
        self._cache[cache_key] = (results, time.time())
        
        # Simple cache cleanup - remove old entries
        current_time = time.time()
        expired_keys = [
            key for key, (_, timestamp) in self._cache.items()
            if current_time - timestamp >= self._cache_ttl
        ]
        for key in expired_keys:
            del self._cache[key]
    
    def clear_cache(self):
        """Clear search result cache"""
        self._cache.clear()
    
    def health_check(self) -> Dict[str, Any]:
        """Check health of all search providers"""
        return {
            "brave_search": self.brave_search.is_available(),
            "duckduckgo": self.duckduckgo_search.is_available(),
            "mock_search": self.mock_search.is_available(),
            "cache_size": len(self._cache)
        }


# Factory function for creating search service
def create_search_service() -> SearchService:
    """
    Factory function to create search service instance.
    
    Returns:
        SearchService: Configured search service
    """
    return SearchService()