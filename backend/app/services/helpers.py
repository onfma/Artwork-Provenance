import structlog
from typing import Dict, Any
from app.services.external_data import WikidataService

logger = structlog.get_logger()
wikidata = WikidataService()

##########################
# WikiData helpers
##########################

def wikidata_parser_for_artist(wikidata_data: Dict[str, Any]) -> Dict[str, Any]:
    """Parse Wikidata response to extract relevant artist information"""
    
    parsed_data = {}
    
    try:
        entities = wikidata_data.get('entities', {})
        for entity_id, entity_data in entities.items():
            
            description = entity_data.get('descriptions', {}).get('ro', {}).get('value', '')
            if description is None or description == '':
                description = entity_data.get('descriptions', {}).get('en', {}).get('value', '')
            parsed_data['description'] = description
            
            claims = entity_data.get('claims', {})
            
            # birth date (P569)
            birth_date_claims = claims.get('P569', [])
            if birth_date_claims:
                birth_date_value = birth_date_claims[0]['mainsnak']['datavalue']['value']['time']
                parsed_data['birth_date'] = format_wikidata_date(birth_date_value)
            
            # death date (P570)
            death_date_claims = claims.get('P570', [])
            if death_date_claims:
                death_date_value = death_date_claims[0]['mainsnak']['datavalue']['value']['time']
                parsed_data['death_date'] = format_wikidata_date(death_date_value)

            # image (P18)
            image_claims = claims.get('P18', [])
            if image_claims:
                image_name = image_claims[0]['mainsnak']['datavalue']['value']
                image_url = f"https://commons.wikimedia.org/wiki/Special:FilePath/{image_name.replace(' ', '_')}"
                parsed_data['image_url'] = image_url

            
    except Exception as e:
        logger.error(f"Error parsing Wikidata for artist: {e}")
    
    return parsed_data

def wikidata_parser_for_artwork(wikidata_data: Dict[str, Any]) -> Dict[str, Any]:
    """Parse Wikidata response to extract relevant artwork information"""
    
    parsed_data = {}
    
    try:
        entities = wikidata_data.get('entities', {})
        for entity_id, entity_data in entities.items():
            
            description = entity_data.get('descriptions', {}).get('en', {}).get('value', '')
            if not description:
                description = entity_data.get('descriptions', {}).get('ro', {}).get('value', '')
            parsed_data['description'] = description
            
            
            claims = entity_data.get('claims', {})
            
            # inception date (P571) + publication date (P577)
            inception_claims = claims.get('P577', []) + claims.get('P571', [])
            if inception_claims:
                inception_value = inception_claims[0]['mainsnak']['datavalue']['value']['time']
                parsed_data['inception_date'] = format_wikidata_date(inception_value)
            
            # location (P276) + location of first performance (P4647)
            location_claims = claims.get('P276', []) + claims.get('P4647', [])
            if location_claims:
                location_id = location_claims[0].get('mainsnak', {}).get('datavalue', {}).get('value', {}).get('id')
                if location_id:
                    parsed_data['location'] = wikidata.get_entity_label(location_id)
            
            # image (P18)
            image_claims = claims.get('P18', [])
            if image_claims:
                image_name = image_claims[0]['mainsnak']['datavalue']['value']
                image_url = f"https://commons.wikimedia.org/wiki/Special:FilePath/{image_name.replace(' ', '_')}"
                parsed_data['image_url'] = image_url
            
    except Exception as e:
        logger.error(f"Error parsing Wikidata for artwork: {e}")
    
    return parsed_data


def format_wikidata_date(date_string: str) -> str:
    """Format Wikidata date string to readable format"""
    try:
        date_string = date_string.lstrip('+').lstrip('-')
        date_part = date_string.split('T')[0]
        
        from datetime import datetime
        parsed_date = datetime.strptime(date_part, '%Y-%m-%d')
        return parsed_date.strftime('%B %d, %Y')
    except Exception as e:
        logger.error(f"Error formatting date {date_string}: {e}")
        return date_string
    


