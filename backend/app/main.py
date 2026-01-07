"""
Main FastAPI application for Heritage Provenance System
Provides REST API for artwork provenance management with SPARQL endpoint
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import structlog

from app.routers import artworks, provenance, sparql, recommendations, visualization, data_import
from app.config import settings
from app.services.rdf_store import RDFStoreService

logger = structlog.get_logger()

app = FastAPI(
    title="Heritage Provenance System",
    description="API for modeling and managing artwork provenance with integration to DBpedia, Wikidata, Getty vocabularies, and Romanian heritage",
    version="1.0.0",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(artworks.router, prefix="/api/artworks", tags=["Artworks"])
app.include_router(provenance.router, prefix="/api/provenance", tags=["Provenance"])
app.include_router(sparql.router, prefix="/api/sparql", tags=["SPARQL"])
app.include_router(recommendations.router, prefix="/api/recommendations", tags=["Recommendations"])
app.include_router(visualization.router, prefix="/api/visualization", tags=["Visualization"])
app.include_router(data_import.router, prefix="/api/import", tags=["Data Import"])


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("Starting Heritage Provenance System")
    
    try:
        rdf_service = RDFStoreService()
        await rdf_service.initialize()
        app.state.rdf_service = rdf_service
        logger.info("RDF store initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize RDF store: {e}")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down Heritage Provenance System")


@app.get("/")
async def root():
    """Root endpoint with system information"""
    return {
        "name": "Heritage Provenance System",
        "version": "1.0.0",
        "description": "API for managing artwork provenance with semantic web integration",
        "endpoints": {
            "docs": "/api/docs",
            "artworks": "/api/artworks",
            "provenance": "/api/provenance",
            "sparql": "/api/sparql",
            "recommendations": "/api/recommendations",
            "visualization": "/api/visualization"
        },
        "integrations": [
            "DBpedia",
            "Wikidata",
            "Getty Vocabularies (AAT, ULAN, TGN)",
            "Europeana",
            "Romanian Heritage"
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
