"""
SPARQL endpoint router
Provides SPARQL query interface
"""
import time
import structlog
from app.models import SPARQLQuery, SPARQLResult
from fastapi import APIRouter, HTTPException, Request

logger = structlog.get_logger()
router = APIRouter()


@router.post("/query")
async def sparql_query(sparql_request: SPARQLQuery, request: Request):
    """Execute SPARQL query against the RDF store"""
    
    rdf_service = request.app.state.rdf_service
    
    try:
        start_time = time.time()
        results = rdf_service.execute_sparql(sparql_request.query)
        query_time_ms = (time.time() - start_time) * 1000

        formatted_results = []
        for row in results:
            formatted_row = {}
            for var in results.vars:
                value = row[var]
                formatted_row[str(var)] = str(value) if value is not None else None
            formatted_results.append(formatted_row)
        
        return SPARQLResult(
            results={"bindings": formatted_results},
            result_count=len(formatted_results),
            query_time_ms=query_time_ms
        )
        
    except Exception as e:
        logger.error(f"Error executing SPARQL query: {e}")
        raise HTTPException(status_code=400, detail=f"Query error: {str(e)}")

