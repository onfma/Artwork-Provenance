"""
SPARQL endpoint router
Provides SPARQL query interface
"""

from fastapi import APIRouter, HTTPException, Request, Query
from fastapi.responses import Response
from typing import Optional
import structlog

from app.models import SPARQLQuery, SPARQLResult

logger = structlog.get_logger()
router = APIRouter()


@router.post("/query", response_model=SPARQLResult)
async def sparql_query(sparql_request: SPARQLQuery, request: Request):
    """Execute SPARQL query against the RDF store"""
    
    rdf_service = request.app.state.rdf_service
    
    try:
        results = rdf_service.execute_sparql(
            sparql_request.query,
            endpoint="local",
            output_format=sparql_request.output_format
        )
        
        return SPARQLResult(
            results=results['results'],
            query_time_ms=results['query_time_ms'],
            result_count=results['result_count']
        )
        
    except Exception as e:
        logger.error(f"Error executing SPARQL query: {e}")
        raise HTTPException(status_code=400, detail=f"Query error: {str(e)}")


@router.get("/query")
async def sparql_query_get(
    request: Request,
    query: str = Query(..., description="SPARQL query string"),
    format: str = Query("json", regex="^(json|xml|csv|tsv)$")
):
    """Execute SPARQL query via GET (standard SPARQL protocol)"""
    
    rdf_service = request.app.state.rdf_service
    
    try:
        results = rdf_service.execute_sparql(query, endpoint="local", output_format=format)
        
        # Return appropriate content type
        content_types = {
            "json": "application/sparql-results+json",
            "xml": "application/sparql-results+xml",
            "csv": "text/csv",
            "tsv": "text/tab-separated-values"
        }
        
        return Response(
            content=str(results),
            media_type=content_types.get(format, "application/json")
        )
        
    except Exception as e:
        logger.error(f"Error executing SPARQL query: {e}")
        raise HTTPException(status_code=400, detail=f"Query error: {str(e)}")


@router.get("/statistics")
async def get_statistics(request: Request):
    """Get statistical information via SPARQL"""
    
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
        return results
    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/federated/dbpedia")
async def query_dbpedia(query: str = Query(..., description="SPARQL query for DBpedia")):
    """Execute federated query against DBpedia"""
    
    from app.services.rdf_store import RDFStoreService
    rdf_service = RDFStoreService()
    
    try:
        results = rdf_service.execute_sparql(query, endpoint="dbpedia")
        return results
    except Exception as e:
        logger.error(f"Error querying DBpedia: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/federated/wikidata")
async def query_wikidata(query: str = Query(..., description="SPARQL query for Wikidata")):
    """Execute federated query against Wikidata"""
    
    from app.services.rdf_store import RDFStoreService
    rdf_service = RDFStoreService()
    
    try:
        results = rdf_service.execute_sparql(query, endpoint="wikidata")
        return results
    except Exception as e:
        logger.error(f"Error querying Wikidata: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/federated/getty")
async def query_getty(query: str = Query(..., description="SPARQL query for Getty vocabularies")):
    """Execute federated query against Getty vocabularies"""
    
    from app.services.rdf_store import RDFStoreService
    rdf_service = RDFStoreService()
    
    try:
        results = rdf_service.execute_sparql(query, endpoint="getty")
        return results
    except Exception as e:
        logger.error(f"Error querying Getty: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/examples")
async def get_example_queries():
    """Get example SPARQL queries"""
    
    examples = {
        "list_all_artworks": """
PREFIX hp: <http://arp-greatteam.org/heritage-provenance#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?artwork ?title ?artist ?date
WHERE {
    ?artwork a hp:ArtisticWork ;
             dcterms:title ?title .
    OPTIONAL { ?artwork dcterms:creator ?artist }
    OPTIONAL { ?artwork dcterms:created ?date }
}
LIMIT 10
        """,
        "artworks_by_artist": """
PREFIX hp: <http://arp-greatteam.org/heritage-provenance#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>

SELECT ?artwork ?title ?date
WHERE {
    ?artwork a hp:ArtisticWork ;
             dcterms:title ?title ;
             dcterms:creator ?artist .
    ?artist foaf:name "Artist Name Here" .
    OPTIONAL { ?artwork dcterms:created ?date }
}
        """,
        "provenance_chain": """
PREFIX hp: <http://arp-greatteam.org/heritage-provenance#>
PREFIX prov: <http://www.w3.org/ns/prov#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?artwork ?title ?event ?eventType ?date ?fromAgent ?toAgent
WHERE {
    ?artwork a hp:ArtisticWork ;
             dcterms:title ?title ;
             hp:hasProvenanceEvent ?event .
    ?event hp:eventType ?eventType ;
           dcterms:date ?date .
    OPTIONAL { ?event hp:fromAgent ?fromAgent }
    OPTIONAL { ?event hp:toAgent ?toAgent }
}
ORDER BY ?date
        """,
        "romanian_heritage": """
PREFIX hp: <http://arp-greatteam.org/heritage-provenance#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?artwork ?title ?artist ?location
WHERE {
    ?artwork a hp:ArtisticWork ;
             dcterms:title ?title ;
             hp:romanianHeritage true .
    OPTIONAL { ?artwork dcterms:creator ?artist }
    OPTIONAL { ?artwork hp:currentLocation ?location }
}
        """,
        "artworks_by_century": """
PREFIX hp: <http://arp-greatteam.org/heritage-provenance#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

SELECT ?artwork ?title ?date
WHERE {
    ?artwork a hp:ArtisticWork ;
             dcterms:title ?title ;
             dcterms:created ?date .
    FILTER(YEAR(?date) >= 1800 && YEAR(?date) < 1900)
}
        """
    }
    
    return {
        "description": "Example SPARQL queries for the Heritage Provenance System",
        "examples": examples
    }
