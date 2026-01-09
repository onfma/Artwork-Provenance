"""
Locations API router
Endpoints for managing locations
"""
import structlog
from fastapi import APIRouter, Query, Request
from app.services.external_data import WikidataService

logger = structlog.get_logger()
router = APIRouter()
wikidata = WikidataService()



@router.get("/")
async def list_locations(
    request: Request
):
    """List all locations with optional filters"""
    
    rdf_service = request.app.state.rdf_service
    
    try:
        locations = rdf_service.get_all_locations()
        return {
            "count": len(locations),
            "locations": locations
        }
    except Exception as e:
        logger.error(f"Error retrieving locations: {e}")
        return {
            "error": "Failed to retrieve locations",
            "count": 0,
            "locations": []
        }
    

@router.get("/{location_id}")
async def get_location(location_id: str, request: Request):
    """Get a specific location by ID with complete details"""
    
    rdf_service = request.app.state.rdf_service
    location_uri = f"http://arp-greatteam.org/heritage-provenance/location/{location_id}"

    try:
        location = rdf_service.get_location(location_uri)
        
        if location is None:
            return {
                "error": "Location not found",
                "location_id": location_id
            }
        
        return location
        
    except Exception as e:
        logger.error(f"Error retrieving location {location_id}: {e}")
        return {
            "error": "Failed to retrieve location",
            "location_id": location_id
        }


