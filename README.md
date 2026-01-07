# Heritage Provenance System

A comprehensive web platform for modeling and managing artwork provenance with integration to DBpedia, Wikidata, Getty vocabularies, Europeana, and Romanian cultural heritage.

## Features

- **Artwork Management**: Complete CRUD operations for artworks with rich metadata
- **Provenance Tracking**: Full provenance chain tracking with events, agents, and locations
- **SPARQL Endpoint**: Query interface for RDF data with federated query support
- **External Integration**: 
  - DBpedia: Artist and artwork information
  - Wikidata: Linked data enrichment
  - Getty Vocabularies (AAT, ULAN, TGN): Controlled vocabularies
  - Europeana: European cultural heritage datasets
  - Romanian Heritage: Special integration for Romanian museums
- **Visualizations**: Interactive charts, network graphs, and geographic maps
- **Recommendation Engine**: Discover similar artworks based on multiple criteria
- **Semantic Web**: Built on CIDOC-CRM ontology with RDF/OWL support

## Architecture

```
Artwork-Provenance/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── main.py         # FastAPI application
│   │   ├── config.py       # Configuration settings
│   │   ├── models.py       # Pydantic models
│   │   ├── routers/        # API endpoints
│   │   │   ├── artworks.py
│   │   │   ├── provenance.py
│   │   │   ├── sparql.py
│   │   │   ├── recommendations.py
│   │   │   └── visualization.py
│   │   └── services/       # Business logic
│   │       ├── rdf_store.py
│   │       ├── external_data.py
│   │       └── recommendations.py
│   ├── data/               # Data storage
│   ├── ontology/           # OWL ontologies
│   │   ├── cidoc_crm.owl
│   │   └── provenance-ontology.owl
│   └── requirements.txt
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── pages/          # Page components
│   │   ├── api.js          # API client
│   │   └── main.jsx
│   └── package.json
└── docs/                   # Documentation

```

## Installation

### Backend Setup

1. **Create Python virtual environment**:
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Configure environment**:
```bash
copy .env.example .env
# Edit .env with your settings
```

4. **Run the backend**:
```bash
python -m app.main
```

The API will be available at `http://localhost:8000`
- API Documentation: `http://localhost:8000/api/docs`
- SPARQL Endpoint: `http://localhost:8000/api/sparql/query`

### Frontend Setup

1. **Install dependencies**:
```bash
cd frontend
npm install
```

2. **Configure environment**:
```bash
copy .env.example .env
```

3. **Run development server**:
```bash
npm run dev
```

The frontend will be available at `http://localhost:3000`

## Usage

### REST API

#### Artworks
- `GET /api/artworks` - List all artworks
- `POST /api/artworks` - Create new artwork
- `GET /api/artworks/{id}` - Get artwork details
- `PUT /api/artworks/{id}` - Update artwork
- `DELETE /api/artworks/{id}` - Delete artwork
- `GET /api/artworks/{id}/enrich?source=wikidata` - Enrich from external sources

#### Provenance
- `GET /api/provenance/{artwork_id}/chain` - Get provenance chain
- `POST /api/provenance/{artwork_id}/events` - Add provenance event
- `GET /api/provenance/timeline/{artwork_id}` - Get timeline visualization

#### SPARQL
- `POST /api/sparql/query` - Execute SPARQL query
- `GET /api/sparql/examples` - Get example queries
- `GET /api/sparql/statistics` - Get collection statistics
- `GET /api/sparql/federated/dbpedia` - Query DBpedia
- `GET /api/sparql/federated/wikidata` - Query Wikidata

#### Recommendations
- `GET /api/recommendations/{artwork_id}` - Get similar artworks
- `GET /api/recommendations/{artwork_id}/similar-provenance` - Find similar provenance

#### Visualizations
- `GET /api/visualization/statistics/overview` - Overview statistics
- `GET /api/visualization/statistics/by-type` - Artworks by type
- `GET /api/visualization/statistics/by-century` - Artworks by century
- `GET /api/visualization/statistics/top-artists` - Top artists
- `GET /api/visualization/network/provenance/{artwork_id}` - Provenance network
- `GET /api/visualization/map/locations` - Geographic map data

### SPARQL Examples

**List all artworks:**
```sparql
PREFIX hp: <http://arp-greatteam.org/heritage-provenance#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?artwork ?title ?artist
WHERE {
    ?artwork a hp:ArtisticWork ;
             dcterms:title ?title .
    OPTIONAL { ?artwork dcterms:creator ?artist }
}
```

**Provenance chain:**
```sparql
PREFIX hp: <http://arp-greatteam.org/heritage-provenance#>

SELECT ?event ?eventType ?date ?fromAgent ?toAgent
WHERE {
    <artwork-uri> hp:hasProvenanceEvent ?event .
    ?event hp:eventType ?eventType ;
           dcterms:date ?date .
    OPTIONAL { ?event hp:fromAgent ?fromAgent }
    OPTIONAL { ?event hp:toAgent ?toAgent }
}
ORDER BY ?date
```

## Technology Stack

### Backend
- **FastAPI**: Modern Python web framework
- **RDFLib**: RDF processing and SPARQL queries
- **SPARQLWrapper**: Federated SPARQL queries
- **scikit-learn**: Recommendation engine
- **Pydantic**: Data validation

### Frontend
- **React**: UI framework
- **Vite**: Build tool
- **TailwindCSS**: Styling
- **React Query**: Data fetching
- **Plotly.js**: Visualizations
- **Leaflet**: Maps

### Ontologies & Standards
- **CIDOC-CRM**: Cultural heritage conceptual reference model
- **W3C PROV**: Provenance ontology
- **Getty Vocabularies**: AAT, ULAN, TGN
- **Dublin Core**: Metadata terms

## Data Sources

1. **DBpedia** (`https://dbpedia.org/sparql`): Artist biographies, artwork information
2. **Wikidata** (`https://query.wikidata.org/sparql`): Linked open data
3. **Getty AAT**: Art & Architecture Thesaurus
4. **Getty ULAN**: Union List of Artist Names
5. **Getty TGN**: Thesaurus of Geographic Names
6. **Europeana**: European cultural heritage collections
7. **Romanian Heritage**: National museums and INP data

## Development

### Adding a New Artwork
```python
import requests

artwork = {
    "title": "Portrait",
    "title_ro": "Portret",
    "artist_name": "Nicolae Grigorescu",
    "creation_date": "1880-01-01",
    "artwork_type": "painting",
    "romanian_heritage": True,
    "wikidata_id": "Q123456"
}

response = requests.post("http://localhost:8000/api/artworks", json=artwork)
```

### Running Tests
```bash
cd backend
pytest
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License

## Contact

For questions or support, please open an issue on GitHub.

---

**Start scope**: Show the provenance chain of a single Romanian painting and link its artist and current location to Wikidata.