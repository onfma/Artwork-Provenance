# Heritage Provenance System

A comprehensive full-stack web application for modeling, managing, and visualizing artwork provenance using Semantic Web technologies and RDF. The system integrates with Wikidata, Getty Vocabularies, and Romanian heritage data to provide rich contextual information about artworks, artists, and their historical existence.

[Watch Project Presentation (Video)](prezWeb.mp4)

## 🎨 Features

### Core Functionality
- **Artwork Management**: Track artworks with detailed metadata
- **Artist Profiles**: Dedicated pages with biography, timeline, artwork gallery, and external data enrichment (Wikidata)
- **Provenance Tracking**: Document complete ownership and location history of artworks
- **SPARQL Endpoint**: Query the RDF knowledge graph using SPARQL
- **Visualization**: Interactive network graphs and timeline visualizations
- **Recommendations**: ML-powered artwork recommendations based on similarity

### Semantic Web Integration
- **CIDOC-CRM Ontology**: Industry-standard cultural heritage modeling
- **PROV-O**: W3C provenance ontology for tracking artwork history
- **RDF Triple Store**: Knowledge graph storage using RDFLib
- **RDFa Integration**: Frontend components annotated with Schema.org vocabulary for machine-readable metadata
- **External Data Sources**:
  - Wikidata for additional contextual data
  - Getty AAT (Art & Architecture Thesaurus) for terminology
- **Romanian Heritage Data**: Preloaded cultural heritage dataset

## 🏗️ Architecture

### Backend
- **Framework**: FastAPI (Python)
- **RDF Store**: RDFLib with support for Virtuoso and GraphDB
- **APIs**: RESTful endpoints + SPARQL query interface
- **ML**: scikit-learn for recommendation engine

### Frontend
- **Framework**: React 18 with React Router
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **Visualization**: 
  - Plotly.js for charts
  - vis-network for graph visualization
  - Leaflet for maps
- **State Management**: TanStack Query (React Query)
- **UI Components**: Headless UI + Heroicons

## 📋 Prerequisites

- **Python**: 3.9+
- **Node.js**: 18+
- **Redis**: 6.0+ (optional, for caching)
- **Docker**: For containerized deployment

## 🚀 Getting Started

### Backend Setup

1. **Navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Import Romanian heritage data (optional)**
   ```bash
   python scripts/import_romanian_heritage.py
   ```

6. **Run the backend server**
   ```bash
   python -m app.main
   ```

   The API will be available at `http://localhost:8000`
   - API Documentation: `http://localhost:8000/api/docs`
   - OpenAPI Spec: `http://localhost:8000/api/openapi.json`

### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with backend URL if different from default
   ```

4. **Run the development server**
   ```bash
   npm run dev
   ```

   The frontend will be available at `http://localhost:3000`

## 📚 API Endpoints

### Artworks
- `GET /api/artworks` - List all artworks
- `GET /api/artworks/{id}` - Get artwork details

### Artists
- `GET /api/artists` - List all artists
- `GET /api/artists/{id}` - Get artist details
- `GET /api/artists/getty/{id}` - Get artist details by Getty ID

### Provenance
- `GET /api/provenance/{artwork_id}` - Get provenance chain
- `GET /api/provenance/{event_id}` - Get provenance event

### Locations
- `GET /api/locations` - List locations
- `GET /api/locations/{id}` - Get location details

### SPARQL
- `POST /api/sparql/query` - Execute SPARQL query

### Recommendations
- `GET /api/recommendations/{artwork_id}` - Get similar artworks

### Visualization
- `GET /api/visualization/statistics/overview` - Get overview statistics (total artworks, artists, events, locations)
- `GET /api/visualization/statistics/by-type` - Get distribution of artworks by type
- `GET /api/visualization/statistics/by-material` - Get distribution of artworks by material
- `GET /api/visualization/statistics/top-artists` - Get top artists by number of artworks
- `GET /api/visualization/statistics/top-locations` - Get top locations by number of artworks
- `GET /api/visualization/statistics/network/artists/{artist_id}` - Get artist relationship network from Getty
- `GET /api/visualization/map/locations` - Get map visualization data for artwork locations

## 🗄️ Data Model

The system uses CIDOC-CRM for cultural heritage modeling:

- **E22_Man-Made_Object**: Artworks
- **E21_Person**: Artists and owners
- **E53_Place**: Galleries, museums, locations
- **E8_Acquisition**: Provenance events
- **E52_Time-Span**: Temporal information

## 📖 Documentation

- **Project Documentation**: See `docs/sholarly.html`
- **System Diagram**: See `docs/diagram.jpg`
- **API Documentation**: Available at `/api/docs` when running the backend
- **OpenAPI Specification**: See `docs/openapi.json` or `docs/OPENAPI.md`
- **Entities examples**:
   - pre parsed RDF data: `docs/entity-example.xml`
   - RDF data: `docs/RDFs-example.nt`
- **Ontologies**: 
  - CIDOC-CRM: `backend/ontology/cidoc_crm.owl`
  - PROV-O: `backend/ontology/prov-o.owl`

## 🎯 Use Cases

1. **Museum Collections Management**: Track artwork provenance and location
2. **Research**: Query cultural heritage data using SPARQL
3. **Discovery**: Find similar artworks using ML recommendations
4. **Visualization**: Explore artwork relationships and timelines

## 👥 Authors

Great Team (Tehnologii Web 2 - Ianuarie 2026)
