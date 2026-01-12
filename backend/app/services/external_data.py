"""
External data integration services
Integrates with Wikidata, Getty, and Romanian heritage sources
"""

import httpx
import aiohttp
import structlog
from app.config import settings
from typing import Dict, Any, List, Optional
from SPARQLWrapper import SPARQLWrapper, JSON


logger = structlog.get_logger()


class WikidataService:
    """Service for querying Wikidata"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'HeritageProvenanceSystem/1.0 (https://github.com/onfma/Artwork-Provenance; contact@yahoo.com)'
        }

    async def search_wikidata(self, search_term):
        """Search Wikidata entities"""
        
        url = "https://www.wikidata.org/w/api.php"
        params = {
            'action': 'wbsearchentities',
            'format': 'json',
            'language': 'en',
            'search': search_term
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, headers=self.headers, timeout=10.0)
                response.raise_for_status()
                results = response.json()
                
                return results
        
        except Exception as e:
            logger.error(f"HTTP error querying Wikidata API: {e}")
            return None
    
    async def get_entity(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Get entity details from Wikidata by ID"""
        url = "https://www.wikidata.org/wiki/Special:EntityData/{}.json".format(entity_id)
    
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=self.headers, timeout=10.0)
                response.raise_for_status()
                return response.json()
        
        except Exception as e:
            logger.error(f"HTTP error getting Wikidata entity {entity_id}: {e}")
            return None
    
    async def get_entity_label(self, entity_id: str) -> Optional[str]:
        """Get the label (name) for a Wikidata entity by ID"""
        
        try:
            data = await self.get_entity(entity_id) 
            entity_data = data.get('entities', {}).get(entity_id, {})
            labels = entity_data.get('labels', {})
            
            if 'ro' in labels:
                return labels['ro']['value']
            elif 'en' in labels:
                return labels['en']['value']
            elif labels:
                return next(iter(labels.values()))['value']
            
            return None
        
        except Exception as e:
            logger.error(f"HTTP error getting label for entity {entity_id}: {e}")
            return None    


class GettyService:
    """Service for querying Getty vocabularies (AAT, ULAN, TGN)"""
    
    def __init__(self):
        self.endpoint = SPARQLWrapper(settings.GETTY_AAT_SPARQL)
        self.endpoint.setReturnFormat(JSON)
    
    async def get_wikidata_id(self, getty_link: str) -> Optional[str]:
        """Extract Wikidata ID from Getty link if available"""
        artist_id = getty_link.split("/")[-1]
        
        query = f"""
        PREFIX gvp: <http://vocab.getty.edu/ontology#>
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

        SELECT ?wikidataID
        WHERE {{
            ulan:{artist_id} skos:exactMatch ?wikidataID .
            FILTER(CONTAINS(STR(?wikidataID), "wikidata.org"))
        }}
        LIMIT 1
        """
        
        try:
            self.endpoint.setQuery(query)
            results = self.endpoint.query().convert()
            bindings = results.get("results", {}).get("bindings", [])
            
            if bindings:
                wikidata_uri = bindings[0]["wikidataID"]["value"]
                wikidata_id = wikidata_uri.split("/")[-1]
                return wikidata_id
            
            return None
        
        except Exception as e:
            logger.error(f"Error querying Getty for Wikidata ID: {e}")
            return None
    
    async def get_location_parent(self, location_link: str) -> Optional[str]:
        """Get broader location from Getty TGN"""
 
        location_id = location_link.split("/")[-1]
        logger.debug(f"Getting broader location for Getty TGN ID: {location_id}")
        
        query = f"""
        PREFIX gvp: <http://vocab.getty.edu/ontology#>
        PREFIX tgn: <http://vocab.getty.edu/tgn/>

        SELECT ?broaderLocation
        WHERE {{
            tgn:{location_id} gvp:parentString ?broaderLocation .
        }}
        LIMIT 1
        """
        
        try:
            self.endpoint.setQuery(query)
            results = self.endpoint.query().convert()

            location = results.get("results", {}).get("bindings", []).get[0].get("broaderLocation", {}).get("value", None)
            if location:
                return location
                
            return None
        
        except Exception as e:
            logger.error(f"Error querying Getty for broader location: {e}")
            return None

    async def get_artist_network(self, artist_getty_link: str) -> Dict[str, Any]:
        """Get artist network based on student_of/teacher_of relationships from Getty ULAN"""

        def _results_formater(results: Dict[str, Any]) -> Dict[str, Any]:
            """Format Getty SPARQL results into structured dict"""
            bindings = results.get("results", {}).get("bindings", [])
            
            formatted = {
                "nodes": [],
                "edges": []
            }
            
            for binding in bindings:
                related_artist = binding.get("relatedArtist", {}).get("value", "")
                relationship_type = binding.get("relationshipType", {}).get("value", "")
                artist_name = binding.get("relatedArtistName", {}).get("value", "Unknown")
                
                # Extract ID from URI
                artist_id = related_artist.split("/")[-1] if related_artist else None
                
                if artist_id:
                    formatted["nodes"].append({
                        "id": artist_id,
                        "uri": related_artist,
                        "name": artist_name
                    })
                    
                    formatted["edges"].append({
                        "target": artist_id,
                        "relationship": relationship_type
                    })
            
            return formatted
        
        artist_id = "ulan:" + artist_getty_link.split("/")[-1]
        
        query = f"""
        PREFIX ulan: <http://vocab.getty.edu/ulan/>
        PREFIX gvp:  <http://vocab.getty.edu/ontology#>
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

        SELECT
        ?relatedArtist
        ?relationshipType
        (SAMPLE(COALESCE(?enLabel, ?anyLabel)) AS ?relatedArtistName)
        WHERE {{
        {{
            ?relatedArtist gvp:ulan1101_teacher_of {artist_id} .
            BIND("student_of" AS ?relationshipType)
        }}
        UNION
        {{
            {artist_id} gvp:ulan1101_teacher_of ?relatedArtist .
            BIND("teacher_of" AS ?relationshipType)
        }}

        OPTIONAL {{
            ?relatedArtist skos:prefLabel ?enLabel .
            FILTER (lang(?enLabel) = "en")
        }}

        OPTIONAL {{
            ?relatedArtist skos:prefLabel ?anyLabel .
        }}
        }}
        GROUP BY ?relatedArtist ?relationshipType

        """
        
        try:
            self.endpoint.setQuery(query)
            results = self.endpoint.query().convert()
            results =  _results_formater(results)
            if results["nodes"] or results["edges"]:
                return results
            else:
                return {}
        except Exception as e:
            logger.error(f"Error querying Getty for artist network: {e}")
            return {}
        

    





