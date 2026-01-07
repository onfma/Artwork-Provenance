"""
Provenance API router
Endpoints for managing provenance events and chains
"""
import structlog
from typing import List, Optional
from fastapi import APIRouter,Request
from app.models import ProvenanceEvent

logger = structlog.get_logger()
router = APIRouter()


@router.get("/events")
async def list_events(
    request: Request
):
    """List all events with optional filters"""
    
    rdf_service = request.app.state.rdf_service

@router.get("/{artwork_id}/chain", response_model=List[ProvenanceEvent])
async def get_provenance_chain(artwork_id: str, request: Request):
    """Get complete provenance chain for an artwork (all events associated with it)"""
    
    rdf_service = request.app.state.rdf_service
    artwork_uri = f"http://arp-greatteam.org/heritage-provenance/artwork/{artwork_id}"

@router.get("/events/search")
async def search_events(
    request: Request,
    artist_id: Optional[str] = None,
    location: Optional[str] = None
):
    """Search provenance events with filters"""
    
    rdf_service = request.app.state.rdf_service