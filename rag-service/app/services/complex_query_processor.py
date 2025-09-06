"""
Complex Query Processor for CatalystAI
Handles multi-faceted queries with intelligent decomposition and comprehensive responses
"""

import re
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from loguru import logger

from app.models.requests import SearchRequest, SearchFilter
from app.models.responses import SearchResult, SearchResults
from app.services.search_service import SearchService
from app.services.ranking_service import RankingService

class ComplexQueryProcessor:
    """
    Processes complex, multi-faceted queries and provides comprehensive responses
    covering API discovery, onboarding, integration guidance, and performance analysis
    """
    
    def __init__(self):
        self.search_service = SearchService()
        self.ranking_service = RankingService()
        
        # Query intent patterns
        self.intent_patterns = {
            "api_discovery": [
                r"which APIs?",
                r"what APIs?",
                r"APIs I need",
                r"consume.*API",
                r"API.*consume"
            ],
            "onboarding": [
                r"onboarding.*required",
                r"access.*needed",
                r"permission.*required",
                r"approval.*needed"
            ],
            "integration_guidance": [
                r"recommendations",
                r"best practices",
                r"patterns",
                r"guidance",
                r"how to"
            ],
            "performance_requirements": [
                r"TPS",
                r"throughput",
                r"capacity",
                r"performance",
                r"scaling"
            ],
            "downstream_impact": [
                r"downstream",
                r"infrastructure",
                r"changes.*needed",
                r"support.*traffic"
            ]
        }
        
        # Business domain patterns
        self.domain_patterns = {
            "supply_chain": [
                r"supply chain",
                r"forecasting",
                r"inventory",
                r"logistics",
                r"procurement"
            ],
            "vendor_management": [
                r"vendor",
                r"supplier",
                r"partner",
                r"vendorId"
            ],
            "analytics": [
                r"analytics",
                r"insights",
                r"reporting",
                r"metrics"
            ]
        }
    
    async def process_complex_query(
        self,
        query: str,
        vector_client: Any = None,
        embedding_model: Any = None
    ) -> Dict[str, Any]:
        """
        Process a complex query and provide comprehensive response
        
        Args:
            query: Natural language query from product team
            vector_client: Vector database client
            embedding_model: Embedding model for semantic search
            
        Returns:
            Comprehensive response covering all aspects of the query
        """
        
        start_time = datetime.now()
        
        try:
            # Step 1: Analyze query intent and extract key information
            query_analysis = self._analyze_query_intent(query)
            
            # Step 2: Perform targeted searches for each intent
            search_results = await self._perform_targeted_searches(
                query, query_analysis, vector_client, embedding_model
            )
            
            # Step 3: Generate comprehensive response
            comprehensive_response = self._generate_comprehensive_response(
                query, query_analysis, search_results
            )
            
            # Step 4: Add performance analysis and recommendations
            performance_analysis = self._analyze_performance_requirements(query_analysis)
            
            # Step 5: Assess downstream impact
            downstream_impact = self._assess_downstream_impact(query_analysis, performance_analysis)
            
            # Step 6: Generate actionable next steps
            next_steps = self._generate_next_steps(query_analysis, search_results, performance_analysis)
            
            # Combine all components
            final_response = {
                "query": query,
                "query_analysis": query_analysis,
                "api_discovery": search_results.get("api_discovery", []),
                "onboarding_requirements": search_results.get("onboarding", []),
                "integration_recommendations": search_results.get("integration", []),
                "performance_analysis": performance_analysis,
                "downstream_impact": downstream_impact,
                "next_steps": next_steps,
                "summary": self._generate_summary(search_results, performance_analysis),
                "processing_time_ms": (datetime.now() - start_time).total_seconds() * 1000
            }
            
            return final_response
            
        except Exception as e:
            logger.error(f"Error processing complex query: {str(e)}")
            raise
    
    def _analyze_query_intent(self, query: str) -> Dict[str, Any]:
        """Analyze query to extract intent and key information"""
        
        analysis = {
            "primary_intent": self._identify_primary_intent(query),
            "detected_intents": self._detect_all_intents(query),
            "business_domain": self._identify_business_domain(query),
            "performance_requirements": self._extract_performance_requirements(query),
            "key_entities": self._extract_key_entities(query),
            "business_context": self._identify_business_context(query)
        }
        
        return analysis
    
    def _identify_primary_intent(self, query: str) -> str:
        """Identify the primary intent of the query"""
        
        # Count matches for each intent
        intent_scores = {}
        for intent, patterns in self.intent_patterns.items():
            score = sum(len(re.findall(pattern, query, re.IGNORECASE)) for pattern in patterns)
            intent_scores[intent] = score
        
        # Return intent with highest score
        primary_intent = max(intent_scores.items(), key=lambda x: x[1])
        return primary_intent[0] if primary_intent[1] > 0 else "general_inquiry"
    
    def _detect_all_intents(self, query: str) -> List[str]:
        """Detect all intents present in the query"""
        
        detected_intents = []
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, query, re.IGNORECASE):
                    detected_intents.append(intent)
                    break
        
        return list(set(detected_intents))
    
    def _identify_business_domain(self, query: str) -> str:
        """Identify the business domain from the query"""
        
        for domain, patterns in self.domain_patterns.items():
            for pattern in patterns:
                if re.search(pattern, query, re.IGNORECASE):
                    return domain
        
        return "general"
    
    def _extract_performance_requirements(self, query: str) -> Dict[str, Any]:
        """Extract performance requirements from the query"""
        
        # Look for TPS/throughput requirements
        tps_match = re.search(r'(\d+)\s*TPS', query, re.IGNORECASE)
        throughput_match = re.search(r'(\d+)\s*requests?', query, re.IGNORECASE)
        
        requirements = {
            "tps_required": None,
            "throughput_required": None,
            "performance_critical": False
        }
        
        if tps_match:
            requirements["tps_required"] = int(tps_match.group(1))
            requirements["performance_critical"] = requirements["tps_required"] > 1000
        
        if throughput_match:
            requirements["throughput_required"] = int(throughput_match.group(1))
        
        return requirements
    
    def _extract_key_entities(self, query: str) -> List[str]:
        """Extract key entities from the query"""
        
        entities = []
        
        # Look for common entity patterns
        entity_patterns = [
            r'vendorId',
            r'customerId',
            r'orderId',
            r'productId',
            r'userId'
        ]
        
        for pattern in entity_patterns:
            if re.search(pattern, query, re.IGNORECASE):
                entities.append(pattern)
        
        # Look for business concepts
        business_concepts = [
            r'supply chain',
            r'forecasting',
            r'analytics',
            r'reporting',
            r'integration'
        ]
        
        for concept in business_concepts:
            if re.search(concept, query, re.IGNORECASE):
                entities.append(concept)
        
        return entities
    
    def _identify_business_context(self, query: str) -> str:
        """Identify the business context of the query"""
        
        context_indicators = {
            "new_feature": [r"building.*new feature", r"new feature", r"developing"],
            "integration": [r"integrating", r"integration", r"consume.*API"],
            "performance": [r"performance", r"scaling", r"capacity"],
            "maintenance": [r"maintenance", r"upgrade", r"update"]
        }
        
        for context, patterns in context_indicators.items():
            for pattern in patterns:
                if re.search(pattern, query, re.IGNORECASE):
                    return context
        
        return "general"
    
    async def _perform_targeted_searches(
        self,
        query: str,
        query_analysis: Dict[str, Any],
        vector_client: Any,
        embedding_model: Any
    ) -> Dict[str, List[SearchResult]]:
        """Perform targeted searches based on detected intents"""
        
        search_results = {}
        
        # API Discovery Search
        if "api_discovery" in query_analysis["detected_intents"]:
            api_results = await self._search_for_apis(query, query_analysis, vector_client, embedding_model)
            search_results["api_discovery"] = api_results
        
        # Onboarding Requirements Search
        if "onboarding" in query_analysis["detected_intents"]:
            onboarding_results = await self._search_for_onboarding(query, query_analysis, vector_client, embedding_model)
            search_results["onboarding"] = onboarding_results
        
        # Integration Guidance Search
        if "integration_guidance" in query_analysis["detected_intents"]:
            integration_results = await self._search_for_integration_guidance(query, query_analysis, vector_client, embedding_model)
            search_results["integration"] = integration_results
        
        return search_results
    
    async def _search_for_apis(
        self,
        query: str,
        query_analysis: Dict[str, Any],
        vector_client: Any,
        embedding_model: Any
    ) -> List[SearchResult]:
        """Search for relevant APIs based on business domain and requirements"""
        
        # Create domain-specific search filters
        filters = SearchFilter(
            api_styles=["REST", "GraphQL", "SOAP"],
            tags=query_analysis.get("business_domain", []),
            environments=["DEV", "STAGING", "PRODUCTION"]
        )
        
        # Perform search
        search_request = SearchRequest(
            query=query,
            filters=filters,
            limit=10,
            include_citations=True,
            rerank=True
        )
        
        results = await self.search_service.hybrid_search(
            query=query,
            filters=filters,
            limit=10,
            vector_client=vector_client,
            embedding_model=embedding_model
        )
        
        return results.results
    
    async def _search_for_onboarding(
        self,
        query: str,
        query_analysis: Dict[str, Any],
        vector_client: Any,
        embedding_model: Any
    ) -> List[SearchResult]:
        """Search for onboarding requirements and access information"""
        
        # Search for onboarding documentation
        onboarding_query = f"onboarding access requirements {query_analysis.get('business_domain', '')} API"
        
        filters = SearchFilter(
            tags=["onboarding", "access", "permissions", "scopes"],
            environments=["DEV", "STAGING", "PRODUCTION"]
        )
        
        results = await self.search_service.hybrid_search(
            query=onboarding_query,
            filters=filters,
            limit=5,
            vector_client=vector_client,
            embedding_model=embedding_model
        )
        
        return results.results
    
    async def _search_for_integration_guidance(
        self,
        query: str,
        query_analysis: Dict[str, Any],
        vector_client: Any,
        embedding_model: Any
    ) -> List[SearchResult]:
        """Search for integration guidance and best practices"""
        
        # Search for integration documentation
        integration_query = f"integration best practices patterns {query_analysis.get('business_domain', '')} API"
        
        filters = SearchFilter(
            tags=["integration", "best-practices", "patterns", "guidance"],
            environments=["DEV", "STAGING", "PRODUCTION"]
        )
        
        results = await self.search_service.hybrid_search(
            query=integration_query,
            filters=filters,
            limit=5,
            vector_client=vector_client,
            embedding_model=embedding_model
        )
        
        return results.results
    
    def _generate_comprehensive_response(
        self,
        query: str,
        query_analysis: Dict[str, Any],
        search_results: Dict[str, List[SearchResult]]
    ) -> Dict[str, Any]:
        """Generate comprehensive response based on search results"""
        
        response = {
            "query_analysis": query_analysis,
            "discovered_apis": self._format_api_discovery_results(search_results.get("api_discovery", [])),
            "onboarding_requirements": self._format_onboarding_requirements(search_results.get("onboarding", [])),
            "integration_recommendations": self._format_integration_recommendations(search_results.get("integration", []))
        }
        
        return response
    
    def _format_api_discovery_results(self, results: List[SearchResult]) -> List[Dict[str, Any]]:
        """Format API discovery results for response"""
        
        formatted_apis = []
        for result in results:
            api_info = {
                "api_name": result.title,
                "service": result.service_metadata.service_name if result.service_metadata else "Unknown",
                "system": result.service_metadata.system_name if result.service_metadata else "Unknown",
                "endpoints": self._extract_endpoints_from_result(result),
                "relevance_score": result.relevance_score,
                "performance_score": result.performance_score,
                "citations": [citation.source_ref for citation in result.citations]
            }
            formatted_apis.append(api_info)
        
        return formatted_apis
    
    def _extract_endpoints_from_result(self, result: SearchResult) -> List[Dict[str, Any]]:
        """Extract endpoint information from search result"""
        
        endpoints = []
        
        if result.endpoint_metadata:
            endpoint = {
                "method": result.endpoint_metadata.method,
                "path": result.endpoint_metadata.path,
                "description": result.endpoint_metadata.description or result.endpoint_metadata.summary,
                "supports_vendor_id": "vendorId" in (result.endpoint_metadata.path or "")
            }
            endpoints.append(endpoint)
        
        return endpoints
    
    def _format_onboarding_requirements(self, results: List[SearchResult]) -> List[Dict[str, Any]]:
        """Format onboarding requirements for response"""
        
        # This would extract onboarding information from search results
        # For now, return a template structure
        return []
    
    def _format_integration_recommendations(self, results: List[SearchResult]) -> List[Dict[str, Any]]:
        """Format integration recommendations for response"""
        
        # This would extract integration guidance from search results
        # For now, return a template structure
        return []
    
    def _analyze_performance_requirements(self, query_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze performance requirements and provide recommendations"""
        
        performance_req = query_analysis.get("performance_requirements", {})
        tps_required = performance_req.get("tps_required", 0)
        
        analysis = {
            "tps_requirement": tps_required,
            "performance_critical": tps_required > 1000,
            "scaling_needed": tps_required > 500,
            "recommendations": self._generate_performance_recommendations(tps_required),
            "estimated_costs": self._estimate_infrastructure_costs(tps_required)
        }
        
        return analysis
    
    def _generate_performance_recommendations(self, tps_required: int) -> List[str]:
        """Generate performance recommendations based on TPS requirements"""
        
        recommendations = []
        
        if tps_required > 2000:
            recommendations.extend([
                "Implement horizontal scaling for all services",
                "Add load balancers and auto-scaling groups",
                "Implement request queuing and throttling",
                "Use CDN for static data and caching layers"
            ])
        elif tps_required > 1000:
            recommendations.extend([
                "Implement horizontal scaling for critical services",
                "Add read replicas for databases",
                "Implement connection pooling and caching",
                "Monitor and optimize database queries"
            ])
        elif tps_required > 500:
            recommendations.extend([
                "Implement basic caching strategies",
                "Optimize database queries",
                "Use connection pooling",
                "Monitor performance metrics"
            ])
        
        return recommendations
    
    def _estimate_infrastructure_costs(self, tps_required: int) -> Dict[str, str]:
        """Estimate infrastructure costs based on TPS requirements"""
        
        if tps_required > 2000:
            return {
                "additional_compute": "$2,000-5,000/month",
                "load_balancers": "$500-1,000/month",
                "database_scaling": "$1,000-3,000/month",
                "monitoring_tools": "$200-500/month"
            }
        elif tps_required > 1000:
            return {
                "additional_compute": "$1,000-3,000/month",
                "load_balancers": "$300-800/month",
                "database_scaling": "$500-2,000/month",
                "monitoring_tools": "$100-300/month"
            }
        else:
            return {
                "additional_compute": "$500-1,500/month",
                "load_balancers": "$100-500/month",
                "database_scaling": "$200-1,000/month",
                "monitoring_tools": "$50-200/month"
            }
    
    def _assess_downstream_impact(
        self,
        query_analysis: Dict[str, Any],
        performance_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Assess downstream impact of the requirements"""
        
        impact = {
            "infrastructure_team": self._get_infrastructure_impact(performance_analysis),
            "platform_team": self._get_platform_impact(performance_analysis),
            "security_team": self._get_security_impact(query_analysis),
            "data_team": self._get_data_team_impact(performance_analysis),
            "estimated_timeline": self._estimate_implementation_timeline(performance_analysis)
        }
        
        return impact
    
    def _get_infrastructure_impact(self, performance_analysis: Dict[str, Any]) -> List[str]:
        """Get infrastructure team impact"""
        
        tps_required = performance_analysis.get("tps_requirement", 0)
        impacts = []
        
        if tps_required > 2000:
            impacts.extend([
                "Scale all services to support high throughput",
                "Add load balancers and auto-scaling groups",
                "Implement horizontal scaling for all services",
                "Upgrade database instances and add read replicas"
            ])
        elif tps_required > 1000:
            impacts.extend([
                "Scale critical services for medium throughput",
                "Add load balancers for critical services",
                "Implement horizontal scaling for critical services",
                "Add read replicas for databases"
            ])
        
        return impacts
    
    def _get_platform_impact(self, performance_analysis: Dict[str, Any]) -> List[str]:
        """Get platform team impact"""
        
        tps_required = performance_analysis.get("tps_requirement", 0)
        impacts = []
        
        if tps_required > 1000:
            impacts.extend([
                "Update rate limiting policies for new TPS requirements",
                "Implement request queuing and throttling mechanisms",
                "Add monitoring and alerting for new services",
                "Update API gateway configurations"
            ])
        
        return impacts
    
    def _get_security_impact(self, query_analysis: Dict[str, Any]) -> List[str]:
        """Get security team impact"""
        
        impacts = [
            "Review and approve new API access requests",
            "Update security policies for increased traffic",
            "Implement additional monitoring for security events",
            "Review and approve new service deployments"
        ]
        
        return impacts
    
    def _get_data_team_impact(self, performance_analysis: Dict[str, Any]) -> List[str]:
        """Get data team impact"""
        
        tps_required = performance_analysis.get("tps_requirement", 0)
        impacts = []
        
        if tps_required > 1000:
            impacts.extend([
                "Optimize database queries for high throughput operations",
                "Implement data partitioning for better performance",
                "Add caching layers for frequently accessed data",
                "Set up data backup and recovery procedures"
            ])
        
        return impacts
    
    def _estimate_implementation_timeline(self, performance_analysis: Dict[str, Any]) -> Dict[str, str]:
        """Estimate implementation timeline"""
        
        tps_required = performance_analysis.get("tps_requirement", 0)
        
        if tps_required > 2000:
            return {
                "infrastructure_scaling": "2-3 weeks",
                "security_review": "1 week",
                "performance_testing": "1-2 weeks",
                "total_implementation": "4-6 weeks"
            }
        elif tps_required > 1000:
            return {
                "infrastructure_scaling": "1-2 weeks",
                "security_review": "1 week",
                "performance_testing": "1 week",
                "total_implementation": "3-4 weeks"
            }
        else:
            return {
                "infrastructure_scaling": "1 week",
                "security_review": "3-5 days",
                "performance_testing": "3-5 days",
                "total_implementation": "2-3 weeks"
            }
    
    def _generate_next_steps(
        self,
        query_analysis: Dict[str, Any],
        search_results: Dict[str, List[SearchResult]],
        performance_analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate actionable next steps"""
        
        next_steps = []
        
        # High priority steps
        if search_results.get("api_discovery"):
            next_steps.append({
                "priority": "High",
                "action": "Submit API access requests for discovered services",
                "owner": "Product Team",
                "timeline": "Immediate"
            })
        
        if performance_analysis.get("performance_critical"):
            next_steps.append({
                "priority": "High",
                "action": "Engage Infrastructure team for capacity planning",
                "owner": "Product Team",
                "timeline": "This week"
            })
        
        # Medium priority steps
        next_steps.extend([
            {
                "priority": "Medium",
                "action": "Design integration architecture with Engineering team",
                "owner": "Engineering Team",
                "timeline": "Next 2 weeks"
            },
            {
                "priority": "Medium",
                "action": "Create performance test plan",
                "owner": "QA Team",
                "timeline": "Next 2 weeks"
            }
        ])
        
        # Low priority steps
        next_steps.append({
            "priority": "Low",
            "action": "Document integration patterns and best practices",
            "owner": "Engineering Team",
            "timeline": "Ongoing"
        })
        
        return next_steps
    
    def _generate_summary(
        self,
        search_results: Dict[str, List[SearchResult]],
        performance_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate summary of the comprehensive response"""
        
        api_count = len(search_results.get("api_discovery", []))
        scaling_needed = performance_analysis.get("scaling_needed", False)
        tps_required = performance_analysis.get("tps_requirement", 0)
        
        summary = {
            "apis_identified": api_count,
            "scaling_required": scaling_needed,
            "performance_critical": tps_required > 1000,
            "estimated_timeline": self._get_timeline_summary(performance_analysis),
            "estimated_cost": self._get_cost_summary(performance_analysis)
        }
        
        return summary
    
    def _get_timeline_summary(self, performance_analysis: Dict[str, Any]) -> str:
        """Get timeline summary"""
        
        tps_required = performance_analysis.get("tps_requirement", 0)
        
        if tps_required > 2000:
            return "4-6 weeks"
        elif tps_required > 1000:
            return "3-4 weeks"
        else:
            return "2-3 weeks"
    
    def _get_cost_summary(self, performance_analysis: Dict[str, Any]) -> str:
        """Get cost summary"""
        
        costs = performance_analysis.get("estimated_costs", {})
        total_min = sum(int(cost.replace("$", "").replace("/month", "").split("-")[0]) for cost in costs.values())
        total_max = sum(int(cost.replace("$", "").replace("/month", "").split("-")[1]) for cost in costs.values())
        
        return f"${total_min:,}-{total_max:,}/month additional"
