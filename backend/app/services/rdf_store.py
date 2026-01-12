"""
RDF Store Service - Manages RDF data and SPARQL queries
"""

import structlog
from typing import Dict, Any
from urllib.parse import quote
from app.config import settings
from SPARQLWrapper import SPARQLWrapper
from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, RDFS, OWL, XSD, DCTERMS, FOAF

from app.models import ArtworkType


logger = structlog.get_logger()

TYPE_KEYWORDS = {
    "drawing": ["desen", "drawing", "schiță", "schita", "sketch", "creion", "pencil", "cărbune", "charcoal", "tuș", "ink", "pastel", "grafică", "graphic"],
    "print": ["gravură", "gravura", "print", "litografie", "lithograph", "acvaforte", "etching", "xilogravură", "woodcut", "stampă", "serigrafie"],
    "photograph": ["fotografie", "fotografia", "photograph", "photo", "foto", "negativ", "negative", "daguerreotype"],
    "manuscript": ["manuscris", "manuscript", "document", "scrisoare", "letter", "incunabul", "carte"],
    "installation": ["instalație", "instalatie", "installation"],
    "artifact": ["artefact", "artifact", "ceramică", "ceramic", "pottery", "porțelan", "textil", "textile", "covor", "carpet", "tapiserie", "monedă", "coin", "bijuterie", "jewelry", "mobilier", "furniture", "vas", "vessel"],
    "sculpture": ["sculptură", "sculptura", "sculpture", "statuie", "statue", "bust", "relief", "bronz", "bronze", "marmură", "marble", "ronde-bosse"],
    "painting": ["pictură", "pictura", "painting", "ulei", "oil", "pânză", "panza", "canvas"]
}


class RDFStoreService:
    """Service for RDF data management and SPARQL queries"""
    
    def __init__(self):
        self.graph = Graph()
        
        self.ns = {
            'dbo': Namespace("http://dbpedia.org/ontology/"),
            'wdt': Namespace("http://www.wikidata.org/prop/direct/"),
            'gvp': Namespace("http://vocab.getty.edu/ontology#"),
            'aat': Namespace("http://vocab.getty.edu/aat/"),
            'ulan': Namespace("http://vocab.getty.edu/ulan/"),
            'tgn': Namespace("http://vocab.getty.edu/tgn/"),
            'prov': Namespace("http://www.w3.org/ns/prov#"),
            'crm': Namespace("http://www.cidoc-crm.org/cidoc-crm/"),
            'aat': Namespace("http://vocab.getty.edu/aat/")
        }
        
        for prefix, namespace in self.ns.items():
            self.graph.bind(prefix, namespace)
        
        self.graph.bind('rdf', RDF)
        self.graph.bind('rdfs', RDFS)
        self.graph.bind('owl', OWL)
        self.graph.bind('xsd', XSD)
        self.graph.bind('dcterms', DCTERMS)
        self.graph.bind('foaf', FOAF)
        
        self.dbpedia_endpoint = SPARQLWrapper(settings.DBPEDIA_SPARQL)
        self.wikidata_endpoint = SPARQLWrapper(settings.WIKIDATA_SPARQL)
        self.getty_endpoint = SPARQLWrapper(settings.GETTY_AAT_SPARQL)
        
    
    async def initialize(self):
        """Initialize RDF store and load ontologies"""
        try:
            # Load ontologies
            logger.info("Loading CIDOC-CRM ontology")
            self.graph.parse(settings.CIDOC_CRM_FILE, format="xml")
            
            logger.info("Loading Prov ontology")
            self.graph.parse(settings.PROV_FILE, format="ttl")
            
            # Load data files from data directory
            await self.load_data_files()
            
            logger.info(f"RDF graph initialized with {len(self.graph)} triples")
            
        except Exception as e:
            logger.error(f"Error initializing RDF store: {e}")
            raise
    
    async def load_data_files(self):
        """Load all RDF data files from the data directory"""
        from pathlib import Path
        
        data_dir = Path(settings.DATA_DIR)
        
        if not data_dir.exists():
            logger.warning(f"Data directory not found: {data_dir}")
            return
        
        for ext in ['*.ttl', '*.rdf', '*.owl', '*.nt', '*.jsonld']:
            for file_path in data_dir.glob(ext):
                try:
                    logger.info(f"Loading data file: {file_path.name}")
                    
                    format_map = {
                        '.ttl': 'turtle',
                        '.rdf': 'xml',
                        '.owl': 'xml',
                        '.nt': 'nt',
                        '.jsonld': 'json-ld'
                    }
                    file_format = format_map.get(file_path.suffix, 'turtle')
                    
                    self.graph.parse(str(file_path), format=file_format)
                    logger.info(f"Loaded {file_path.name} successfully")
                    
                except Exception as e:
                    logger.error(f"Error loading {file_path.name}: {e}")
    
    def save_to_file(self, filepath: str, format: str = "turtle"):
        """Save RDF graph to file"""
        try:
            logger.info(f"Starting to serialize {len(self.graph)} triples to {filepath}")
            self.graph.serialize(destination=filepath, format=format)
            logger.info(f"RDF graph saved successfully to {filepath}")
        except Exception as e:
            logger.error(f"Error saving RDF graph: {e}")
            raise


    ##########################
    # Adding entities as RDFs
    ##########################

    def add_artwork(self, artwork_uri: str, artwork_data: Dict[str, Any]) -> bool:
        """Add artwork to RDF store"""

        def add_artwork_id(artwork_id: str):
            try:                
                identifier_uri = URIRef(f"{artwork_uri}/identifier/{quote(artwork_id, safe='')}")
                self.graph.add((identifier_uri, RDF.type, crm.E42_Identifier))
                self.graph.add((identifier_uri, crm.P190_has_symbolic_content, Literal(artwork_id)))
                
                self.graph.add((artwork_ref, crm.P1_is_identified_by, identifier_uri))
                return True
            except Exception as e:
                logger.error(f"Error adding artwork to RDF store: {e}")
            return False
        
        def add_artwork_title(title: str):
            try:
                title_uri = URIRef(f"{artwork_uri}/title/{quote(title, safe='')}")
                self.graph.add((title_uri, RDF.type, crm.E35_Title))
                self.graph.add((title_uri, crm.P190_has_symbolic_content, Literal(title)))

                self.graph.add((artwork_ref, crm.P102_has_title, title_uri))
                return True
            except Exception as e:
                logger.error(f"Error adding artwork title to RDF store: {e}")
            return False

        try:
            prov = self.ns['prov']
            crm = self.ns['crm']
            artwork_ref = URIRef(artwork_uri)
            
            self.graph.add((artwork_ref, RDF.type, prov.Entity))
            self.graph.add((artwork_ref, RDF.type, crm.E22_Man_Made_Object))
            add_artwork_id(artwork_data.get('inventoryNumber'))
            add_artwork_title(artwork_data.get('title'))
            
            if artwork_data.get('imageURL'):
                self.graph.add((artwork_ref, FOAF.depiction, URIRef(artwork_data.get('imageURL'))))

            if artwork_data.get('type_uri'):
                self.graph.add((artwork_ref, crm.P2_has_type, URIRef(artwork_data.get('type_uri'))))
            if artwork_data.get('subject_uri'):
                self.graph.add((artwork_ref, crm.P15_was_influenced_by, URIRef(artwork_data.get('subject_uri'))))
            if artwork_data.get('material_uri'):
                self.graph.add((artwork_ref, crm.P45_consists_of, URIRef(artwork_data.get('material_uri'))))
            logger.info(f"Added artwork to RDF store: {artwork_uri}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding artwork to RDF store: {e}")
            return False
    
    def add_entity(self, entity_type: str, entity_uri: str, entity_name: str, entity_link: str) -> bool:
        """Add artwork details entities to RDF store"""      
        try:
            crm = self.ns['crm']
            prov = self.ns['prov']
            entity_ref = URIRef(entity_uri)

            if entity_link:
                self.graph.add((entity_ref, OWL.sameAs, URIRef(f"{entity_link}")))
            
            if entity_type == 'provider' or entity_type == 'institute':
                self.graph.add((entity_ref, RDF.type, prov.Agent))
            else:
                self.graph.add((entity_ref, RDFS.label, Literal(entity_name)))
                if entity_type == 'type':
                    self.graph.add((entity_ref, RDF.type, crm.E55_Type))
                elif entity_type == 'subject':
                    self.graph.add((entity_ref, RDF.type, crm.E28_Conceptual_Object))
                elif entity_type == 'material':
                    self.graph.add((entity_ref, RDF.type, crm.E57_Material))

            logger.info(f"Added {entity_type} to RDF store: {entity_uri}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding {entity_type} to RDF store: {e}")
            return False
        
        
    def add_artist(self, artist_uri: str, artist_data: Dict[str, Any]) -> bool:
        """Add artist to RDF store"""

        try:
            prov = self.ns['prov']
            crm = self.ns['crm']
            artist_ref = URIRef(artist_uri)
            
            self.graph.add((artist_ref, RDF.type, prov.Agent))
            self.graph.add((artist_ref, RDF.type, crm.E21_Person))
            self.graph.add((artist_ref, FOAF.name, Literal(artist_data['creator'])))
            
            if 'creatorULAN' in artist_data and artist_data['creatorULAN']:
                self.graph.add((artist_ref, OWL.sameAs, URIRef(f"{artist_data['creatorULAN']}")))

            logger.info(f"Added artist to RDF store: {artist_uri}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding artist to RDF store: {e}")
            return False
    
    def add_location(self, location_uri: str, location_data: Dict[str, Any]) -> bool:
        """Add location to RDF store"""

        prov = self.ns['prov']
        crm = self.ns['crm']
        location_ref = URIRef(location_uri)

        try:
            self.graph.add((location_ref, RDF.type, prov.Location))
            self.graph.add((location_ref, RDF.type, crm.E53_Place))
            self.graph.add((location_ref, RDFS.label, Literal(location_data['location'])))
            
            if 'locationTGN' in location_data and location_data['locationTGN']:
                self.graph.add((location_ref, OWL.sameAs, URIRef(f"{location_data['locationTGN']}")))

            logger.info(f"Added location to RDF store: {location_uri}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding location to RDF store: {e}")
            return False

    def add_provenance_event(self, event_uri: str, event_data: Dict[str, Any]) -> bool:
        """Add provenance event to RDF store"""
        try:
            prov = self.ns['prov']
            crm = self.ns['crm']
            event_ref = URIRef(event_uri)
            
            self.graph.add((event_ref, RDF.type, prov.Activity))
            self.graph.add((event_ref, RDF.type, crm.E12_Production))
            self.graph.add((event_ref, RDFS.label, Literal(event_data['type'])))

            self.graph.add((event_ref, crm.P14_carried_out_by, URIRef(event_data['artist_uri'])))
            self.graph.add((event_ref, crm.P7_took_place_at, URIRef(event_data['location_uri'])))
            self.graph.add((event_ref, crm.P108_has_produced, URIRef(event_data['artwork_uri'])))
            self.graph.add((event_ref, crm.P4_has_time_span, Literal(event_data['date'])))
            self.graph.add((event_ref, crm.P109_has_current_or_former_curator, URIRef(event_data['provider_uri'])))
            self.graph.add((event_ref, crm.P50i_is_currently_held_by, URIRef(event_data['institute_uri'])))

            logger.info(f"Added provenance event to RDF store: {event_uri}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding provenance event to RDF store: {e}")
            return False

    ##########################
    # Querying RDFs [SPARQL]
    ##########################

    def get_all_artworks(self, filters: Dict[str, str] = None, search: str = None, limit: int = 20, skip: int = 0) -> list:
        """Query all artworks from RDF store with optional filters"""
        
        filter_clauses = ""
        search_filter = ""
        
        if filters:
            if filters.get('type'):
                type_key = filters['type'].lower()
                keywords = TYPE_KEYWORDS.get(type_key, [type_key])
                keyword_conditions = " || ".join([f'CONTAINS(LCASE(?typeLabel), "{k}")' for k in keywords])
                filter_clauses += f"""
            ?artwork crm:P2_has_type ?type .
            ?type rdfs:label ?typeLabel .
            FILTER({keyword_conditions})"""
            if filters.get('material_uri'):
                filter_clauses += f"\n            ?artwork crm:P45_consists_of <{filters['material_uri']}> ."
            if filters.get('subject_uri'):
                filter_clauses += f"\n            ?artwork crm:P15_was_influenced_by <{filters['subject_uri']}> ."
            if filters.get('artist_uri'):
                filter_clauses += f"""
            ?event crm:P108_has_produced ?artwork ;
                   crm:P14_carried_out_by <{filters['artist_uri']}> ."""
            if filters.get('location_uri'):
                filter_clauses += f"""
            ?event crm:P108_has_produced ?artwork ;
                   crm:P7_took_place_at <{filters['location_uri']}> ."""

        if search:
            safe_search = search.replace('"', '\\"')
            search_filter = f'FILTER(CONTAINS(LCASE(?title), LCASE("{safe_search}")))'
        
        query = f"""
        PREFIX prov: <http://www.w3.org/ns/prov#>
        PREFIX crm: <http://www.cidoc-crm.org/cidoc-crm/>
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
        
        SELECT DISTINCT ?artwork ?identifier ?title ?imageURL
        WHERE {{
            ?artwork a prov:Entity ;
                     a crm:E22_Man_Made_Object .{filter_clauses}
            
            OPTIONAL {{
                ?artwork crm:P1_is_identified_by ?id .
                ?id crm:P190_has_symbolic_content ?identifier .
            }}
            
            OPTIONAL {{
                ?artwork crm:P102_has_title ?titleNode .
                ?titleNode crm:P190_has_symbolic_content ?title .
            }}

            OPTIONAL {{
                ?artwork foaf:depiction ?imageURL .
            }}

            {search_filter}
        }}
        ORDER BY ?identifier
        LIMIT {limit}
        OFFSET {skip}
        """
        
        try:
            results = self.graph.query(query)
            artworks = []
            
            for row in results:
                artwork_uri = str(row.artwork)
                artwork_id = artwork_uri.split('/')[-1]
                
                artwork_data = {
                    'id': artwork_id,
                    'uri': artwork_uri,
                    'inventoryNumber': str(row.identifier) if row.identifier else None,
                    'title': str(row.title) if row.title else None,
                    'imageURL': str(row.imageURL) if row.imageURL else None
                }
                artworks.append(artwork_data)
            
            logger.info(f"Retrieved {len(artworks)} artworks from RDF store")
            return artworks
            
        except Exception as e:
            logger.error(f"Error querying artworks: {e}")
            return []

    def get_artwork(self, artwork_uri: str) -> Dict[str, Any]:
        """Query specific artwork details from RDF store"""
        query = f"""
        PREFIX prov: <http://www.w3.org/ns/prov#>
        PREFIX crm: <http://www.cidoc-crm.org/cidoc-crm/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        
        SELECT ?identifier ?title ?imageURL 
               ?type ?typeLabel ?typeLink 
               ?subject ?subjectLabel ?subjectLink
               ?material ?materialLabel ?materialLink
               ?artist ?artistName ?location ?locationName ?date ?event
        WHERE {{
            <{artwork_uri}> a prov:Entity ;
                          a crm:E22_Man_Made_Object .
            
            OPTIONAL {{
                <{artwork_uri}> crm:P1_is_identified_by ?id .
                ?id crm:P190_has_symbolic_content ?identifier .
            }}
            
            OPTIONAL {{
                <{artwork_uri}> crm:P102_has_title ?titleNode .
                ?titleNode crm:P190_has_symbolic_content ?title .
            }}

            OPTIONAL {{
                <{artwork_uri}> foaf:depiction ?imageURL .
            }}
            
            OPTIONAL {{
                <{artwork_uri}> crm:P2_has_type ?type .
                ?type rdfs:label ?typeLabel .
                ?type owl:sameAs ?typeLink .
            }}
            
            OPTIONAL {{
                <{artwork_uri}> crm:P15_was_influenced_by ?subject .
                ?subject rdfs:label ?subjectLabel .
                ?subject owl:sameAs ?subjectLink .
            }}
            
            OPTIONAL {{
                <{artwork_uri}> crm:P45_consists_of ?material .
                ?material rdfs:label ?materialLabel .
                ?material owl:sameAs ?materialLink .
            }}
            
            OPTIONAL {{
                ?event crm:P108_has_produced <{artwork_uri}> ;
                       crm:P14_carried_out_by ?artist ;
                       crm:P7_took_place_at ?location ;
                       crm:P4_has_time_span ?date .
                ?artist foaf:name ?artistName .
                ?location rdfs:label ?locationName .
            }}
        }}
        """
        
        try:
            results = self.graph.query(query)
            
            if not results:
                return None
            
            artwork_data = {
                'id': artwork_uri.split('/')[-1],
                'uri': artwork_uri,
                'inventoryNumber': None,
                'title': None,
                'imageURL': None,
                'artist': None,
                'location': None,
                'date': None,
                'type': None,
                'subject': None,
                'material': None,
                'event': None
            }
            
            for row in results:
                if row.identifier:
                    artwork_data['inventoryNumber'] = str(row.identifier)
                if row.title:
                    artwork_data['title'] = str(row.title)
                if row.imageURL:
                    artwork_data['imageURL'] = str(row.imageURL)
                if row.typeLabel:
                    artwork_data['type'] = {
                        'uri': str(row.type) if row.type else None,
                        'label': str(ArtworkType.from_text(row.typeLabel)),
                        'link': str(row.typeLink) if row.typeLink else None
                    }
                if row.subjectLabel:
                    artwork_data['subject'] = {
                        'uri': str(row.subject) if row.subject else None,
                        'label': str(row.subjectLabel),
                        'link': str(row.subjectLink) if row.subjectLink else None
                    }
                if row.materialLabel:
                    artwork_data['material'] = {
                        'uri': str(row.material) if row.material else None,
                        'label': str(row.materialLabel),
                        'link': str(row.materialLink) if row.materialLink else None
                    }
                if row.artistName:
                    artwork_data['artist'] = {
                        'uri': str(row.artist) if row.artist else None,
                        'name': str(row.artistName)
                    }
                if row.date:
                    artwork_data['date'] = str(row.date)
                if row.locationName:
                    artwork_data['location'] = {
                        'uri': str(row.location) if row.location else None,
                        'name': str(row.locationName)
                    }
                if row.event:
                    artwork_data['event'] = str(row.event)
            
            logger.info(f"Retrieved artwork details for: {artwork_uri}")
            return artwork_data
            
        except Exception as e:
            logger.error(f"Error querying artwork details: {e}")
            return None


    def get_all_artists(self, filters: Dict[str, str] = None, limit: int = None) -> list:
        """Query all artists from RDF store with optional filters"""
        
        filter_clauses = ""
        
        if filters:
            if filters.get('location_uri'):
                filter_clauses += f"""
            ?event crm:P14_carried_out_by ?artist ;
                   crm:P7_took_place_at <{filters['location_uri']}> ."""
        
        query = f"""
        PREFIX prov: <http://www.w3.org/ns/prov#>
        PREFIX crm: <http://www.cidoc-crm.org/cidoc-crm/>
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        
        SELECT DISTINCT ?artist ?name ?ulan
        WHERE {{
            ?artist a prov:Agent ;
                    a crm:E21_Person ;
                    foaf:name ?name .{filter_clauses}
            OPTIONAL {{ ?artist owl:sameAs ?ulan . FILTER(CONTAINS(STR(?ulan), "ulan")) }}
        }}
        ORDER BY ?name
        """
        
        try:
            results = self.graph.query(query)
            artists = []
            
            for row in results:
                artist_uri = str(row.artist)
                artist_id = artist_uri.split('/')[-1]
                
                artist_data = {
                    'id': artist_id,
                    'uri': artist_uri,
                    'name': str(row.name),
                    'getty': str(row.ulan) if row.ulan else None
                }
                artists.append(artist_data)
            
            logger.info(f"Retrieved {len(artists)} artists from RDF store")
            return artists
            
        except Exception as e:
            logger.error(f"Error querying artists: {e}")
            return []
        
    def get_artist(self, artist_uri: str) -> Dict[str, Any]:
        """Query specific artist details from RDF store including all associated artworks"""
        query = f"""
        PREFIX prov: <http://www.w3.org/ns/prov#>
        PREFIX crm: <http://www.cidoc-crm.org/cidoc-crm/>
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT ?name ?ulan ?artwork ?artworkTitle ?artworkIdentifier ?artworkImageURL
        WHERE {{
            <{artist_uri}> a prov:Agent ;
                          a crm:E21_Person ;
                          foaf:name ?name .
            
            OPTIONAL {{
                <{artist_uri}> owl:sameAs ?ulan .
                FILTER(CONTAINS(STR(?ulan), "ulan"))
            }}
            
            OPTIONAL {{
                ?event crm:P14_carried_out_by <{artist_uri}> ;
                       crm:P108_has_produced ?artwork .
                
                OPTIONAL {{
                    ?artwork crm:P102_has_title ?titleNode .
                    ?titleNode crm:P190_has_symbolic_content ?artworkTitle .
                }}
                
                OPTIONAL {{
                    ?artwork crm:P1_is_identified_by ?id .
                    ?id crm:P190_has_symbolic_content ?artworkIdentifier .
                }}

                OPTIONAL {{
                    ?artwork foaf:depiction ?artworkImageURL .
                }}
            }}
        }}
        """
        
        try:
            results = self.graph.query(query)
            
            if not results:
                return None
            
            artist_data = {
                'id': artist_uri.split('/')[-1],
                'uri': artist_uri,
                'name': None,
                'getty': None,
                'artworks': []
            }
            
            artworks_dict = {}
            
            for row in results:
                if row.name and not artist_data['name']:
                    artist_data['name'] = str(row.name)
                if row.ulan and not artist_data['getty']:
                    artist_data['getty'] = str(row.ulan)
                
                if row.artwork:
                    artwork_uri = str(row.artwork)
                    artwork_id = artwork_uri.split('/')[-1]
                    
                    if artwork_id not in artworks_dict:
                        artworks_dict[artwork_id] = {
                            'id': artwork_id,
                            'uri': artwork_uri,
                            'title': str(row.artworkTitle) if row.artworkTitle else None,
                            'imageURL': str(row.artworkImageURL) if row.artworkImageURL else None,
                            'inventoryNumber': str(row.artworkIdentifier) if row.artworkIdentifier else None
                        }
            
            artist_data['artworks'] = list(artworks_dict.values())
            
            logger.info(f"Retrieved artist details for: {artist_uri} with {len(artist_data['artworks'])} artworks")
            return artist_data
            
        except Exception as e:
            logger.error(f"Error querying artist details: {e}")
            return None

    def get_artist_by_getty_id(self, artist_getty_id) -> Dict[str, Any]:
        """Query specific artist by Getty ULAN ID from RDF store"""
        
        query = f"""
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        
        SELECT ?artist
        WHERE {{
            ?artist owl:sameAs <http://vocab.getty.edu/ulan/{artist_getty_id}> .
        }}
        """
        
        try:
            results = self.graph.query(query)
            artists = []
            for row in results:
                artist_uri = str(row.artist)
                artists.append(self.get_artist(artist_uri))
            
            return artists
            
        except Exception as e:
            logger.error(f"Error querying artist by Getty ID: {e}")
            return None


    def get_all_locations(self) -> list:
        """Query all locations from RDF store"""
        query = """
        PREFIX prov: <http://www.w3.org/ns/prov#>
        PREFIX crm: <http://www.cidoc-crm.org/cidoc-crm/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        
        SELECT ?location ?name ?tgn
        WHERE {
            ?location a prov:Location ;
                      a crm:E53_Place ;
                      rdfs:label ?name .
            OPTIONAL { ?location owl:sameAs ?tgn . FILTER(CONTAINS(STR(?tgn), "tgn")) }
        }
        ORDER BY ?name
        """
        
        try:
            results = self.graph.query(query)
            locations = []
            
            for row in results:
                location_uri = str(row.location)
                location_id = location_uri.split('/')[-1]
                
                location_data = {
                    'id': location_id,
                    'uri': location_uri,
                    'name': str(row.name),
                    'getty': str(row.tgn) if row.tgn else None
                }
                locations.append(location_data)
            
            logger.info(f"Retrieved {len(locations)} locations from RDF store")
            return locations
            
        except Exception as e:
            logger.error(f"Error querying locations: {e}")
            return []
    
    def get_location(self, location_uri: str) -> Dict[str, Any]:
        """Query specific location details from RDF store including all associated artworks"""
        query = f"""
        PREFIX prov: <http://www.w3.org/ns/prov#>
        PREFIX crm: <http://www.cidoc-crm.org/cidoc-crm/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
        
        SELECT ?name ?tgn ?artwork ?artworkTitle ?artworkIdentifier ?artworkImageURL
        WHERE {{
            <{location_uri}> a prov:Location ;
                            a crm:E53_Place ;
                            rdfs:label ?name .
            
            OPTIONAL {{
                <{location_uri}> owl:sameAs ?tgn .
                FILTER(CONTAINS(STR(?tgn), "tgn"))
            }}
            
            OPTIONAL {{
                ?event crm:P7_took_place_at <{location_uri}> ;
                       crm:P108_has_produced ?artwork .
                
                OPTIONAL {{
                    ?artwork crm:P102_has_title ?titleNode .
                    ?titleNode crm:P190_has_symbolic_content ?artworkTitle .
                }}
                
                OPTIONAL {{
                    ?artwork crm:P1_is_identified_by ?id .
                    ?id crm:P190_has_symbolic_content ?artworkIdentifier .
                }}
                
                OPTIONAL {{
                    ?artwork foaf:depiction ?artworkImageURL .
                }}
            }}
        }}
        """
        
        try:
            results = self.graph.query(query)
            
            if not results:
                return None
            
            location_data = {
                'id': location_uri.split('/')[-1],
                'uri': location_uri,
                'name': None,
                'getty': None,
                'artworks': []
            }
            
            artworks_dict = {}
            
            for row in results:
                if row.name and not location_data['name']:
                    location_data['name'] = str(row.name)
                if row.tgn and not location_data['getty']:
                    location_data['getty'] = str(row.tgn)
                
                if row.artwork:
                    artwork_uri = str(row.artwork)
                    artwork_id = artwork_uri.split('/')[-1]
                    
                    if artwork_id not in artworks_dict:
                        artworks_dict[artwork_id] = {
                            'id': artwork_id,
                            'uri': artwork_uri,
                            'title': str(row.artworkTitle) if row.artworkTitle else None,
                            'imageURL': str(row.artworkImageURL) if row.artworkImageURL else None,
                            'inventoryNumber': str(row.artworkIdentifier) if row.artworkIdentifier else None
                        }
            
            location_data['artworks'] = list(artworks_dict.values())
            
            logger.info(f"Retrieved location details for: {location_uri} with {len(location_data['artworks'])} artworks")
            return location_data
            
        except Exception as e:
            logger.error(f"Error querying location details: {e}")
            return None
        
    
    def get_all_events(self) -> list:
        """Query all provenance events from RDF store"""
        query = """
        PREFIX prov: <http://www.w3.org/ns/prov#>
        PREFIX crm: <http://www.cidoc-crm.org/cidoc-crm/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
        
        SELECT ?event ?type ?artwork ?artworkTitle ?artist ?artistName ?location ?locationName ?date
        WHERE {
            ?event a prov:Activity ;
                   a crm:E12_Production ;
                   rdfs:label ?type .
            
            OPTIONAL {
                ?event crm:P108_has_produced ?artwork .
                OPTIONAL {
                    ?artwork crm:P102_has_title ?titleNode .
                    ?titleNode crm:P190_has_symbolic_content ?artworkTitle .
                }
            }
            
            OPTIONAL {
                ?event crm:P14_carried_out_by ?artist .
                ?artist foaf:name ?artistName .
            }
            
            OPTIONAL {
                ?event crm:P7_took_place_at ?location .
                ?location rdfs:label ?locationName .
            }
            
            OPTIONAL {
                ?event crm:P4_has_time_span ?date .
            }
        }
        ORDER BY ?date
        """
        
        try:
            results = self.graph.query(query)
            events = []
            
            for row in results:
                event_uri = str(row.event)
                event_id = event_uri.split('/')[-1]
                
                event_data = {
                    'id': event_id,
                    'uri': event_uri,
                    'type': str(row.type) if row.type else None,
                    'artwork': {
                        'uri': str(row.artwork) if row.artwork else None,
                        'title': str(row.artworkTitle) if row.artworkTitle else None
                    } if row.artwork else None,
                    'artist': {
                        'uri': str(row.artist) if row.artist else None,
                        'name': str(row.artistName) if row.artistName else None
                    } if row.artist else None,
                    'location': {
                        'uri': str(row.location) if row.location else None,
                        'name': str(row.locationName) if row.locationName else None
                    } if row.location else None,
                    'date': str(row.date) if row.date else None
                }
                events.append(event_data)
            
            logger.info(f"Retrieved {len(events)} provenance events from RDF store")
            return events
            
        except Exception as e:
            logger.error(f"Error querying provenance events: {e}")
            return []
        
    def get_event(self, event_uri: str) -> Dict[str, Any]:
        """Query specific provenance event details from RDF store"""
        query = f"""
        PREFIX prov: <http://www.w3.org/ns/prov#>
        PREFIX crm: <http://www.cidoc-crm.org/cidoc-crm/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
        
        SELECT ?type ?artwork ?artworkTitle ?artworkIdentifier ?artworkImageURL
               ?artist ?artistName ?location ?locationName ?date
        WHERE {{
            <{event_uri}> a prov:Activity ;
                         a crm:E12_Production ;
                         rdfs:label ?type .
            
            OPTIONAL {{
                <{event_uri}> crm:P108_has_produced ?artwork .
                OPTIONAL {{
                    ?artwork crm:P102_has_title ?titleNode .
                    ?titleNode crm:P190_has_symbolic_content ?artworkTitle .
                }}
                OPTIONAL {{
                    ?artwork crm:P1_is_identified_by ?id .
                    ?id crm:P190_has_symbolic_content ?artworkIdentifier .
                }}
                OPTIONAL {{
                    ?artwork foaf:depiction ?artworkImageURL .
                }}
            }}
            
            OPTIONAL {{
                <{event_uri}> crm:P14_carried_out_by ?artist .
                ?artist foaf:name ?artistName .
            }}
            
            OPTIONAL {{
                <{event_uri}> crm:P7_took_place_at ?location .
                ?location rdfs:label ?locationName .
            }}
            
            OPTIONAL {{
                <{event_uri}> crm:P4_has_time_span ?date .
            }}
        }}
        """
        
        try:
            results = self.graph.query(query)
            
            if not results:
                return None
            
            event_data = {
                'id': event_uri.split('/')[-1],
                'uri': event_uri,
                'type': None,
                'artwork': None,
                'artist': None,
                'location': None,
                'date': None
            }
            
            for row in results:
                if row.type:
                    event_data['type'] = str(row.type)
                if row.artwork:
                    event_data['artwork'] = {
                        'uri': str(row.artwork),
                        'title': str(row.artworkTitle) if row.artworkTitle else None,
                        'inventoryNumber': str(row.artworkIdentifier) if row.artworkIdentifier else None,
                        'imageURL': str(row.artworkImageURL) if row.artworkImageURL else None
                    }
                if row.artist:
                    event_data['artist'] = {
                        'uri': str(row.artist),
                        'name': str(row.artistName) if row.artistName else None
                    }
                if row.location:
                    event_data['location'] = {
                        'uri': str(row.location),
                        'name': str(row.locationName) if row.locationName else None
                    }
                if row.date:
                    event_data['date'] = str(row.date)
            
            logger.info(f"Retrieved event details for: {event_uri}")
            return event_data
            
        except Exception as e:
            logger.error(f"Error querying event details: {e}")
            return None
    
    def get_provenance_chain(self, artwork_uri: str) -> list:
        """Query all provenance events for a specific artwork from RDF store"""
        query = f"""
        PREFIX prov: <http://www.w3.org/ns/prov#>
        PREFIX crm: <http://www.cidoc-crm.org/cidoc-crm/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
        
        SELECT ?event ?type ?artist ?artistName ?location ?locationName ?date
        WHERE {{
            ?event a prov:Activity ;
                   a crm:E12_Production ;
                   rdfs:label ?type ;
                   crm:P108_has_produced <{artwork_uri}> .
            
            OPTIONAL {{
                ?event crm:P14_carried_out_by ?artist .
                ?artist foaf:name ?artistName .
            }}
            
            OPTIONAL {{
                ?event crm:P7_took_place_at ?location .
                ?location rdfs:label ?locationName .
            }}
            
            OPTIONAL {{
                ?event crm:P4_has_time_span ?date .
            }}
        }}
        ORDER BY ?date
        """
        
        try:
            results = self.graph.query(query)
            events = []
            
            for row in results:
                event_uri = str(row.event)
                event_id = event_uri.split('/')[-1]
                
                event_data = {
                    'id': event_id,
                    'uri': event_uri,
                    'type': str(row.type) if row.type else None,
                    'artist': {
                        'uri': str(row.artist) if row.artist else None,
                        'name': str(row.artistName) if row.artistName else None
                    } if row.artist else None,
                    'location': {
                        'uri': str(row.location) if row.location else None,
                        'name': str(row.locationName) if row.locationName else None
                    } if row.location else None,
                    'date': str(row.date) if row.date else None
                }
                events.append(event_data)
            
            logger.info(f"Retrieved {len(events)} provenance events for artwork: {artwork_uri}")
            return events
            
        except Exception as e:
            logger.error(f"Error querying events for artwork: {e}")
            return []
        

    ##########################
    # General Querying [SPARQL]
    ##########################

    def execute_sparql(self, query: str) -> Any:
        """Execute arbitrary SPARQL query against RDF store"""
        try:
            results = self.graph.query(query)
            logger.info("Executed SPARQL query successfully")
            return results
        except Exception as e:
            logger.error(f"Error executing SPARQL query: {e}")
            return None
