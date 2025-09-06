"""
Search service for API discovery with SOLAR-style ranking
Implements hybrid search combining vector similarity, keyword search, and re-ranking
"""

import time
from typing import List, Dict, Any, Optional, AsyncGenerator
from datetime import datetime
from loguru import logger

from app.models.requests import SearchRequest, SearchFilter
from app.models.responses import SearchResult, SearchResults, Citation
from app.core.vector_client import VectorClient
from app.services.embedding_service import EmbeddingService
from app.services.ranking_service import RankingService

class SearchService:
    """Service for API discovery search with intelligent ranking"""
    
    def __init__(self):
        self.ranking_service = RankingService()
        self.embedding_service = EmbeddingService()
    
    async def hybrid_search(
        self,
        query: str,
        filters: Optional[SearchFilter] = None,
        limit: int = 10,
        vector_client: VectorClient = None,
        embedding_model: Any = None
    ) -> SearchResults:
        """
        Perform hybrid search combining multiple search strategies:
        1. Vector similarity search
        2. Keyword/BM25 search
        3. Re-ranking with cross-encoder
        4. SOLAR-style signal scoring
        """
        
        start_time = time.time()
        
        try:
            # Step 1: Generate query embedding
            query_embedding = await self.embedding_service.generate_embeddings(
                texts=[query],
                model=embedding_model
            )
            
            # Step 2: Vector similarity search
            vector_results = await vector_client.similarity_search(
                query_embedding[0],
                limit=50,  # Get more results for re-ranking
                filters=self._build_vector_filters(filters)
            )
            
            # Step 3: Keyword search (if available)
            keyword_results = await self._keyword_search(query, filters, limit=50)
            
            # Step 4: Merge and deduplicate results
            merged_results = self._merge_search_results(vector_results, keyword_results)
            
            # Step 5: Re-ranking with cross-encoder
            if len(merged_results) > 10:
                reranked_results = await self.ranking_service.rerank_results(
                    query=query,
                    results=merged_results[:20],  # Limit for re-ranking
                    model="cross-encoder-ms-marco-MiniLM-L-6-v2"
                )
                merged_results = reranked_results + merged_results[20:]
            
            # Step 6: Apply SOLAR-style scoring
            scored_results = await self._apply_solar_scoring(
                query=query,
                results=merged_results[:limit],
                filters=filters
            )
            
            # Step 7: Generate citations
            citations = self._generate_citations(scored_results)
            
            search_time = (time.time() - start_time) * 1000
            
            return SearchResults(
                results=scored_results,
                total_count=len(scored_results),
                search_time_ms=search_time,
                query=query,
                filters_applied=self._serialize_filters(filters),
                model_used=str(embedding_model),
                reranking_applied=len(merged_results) > 10,
                citations_included=True
            )
            
        except Exception as e:
            logger.error(f"Error during hybrid search: {str(e)}")
            raise
    
    async def stream_search(
        self,
        query: str,
        filters: Optional[SearchFilter] = None,
        limit: int = 10,
        vector_client: VectorClient = None,
        embedding_model: Any = None
    ) -> AsyncGenerator[SearchResult, None]:
        """Stream search results for real-time updates"""
        
        try:
            # Perform initial search
            results = await self.hybrid_search(
                query=query,
                filters=filters,
                limit=limit,
                vector_client=vector_client,
                embedding_model=embedding_model
            )
            
            # Stream results one by one
            for result in results.results:
                yield result
                
        except Exception as e:
            logger.error(f"Error during stream search: {str(e)}")
    
    async def _keyword_search(
        self,
        query: str,
        filters: Optional[SearchFilter] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Perform keyword-based search (BM25 equivalent)"""
        # This would integrate with a keyword search service
        # For now, return empty results
        return []
    
    def _merge_search_results(
        self,
        vector_results: List[Dict[str, Any]],
        keyword_results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Merge and deduplicate search results"""
        
        merged = {}
        
        # Add vector results with their scores
        for result in vector_results:
            result_id = result.get("id")
            if result_id:
                merged[result_id] = {
                    **result,
                    "vector_score": result.get("score", 0.0),
                    "keyword_score": 0.0
                }
        
        # Add keyword results, merging with existing ones
        for result in keyword_results:
            result_id = result.get("id")
            if result_id in merged:
                merged[result_id]["keyword_score"] = result.get("score", 0.0)
            else:
                merged[result_id] = {
                    **result,
                    "vector_score": 0.0,
                    "keyword_score": result.get("score", 0.0)
                }
        
        # Convert to list and sort by combined score
        merged_list = list(merged.values())
        merged_list.sort(key=lambda x: x.get("vector_score", 0) + x.get("keyword_score", 0), reverse=True)
        
        return merged_list
    
    async def _apply_solar_scoring(
        self,
        query: str,
        results: List[Dict[str, Any]],
        filters: Optional[SearchFilter] = None
    ) -> List[SearchResult]:
        """Apply SOLAR-style scoring to search results"""
        
        scored_results = []
        
        for result in results:
            # Calculate individual scores
            relevance_score = result.get("vector_score", 0.0)
            performance_score = self._calculate_performance_score(result)
            geographic_score = self._calculate_geographic_score(result, filters)
            freshness_score = self._calculate_freshness_score(result)
            permission_score = self._calculate_permission_score(result, filters)
            historical_score = self._calculate_historical_score(result)
            popularity_score = self._calculate_popularity_score(result)
            
            # Calculate final weighted score
            final_score = self._calculate_final_score(
                relevance_score=relevance_score,
                performance_score=performance_score,
                geographic_score=geographic_score,
                freshness_score=freshness_score,
                permission_score=permission_score,
                historical_score=historical_score,
                popularity_score=popularity_score
            )
            
            # Create SearchResult object
            search_result = SearchResult(
                result_id=result.get("id", ""),
                result_type=result.get("type", "endpoint"),
                title=result.get("title", ""),
                content=result.get("content", ""),
                score=final_score,
                relevance_score=relevance_score,
                performance_score=performance_score,
                geographic_score=geographic_score,
                freshness_score=freshness_score,
                permission_score=permission_score,
                historical_score=historical_score,
                popularity_score=popularity_score,
                api_metadata=result.get("api_metadata"),
                service_metadata=result.get("service_metadata"),
                endpoint_metadata=result.get("endpoint_metadata"),
                citations=result.get("citations", []),
                properties=result.get("properties", {}),
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            scored_results.append(search_result)
        
        # Sort by final score
        scored_results.sort(key=lambda x: x.score, reverse=True)
        
        return scored_results
    
    def _calculate_performance_score(self, result: Dict[str, Any]) -> Optional[float]:
        """Calculate performance score based on latency and availability"""
        latency = result.get("latency_ms_p50")
        availability = result.get("availability_slo")
        
        if latency is None and availability is None:
            return None
        
        score = 0.0
        
        # Latency scoring (lower is better)
        if latency is not None:
            if latency < 100:
                score += 0.4
            elif latency < 500:
                score += 0.3
            elif latency < 1000:
                score += 0.2
            else:
                score += 0.1
        
        # Availability scoring (higher is better)
        if availability is not None:
            if availability >= 0.999:
                score += 0.6
            elif availability >= 0.99:
                score += 0.4
            elif availability >= 0.95:
                score += 0.2
            else:
                score += 0.1
        
        return min(score, 1.0)
    
    def _calculate_geographic_score(self, result: Dict[str, Any], filters: Optional[SearchFilter]) -> Optional[float]:
        """Calculate geographic proximity score"""
        if not filters or not filters.regions:
            return None
        
        result_region = result.get("region")
        if not result_region:
            return None
        
        # Simple region matching (could be enhanced with actual geographic distance)
        if result_region in filters.regions:
            return 1.0
        elif any(region in result_region for region in filters.regions):
            return 0.7
        else:
            return 0.3
    
    def _calculate_freshness_score(self, result: Dict[str, Any]) -> Optional[float]:
        """Calculate freshness score based on last update"""
        last_updated = result.get("last_updated")
        if not last_updated:
            return None
        
        try:
            if isinstance(last_updated, str):
                from datetime import datetime
                last_updated = datetime.fromisoformat(last_updated.replace('Z', '+00:00'))
            
            days_old = (datetime.now() - last_updated).days
            
            if days_old < 30:
                return 1.0
            elif days_old < 90:
                return 0.8
            elif days_old < 180:
                return 0.6
            elif days_old < 365:
                return 0.4
            else:
                return 0.2
                
        except:
            return None
    
    def _calculate_permission_score(self, result: Dict[str, Any], filters: Optional[SearchFilter]) -> Optional[float]:
        """Calculate permission fit score"""
        if not filters or not filters.scope_ids:
            return None
        
        result_scopes = result.get("scopes", [])
        if not result_scopes:
            return None
        
        # Calculate overlap between user scopes and result scopes
        overlap = len(set(filters.scope_ids) & set(result_scopes))
        total_user_scopes = len(filters.scope_ids)
        
        if total_user_scopes == 0:
            return None
        
        return overlap / total_user_scopes
    
    def _calculate_historical_score(self, result: Dict[str, Any]) -> Optional[float]:
        """Calculate historical success score"""
        # This would integrate with feedback/usage data
        # For now, return a default score
        return 0.5
    
    def _calculate_popularity_score(self, result: Dict[str, Any]) -> Optional[float]:
        """Calculate popularity score based on usage metrics"""
        # This would integrate with actual usage data
        # For now, return a default score
        return 0.5
    
    def _calculate_final_score(
        self,
        relevance_score: float,
        performance_score: Optional[float],
        geographic_score: Optional[float],
        freshness_score: Optional[float],
        permission_score: Optional[float],
        historical_score: Optional[float],
        popularity_score: Optional[float]
    ) -> float:
        """Calculate final weighted score using SOLAR-style approach"""
        
        # Weights for different factors
        weights = {
            "relevance": 0.4,
            "performance": 0.15,
            "geographic": 0.1,
            "freshness": 0.1,
            "permission": 0.15,
            "historical": 0.05,
            "popularity": 0.05
        }
        
        final_score = relevance_score * weights["relevance"]
        
        if performance_score is not None:
            final_score += performance_score * weights["performance"]
        
        if geographic_score is not None:
            final_score += geographic_score * weights["geographic"]
        
        if freshness_score is not None:
            final_score += freshness_score * weights["freshness"]
        
        if permission_score is not None:
            final_score += permission_score * weights["permission"]
        
        if historical_score is not None:
            final_score += historical_score * weights["historical"]
        
        if popularity_score is not None:
            final_score += popularity_score * weights["popularity"]
        
        return min(final_score, 1.0)
    
    def _generate_citations(self, results: List[SearchResult]) -> List[Citation]:
        """Generate citations for search results"""
        citations = []
        
        for result in results:
            if result.citations:
                citations.extend(result.citations)
        
        return citations
    
    def _build_vector_filters(self, filters: Optional[SearchFilter]) -> Dict[str, Any]:
        """Build filters for vector search"""
        if not filters:
            return {}
        
        vector_filters = {}
        
        if filters.environments:
            vector_filters["environment"] = {"$in": [env.value for env in filters.environments]}
        
        if filters.api_styles:
            vector_filters["api_style"] = {"$in": [style.value for style in filters.api_styles]}
        
        if filters.systems:
            vector_filters["system_name"] = {"$in": filters.systems}
        
        if filters.services:
            vector_filters["service_name"] = {"$in": filters.services}
        
        if filters.tags:
            vector_filters["tags"] = {"$in": filters.tags}
        
        if filters.pii_flagged is not None:
            vector_filters["pii_flagged"] = filters.pii_flagged
        
        if filters.regions:
            vector_filters["region"] = {"$in": filters.regions}
        
        return vector_filters
    
    def _serialize_filters(self, filters: Optional[SearchFilter]) -> Dict[str, Any]:
        """Serialize filters for response"""
        if not filters:
            return {}
        
        return {
            "environments": [env.value for env in filters.environments] if filters.environments else None,
            "api_styles": [style.value for style in filters.api_styles] if filters.api_styles else None,
            "systems": filters.systems,
            "services": filters.services,
            "tags": filters.tags,
            "pii_flagged": filters.pii_flagged,
            "regions": filters.regions,
            "latency_max_ms": filters.latency_max_ms,
            "availability_min": filters.availability_min,
            "scope_ids": filters.scope_ids
        }
    
    async def record_feedback(
        self,
        query: str,
        chosen_result_id: str,
        candidate_ids: List[str],
        label: str,
        user_id: str
    ):
        """Record user feedback for search results"""
        try:
            # This would store feedback in a database for improving ranking
            logger.info(f"Feedback recorded: query='{query}', chosen={chosen_result_id}, label={label}, user={user_id}")
            
            # Could trigger model retraining or ranking adjustment
            await self._update_ranking_weights(query, chosen_result_id, candidate_ids, label)
            
        except Exception as e:
            logger.error(f"Error recording feedback: {str(e)}")
            raise
    
    async def _update_ranking_weights(
        self,
        query: str,
        chosen_result_id: str,
        candidate_ids: List[str],
        label: str
    ):
        """Update ranking weights based on feedback"""
        # This would implement adaptive ranking weight adjustment
        # For now, just log the feedback
        logger.info(f"Updating ranking weights for query: {query}")
