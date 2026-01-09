"""
Provenance API router
Endpoints for managing provenance events and chains
"""
import structlog
from fastapi import APIRouter,Request

logger = structlog.get_logger()
router = APIRouter()


@router.get("/")
async def list_events(
    request: Request
):
    """List all events with optional filters"""
    
    rdf_service = request.app.state.rdf_service
    
    try:
        events = rdf_service.get_all_events()
        return {
            "count": len(events),
            "events": events
        }
    except Exception as e:
        logger.error(f"Error retrieving events: {e}")
        return {
            "error": "Failed to retrieve events",
            "count": 0,
            "events": []
        }
    
@router.get("/{event_id}")
async def get_event(event_id: str, request: Request):
    """Get a specific provenance event by ID with complete details"""
    
    rdf_service = request.app.state.rdf_service
    event_uri = f"http://arp-greatteam.org/heritage-provenance/event/{event_id}"

    try:
        event = rdf_service.get_event(event_uri)
        
        if event is None:
            return {
                "error": "Event not found",
                "event_id": event_id
            }
        
        return event
        
    except Exception as e:
        logger.error(f"Error retrieving event {event_id}: {e}")
        return {
            "error": "Failed to retrieve event",
            "event_id": event_id
        }

@router.get("/{artwork_id}/chain")
async def get_provenance_chain(artwork_id: str, request: Request):
    """Get complete provenance chain for an artwork (all events associated with it)"""
    
    rdf_service = request.app.state.rdf_service
    artwork_uri = f"http://arp-greatteam.org/heritage-provenance/artwork/{artwork_id}"

    rdf_service = request.app.state.rdf_service
    
    try:
        chain = rdf_service.get_provenance_chain(artwork_uri)
        return {
            "count": len(chain),
            "chain": chain
        }
    except Exception as e:
        logger.error(f"Error retrieving events: {e}")
        return {
            "error": "Failed to retrieve events",
            "count": 0,
            "chain": []
        }