"""
Locations API router
Endpoints for managing locations
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
async def list_locations(
    request: Request
):
    """List all locations with optional filters"""
    
    rdf_service = request.app.state.rdf_service
    

@router.get("/{location_id}")
async def get_location(location_id: str, request: Request):
    """Get a specific location by ID with complete details"""
    
    rdf_service = request.app.state.rdf_service
    location_uri = f"http://arp-greatteam.org/heritage-provenance/location/{location_id}"


@router.get("/{location_id}/enrich")
async def enrich_location(location_id: str, source: str = Query(..., regex="^(dbpedia|wikidata|getty)$")):
    """Enrich location data from external sources"""
    
    location_uri = f"http://arp-greatteam.org/heritage-provenance/location/{location_id}"
    
    if source == "dbpedia":
        # Search DBpedia for additional information
        result = await dbpedia.get_location_info(location_id)
        return {"source": "dbpedia", "data": result}
    
    elif source == "wikidata":
        # Get Wikidata information
        result = await wikidata.get_location_info(location_id)
        return {"source": "wikidata", "data": result}
    
    elif source == "getty":
        # Get Getty vocabulary information
        result = await getty.search_art_term(location_id)
        return {"source": "getty", "data": result}
    
    return {"message": "Enrichment complete"}
