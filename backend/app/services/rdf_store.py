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


logger = structlog.get_logger()


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

            if artwork_data.get('type_uri'):
                self.graph.add((artwork_ref, crm.P2_has_type, URIRef(artwork_data.get('type_uri'))))
            if artwork_data.get('subject_uri'):
                self.graph.add((artwork_ref, crm.P15_was_influenced_by, URIRef(artwork_data.get('subject_uri'))))
            if artwork_data.get('material_uri'):
                self.graph.add((artwork_ref, crm.P45_consists_of, URIRef(artwork_data.get('material_uri'))))
            if artwork_data.get('provider_uri'):
                self.graph.add((artwork_ref, crm.P70_documents, URIRef(artwork_data.get('provider_uri'))))
            if artwork_data.get('institute_uri'):
                self.graph.add((artwork_ref, crm.P50i_is_currently_held_by, URIRef(artwork_data.get('institute_uri'))))
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
            
            if entity_type == 'provider':
                self.graph.add((entity_ref, RDF.type, prov.Agent))
                self.graph.add((entity_ref, OWL.sameAs, URIRef(f"{entity_link}")))
            elif entity_type == 'institute':
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
            
            if 'location' in location_data:
                for loc_name in location_data['location']:
                    self.graph.add((location_ref, RDFS.label, Literal(loc_name)))
            
            if 'locationTGN' in location_data and location_data['locationTGN']:
                self.graph.add((location_ref, OWL.sameAs, URIRef(f"{location_data['locationTGN']}")))

            logger.info(f"Added location to RDF store: {location_uri}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding location to RDF store: {e}")
            return False

    def add_provenance_event(self, event_uri: str, artwork_uri: str, artist_uri: str, event_type: str, location_uri: str) -> bool:
        """Add provenance event to RDF store"""
        try:
            prov = self.ns['prov']
            crm = self.ns['crm']
            event_ref = URIRef(event_uri)
            
            self.graph.add((event_ref, RDF.type, prov.Activity))
            self.graph.add((event_ref, RDF.type, crm.E12_Production))
            self.graph.add((event_ref, RDFS.label, Literal(event_type)))

            self.graph.add((event_ref, crm.P14_carried_out_by, URIRef(artist_uri)))
            self.graph.add((event_ref, crm.P7_took_place_at, URIRef(location_uri)))
            self.graph.add((event_ref, crm.P108_has_produced, URIRef(artwork_uri)))

            logger.info(f"Added provenance event to RDF store: {event_uri}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding provenance event to RDF store: {e}")
            return False

    ##########################
    # Querying RDFs
    ##########################

    def get_all_artworks(self) -> list:
        """Query all artworks from RDF store"""
        query = """
        PREFIX prov: <http://www.w3.org/ns/prov#>
        PREFIX crm: <http://www.cidoc-crm.org/cidoc-crm/>
        
        SELECT ?artwork ?identifier ?title
        WHERE {
            ?artwork a prov:Entity ;
                     a crm:E22_Man_Made_Object .
            
            OPTIONAL {
                ?artwork crm:P1_is_identified_by ?id .
                ?id crm:P190_has_symbolic_content ?identifier .
            }
            
            OPTIONAL {
                ?artwork crm:P102_has_title ?titleNode .
                ?titleNode crm:P190_has_symbolic_content ?title .
            }
        }
        ORDER BY ?identifier
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
                    'title': str(row.title) if row.title else None
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
        
        SELECT ?identifier ?title ?type ?typeLabel ?subject ?subjectLabel
               ?material ?materialLabel ?provider ?institute
               ?artist ?artistName ?location ?locationName ?event
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
                <{artwork_uri}> crm:P2_has_type ?type .
                ?type rdfs:label ?typeLabel .
            }}
            
            OPTIONAL {{
                <{artwork_uri}> crm:P15_was_influenced_by ?subject .
                ?subject rdfs:label ?subjectLabel .
            }}
            
            OPTIONAL {{
                <{artwork_uri}> crm:P45_consists_of ?material .
                ?material rdfs:label ?materialLabel .
            }}
            
            OPTIONAL {{
                <{artwork_uri}> crm:P70_documents ?provider .
            }}
            
            OPTIONAL {{
                <{artwork_uri}> crm:P50i_is_currently_held_by ?institute .
            }}
            
            OPTIONAL {{
                ?event crm:P108_has_produced <{artwork_uri}> ;
                       crm:P14_carried_out_by ?artist ;
                       crm:P7_took_place_at ?location .
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
                'type': None,
                'subject': None,
                'material': None,
                'provider': None,
                'institute': None,
                'artist': None,
                'location': None,
                'event': None
            }
            
            for row in results:
                if row.identifier:
                    artwork_data['inventoryNumber'] = str(row.identifier)
                if row.title:
                    artwork_data['title'] = str(row.title)
                if row.typeLabel:
                    artwork_data['type'] = {
                        'uri': str(row.type) if row.type else None,
                        'label': str(row.typeLabel)
                    }
                if row.subjectLabel:
                    artwork_data['subject'] = {
                        'uri': str(row.subject) if row.subject else None,
                        'label': str(row.subjectLabel)
                    }
                if row.materialLabel:
                    artwork_data['material'] = {
                        'uri': str(row.material) if row.material else None,
                        'label': str(row.materialLabel)
                    }
                if row.provider:
                    artwork_data['provider'] = str(row.provider)
                if row.institute:
                    artwork_data['institute'] = str(row.institute)
                if row.artistName:
                    artwork_data['artist'] = {
                        'uri': str(row.artist) if row.artist else None,
                        'name': str(row.artistName)
                    }
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


    def get_all_artists(self) -> list:
        """Query all artists from RDF store"""
        query = """
        PREFIX prov: <http://www.w3.org/ns/prov#>
        PREFIX crm: <http://www.cidoc-crm.org/cidoc-crm/>
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        
        SELECT ?artist ?name ?ulan
        WHERE {
            ?artist a prov:Agent ;
                    a crm:E21_Person ;
                    foaf:name ?name .
            OPTIONAL { ?artist owl:sameAs ?ulan . FILTER(CONTAINS(STR(?ulan), "ulan")) }
        }
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
        
        SELECT ?name ?ulan ?artwork ?artworkTitle ?artworkIdentifier
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
                            'inventoryNumber': str(row.artworkIdentifier) if row.artworkIdentifier else None
                        }
            
            artist_data['artworks'] = list(artworks_dict.values())
            
            logger.info(f"Retrieved artist details for: {artist_uri} with {len(artist_data['artworks'])} artworks")
            return artist_data
            
        except Exception as e:
            logger.error(f"Error querying artist details: {e}")
            return None
