# API Specification

## Overview

The Heritage Provenance System provides a comprehensive REST API for managing artwork provenance with semantic web integration. The API is built with FastAPI and automatically generates OpenAPI 3.0 specifications.

### Interactive Documentation
- **Swagger UI**: `http://localhost:8000/api/docs`
- **OpenAPI JSON**: `http://localhost:8000/api/openapi.json`


## API Architecture

The API follows RESTful principles and is organized into the following modules:

| Module | Prefix | Description |
|--------|--------|-------------|
| Artworks | `/api/artworks` | Manage artworks and their metadata |
| Artists | `/api/artists` | Manage artist information |
| Provenance | `/api/provenance` | Track provenance events and chains |
| Locations | `/api/locations` | Manage physical locations |
| Recommendations | `/api/recommendations` | Get artwork recommendations |
| Visualization | `/api/visualization` | Generate visualizations |
| SPARQL | `/api/sparql` | Execute SPARQL queries |

## Practical Usage Examples

### Example 1: Discovering Artworks

**Scenario**: A researcher wants to find all artworks part of Patrimoniul Cultural Național al Romaniei.

```bash
# 1. List all Romanian artworks
curl -X GET "http://localhost:8000/api/artworks?limit=50" \
  -H "accept: application/json"
```

**Response Example**:
```json
{
  "count": 50,
  "artworks": [
    {
    "id": "755567e9-bf30-4f70-a8f4-0e2da94ff2bc",
    "uri": "http://arp-greatteam.org/heritage-provenance/artwork/755567e9-bf30-4f70-a8f4-0e2da94ff2bc",
    "inventoryNumber": "număr de inventar: 0000",
    "title": "Deisis",
    "imageURL": "https://clasate.cimec.ro/medium/imagini14/a0e18bde0d224cbeac2e51a790297283.jpg"
    },
    {
    "id": "b6c234af-f8e2-4699-a207-b19f20dbe213",
    "uri": "http://arp-greatteam.org/heritage-provenance/artwork/b6c234af-f8e2-4699-a207-b19f20dbe213",
    "inventoryNumber": "număr de inventar: 000001",
    "title": "Mitologie pe limba românească",
    "imageURL": "https://clasate.cimec.ro/medium/imagini31/b4a58835b8264aeca622e20850355fbc.jpg"
    }, 
    ...
  ]
}
```

### Example 2: Tracing Artwork Provenance

**Scenario**: A museum curator needs to trace the complete provenance chain of an artwork for an exhibition catalog.

```bash
# 1. Get the artwork details
curl -X GET "http://localhost:8000/api/artworks/755567e9-bf30-4f70-a8f4-0e2da94ff2bc" \
  -H "accept: application/json"

# 2. Get detailed information about a specific artwork
curl -X GET "http://localhost:8000/api/artworks/755567e9-bf30-4f70-a8f4-0e2da94ff2bc" \
  -H "accept: application/json"

# 3. Get detailed information about a specific artwork's creation
curl -X GET "http://localhost:8000/api/provenance/0cab49bf-d44b-4813-8487-a0a1c782a23c" \
  -H "accept: application/json"
```

**Response Example**:
```json
{
  "id": "755567e9-bf30-4f70-a8f4-0e2da94ff2bc",
  "uri": "http://arp-greatteam.org/heritage-provenance/artwork/755567e9-bf30-4f70-a8f4-0e2da94ff2bc",
  "inventoryNumber": "număr de inventar: 0000",
  "title": "Deisis",
  "imageURL": "https://clasate.cimec.ro/medium/imagini14/a0e18bde0d224cbeac2e51a790297283.jpg",
  "artist": {
    "uri": "http://arp-greatteam.org/heritage-provenance/artist/61a55fb8-b802-4fa1-b8ca-06dfec561ca9",
    "name": "Unknown Artist"
    },
  "location": {
    "uri": "http://arp-greatteam.org/heritage-provenance/location/188bd79d-2a04-4bf0-a902-9531e78ee3e6",
    "name": "Unknown Location"
  },
  "date": "a doua jumătate a secolului al XVII-lea",
  "type": {
    "uri": "http://arp-greatteam.org/heritage-provenance/attributes/50794727-fb6c-46f8-9ed9-9aae311bc540",
    "label": "Artifact",
    "link": "http://vocab.getty.edu/aat/300033945"
  },
  "subject": {
    "uri": "http://arp-greatteam.org/heritage-provenance/attributes/a79d609a-ddbc-4cc9-9007-8025b418038e",
    "label": "Școală grecească (școală)",
    "link": "http://vocab.getty.edu/aat/300266106"
  },
  "material": {
    "uri": "http://arp-greatteam.org/heritage-provenance/attributes/0062cc41-0481-4834-9b9f-492618ac1b14",
    "label": "tempera și foiță de aur pe lemn",
    "link": "http://vocab.getty.edu/aat/300015062"
  },
  "wikidata_enrichment": {
    "wikidata_id": "Q1207453",
    "data": {
      "description": "artistic theme of Jesus flanked by the Virgin Mary and John the Baptist, sometimes with other saints",
      "image_url": "https://commons.wikimedia.org/wiki/Special:FilePath/Deesis.jpg"
    }
  },
  "event": {
    "id": "0cab49bf-d44b-4813-8487-a0a1c782a23c",
    "uri": "http://arp-greatteam.org/heritage-provenance/event/0cab49bf-d44b-4813-8487-a0a1c782a23c",
    "type": "creation",
    "artwork": {
      "uri": "http://arp-greatteam.org/heritage-provenance/artwork/755567e9-bf30-4f70-a8f4-0e2da94ff2bc",
      "title": "Deisis",
      "inventoryNumber": "număr de inventar: 0000",
      "imageURL": "https://clasate.cimec.ro/medium/imagini14/a0e18bde0d224cbeac2e51a790297283.jpg"
    },
    "artist": {
      "uri": "http://arp-greatteam.org/heritage-provenance/artist/61a55fb8-b802-4fa1-b8ca-06dfec561ca9",
      "name": "Unknown Artist"
    },
    "location": {
      "uri": "http://arp-greatteam.org/heritage-provenance/location/188bd79d-2a04-4bf0-a902-9531e78ee3e6",
      "name": "Unknown Location"
    },
    "date": "a doua jumătate a secolului al XVII-lea"
  }
}
```

### Example 3: Discovering Similar Artworks

**Scenario**: A visitor in a museum wants to discover artworks similar to one they're viewing.

```bash
# Get recommendations for an artwork based on multiple criteria
curl -X GET "http://localhost:8000/api/recommendations/755567e9-bf30-4f70-a8f4-0e2da94ff2bc?limit=5" \
  -H "accept: application/json"

# Get recommendations with specific filtering
curl -X GET "http://localhost:8000/api/recommendations/755567e9-bf30-4f70-a8f4-0e2da94ff2bc?limit=5&min_score=0.7" \
  -H "accept: application/json"
```

**Response Example**:
```json
{
  "artwork_id": "755567e9-bf30-4f70-a8f4-0e2da94ff2bc",
  "recommendations": [
    {
      "id": "b6c234af-f8e2-4699-a207-b19f20dbe213",
      "uri": "http://arp-greatteam.org/heritage-provenance/artwork/b6c234af-f8e2-4699-a207-b19f20dbe213",
      "title": "Mitologie pe limba românească",
      "inventoryNumber": "număr de inventar: 000001",
      "imageURL": "https://clasate.cimec.ro/medium/imagini31/b4a58835b8264aeca622e20850355fbc.jpg",
      "similarity_score": 0.825,
      "reasons": [
        "Same artist: Unknown Artist",
        "Same type: Artifact",
        "Same location: Unknown Location",
        "Both part of Romanian heritage"
      ]
    },
    ...
  ]
}
```


### Example 4: Discover a Artist's Network

**Scenario**: A researcher wants to explore an artist's professional network and discover relationships with other artists (teachers or students).

```bash
curl -X POST "http://localhost:8000/api/visualization/statistics/network/artists/5a4d2e7f-4f3e-4574-8774-75db4883e2c1" \
  -H "accept: application/json" \
```

**Response Example**:
```json
{
  "nodes": [
    {
      "id": "500019613",
      "uri": "http://vocab.getty.edu/ulan/500019613",
      "name": "Luchian, Ștefan"
    },
    {
      "id": "500017470",
      "uri": "http://vocab.getty.edu/ulan/500017470",
      "name": "Petrascu, Gheorghe"
    }
  ],
  "edges": [
    {
      "target": "500019613",
      "relationship": "teacher_of"
    },
    {
      "target": "500017470",
      "relationship": "teacher_of"
    }
  ]
}
```


### Example 5: Advanced SPARQL Queries

**Scenario**: A researcher wants to perform complex queries across the knowledge graph.

```bash
# Execute a custom SPARQL query to find artworks by period
curl -X POST "http://localhost:8000/api/sparql/query" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "SELECT ?artwork ?title WHERE { ?artwork a <http://www.cidoc-crm.org/cidoc-crm/E22_Human-Made_Object> ; <http://purl.org/dc/terms/title> ?title . } LIMIT 10"
  }'
```

**Response Example**:
```json
{
  "results": {
    "bindings": [
      {
        "artwork": {
          "type": "uri",
          "value": "http://arp-greatteam.org/heritage-provenance/artwork/755567e9-bf30-4f70-a8f4-0e2da94ff2bc"
        },
        "title": {
          "type": "literal",
          "value": "Deisis"
        }
      }
    ]
  }
}
```