"""
Artworks API router
Endpoints for managing artworks
"""
import structlog
from fastapi import APIRouter, HTTPException, Query, Request
from app.services.external_data import DBpediaService, WikidataService, GettyService

logger = structlog.get_logger()
router = APIRouter()

dbpedia = DBpediaService()
wikidata = WikidataService()
getty = GettyService()


@router.get("/")
async def list_artworks(
    request: Request
):
    """List all artworks with optional filters"""
    
    rdf_service = request.app.state.rdf_service
    

@router.get("/{artwork_id}")
async def get_artwork(artwork_id: str, request: Request):
    """Get a specific artwork by ID with complete details"""
    
    rdf_service = request.app.state.rdf_service
    artwork_uri = f"http://arp-greatteam.org/heritage-provenance/artwork/{artwork_id}"


@router.get("/{artwork_id}/enrich")
async def enrich_artwork(artwork_id: str, source: str = Query(..., regex="^(dbpedia|wikidata|getty)$")):
    """Enrich artwork data from external sources"""
    
    artwork_uri = f"http://arp-greatteam.org/heritage-provenance/artwork/{artwork_id}"