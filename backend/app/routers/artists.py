"""
Artists API router
Endpoints for managing artists
"""

import structlog
from typing import Dict, Any, Optional
from fastapi import APIRouter, Query, Request
from app.services import wikidata_parser_for_artist
from app.services.external_data import WikidataService, GettyService

logger = structlog.get_logger()
router = APIRouter()
wikidata = WikidataService()
getty = GettyService()


@router.get("/")
async def list_artists(
    request: Request,
    location_id: str = Query(None, description="Filter by location ID where they created artworks"),
    limit: int = Query(100, ge=1, description="Maximum number of results")
):
    """List all artists with optional filters"""
    
    rdf_service = request.app.state.rdf_service
    
    try:
        filters = {}
        if location_id and location_id != '':
            filters['location_uri'] = f"http://arp-greatteam.org/heritage-provenance/location/{location_id}"
        
        artists = rdf_service.get_all_artists(filters=filters, limit=limit)
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
        else:
            artist = await wikidata_enrichment(artist)
            
        return artist
        
    except Exception as e:
        logger.error(f"Error retrieving artist {artist_id}: {e}")
        return {
            "error": "Failed to retrieve artist",
            "artist_id": artist_id
        }

@router.get("/getty/{artist_getty_id}")
async def get_artist(artist_getty_id: str, request: Request):
    """Get a specific artist by GETTY ID with complete details"""
    
    rdf_service = request.app.state.rdf_service

    try:
        artists = rdf_service.get_artist_by_getty_id(artist_getty_id)

        for artist in artists:
            if artist.get('name') is None:
                temp_artist = {
                    'id': '',
                    'name': None,
                    'wikidata_id': getty.get_wikidata_id(artist_getty_id),
                    "getty_link": artist_getty_id
                }
                artist = temp_artist
            artist = await wikidata_enrichment(artist)  
        
        return artists
        
    except Exception as e:
        logger.error(f"Error retrieving artist {artist_getty_id}: {e}")
        return {
            "error": "Failed to retrieve artist",
            "artist_getty_link": artist_getty_id
        }

async def wikidata_enrichment(artist: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Helper function to enrich artist data with Wikidata"""
    
    try:
        wikidata_response = {}
        
        if artist.get('name') is None:
            result = await wikidata.search_wikidata(artist.get('wikidata_id'))
        else:
            result = await wikidata.search_wikidata(artist.get('name'))
        
        if result and 'search' in result and len(result['search']) > 0:
            wikidata_id = result['search'][0]['id']
            wikidata_info = await wikidata.get_entity(wikidata_id)
            
            wikidata_response['wikidata_id'] = wikidata_id
            wikidata_response['data'] = wikidata_parser_for_artist(wikidata_info)
        else:
            wikidata_response['message'] = 'No results found'
    except Exception as e:
        logger.error(f"Error enriching artist {artist.get('id')} with Wikidata: {e}")

    
    artist['wikidata_enrichment'] = wikidata_response
    return artist

