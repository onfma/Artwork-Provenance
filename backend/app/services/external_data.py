"""
External data integration services
Integrates with DBpedia, Wikidata, Europeana, Getty, and Romanian heritage sources
"""

import httpx
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
        url = "https://www.wikidata.org/w/api.php"
        params = {
            'action': 'wbgetentities',
            'ids': entity_id,
            'props': 'labels',
            'languages': f'ro|en',
            'format': 'json'
        }
        
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




class DBpediaService:
    """Service for querying DBpedia"""
    
    def __init__(self):
        self.endpoint = SPARQLWrapper(settings.DBPEDIA_SPARQL)
        self.endpoint.setReturnFormat(JSON)
    

    async def search_artist(self, artist_name: str) -> Optional[Dict[str, Any]]:
        """Search for artist in DBpedia"""
        query = f"""
        PREFIX dbo: <http://dbpedia.org/ontology/>
        PREFIX dbp: <http://dbpedia.org/property/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema/>
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
        
        SELECT ?artist ?name ?birthDate ?deathDate ?abstract ?thumbnail
        WHERE {{
            ?artist a dbo:Artist ;
                    foaf:name ?name ;
                    dbo:abstract ?abstract .
            FILTER (lang(?abstract) = 'en')
            FILTER (regex(?name, "{artist_name}", "i"))
            OPTIONAL {{ ?artist dbo:birthDate ?birthDate }}
            OPTIONAL {{ ?artist dbo:deathDate ?deathDate }}
            OPTIONAL {{ ?artist dbo:thumbnail ?thumbnail }}
        }}
        LIMIT 5
        """
        
        try:
            self.endpoint.setQuery(query)
            results = self.endpoint.query().convert()
            return results
        except Exception as e:
            logger.error(f"Error querying DBpedia: {e}")
            return None
    
    async def get_artwork_info(self, artwork_name: str) -> Optional[Dict[str, Any]]:
        """Get artwork information from DBpedia"""
        query = f"""
        PREFIX dbo: <http://dbpedia.org/ontology/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema/>
        
        SELECT ?artwork ?label ?author ?museum ?abstract ?thumbnail
        WHERE {{
            ?artwork a dbo:Artwork ;
                     rdfs:label ?label ;
                     dbo:abstract ?abstract .
            FILTER (lang(?abstract) = 'en')
            FILTER (regex(?label, "{artwork_name}", "i"))
            OPTIONAL {{ ?artwork dbo:author ?author }}
            OPTIONAL {{ ?artwork dbo:museum ?museum }}
            OPTIONAL {{ ?artwork dbo:thumbnail ?thumbnail }}
        }}
        LIMIT 5
        """
        
        try:
            self.endpoint.setQuery(query)
            results = self.endpoint.query().convert()
            return results
        except Exception as e:
            logger.error(f"Error querying DBpedia: {e}")
            return None


class EuropeanaService:
    """Service for querying Europeana API"""
    
    def __init__(self):
        self.api_url = settings.EUROPEANA_API_URL
        self.api_key = settings.EUROPEANA_API_KEY
    
    async def search_artworks(self, query: str, rows: int = 10) -> Optional[List[Dict[str, Any]]]:
        """Search for artworks in Europeana"""
        if not self.api_key:
            logger.warning("Europeana API key not configured")
            return None
        
        url = f"{self.api_url}/search.json"
        params = {
            "wskey": self.api_key,
            "query": query,
            "rows": rows,
            "profile": "rich"
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Error querying Europeana: {e}")
            return None


class GettyService:
    """Service for querying Getty vocabularies (AAT, ULAN, TGN)"""
    
    def __init__(self):
        self.endpoint = SPARQLWrapper(settings.GETTY_AAT_SPARQL)
        self.endpoint.setReturnFormat(JSON)
    
    async def search_art_term(self, term: str) -> Optional[Dict[str, Any]]:
        """Search Art & Architecture Thesaurus (AAT)"""
        query = f"""
        PREFIX gvp: <http://vocab.getty.edu/ontology#>
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        
        SELECT ?concept ?label ?scopeNote
        WHERE {{
            ?concept a gvp:Concept ;
                     skos:prefLabel ?label ;
                     skos:inScheme aat: .
            FILTER (regex(?label, "{term}", "i"))
            OPTIONAL {{ ?concept skos:scopeNote ?scopeNote }}
        }}
        LIMIT 10
        """
        
        try:
            self.endpoint.setQuery(query)
            results = self.endpoint.query().convert()
            return results
        except Exception as e:
            logger.error(f"Error querying Getty AAT: {e}")
            return None
    
    async def search_artist_ulan(self, artist_name: str) -> Optional[Dict[str, Any]]:
        """Search Union List of Artist Names (ULAN)"""
        query = f"""
        PREFIX gvp: <http://vocab.getty.edu/ontology#>
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
        
        SELECT ?artist ?name ?birthDate ?deathDate ?nationality
        WHERE {{
            ?artist a gvp:PersonConcept ;
                    skos:prefLabel ?name ;
                    skos:inScheme ulan: .
            FILTER (regex(?name, "{artist_name}", "i"))
            OPTIONAL {{ ?artist gvp:biographyPreferred/gvp:estStart ?birthDate }}
            OPTIONAL {{ ?artist gvp:biographyPreferred/gvp:estEnd ?deathDate }}
            OPTIONAL {{ ?artist gvp:nationalityPreferred/skos:prefLabel ?nationality }}
        }}
        LIMIT 10
        """
        
        try:
            self.endpoint.setQuery(query)
            results = self.endpoint.query().convert()
            return results
        except Exception as e:
            logger.error(f"Error querying Getty ULAN: {e}")
            return None
    
    async def search_place_tgn(self, place_name: str) -> Optional[Dict[str, Any]]:
        """Search Thesaurus of Geographic Names (TGN)"""
        query = f"""
        PREFIX gvp: <http://vocab.getty.edu/ontology#>
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        
        SELECT ?place ?name ?coordinates ?placeType
        WHERE {{
            ?place a gvp:AdminPlaceConcept ;
                   skos:prefLabel ?name ;
                   skos:inScheme tgn: .
            FILTER (regex(?name, "{place_name}", "i"))
            OPTIONAL {{ ?place foaf:focus/gvp:coordPreferred ?coordinates }}
            OPTIONAL {{ ?place gvp:placeTypePreferred/skos:prefLabel ?placeType }}
        }}
        LIMIT 10
        """
        
        try:
            self.endpoint.setQuery(query)
            results = self.endpoint.query().convert()
            return results
        except Exception as e:
            logger.error(f"Error querying Getty TGN: {e}")
            return None


