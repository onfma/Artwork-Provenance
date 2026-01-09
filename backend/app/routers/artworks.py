"""
Artworks API router
Endpoints for managing artworks
"""
import structlog
from fastapi import APIRouter, Query, Request
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
    
    try:
        artworks = rdf_service.get_all_artworks()
        return {
            "count": len(artworks),
            "artworks": artworks
        }
    except Exception as e:
        logger.error(f"Error retrieving artworks: {e}")
        return {
            "error": "Failed to retrieve artworks",
            "count": 0,
            "artworks": []
        }

@router.get("/{artwork_id}")
async def get_artwork(artwork_id: str, request: Request):
    """Get a specific artwork by ID with complete details"""
    
    rdf_service = request.app.state.rdf_service
    artwork_uri = f"http://arp-greatteam.org/heritage-provenance/artwork/{artwork_id}"
    
    try:
        artwork = rdf_service.get_artwork(artwork_uri)
        
        if artwork is None:
            return {
                "error": "Artwork not found",
                "artwork_id": artwork_id
            }
        
        return artwork
        
    except Exception as e:
        logger.error(f"Error retrieving artwork {artwork_id}: {e}")
        return {
            "error": "Failed to retrieve artwork",
            "artwork_id": artwork_id
        }


@router.get("/{artwork_id}/enrich")
async def enrich_artwork(artwork_id: str, source: str = Query(..., regex="^(dbpedia|wikidata|getty)$")):
    """Enrich artwork data from external sources"""
    
    artwork_uri = f"http://arp-greatteam.org/heritage-provenance/artwork/{artwork_id}"