"""
Visualization API router
Endpoints for generating visualization data
"""

import structlog
from typing import Dict, Any
from app.services.external_data import GettyService
from fastapi import APIRouter, HTTPException, Request, Query

logger = structlog.get_logger()
router = APIRouter()
getty = GettyService()


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
async def get_artworks_by_type(request: Request, limit: int = Query(10, ge=1, le=50)):
    """Get distribution of artworks by type"""
    
    rdf_service = request.app.state.rdf_service
    
    query = f"""
    PREFIX prov: <http://www.w3.org/ns/prov#>
    PREFIX crm:  <http://www.cidoc-crm.org/cidoc-crm/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

    SELECT ?typeLabel (COUNT(?artwork) AS ?artwork_count)
    WHERE {{
        ?artwork a prov:Entity ;
                crm:P2_has_type ?type .

        ?type rdfs:label ?typeLabel .
    }}
    GROUP BY ?type ?typeLabel
    ORDER BY DESC(?artwork_count)
    LIMIT {limit}
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

@router.get("/statistics/by-material")
async def get_artworks_by_material(request: Request, limit: int = Query(10, ge=1, le=50)):
    """Get distribution of artworks by material"""
    
    rdf_service = request.app.state.rdf_service
    
    query = f"""
    PREFIX prov: <http://www.w3.org/ns/prov#>
    PREFIX crm:  <http://www.cidoc-crm.org/cidoc-crm/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

    SELECT ?materialLabel (COUNT(?artwork) AS ?artwork_count)
    WHERE {{
        ?artwork a prov:Entity ;
                crm:P45_consists_of ?material .

        ?material rdfs:label ?materialLabel .
        FILTER(?materialLabel != "Unknown")
    }}
    GROUP BY ?material ?materialLabel
    ORDER BY DESC(?artwork_count)
    LIMIT {limit}
    """
    
    try:
        results = rdf_service.execute_sparql(query)
        
        distribution = []
        for row in results:
            distribution.append({
                "material": str(row.materialLabel),
                "count": int(row.artwork_count)
            })
        
        return {
            "chart_type": "pie",
            "title": "Artworks by Material",
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

@router.get("/map/locations")
async def get_location_map(request: Request):
    """Get map visualization data for artwork locations"""
    
    rdf_service = request.app.state.rdf_service

    continents = {
        "Europe": {
            "coords": {"lat": 54.5260, "lng": 15.2551},
            "artworks_count": 0
        },
        "Asia": {
            "coords": {"lat": 34.0479, "lng": 100.6197},
            "artworks_count": 0
        },
        "Africa": {
            "coords": {"lat": -8.7832, "lng": 34.5085},
            "artworks_count": 0
        },
        "North America": {
            "coords": {"lat": 54.5260, "lng": -105.2551},
            "artworks_count": 0
        },
        "South America": {
            "coords": {"lat": -8.7832, "lng": -55.4915},
            "artworks_count": 0
        },
        "Australia": {
            "coords": {"lat": -25.2744, "lng": 133.7751},
            "artworks_count": 0
        }
    }
    
    query = """
    PREFIX prov: <http://www.w3.org/ns/prov#>
    PREFIX crm:  <http://www.cidoc-crm.org/cidoc-crm/>
    PREFIX owl:  <http://www.w3.org/2002/07/owl#>
    
    SELECT ?location ?locationLabel ?locationTGN (COUNT(?artwork) AS ?artworks_count)
    WHERE {
        ?location a prov:Location ;
                  owl:sameAs ?locationTGN .
        ?location rdfs:label ?locationLabel .
        FILTER(CONTAINS(STR(?locationTGN), "tgn"))
        
        ?event crm:P7_took_place_at ?location ;
               crm:P108_has_produced ?artwork .
    }
    GROUP BY ?location ?locationLabel ?locationTGN
    ORDER BY DESC(?artworks_count)
    LIMIT 1
    """
    
    try:
        results = rdf_service.execute_sparql(query)
        
        for row in results:
            location_label = str(row.locationLabel)
            location_getty = str(row.locationTGN)
            artworks_count = int(row.artworks_count)

            logger.debug(f"Processing location: {location_label}, {location_getty} with {artworks_count} artworks")
            
            broader_location = await getty.get_location_parent(location_getty)
            if broader_location:
                for continent in continents:
                    if continent in broader_location:
                        continents[continent]["artworks_count"] += artworks_count
                        break

        return {
            "map_type": "markers",
            "markers": continents,
            "center": {"lat": 45.9432, "lng": 24.9668}  # Romania center
        }
        
    except Exception as e:
        logger.error(f"Error generating location map: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/statistics/network/artists/{artist_id}")
async def get_network_artists(request: Request, artist_id: str):
    """ Get network of artists connected to a specific artist by student_of/teacher_of relationships """
    
    rdf_service = request.app.state.rdf_service
    artist_uri = f"http://arp-greatteam.org/heritage-provenance/artist/{artist_id}"

    try:
        artist_data = rdf_service.get_artist(artist_uri)

        if artist_data is None or artist_data.get('getty') is None:
            return {"message": "No Getty link available for this artist."}
        
        network = {}
        
        network = await getty.get_artist_network(artist_data['getty'])
        if network == {}:
            return {"message": "No network data available from Getty for this artist."}
        network["nodes"].append({
            "id": artist_data['getty'].split("/")[-1],
            "uri": artist_data['getty'],
            "name": artist_data['name']
        })
        return network 
        
    
    except Exception as e:
        logger.error(f"Error retrieving artist network for {artist_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
