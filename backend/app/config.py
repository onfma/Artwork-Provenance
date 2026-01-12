"""
Configuration settings for Heritage Provenance System
"""

from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "Heritage Provenance System"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8080",
        "http://127.0.0.1:3000",
        "https://artwork-provenance.vercel.app"
    ]
    
    # RDF Store (Virtuoso or GraphDB)
    RDF_STORE_TYPE: str = "rdflib"  # Options: virtuoso, graphdb, rdflib
    RDF_STORE_URL: str = "http://localhost:8890/sparql"
    RDF_STORE_UPDATE_URL: str = "http://localhost:8890/sparql-auth"
    
    # Triple Store Authentication
    VIRTUOSO_USER: str = "dba"
    VIRTUOSO_PASSWORD: str = "dba"
    
    # Named Graph URIs
    BASE_GRAPH_URI: str = "http://arp-greatteam.org/heritage-provenance"
    ARTWORKS_GRAPH: str = "http://arp-greatteam.org/heritage-provenance/artworks"
    ARTISTS_GRAPH: str = "http://arp-greatteam.org/heritage-provenance/artists"
    PROVENANCE_GRAPH: str = "http://arp-greatteam.org/heritage-provenance/provenance"
    ROMANIAN_GRAPH: str = "http://arp-greatteam.org/heritage-provenance/romanian"
    
    # External Data Sources
    DBPEDIA_SPARQL: str = "https://dbpedia.org/sparql"
    WIKIDATA_SPARQL: str = "https://query.wikidata.org/sparql"
    EUROPEANA_API_KEY: str = os.getenv("EUROPEANA_API_KEY", "")
    EUROPEANA_API_URL: str = "https://api.europeana.eu/record/v2"
    
    # Getty Vocabularies
    GETTY_AAT_SPARQL: str = "http://vocab.getty.edu/sparql"
    GETTY_ULAN_SPARQL: str = "http://vocab.getty.edu/sparql"
    GETTY_TGN_SPARQL: str = "http://vocab.getty.edu/sparql"
    
    # Romanian Heritage
    ROMANIAN_HERITAGE_API: str = "http://patrimoniu.ro/api"
    
    # MongoDB (for caching and analytics)
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB: str = "artwork_provenance"
    
    # Redis (for caching)
    REDIS_URL: str = "redis://localhost:6379"
    REDIS_CACHE_TTL: int = 3600  # 1 hour
    
    # Recommendation Engine
    SIMILARITY_THRESHOLD: float = 0.7
    MAX_RECOMMENDATIONS: int = 10
    
    # Pagination
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100
    
    # Ontology Files
    CIDOC_CRM_FILE: str = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ontology", "cidoc_crm.owl")
    PROV_FILE: str = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ontology", "prov-o.owl")
    
    # Data Directory
    DATA_DIR: str = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
