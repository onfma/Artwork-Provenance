## Data Import and Ontology Modeling

### Overview
This documentation describes how artwork provenance data is imported and modeled as ontology instances representing artworks, artists, and provenance events.

### Data Import Process
The import workflow processes provenance records to create:
- **Artwork instances**: Physical objects with titles, dimensions, materials, and creation dates
- **Artist instances**: Creators linked to artworks through production events
- **Event instances**: Provenance activities including creation, acquisition, transfer, exhibition, and sale events

### Ontology Modeling for Artworks

#### 1. **Artwork Creation**
- Each artwork becomes an instance of the `Artwork` class
- Properties include title, creation date, medium, dimensions
- Unique URIs are generated for each artwork (e.g., `artwork/123`)

#### 2. **Artist Modeling**
- Artists are instances of the `Person` or `Organization` class
- Artist properties include name, birth/death dates, nationality
- Artists are linked to artworks through `Production` events

#### 3. **Event Modeling**
- Each provenance activity creates an event instance (e.g., `Acquisition`, `Transfer`, `Exhibition`)
- Events have timestamps, locations, and participants (actors)
- Events reference the artwork they involve and connect sequential ownership changes

### Relationships
- **Production events** link artists to artworks they created
- **Transfer events** document ownership changes between parties
- **Temporal properties** establish chronological sequences of provenance
- **Location properties** track where artworks were held or displayed
