from typing import Optional, Dict, List, Any
import requests
import logging

logger = logging.getLogger(__name__)

class DBService:
    """Service class to handle all database interactions"""
    
    API_URL = 'https://api.jsonbin.io/v3/b/67aa6b3aacd3cb34a8dd1abb'
    API_HEADERS = {
        'X-Master-Key': '$2a$10$j9N2X2cOS686Gk5IRXITw.8JhMMn9o/66t2N9h2twDPIkLse3uVHW'
    }

    @classmethod
    def get_all_records(cls) -> List[Dict[str, Any]]:
        """Fetch all records from DB"""
        try:
            response = requests.get(cls.API_URL, headers=cls.API_HEADERS)
            if response.status_code == 200:
                return response.json()['record']
            logger.error("Failed to fetch data from DB: %s", response.status_code)
        except Exception as e:
            logger.error("Error accessing DB: %s", str(e))
            logger.exception("Full traceback:")
        return []

    @classmethod
    def find_account_by_id(cls, member_id: str) -> Optional[Dict[str, Any]]:
        """Find a specific account by ID"""
        records = cls.get_all_records()
        for record in records:
            if record['memberID'].strip("'") == member_id.strip("'"):
                return record
        return None

    @classmethod
    def get_child_accounts(cls, child_ids: str) -> List[Dict[str, Any]]:
        """Get details for all child accounts"""
        if not child_ids:
            return []
            
        child_details = []
        records = cls.get_all_records()
        
        # Split and clean the child IDs
        ids = [id.strip() for id in child_ids.split(',')]
        
        for child_id in ids:
            for record in records:
                if record['memberID'].strip("'") == child_id.strip("'"):
                    child_details.append({
                        'memberID': record['memberID'],
                        'name': record['name'],
                        'dob': record['dob'],
                        'policyEndDate': record['policyEndDate']
                    })
                    break
                    
        return child_details 