"""
Data importer service for loading external datasets
Supports Romanian heritage data (INP), Europeana EDM, and other formats
"""

import requests
import structlog
from uuid import uuid4
from typing import Dict, Any
import xml.etree.ElementTree as ET

logger = structlog.get_logger()

base_uri = "http://arp-greatteam.org/heritage-provenance/"


class DataImporter:
    """Import data from external sources"""
    
    def __init__(self, rdf_service):
        self.rdf_service = rdf_service
        self.created_artists = {}  # {artist_name: artist_uri}
        self.created_locations = {}  # {location_name: location_uri}
        self.created_entities = {}  # {(entity_name, entity_link): entity_uri}
        
    def import_from_url(self, url: str, format: str = "edm") -> Dict[str, Any]:
        """Download and import data from URL"""
        
        try:
            logger.info(f"Downloading data from: {url}")
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            if format == "edm":
                return self.import_edm_xml(response.content)
            else:
                raise ValueError(f"Unsupported format: {format}")
                
        except Exception as e:
            logger.error(f"Error importing from URL: {e}")
            raise
    
    def import_edm_xml(self, xml_content: bytes) -> Dict[str, Any]:
        """Import Europeana Data Model XML"""
        try:
            root = ET.fromstring(xml_content)
            
            ns = {
                'edm': "http://www.europeana.eu/schemas/edm/",
                'dc': "http://purl.org/dc/elements/1.1/",
                'ore': "http://www.openarchives.org/ore/terms/",
                'dcterms': "http://purl.org/dc/terms/",
                'rdf': "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
            }
            
            errors = []
            imported_count = 0
            
            for artwork in root.findall('.//edm:ProvidedCHO', ns):
                try:
                    success = self._parse_edm_cho(artwork, ns)
                    if success:
                        imported_count += 1
                    else:
                        errors.append(f"Failed to import artwork with identifier: {artwork.find('dc:identifier', ns).text if artwork.find('dc:identifier', ns) is not None else 'unknown'}")
                except Exception as e:
                    errors.append(f"Exception: {str(e)}")
                    logger.warning(f"Error processing Artworks: {e}")
            logger.info(f"Imported {imported_count} artworks from EDM XML")
            
            return {
                "imported": imported_count,
                "errors": len(errors),
                "error_details": errors[:10]
            }

        except Exception as e:
            logger.error(f"Error parsing EDM XML: {e}")
            raise
    
    def _find_or_create_artist(self, creator_name: str, creator_ulan: str = None) -> str:
        """Find existing artist or create new one"""
        if not creator_name:
            creator_name = "Unknown Artist"
        
        if creator_name in self.created_artists:
            logger.debug(f"Reusing existing artist: {creator_name}")
            return self.created_artists[creator_name]
        
        artist_id = str(uuid4())
        artist_uri = f"{base_uri}artist/{artist_id}"
        artist_data = {
            'creator': creator_name,
            'creatorULAN': creator_ulan
        }
        
        if self.rdf_service.add_artist(artist_uri, artist_data):
            self.created_artists[creator_name] = artist_uri
            logger.info(f"Created new artist: {creator_name}")
            return artist_uri
        
        return None
    
    def _find_or_create_location(self, location_names: list, location_tgn: str = None) -> str:
        """Find existing location or create new one"""
        if not location_names:
            location_names = ["Unknown Location"]
        
        location_key = location_names[0]
        
        if location_key in self.created_locations:
            logger.debug(f"Reusing existing location: {location_key}")
            return self.created_locations[location_key]
        
        location_id = str(uuid4())
        location_uri = f"{base_uri}location/{location_id}"
        location_data = {
            'location': location_names,
            'locationTGN': location_tgn
        }
        
        if self.rdf_service.add_location(location_uri, location_data):
            self.created_locations[location_key] = location_uri
            logger.info(f"Created new location: {location_key}")
            return location_uri
        
        return None
    
    def _find_or_create_entity(self, entity_type: str, names: list, link: str = None) -> str:
        if not names:
            names = ["Unknown"]
        
        entity_key = names[0], link
        
        if entity_key in self.created_entities:
            logger.debug(f"Reusing existing entity: {entity_key}")
            return self.created_entities[entity_key]
        
        entity_id = str(uuid4())
        entity_uri = f"{base_uri}attributes/{entity_id}"
        
        if self.rdf_service.add_entity(entity_type, entity_uri, names[0], link):
            self.created_entities[entity_key] = entity_uri
            logger.info(f"Created new entity: {entity_key}")
            return entity_uri
        
        return None
        

    def _parse_edm_cho(self, cho_element, namespaces: Dict[str, str]) -> bool:
        """Parse a single EDM ProvidedCHO element (ARTWORK) with all additional information"""
        
        def get_text(element, tag, ns_key='dc'):
            elem = element.find(f'{ns_key}:{tag}', namespaces)
            return elem.text if elem is not None else None
        
        def get_attr_text(element, tag, ns_key='dc'):
            for el in element.findall(f'.//{ns_key}:{tag}', namespaces):
                val = el.get('{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource')
                if val:
                    return val
            return None
        
        def get_all_text(element, tag, ns_key='dc'):
            return [e.text for e in element.findall(f'{ns_key}:{tag}', namespaces) if e.text]
        

        inventoryNumber = get_text(cho_element, 'identifier', 'dc')
        if not inventoryNumber:
            return False
        
        creator_name = get_text(cho_element, 'creator', 'dc')
        creator_ulan = get_attr_text(cho_element, 'creator', 'dc')
        artist_uri = self._find_or_create_artist(creator_name, creator_ulan)
        
        location_names = get_all_text(cho_element, 'spatial', 'dcterms')
        location_tgn = get_attr_text(cho_element, 'spatial', 'dcterms')
        location_uri = self._find_or_create_location(location_names, location_tgn)



        type_names = get_all_text(cho_element, 'type', 'dc')
        type_aat = get_attr_text(cho_element, 'type', 'dc')
        type_uri = self._find_or_create_entity('type', type_names, type_aat)

        subject_name = get_text(cho_element, 'subject', 'dc')
        subject_aat = get_attr_text(cho_element, 'subject', 'dc')
        subject_uri = self._find_or_create_entity('subject', [subject_name] if subject_name else [], subject_aat)
        
        material_names = get_all_text(cho_element, 'medium', 'dcterms')
        material_aat = get_attr_text(cho_element, 'medium', 'dcterms')
        material_uri = self._find_or_create_entity('material', material_names, material_aat)

        provider_wikidata_link = get_text(cho_element, 'provider', 'edm')
        provider_uri = self._find_or_create_entity('provider', [], provider_wikidata_link)

        institute_name = get_text(cho_element, 'dataProvider', 'edm')
        institute_uri = self._find_or_create_entity('institute', [institute_name] if institute_name else [], None)



        artwork_id = str(uuid4())
        artwork_uri = f"{base_uri}artwork/{artwork_id}"
        artwork_data = {
            'inventoryNumber': inventoryNumber,
            'title': get_text(cho_element, 'title', 'dc'),
            'description': get_all_text(cho_element, 'description', 'dc'),
            'creationDate': get_text(cho_element, 'created', 'dcterms'),
            'dimensions': get_all_text(cho_element, 'extent', 'dcterms'),
            'imageURL': get_attr_text(cho_element, 'isShownBy', 'edm'),
            'type_uri': type_uri,
            'subject_uri': subject_uri,
            'material_uri': material_uri,
            'provider_uri': provider_uri,
            'institute_uri': institute_uri
        }
        success_artwork = self.rdf_service.add_artwork(artwork_uri, artwork_data)
        
        if not success_artwork:
            return False
        
        if artist_uri and location_uri:
            event_id = str(uuid4())
            event_uri = f"{base_uri}event/{event_id}"
            self.rdf_service.add_provenance_event(event_uri, artwork_uri, artist_uri, 'creation', location_uri)
        
        return True
