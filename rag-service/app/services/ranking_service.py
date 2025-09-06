"""
Ranking service for re-ranking search results
Uses cross-encoder models for improved relevance scoring
"""

import time
from typing import List, Dict, Any, Optional
from loguru import logger

class RankingService:
    """Service for re-ranking search results using cross-encoder models"""
    
    def __init__(self):
        self.models = {}
        self.default_model = "cross-encoder-ms-marco-MiniLM-L-6-v2"
    
    async def rerank_results(
        self,
        query: str,
        results: List[Dict[str, Any]],
        model: Optional[str] = None,
        batch_size: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Re-rank search results using cross-encoder model
        
        Args:
            query: Search query
            results: List of search results to re-rank
            model: Cross-encoder model to use
            batch_size: Batch size for processing
            
        Returns:
            Re-ranked list of results
        """
        
        if not results:
            return []
        
        model_name = model or self.default_model
        start_time = time.time()
        
        try:
            # Get or load the cross-encoder model
            cross_encoder = await self._get_model(model_name)
            
            # Prepare query-result pairs for scoring
            query_result_pairs = []
            for result in results:
                # Create text representation of result
                result_text = self._create_result_text(result)
                query_result_pairs.append((query, result_text))
            
            # Score pairs in batches
            if batch_size and len(query_result_pairs) > batch_size:
                scores = []
                for i in range(0, len(query_result_pairs), batch_size):
                    batch = query_result_pairs[i:i + batch_size]
                    batch_scores = cross_encoder.predict(batch)
                    scores.extend(batch_scores)
            else:
                scores = cross_encoder.predict(query_result_pairs)
            
            # Update results with new scores
            for i, result in enumerate(results):
                result["rerank_score"] = float(scores[i])
                result["original_rank"] = i
            
            # Sort by re-rank score
            reranked_results = sorted(results, key=lambda x: x["rerank_score"], reverse=True)
            
            processing_time = (time.time() - start_time) * 1000
            logger.info(f"Re-ranked {len(results)} results using {model_name} in {processing_time:.2f}ms")
            
            return reranked_results
            
        except Exception as e:
            logger.error(f"Error during re-ranking: {str(e)}")
            # Return original results if re-ranking fails
            return results
    
    def _create_result_text(self, result: Dict[str, Any]) -> str:
        """Create text representation of result for cross-encoder scoring"""
        
        text_parts = []
        
        # Add title
        if result.get("title"):
            text_parts.append(f"Title: {result['title']}")
        
        # Add content
        if result.get("content"):
            text_parts.append(f"Content: {result['content']}")
        
        # Add API metadata if available
        if result.get("api_metadata"):
            api_meta = result["api_metadata"]
            if api_meta.get("description"):
                text_parts.append(f"API Description: {api_meta['description']}")
            if api_meta.get("tags"):
                text_parts.append(f"Tags: {', '.join(api_meta['tags'])}")
        
        # Add endpoint metadata if available
        if result.get("endpoint_metadata"):
            endpoint_meta = result["endpoint_metadata"]
            if endpoint_meta.get("summary"):
                text_parts.append(f"Endpoint Summary: {endpoint_meta['summary']}")
            if endpoint_meta.get("description"):
                text_parts.append(f"Endpoint Description: {endpoint_meta['description']}")
        
        # Add service metadata if available
        if result.get("service_metadata"):
            service_meta = result["service_metadata"]
            if service_meta.get("description"):
                text_parts.append(f"Service Description: {service_meta['description']}")
        
        # Join all parts
        result_text = " | ".join(text_parts)
        
        # Truncate if too long (cross-encoders have input length limits)
        max_length = 512
        if len(result_text) > max_length:
            result_text = result_text[:max_length] + "..."
        
        return result_text
    
    async def _get_model(self, model_name: str):
        """Get or load a cross-encoder model"""
        
        if model_name not in self.models:
            try:
                logger.info(f"Loading cross-encoder model: {model_name}")
                
                # Import here to avoid loading models at startup
                from sentence_transformers import CrossEncoder
                
                model = CrossEncoder(model_name)
                self.models[model_name] = model
                logger.info(f"Successfully loaded cross-encoder model: {model_name}")
                
            except Exception as e:
                logger.error(f"Error loading cross-encoder model {model_name}: {str(e)}")
                # Fallback to default model
                if model_name != self.default_model:
                    logger.info(f"Falling back to default cross-encoder model: {self.default_model}")
                    return await self._get_model(self.default_model)
                else:
                    raise
        
        return self.models[model_name]
    
    def get_model_info(self, model_name: str) -> Dict[str, Any]:
        """Get information about a specific cross-encoder model"""
        try:
            model = self.models.get(model_name)
            if model:
                return {
                    "name": model_name,
                    "max_seq_length": getattr(model, 'max_seq_length', 'Unknown'),
                    "device": str(getattr(model, 'device', 'Unknown')),
                    "loaded": True
                }
            else:
                return {
                    "name": model_name,
                    "loaded": False
                }
        except Exception as e:
            return {
                "name": model_name,
                "error": str(e),
                "loaded": False
            }
    
    def list_loaded_models(self) -> List[str]:
        """List all currently loaded cross-encoder models"""
        return list(self.models.keys())
    
    def unload_model(self, model_name: str) -> bool:
        """Unload a specific cross-encoder model to free memory"""
        try:
            if model_name in self.models:
                del self.models[model_name]
                logger.info(f"Unloaded cross-encoder model: {model_name}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error unloading cross-encoder model {model_name}: {str(e)}")
            return False
    
    async def batch_rerank(
        self,
        queries: List[str],
        results_list: List[List[Dict[str, Any]]],
        model: Optional[str] = None
    ) -> List[List[Dict[str, Any]]]:
        """
        Batch re-rank multiple query-result sets
        
        Args:
            queries: List of search queries
            results_list: List of result lists (one per query)
            model: Cross-encoder model to use
            
        Returns:
            List of re-ranked result lists
        """
        
        if len(queries) != len(results_list):
            raise ValueError("Number of queries must match number of result lists")
        
        reranked_results = []
        
        for query, results in zip(queries, results_list):
            reranked = await self.rerank_results(query, results, model)
            reranked_results.append(reranked)
        
        return reranked_results
    
    def calculate_ranking_metrics(
        self,
        original_results: List[Dict[str, Any]],
        reranked_results: List[Dict[str, Any]],
        relevant_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Calculate ranking quality metrics
        
        Args:
            original_results: Original search results
            reranked_results: Re-ranked search results
            relevant_ids: List of relevant result IDs (for precision/recall)
            
        Returns:
            Dictionary of ranking metrics
        """
        
        metrics = {
            "total_results": len(original_results),
            "reranking_applied": len(reranked_results) > 0,
            "score_changes": [],
            "rank_changes": []
        }
        
        if not reranked_results:
            return metrics
        
        # Calculate score changes
        for i, result in enumerate(reranked_results):
            original_score = result.get("original_score", 0.0)
            rerank_score = result.get("rerank_score", 0.0)
            
            if original_score > 0:
                score_change = (rerank_score - original_score) / original_score
                metrics["score_changes"].append({
                    "result_id": result.get("id", f"result_{i}"),
                    "original_score": original_score,
                    "rerank_score": rerank_score,
                    "change_percent": score_change * 100
                })
        
        # Calculate rank changes
        original_ranks = {result.get("id", f"result_{i}"): i for i, result in enumerate(original_results)}
        
        for i, result in enumerate(reranked_results):
            result_id = result.get("id", f"result_{i}")
            original_rank = original_ranks.get(result_id, i)
            rank_change = original_rank - i  # Positive means improved rank
            
            metrics["rank_changes"].append({
                "result_id": result_id,
                "original_rank": original_rank,
                "new_rank": i,
                "rank_change": rank_change
            })
        
        # Calculate average metrics
        if metrics["score_changes"]:
            avg_score_change = sum(change["change_percent"] for change in metrics["score_changes"]) / len(metrics["score_changes"])
            metrics["average_score_change_percent"] = avg_score_change
        
        if metrics["rank_changes"]:
            avg_rank_change = sum(change["rank_change"] for change in metrics["rank_changes"]) / len(metrics["rank_changes"])
            metrics["average_rank_change"] = avg_rank_change
        
        # Calculate precision/recall if relevant IDs provided
        if relevant_ids:
            metrics["precision_at_k"] = {}
            metrics["recall_at_k"] = {}
            
            for k in [1, 3, 5, 10]:
                if k <= len(reranked_results):
                    top_k_ids = [result.get("id") for result in reranked_results[:k]]
                    relevant_in_top_k = len(set(top_k_ids) & set(relevant_ids))
                    
                    precision = relevant_in_top_k / k
                    recall = relevant_in_top_k / len(relevant_ids) if relevant_ids else 0
                    
                    metrics["precision_at_k"][f"p@{k}"] = precision
                    metrics["recall_at_k"][f"r@{k}"] = recall
        
        return metrics
