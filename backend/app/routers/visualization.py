"""
Visualization API router
Endpoints for generating visualization data
"""

import structlog
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Request, Query

logger = structlog.get_logger()
router = APIRouter()


@router.get("/statistics/overview")
async def get_overview_statistics(request: Request) -> Dict[str, Any]:
    """Get overview statistics for dashboard"""
    
    rdf_service = request.app.state.rdf_service
    
    query = """
    PREFIX prov: <http://www.w3.org/ns/prov#>

    SELECT
    ?total_artworks
    ?total_artists
    ?total_events
    ?total_locations
    WHERE {
    {
        SELECT (COUNT(DISTINCT ?artwork) AS ?total_artworks)
        WHERE {
        ?artwork a prov:Entity .
        }
    }
    {
        SELECT (COUNT(DISTINCT ?artist) AS ?total_artists)
        WHERE {
        ?artist a prov:Agent .
        }
    }
    {
        SELECT (COUNT(DISTINCT ?event) AS ?total_events)
        WHERE {
        ?event a prov:Activity .
        }
    }
    {
        SELECT (COUNT(DISTINCT ?location) AS ?total_locations)
        WHERE {
        ?location a prov:Location .
        }
    }
    }
    """
    
    try:
        results = rdf_service.execute_sparql(query)
        
        stats = {
            "total_artworks": 0,
            "total_artists": 0,
            "total_events": 0,
            "total_locations": 0
        }
        
        if results:
            for row in results:
                stats["total_artworks"] = int(row.total_artworks) if row.total_artworks else 0
                stats["total_artists"] = int(row.total_artists) if row.total_artists else 0
                stats["total_events"] = int(row.total_events) if row.total_events else 0
                stats["total_locations"] = int(row.total_locations) if row.total_locations else 0
                break 
        
        return stats
        
    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/statistics/by-type")
async def get_artworks_by_type(request: Request):
    """Get distribution of artworks by type"""
    
    rdf_service = request.app.state.rdf_service
    
    query = """
    PREFIX prov: <http://www.w3.org/ns/prov#>
    PREFIX crm:  <http://www.cidoc-crm.org/cidoc-crm/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

    SELECT ?typeLabel (COUNT(?artwork) AS ?artwork_count)
    WHERE {
        ?artwork a prov:Entity ;
                crm:P2_has_type ?type .

        ?type rdfs:label ?typeLabel .
    }
    GROUP BY ?type ?typeLabel
    ORDER BY DESC(?artwork_count)
    """
    
    try:
        results = rdf_service.execute_sparql(query)
        
        distribution = []
        for row in results:
            distribution.append({
                "type": str(row.typeLabel),
                "count": int(row.artwork_count)
            })
        
        return {
            "chart_type": "pie",
            "title": "Artworks by Type",
            "data": distribution
        }
        
    except Exception as e:
        logger.error(f"Error getting artwork distribution: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/statistics/top-artists")
async def get_top_artists(request: Request, limit: int = Query(10, ge=1, le=50)):
    """Get top artists by number of artworks"""
    
    rdf_service = request.app.state.rdf_service
    
    query = f"""
    PREFIX prov: <http://www.w3.org/ns/prov#>
    PREFIX crm:  <http://www.cidoc-crm.org/cidoc-crm/>
    PREFIX foaf: <http://xmlns.com/foaf/0.1/>
    
    SELECT ?artist ?artistName (COUNT(?artwork) as ?artwork_count)
    WHERE {{
        ?event a crm:E12_Production ;
               crm:P14_carried_out_by ?artist ;
               crm:P108_has_produced ?artwork .
        ?artist foaf:name ?artistName .
        FILTER(?artistName != "Unknown Artist")
    }}
    GROUP BY ?artist ?artistName
    ORDER BY DESC(?artwork_count)
    LIMIT {limit}
    """
    
    try:
        results = rdf_service.execute_sparql(query)
        
        artists = []
        for row in results:
            artists.append({
                "artist_uri": str(row.artist),
                "name": str(row.artistName),
                "artwork_count": int(row.artwork_count)
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
    PREFIX prov: <http://www.w3.org/ns/prov#>
    PREFIX crm:  <http://www.cidoc-crm.org/cidoc-crm/>
    PREFIX foaf: <http://xmlns.com/foaf/0.1/>
    
    SELECT ?location ?locationName (COUNT(?artwork) as ?artwork_count)
    WHERE {{
        ?event a crm:E12_Production ;
               crm:P7_took_place_at ?location ;
               crm:P108_has_produced ?artwork .
        ?location foaf:name ?locationName .
        FILTER(?locationName != "Unknown Location")
    }}
    GROUP BY ?location ?locationName
    ORDER BY DESC(?artwork_count)
    LIMIT {limit}
    """
    
    try:
        results = rdf_service.execute_sparql(query)
        
        locations = []
        for row in results:
            locations.append({
                "location_uri": str(row.location),
                "name": str(row.locationName),
                "artwork_count": int(row.artwork_count)
            })
        
        return {
            "chart_type": "bar_horizontal",
            "title": f"Top {limit} Locations",
            "data": locations
        }
        
    except Exception as e:
        logger.error(f"Error getting top locations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# @router.get("/map/locations")
# async def get_location_map(request: Request):
#     """Get map visualization data for artwork locations"""
    
#     rdf_service = request.app.state.rdf_service
    
#     query = """
#     PREFIX hp: <http://arp-greatteam.org/heritage-provenance#>
#     PREFIX dcterms: <http://purl.org/dc/terms/>
#     PREFIX geo: <http://www.w3.org/2003/01/geo/wgs84_pos#>
    
#     SELECT ?location ?name ?lat ?long (COUNT(?artwork) as ?artwork_count)
#     WHERE {
#         ?artwork a hp:ArtisticWork ;
#                  hp:currentLocation ?location .
#         ?location foaf:name ?name .
#         OPTIONAL { ?location geo:lat ?lat }
#         OPTIONAL { ?location geo:long ?long }
#     }
#     GROUP BY ?location ?name ?lat ?long
#     """
    
#     try:
#         results = rdf_service.execute_sparql(query)
        
#         markers = []
#         for binding in results['results']['bindings']:
#             if binding.get('lat') and binding.get('long'):
#                 markers.append({
#                     "location_uri": binding.get('location'),
#                     "name": binding.get('name'),
#                     "latitude": float(binding.get('lat')),
#                     "longitude": float(binding.get('long')),
#                     "artwork_count": int(binding.get('artwork_count', 0))
#                 })
        
#         return {
#             "map_type": "markers",
#             "markers": markers,
#             "center": {"lat": 45.9432, "lng": 24.9668}  # Romania center
#         }
        
#     except Exception as e:
#         logger.error(f"Error generating location map: {e}")
#         raise HTTPException(status_code=500, detail=str(e))
