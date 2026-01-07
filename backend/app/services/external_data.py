"""
External data integration services
Integrates with DBpedia, Wikidata, Europeana, Getty, and Romanian heritage sources
"""

import httpx
from typing import Dict, Any, List, Optional
import structlog
from SPARQLWrapper import SPARQLWrapper, JSON

from app.config import settings

logger = structlog.get_logger()


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


class WikidataService:
    """Service for querying Wikidata"""
    
    def __init__(self):
        self.endpoint = SPARQLWrapper(settings.WIKIDATA_SPARQL)
        self.endpoint.setReturnFormat(JSON)
        self.endpoint.addCustomHttpHeader("User-Agent", "HeritageProvenanceSystem/1.0")
    
    async def search_artist(self, artist_name: str) -> Optional[Dict[str, Any]]:
        """Search for artist in Wikidata"""
        query = f"""
        SELECT ?artist ?artistLabel ?birthDate ?deathDate ?nationality ?nationalityLabel ?image
        WHERE {{
            ?artist wdt:P31 wd:Q5 ;
                    wdt:P106 ?occupation ;
                    rdfs:label ?artistLabel .
            ?occupation wdt:P279* wd:Q483501 .
            FILTER (lang(?artistLabel) = 'en')
            FILTER (regex(?artistLabel, "{artist_name}", "i"))
            OPTIONAL {{ ?artist wdt:P569 ?birthDate }}
            OPTIONAL {{ ?artist wdt:P570 ?deathDate }}
            OPTIONAL {{ ?artist wdt:P27 ?nationality }}
            OPTIONAL {{ ?artist wdt:P18 ?image }}
            SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en,ro". }}
        }}
        LIMIT 5
        """
        
        try:
            self.endpoint.setQuery(query)
            results = self.endpoint.query().convert()
            return results
        except Exception as e:
            logger.error(f"Error querying Wikidata: {e}")
            return None
    
    async def get_artwork_info(self, wikidata_id: str) -> Optional[Dict[str, Any]]:
        """Get artwork information from Wikidata by ID"""
        query = f"""
        SELECT ?artwork ?artworkLabel ?creatorLabel ?inceptionDate ?materialLabel ?locationLabel ?image ?description
        WHERE {{
            BIND(wd:{wikidata_id} AS ?artwork)
            ?artwork wdt:P31 ?artworkType .
            ?artworkType wdt:P279* wd:Q838948 .
            OPTIONAL {{ ?artwork wdt:P170 ?creator }}
            OPTIONAL {{ ?artwork wdt:P571 ?inceptionDate }}
            OPTIONAL {{ ?artwork wdt:P186 ?material }}
            OPTIONAL {{ ?artwork wdt:P276 ?location }}
            OPTIONAL {{ ?artwork wdt:P18 ?image }}
            OPTIONAL {{ ?artwork schema:description ?description . FILTER(lang(?description) = "en") }}
            SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en,ro". }}
        }}
        """
        
        try:
            self.endpoint.setQuery(query)
            results = self.endpoint.query().convert()
            return results
        except Exception as e:
            logger.error(f"Error querying Wikidata: {e}")
            return None
    
    async def search_location(self, location_name: str) -> Optional[Dict[str, Any]]:
        """Search for location in Wikidata"""
        query = f"""
        SELECT ?location ?locationLabel ?coordinates ?countryLabel
        WHERE {{
            ?location rdfs:label ?locationLabel .
            FILTER (lang(?locationLabel) = 'en')
            FILTER (regex(?locationLabel, "{location_name}", "i"))
            ?location wdt:P31 ?type .
            ?type wdt:P279* wd:Q41176 .
            OPTIONAL {{ ?location wdt:P625 ?coordinates }}
            OPTIONAL {{ ?location wdt:P17 ?country }}
            SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en,ro". }}
        }}
        LIMIT 5
        """
        
        try:
            self.endpoint.setQuery(query)
            results = self.endpoint.query().convert()
            return results
        except Exception as e:
            logger.error(f"Error querying Wikidata: {e}")
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


class RomanianHeritageService:
    """Service for Romanian heritage integration"""
    
    def __init__(self):
        self.api_url = settings.ROMANIAN_HERITAGE_API
    
    async def search_monuments(self, query: str) -> Optional[List[Dict[str, Any]]]:
        """Search Romanian monuments and heritage sites"""
        # This is a placeholder - actual Romanian heritage API would be implemented here
        # Could integrate with INP (Institutul Național al Patrimoniului)
        logger.info(f"Searching Romanian heritage for: {query}")
        
        # Mock implementation
        return [{
            "name": f"Romanian Heritage: {query}",
            "type": "monument",
            "location": "Romania",
            "description": "Romanian cultural heritage item"
        }]
    
    async def get_romanian_artworks(self, museum: str = None) -> Optional[List[Dict[str, Any]]]:
        """Get artworks from Romanian museums"""
        # Integration with Romanian museum databases
        # Examples: MNAC (Muzeul Național de Artă Contemporană), 
        # MNAR (Muzeul Național de Artă al României)
        logger.info(f"Fetching Romanian artworks from museum: {museum or 'all'}")
        
        return []
