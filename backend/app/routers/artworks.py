"""
Artworks API router
Endpoints for managing artworks
"""
import structlog
from typing import Dict, Any, Optional
from fastapi import APIRouter, Query, Request
from app.services import wikidata_parser_for_artwork
from app.services.external_data import WikidataService

logger = structlog.get_logger()
router = APIRouter()
wikidata = WikidataService()


@router.get("/")
async def list_artworks(
    request: Request,
    type_id: str = Query(None, description="Filter by type ID"),
    material_id: str = Query(None, description="Filter by material ID"),
    subject_id: str = Query(None, description="Filter by subject ID"),
    artist_id: str = Query(None, description="Filter by artist ID"),
    location_id: str = Query(None, description="Filter by location ID"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of results")
):
    """List all artworks with optional filters"""
    
    rdf_service = request.app.state.rdf_service
    
    try:
        filters = {}
        if type_id and type_id != '':
            filters['type_uri'] = f"http://arp-greatteam.org/heritage-provenance/attributes/{type_id}"
        if material_id and material_id != '':
            filters['material_uri'] = f"http://arp-greatteam.org/heritage-provenance/attributes/{material_id}"
        if subject_id and subject_id != '':
            filters['subject_uri'] = f"http://arp-greatteam.org/heritage-provenance/attributes/{subject_id}"
        if artist_id and artist_id != '':
            filters['artist_uri'] = f"http://arp-greatteam.org/heritage-provenance/artist/{artist_id}"
        if location_id and location_id != '':
            filters['location_uri'] = f"http://arp-greatteam.org/heritage-provenance/location/{location_id}"
        
        artworks = rdf_service.get_all_artworks(filters=filters, limit=limit)
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
        else:
            artwork = await wikidata_enrichment(artwork)
        
        return artwork
        
    except Exception as e:
        logger.error(f"Error retrieving artwork {artwork_id}: {e}")
        return {
            "error": "Failed to retrieve artwork",
            "artwork_id": artwork_id
        }
    


async def wikidata_enrichment(artwork: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Helper function to enrich artwork data with Wikidata"""
    
    if artwork.get('title') is None or artwork.get('title') == '':
        return artwork
    
    try:
        wikidata_response = {}
        result = await wikidata.search_wikidata(artwork.get('title'))
        
        if result and 'search' in result and len(result['search']) > 0:
            wikidata_id = result['search'][0]['id']
            wikidata_info = await wikidata.get_entity(wikidata_id)
            
            wikidata_response['wikidata_id'] = wikidata_id
            wikidata_response['data'] = wikidata_parser_for_artwork(wikidata_info)
        else:
            wikidata_response['message'] = 'No results found'
    except Exception as e:
        logger.error(f"Error enriching artwork {artwork.get('id')} with Wikidata: {e}")

    
    artwork['wikidata_enrichment'] = wikidata_response
    return artwork