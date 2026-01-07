"""
Visualization API router
Endpoints for generating visualization data
"""

from fastapi import APIRouter, HTTPException, Request, Query
from typing import Dict, Any, List
import structlog

logger = structlog.get_logger()
router = APIRouter()


@router.get("/statistics/overview")
async def get_overview_statistics(request: Request) -> Dict[str, Any]:
    """Get overview statistics for dashboard"""
    
    rdf_service = request.app.state.rdf_service
    
    query = """
    PREFIX hp: <http://arp-greatteam.org/heritage-provenance#>
    PREFIX dcterms: <http://purl.org/dc/terms/>
    
    SELECT 
        (COUNT(DISTINCT ?artwork) as ?total_artworks)
        (COUNT(DISTINCT ?artist) as ?total_artists)
        (COUNT(DISTINCT ?event) as ?total_events)
        (COUNT(DISTINCT ?location) as ?total_locations)
    WHERE {
        ?artwork a hp:ArtisticWork .
        OPTIONAL { ?artwork dcterms:creator ?artist }
        OPTIONAL { ?artwork hp:hasProvenanceEvent ?event }
        OPTIONAL { ?artwork hp:currentLocation ?location }
    }
    """
    
    try:
        results = rdf_service.execute_sparql(query)
        
        if results['result_count'] > 0:
            stats = results['results']['bindings'][0]
            return {
                "total_artworks": int(stats.get('total_artworks', 0)),
                "total_artists": int(stats.get('total_artists', 0)),
                "total_events": int(stats.get('total_events', 0)),
                "total_locations": int(stats.get('total_locations', 0))
            }
        
        return {
            "total_artworks": 0,
            "total_artists": 0,
            "total_events": 0,
            "total_locations": 0
        }
        
    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/statistics/by-type")
async def get_artworks_by_type(request: Request):
    """Get distribution of artworks by type"""
    
    rdf_service = request.app.state.rdf_service
    
    query = """
    PREFIX hp: <http://arp-greatteam.org/heritage-provenance#>
    
    SELECT ?type (COUNT(?artwork) as ?count)
    WHERE {
        ?artwork a hp:ArtisticWork ;
                 hp:artworkType ?type .
    }
    GROUP BY ?type
    ORDER BY DESC(?count)
    """
    
    try:
        results = rdf_service.execute_sparql(query)
        
        distribution = []
        for binding in results['results']['bindings']:
            distribution.append({
                "type": binding.get('type'),
                "count": int(binding.get('count', 0))
            })
        
        return {
            "chart_type": "pie",
            "title": "Artworks by Type",
            "data": distribution
        }
        
    except Exception as e:
        logger.error(f"Error getting artwork distribution: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/statistics/by-century")
async def get_artworks_by_century(request: Request):
    """Get distribution of artworks by century"""
    
    rdf_service = request.app.state.rdf_service
    
    query = """
    PREFIX hp: <http://arp-greatteam.org/heritage-provenance#>
    PREFIX dcterms: <http://purl.org/dc/terms/>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    
    SELECT 
        (FLOOR(YEAR(?date)/100) as ?century)
        (COUNT(?artwork) as ?count)
    WHERE {
        ?artwork a hp:ArtisticWork ;
                 dcterms:created ?date .
        FILTER(isNumeric(YEAR(?date)))
    }
    GROUP BY ?century
    ORDER BY ?century
    """
    
    try:
        results = rdf_service.execute_sparql(query)
        
        distribution = []
        for binding in results['results']['bindings']:
            century = int(binding.get('century', 0))
            distribution.append({
                "century": f"{century + 1}th Century",
                "count": int(binding.get('count', 0))
            })
        
        return {
            "chart_type": "bar",
            "title": "Artworks by Century",
            "data": distribution
        }
        
    except Exception as e:
        logger.error(f"Error getting artwork distribution by century: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/statistics/top-artists")
async def get_top_artists(request: Request, limit: int = Query(10, ge=1, le=50)):
    """Get top artists by number of artworks"""
    
    rdf_service = request.app.state.rdf_service
    
    query = f"""
    PREFIX hp: <http://arp-greatteam.org/heritage-provenance#>
    PREFIX dcterms: <http://purl.org/dc/terms/>
    PREFIX foaf: <http://xmlns.com/foaf/0.1/>
    
    SELECT ?artist ?artistName (COUNT(?artwork) as ?artwork_count)
    WHERE {{
        ?artwork a hp:ArtisticWork ;
                 dcterms:creator ?artist .
        ?artist foaf:name ?artistName .
    }}
    GROUP BY ?artist ?artistName
    ORDER BY DESC(?artwork_count)
    LIMIT {limit}
    """
    
    try:
        results = rdf_service.execute_sparql(query)
        
        artists = []
        for binding in results['results']['bindings']:
            artists.append({
                "artist_uri": binding.get('artist'),
                "name": binding.get('artistName'),
                "artwork_count": int(binding.get('artwork_count', 0))
            })
        
        return {
            "chart_type": "bar_horizontal",
            "title": f"Top {limit} Artists",
            "data": artists
        }
        
    except Exception as e:
        logger.error(f"Error getting top artists: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/statistics/top-locations")
async def get_top_locations(request: Request, limit: int = Query(10, ge=1, le=50)):
    """Get top locations by number of artworks"""
    
    rdf_service = request.app.state.rdf_service
    
    query = f"""
    PREFIX hp: <http://arp-greatteam.org/heritage-provenance#>
    PREFIX foaf: <http://xmlns.com/foaf/0.1/>
    
    SELECT ?location ?locationName (COUNT(?artwork) as ?artwork_count)
    WHERE {{
        ?artwork a hp:ArtisticWork ;
                 hp:currentLocation ?location .
        ?location foaf:name ?locationName .
    }}
    GROUP BY ?location ?locationName
    ORDER BY DESC(?artwork_count)
    LIMIT {limit}
    """
    
    try:
        results = rdf_service.execute_sparql(query)
        
        locations = []
        for binding in results['results']['bindings']:
            locations.append({
                "location_uri": binding.get('location'),
                "name": binding.get('locationName'),
                "artwork_count": int(binding.get('artwork_count', 0))
            })
        
        return {
            "chart_type": "bar_horizontal",
            "title": f"Top {limit} Locations",
            "data": locations
        }
        
    except Exception as e:
        logger.error(f"Error getting top locations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/network/provenance/{artwork_id}")
async def get_provenance_network(artwork_id: str, request: Request):
    """Get network visualization data for artwork provenance"""
    
    rdf_service = request.app.state.rdf_service
    artwork_uri = f"http://arp-greatteam.org/heritage-provenance/artwork/{artwork_id}"
    
    query = f"""
    PREFIX hp: <http://arp-greatteam.org/heritage-provenance#>
    PREFIX foaf: <http://xmlns.com/foaf/0.1/>
    
    SELECT ?fromAgent ?fromName ?toAgent ?toName ?event ?eventType
    WHERE {{
        <{artwork_uri}> hp:hasProvenanceEvent ?event .
        ?event hp:eventType ?eventType ;
               hp:fromAgent ?fromAgent ;
               hp:toAgent ?toAgent .
        ?fromAgent foaf:name ?fromName .
        ?toAgent foaf:name ?toName .
    }}
    """
    
    try:
        results = rdf_service.execute_sparql(query)
        
        nodes = {}
        edges = []
        
        for binding in results['results']['bindings']:
            from_uri = binding.get('fromAgent')
            to_uri = binding.get('toAgent')
            
            # Add nodes
            if from_uri and from_uri not in nodes:
                nodes[from_uri] = {
                    "id": from_uri,
                    "label": binding.get('fromName'),
                    "type": "agent"
                }
            
            if to_uri and to_uri not in nodes:
                nodes[to_uri] = {
                    "id": to_uri,
                    "label": binding.get('toName'),
                    "type": "agent"
                }
            
            # Add edge
            edges.append({
                "from": from_uri,
                "to": to_uri,
                "label": binding.get('eventType'),
                "event": binding.get('event')
            })
        
        # Add artwork node
        nodes[artwork_uri] = {
            "id": artwork_uri,
            "label": "Artwork",
            "type": "artwork"
        }
        
        return {
            "nodes": list(nodes.values()),
            "edges": edges,
            "layout": "force_directed"
        }
        
    except Exception as e:
        logger.error(f"Error generating provenance network: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/map/locations")
async def get_location_map(request: Request):
    """Get map visualization data for artwork locations"""
    
    rdf_service = request.app.state.rdf_service
    
    query = """
    PREFIX hp: <http://arp-greatteam.org/heritage-provenance#>
    PREFIX dcterms: <http://purl.org/dc/terms/>
    PREFIX geo: <http://www.w3.org/2003/01/geo/wgs84_pos#>
    
    SELECT ?location ?name ?lat ?long (COUNT(?artwork) as ?artwork_count)
    WHERE {
        ?artwork a hp:ArtisticWork ;
                 hp:currentLocation ?location .
        ?location foaf:name ?name .
        OPTIONAL { ?location geo:lat ?lat }
        OPTIONAL { ?location geo:long ?long }
    }
    GROUP BY ?location ?name ?lat ?long
    """
    
    try:
        results = rdf_service.execute_sparql(query)
        
        markers = []
        for binding in results['results']['bindings']:
            if binding.get('lat') and binding.get('long'):
                markers.append({
                    "location_uri": binding.get('location'),
                    "name": binding.get('name'),
                    "latitude": float(binding.get('lat')),
                    "longitude": float(binding.get('long')),
                    "artwork_count": int(binding.get('artwork_count', 0))
                })
        
        return {
            "map_type": "markers",
            "markers": markers,
            "center": {"lat": 45.9432, "lng": 24.9668}  # Romania center
        }
        
    except Exception as e:
        logger.error(f"Error generating location map: {e}")
        raise HTTPException(status_code=500, detail=str(e))
