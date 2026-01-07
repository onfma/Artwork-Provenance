# API Documentation

## Base URL
`http://localhost:8000/api`

## Authentication
Currently, the API is open. Future versions will include JWT-based authentication.

## Endpoints

### Root
- **GET /** - System information and available endpoints

### Artworks

#### List Artworks
```
GET /artworks?skip=0&limit=20&artwork_type=painting&romanian_heritage=true
```

Query Parameters:
- `skip` (int): Number of records to skip (pagination)
- `limit` (int): Maximum records to return (1-100)
- `artwork_type` (string): Filter by type (painting, sculpture, etc.)
- `artist_name` (string): Filter by artist name
- `romanian_heritage` (boolean): Filter Romanian heritage items

Response:
```json
[
  {
    "uri": "http://arp-greatteam.org/heritage-provenance/artwork/123",
    "title": "Portrait",
    "title_ro": "Portret",
    "artist": {
      "name": "Nicolae Grigorescu",
      "uri": "http://arp-greatteam.org/heritage-provenance/artist/456"
    },
    "creation_date": "1880-01-01",
    "artwork_type": "painting",
    "romanian_heritage": true
  }
]
```

#### Create Artwork
```
POST /artworks
Content-Type: application/json

{
  "title": "Portrait",
  "title_ro": "Portret",
  "artist_name": "Nicolae Grigorescu",
  "creation_date": "1880-01-01",
  "artwork_type": "painting",
  "description": "Beautiful portrait",
  "romanian_heritage": true,
  "wikidata_id": "Q123456"
}
```

#### Get Artwork
```
GET /artworks/{artwork_id}
```

#### Update Artwork
```
PUT /artworks/{artwork_id}
Content-Type: application/json

{
  "title": "Updated Title",
  "description": "Updated description"
}
```

#### Delete Artwork
```
DELETE /artworks/{artwork_id}
```

#### Enrich Artwork
```
GET /artworks/{artwork_id}/enrich?source=wikidata
```

Sources: `dbpedia`, `wikidata`, `getty`

### Provenance

#### Get Provenance Chain
```
GET /provenance/{artwork_id}/chain
```

Returns chronological list of provenance events.

#### Add Provenance Event
```
POST /provenance/{artwork_id}/events
Content-Type: application/json

{
  "event_type": "acquisition",
  "date": "1920-05-15",
  "description": "Purchased by museum",
  "from_agent": {
    "name": "Private Collector",
    "type": "Person"
  },
  "to_agent": {
    "name": "National Museum",
    "type": "Organization"
  },
  "location": {
    "name": "Bucharest",
    "country": "Romania"
  }
}
```

Event types: `acquisition`, `sale`, `transfer`, `exhibition`, `loan`, `restoration`, `theft`, `recovery`, `donation`, `inheritance`

#### Search Events
```
GET /provenance/events/search?event_type=acquisition&start_date=1900-01-01&end_date=2000-12-31
```

#### Get Timeline
```
GET /provenance/timeline/{artwork_id}
```

Returns formatted timeline data for visualization.

### SPARQL

#### Execute Query
```
POST /sparql/query
Content-Type: application/json

{
  "query": "SELECT ?artwork ?title WHERE { ?artwork a hp:ArtisticWork ; dcterms:title ?title }",
  "output_format": "json",
  "reasoning": false
}
```

Response:
```json
{
  "results": {
    "bindings": [...]
  },
  "query_time_ms": 45.2,
  "result_count": 10
}
```

#### Get Examples
```
GET /sparql/examples
```

Returns example SPARQL queries.

#### Get Statistics
```
GET /sparql/statistics
```

Returns collection statistics via SPARQL.

#### Federated Queries
```
GET /sparql/federated/dbpedia?query=...
GET /sparql/federated/wikidata?query=...
GET /sparql/federated/getty?query=...
```

### Recommendations

#### Get Recommendations
```
GET /recommendations/{artwork_id}?max_results=10&criteria=artist,period,type
```

Criteria options: `artist`, `period`, `type`, `location`, `medium`, `description`

Response:
```json
[
  {
    "artwork": {...},
    "similarity_score": 0.85,
    "reasons": ["Same artist: Nicolae Grigorescu", "Same century: 19th"]
  }
]
```

#### Similar Provenance
```
GET /recommendations/{artwork_id}/similar-provenance?max_results=10
```

Finds artworks with similar ownership/transfer patterns.

### Visualizations

#### Overview Statistics
```
GET /visualization/statistics/overview
```

Response:
```json
{
  "total_artworks": 150,
  "total_artists": 45,
  "total_locations": 20,
  "total_events": 320
}
```

#### Artworks by Type
```
GET /visualization/statistics/by-type
```

#### Artworks by Century
```
GET /visualization/statistics/by-century
```

#### Top Artists
```
GET /visualization/statistics/top-artists?limit=10
```

#### Top Locations
```
GET /visualization/statistics/top-locations?limit=10
```

#### Provenance Network
```
GET /visualization/network/provenance/{artwork_id}
```

Returns nodes and edges for network visualization.

#### Location Map
```
GET /visualization/map/locations
```

Returns geographic markers for map visualization.

## Error Responses

```json
{
  "detail": "Error message"
}
```

Status codes:
- 200: Success
- 201: Created
- 400: Bad Request
- 404: Not Found
- 500: Internal Server Error

## Rate Limiting

Currently no rate limiting. Future versions will implement rate limiting.

## SPARQL Prefix Declarations

Common prefixes used in queries:

```sparql
PREFIX hp: <http://arp-greatteam.org/heritage-provenance#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX crm: <http://www.cidoc-crm.org/cidoc-crm/>
PREFIX prov: <http://www.w3.org/ns/prov#>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
PREFIX dbo: <http://dbpedia.org/ontology/>
PREFIX wdt: <http://www.wikidata.org/prop/direct/>
PREFIX gvp: <http://vocab.getty.edu/ontology#>
```
