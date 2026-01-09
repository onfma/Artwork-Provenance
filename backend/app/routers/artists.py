"""
Artists API router
Endpoints for managing artists
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
async def list_artists(
    request: Request
):
    """List all artists with optional filters"""
    
    rdf_service = request.app.state.rdf_service
    
    try:
        artists = rdf_service.get_all_artists()
        return {
            "count": len(artists),
            "artists": artists
        }
    except Exception as e:
        logger.error(f"Error retrieving artists: {e}")
        return {
            "error": "Failed to retrieve artists",
            "count": 0,
            "artists": []
        }

@router.get("/{artist_id}")
async def get_artist(artist_id: str, request: Request):
    """Get a specific artist by ID with complete details"""
    
    rdf_service = request.app.state.rdf_service
    artist_uri = f"http://arp-greatteam.org/heritage-provenance/artist/{artist_id}"

    try:
        artist = rdf_service.get_artist(artist_uri)
        
        if artist is None:
            return {
                "error": "Artist not found",
                "artist_id": artist_id
            }
        
        return artist
        
    except Exception as e:
        logger.error(f"Error retrieving artist {artist_id}: {e}")
        return {
            "error": "Failed to retrieve artist",
            "artist_id": artist_id
        }


@router.get("/{artist_id}/enrich")
async def enrich_artist(artist_id: str, source: str = Query(..., regex="^(dbpedia|wikidata|getty)$")):
    """Enrich artist data from external sources"""
    
    artist_uri = f"http://arp-greatteam.org/heritage-provenance/artist/{artist_id}"
    
    if source == "dbpedia":
        # Search DBpedia for additional information
        result = await dbpedia.get_artist_info(artist_id)
        return {"source": "dbpedia", "data": result}
    
    elif source == "wikidata":
        # Get Wikidata information
        result = await wikidata.get_artist_info(artist_id)
        return {"source": "wikidata", "data": result}
    
    elif source == "getty":
        # Get Getty vocabulary information
        result = await getty.search_art_term(artist_id)
        return {"source": "getty", "data": result}
    
    return {"message": "Enrichment complete"}
