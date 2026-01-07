"""
Recommendation engine for suggesting similar artworks
"""

from typing import List, Dict, Any, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import structlog

from app.models import Artwork, Recommendation
from app.config import settings

logger = structlog.get_logger()


class RecommendationEngine:
    """Engine for generating artwork recommendations"""
    
    def __init__(self):
        self.vectorizer = TfidfVectorizer(max_features=1000)
        self.similarity_threshold = settings.SIMILARITY_THRESHOLD
    
    def generate_recommendations(
        self,
        target_artwork: Artwork,
        all_artworks: List[Artwork],
        max_results: int = 10,
        criteria: List[str] = None
    ) -> List[Recommendation]:
        """Generate recommendations for a target artwork"""
        
        if criteria is None:
            criteria = ["artist", "period", "type", "location"]
        
        recommendations = []
        
        for artwork in all_artworks:
            if artwork.uri == target_artwork.uri:
                continue  # Skip the target artwork itself
            
            similarity_score, reasons = self._calculate_similarity(
                target_artwork, artwork, criteria
            )
            
            if similarity_score >= self.similarity_threshold:
                recommendations.append(
                    Recommendation(
                        artwork=artwork,
                        similarity_score=similarity_score,
                        reasons=reasons
                    )
                )
        
        # Sort by similarity score descending
        recommendations.sort(key=lambda x: x.similarity_score, reverse=True)
        
        return recommendations[:max_results]
    
    def _calculate_similarity(
        self,
        artwork1: Artwork,
        artwork2: Artwork,
        criteria: List[str]
    ) -> Tuple[float, List[str]]:
        """Calculate similarity between two artworks"""
        
        scores = []
        reasons = []
        
        # Artist similarity
        if "artist" in criteria and artwork1.artist and artwork2.artist:
            if artwork1.artist.uri == artwork2.artist.uri or \
               artwork1.artist.name == artwork2.artist.name:
                scores.append(1.0)
                reasons.append(f"Same artist: {artwork1.artist.name}")
            else:
                # Check nationality
                if artwork1.artist.nationality and artwork2.artist.nationality:
                    if artwork1.artist.nationality == artwork2.artist.nationality:
                        scores.append(0.5)
                        reasons.append(f"Same nationality: {artwork1.artist.nationality}")
        
        # Artwork type similarity
        if "type" in criteria:
            if artwork1.artwork_type == artwork2.artwork_type:
                scores.append(1.0)
                reasons.append(f"Same type: {artwork1.artwork_type}")
        
        # Period similarity (based on creation date)
        if "period" in criteria and artwork1.creation_date and artwork2.creation_date:
            try:
                year1 = int(artwork1.creation_date[:4])
                year2 = int(artwork2.creation_date[:4])
                
                # Same century
                century1 = year1 // 100
                century2 = year2 // 100
                
                if century1 == century2:
                    # Within same 50-year period
                    if abs(year1 - year2) <= 50:
                        scores.append(1.0)
                        reasons.append(f"Similar period: {century1 + 1}th century")
                    else:
                        scores.append(0.7)
                        reasons.append(f"Same century: {century1 + 1}th")
            except:
                pass
        
        # Location similarity
        if "location" in criteria and artwork1.current_location and artwork2.current_location:
            if artwork1.current_location.uri == artwork2.current_location.uri or \
               artwork1.current_location.name == artwork2.current_location.name:
                scores.append(1.0)
                reasons.append(f"Same location: {artwork1.current_location.name}")
            elif artwork1.current_location.country == artwork2.current_location.country:
                scores.append(0.6)
                reasons.append(f"Same country: {artwork1.current_location.country}")
        
        # Medium similarity
        if "medium" in criteria and artwork1.medium and artwork2.medium:
            medium_similarity = self._text_similarity(artwork1.medium, artwork2.medium)
            if medium_similarity > 0.7:
                scores.append(medium_similarity)
                reasons.append(f"Similar medium: {artwork2.medium}")
        
        # Description similarity (semantic)
        if "description" in criteria and artwork1.description and artwork2.description:
            desc_similarity = self._text_similarity(artwork1.description, artwork2.description)
            if desc_similarity > 0.5:
                scores.append(desc_similarity * 0.8)  # Weight description less
                reasons.append("Similar themes")
        
        # Romanian heritage bonus
        if artwork1.romanian_heritage and artwork2.romanian_heritage:
            scores.append(0.3)
            reasons.append("Both part of Romanian heritage")
        
        # Calculate weighted average
        if scores:
            final_score = np.mean(scores)
        else:
            final_score = 0.0
        
        return final_score, reasons
    
    def _text_similarity(self, text1: str, text2: str) -> float:
        """Calculate text similarity using TF-IDF and cosine similarity"""
        try:
            vectors = self.vectorizer.fit_transform([text1, text2])
            similarity = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]
            return float(similarity)
        except:
            return 0.0
    
    def find_similar_by_provenance(
        self,
        target_artwork: Artwork,
        all_artworks: List[Artwork]
    ) -> List[Recommendation]:
        """Find artworks with similar provenance patterns"""
        
        recommendations = []
        
        if not target_artwork.provenance_chain:
            return recommendations
        
        # Extract provenance features from target
        target_events = set(event.event_type for event in target_artwork.provenance_chain)
        target_locations = set(
            event.location.name for event in target_artwork.provenance_chain
            if event.location
        )
        target_agents = set()
        for event in target_artwork.provenance_chain:
            if event.from_agent:
                target_agents.add(event.from_agent.name)
            if event.to_agent:
                target_agents.add(event.to_agent.name)
        
        # Compare with other artworks
        for artwork in all_artworks:
            if artwork.uri == target_artwork.uri or not artwork.provenance_chain:
                continue
            
            score = 0.0
            reasons = []
            
            # Compare event types
            artwork_events = set(event.event_type for event in artwork.provenance_chain)
            event_overlap = len(target_events & artwork_events) / len(target_events | artwork_events)
            if event_overlap > 0:
                score += event_overlap * 0.3
                if event_overlap > 0.5:
                    reasons.append("Similar provenance event types")
            
            # Compare locations
            artwork_locations = set(
                event.location.name for event in artwork.provenance_chain
                if event.location
            )
            if target_locations and artwork_locations:
                location_overlap = len(target_locations & artwork_locations) / len(target_locations | artwork_locations)
                if location_overlap > 0:
                    score += location_overlap * 0.4
                    shared_locations = target_locations & artwork_locations
                    if shared_locations:
                        reasons.append(f"Shared provenance locations: {', '.join(list(shared_locations)[:2])}")
            
            # Compare agents (collectors, dealers, etc.)
            artwork_agents = set()
            for event in artwork.provenance_chain:
                if event.from_agent:
                    artwork_agents.add(event.from_agent.name)
                if event.to_agent:
                    artwork_agents.add(event.to_agent.name)
            
            if target_agents and artwork_agents:
                agent_overlap = len(target_agents & artwork_agents) / len(target_agents | artwork_agents)
                if agent_overlap > 0:
                    score += agent_overlap * 0.3
                    shared_agents = target_agents & artwork_agents
                    if shared_agents:
                        reasons.append(f"Shared collectors/dealers: {', '.join(list(shared_agents)[:2])}")
            
            if score >= self.similarity_threshold:
                recommendations.append(
                    Recommendation(
                        artwork=artwork,
                        similarity_score=score,
                        reasons=reasons
                    )
                )
        
        recommendations.sort(key=lambda x: x.similarity_score, reverse=True)
        return recommendations[:settings.MAX_RECOMMENDATIONS]
