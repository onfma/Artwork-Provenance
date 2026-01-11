"""
Data models for the Heritage Provenance System
"""

from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class ProvenanceEventType(str, Enum):
    """Types of provenance events"""
    ACQUISITION = "acquisition"
    SALE = "sale"
    TRANSFER = "transfer"
    EXHIBITION = "exhibition"
    LOAN = "loan"
    RESTORATION = "restoration"
    THEFT = "theft"
    RECOVERY = "recovery"
    DONATION = "donation"
    INHERITANCE = "inheritance"


class ArtworkType(str, Enum):
    """Types of artworks"""
    PAINTING = "painting"
    SCULPTURE = "sculpture"
    DRAWING = "drawing"
    PRINT = "print"
    PHOTOGRAPH = "photograph"
    MANUSCRIPT = "manuscript"
    ARTIFACT = "artifact"
    INSTALLATION = "installation"

    def __str__(self):
        return str(self.value.capitalize())

    @classmethod
    def from_text(cls, text: str) -> "ArtworkType":
        """
        Determine artwork type from text description (multilingual).
        Matches keywords for Romanian and English terms.
        """

        if not text:
            return cls.ARTIFACT
        
        if isinstance(text, dict):
            if 'label' in text.keys():
                text = text['label']
            
        text = text.lower()
        
        # Drawing / Graphics
        if any(w in text for w in [
            "desen", "drawing", "schiță", "schita", "sketch", "creion", "pencil", 
            "cărbune", "charcoal", "tuș", "ink", "pastel", "grafică", "graphic"
        ]):
            return cls.DRAWING
            
        # Prints
        if any(w in text for w in [
            "gravură", "gravura", "print", "litografie", "lithograph", "acvaforte", 
            "etching", "xilogravură", "woodcut", "stampă", "serigrafie"
        ]):
            return cls.PRINT
            
        # Photography
        if any(w in text for w in [
            "fotografie", "fotografia", "photograph", "photo", "foto", 
            "negativ", "negative", "daguerreotype"
        ]):
            return cls.PHOTOGRAPH
            
        # Manuscript
        if any(w in text for w in ["manuscris", "manuscript", "document", "scrisoare", "letter", "incunabul", "carte"]):
            return cls.MANUSCRIPT
            
        # Installation
        if any(w in text for w in ["instalație", "instalatie", "installation"]):
            return cls.INSTALLATION
            
        # Artifacts
        if any(w in text for w in [
            "artefact", "artifact", "ceramică", "ceramic", "pottery", "porțelan", 
            "textil", "textile", "covor", "carpet", "tapiserie", "monedă", "coin", 
            "bijuterie", "jewelry", "mobilier", "furniture", "vas", "vessel"
        ]):
            return cls.ARTIFACT
            
        # Sculpture (check materials often used in sculpture)
        if any(w in text for w in ["sculptură", "sculptura", "sculpture", "statuie", "statue", "bust", "relief", "bronz", "bronze", "marmură", "marble", "ronde-bosse"]):
            return cls.SCULPTURE

        # Painting (Default for "ulei", "canvas", etc, and explicit "pictura")
        # Note: "Painting" is also the default fallback if nothing matches
        
        return cls.ARTIFACT


class ExternalLink(BaseModel):
    """External resource link"""
    source: str = Field(..., description="Source name (DBpedia, Wikidata, etc.)")
    uri: str = Field(..., description="URI of the external resource")
    label: Optional[str] = Field(None, description="Human-readable label")


class Agent(BaseModel):
    """Person or organization"""
    uri: Optional[str] = Field(None, description="URI of the agent")
    name: str = Field(..., description="Name of the agent")
    type: str = Field(..., description="Type: Person or Organization")
    birth_date: Optional[str] = Field(None, description="Birth date")
    death_date: Optional[str] = Field(None, description="Death date")
    nationality: Optional[str] = Field(None, description="Nationality")
    external_links: List[ExternalLink] = Field(default_factory=list)


class Location(BaseModel):
    """Physical location"""
    uri: Optional[str] = Field(None, description="URI of the location")
    name: str = Field(..., description="Name of the location")
    address: Optional[str] = Field(None, description="Physical address")
    city: Optional[str] = Field(None, description="City")
    country: Optional[str] = Field(None, description="Country")
    coordinates: Optional[Dict[str, float]] = Field(None, description="Lat/Long coordinates")
    external_links: List[ExternalLink] = Field(default_factory=list)


class ProvenanceEvent(BaseModel):
    """Provenance event in the artwork's history"""
    uri: Optional[str] = Field(None, description="URI of the event")
    event_type: ProvenanceEventType = Field(..., description="Type of provenance event")
    date: Optional[str] = Field(None, description="Date of the event (ISO 8601)")
    location: Optional[Location] = Field(None, description="Location where event occurred")


class Artwork(BaseModel):
    """Artistic work with provenance"""
    uri: Optional[str] = Field(None, description="URI of the artwork")
    title: str = Field(..., description="Title of the artwork")
    title_ro: Optional[str] = Field(None, description="Romanian title")
    artist: Optional[Agent] = Field(None, description="Creator of the artwork")
    creation_date: Optional[str] = Field(None, description="Date created")
    artwork_type: ArtworkType = Field(..., description="Type of artwork")
    medium: Optional[str] = Field(None, description="Medium/materials used")
    dimensions: Optional[Dict[str, float]] = Field(None, description="Dimensions (height, width, depth in cm)")
    description: Optional[str] = Field(None, description="Description of the artwork")
    description_ro: Optional[str] = Field(None, description="Romanian description")
    current_location: Optional[Location] = Field(None, description="Current location")
    current_owner: Optional[Agent] = Field(None, description="Current owner")
    provenance_chain: List[ProvenanceEvent] = Field(default_factory=list, description="Chronological provenance history")
    external_links: List[ExternalLink] = Field(default_factory=list)
    romanian_heritage: bool = Field(False, description="Part of Romanian heritage")
    getty_classification: Optional[str] = Field(None, description="Getty AAT classification")
    images: List[str] = Field(default_factory=list, description="Image URLs")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ArtworkCreate(BaseModel):
    """Model for creating a new artwork"""
    title: str
    title_ro: Optional[str] = None
    artist_name: Optional[str] = None
    artist_uri: Optional[str] = None
    creation_date: Optional[str] = None
    artwork_type: ArtworkType
    medium: Optional[str] = None
    dimensions: Optional[Dict[str, float]] = None
    description: Optional[str] = None
    description_ro: Optional[str] = None
    current_location_name: Optional[str] = None
    current_owner_name: Optional[str] = None
    romanian_heritage: bool = False
    wikidata_id: Optional[str] = None
    dbpedia_uri: Optional[str] = None


class ArtworkUpdate(BaseModel):
    """Model for updating an artwork"""
    title: Optional[str] = None
    title_ro: Optional[str] = None
    description: Optional[str] = None
    description_ro: Optional[str] = None
    medium: Optional[str] = None
    dimensions: Optional[Dict[str, float]] = None
    current_location_name: Optional[str] = None
    current_owner_name: Optional[str] = None


class SPARQLQuery(BaseModel):
    """SPARQL query request"""
    query: str = Field(..., description="SPARQL query string")
    output_format: str = Field("json", description="Output format: json, xml, csv, tsv")
    reasoning: bool = Field(False, description="Enable OWL reasoning")


class SPARQLResult(BaseModel):
    """SPARQL query result"""
    results: Dict[str, Any]
    query_time_ms: float
    result_count: int


class RecommendationRequest(BaseModel):
    """Request for artwork recommendations"""
    artwork_uri: str = Field(..., description="URI of the artwork to base recommendations on")
    max_results: int = Field(10, description="Maximum number of recommendations")
    criteria: List[str] = Field(
        default_factory=lambda: ["artist", "period", "type", "location"],
        description="Criteria for recommendations"
    )


class Recommendation(BaseModel):
    """Recommended artwork"""
    artwork: Artwork
    similarity_score: float = Field(..., description="Similarity score (0-1)")
    reasons: List[str] = Field(..., description="Reasons for recommendation")


class Statistics(BaseModel):
    """Statistical information about the collection"""
    total_artworks: int
    total_artists: int
    total_locations: int
    total_provenance_events: int
    artworks_by_type: Dict[str, int]
    artworks_by_century: Dict[str, int]
    artworks_by_country: Dict[str, int]
    romanian_heritage_count: int
    most_active_locations: List[Dict[str, Any]]
    most_prolific_artists: List[Dict[str, Any]]
