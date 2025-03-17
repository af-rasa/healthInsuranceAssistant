import requests
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)

class ConnectionManager:
    """
    Manages connections to the database API.
    Currently supports JSONbin.io for member data retrieval.
    """
    
    def __init__(self):
        self.base_url = "https://api.jsonbin.io/v3/b/67aa6b3aacd3cb34a8dd1abb"
        self.headers = {
            'X-Master-Key': '$2a$10$j9N2X2cOS686Gk5IRXITw.8JhMMn9o/66t2N9h2twDPIkLse3uVHW'
        }
    
    def get_member_data(self, member_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves member data from the database by member ID.
        
        Args:
            member_id: The member's unique identifier
            
        Returns:
            Dictionary containing member data if found, None otherwise
        """
        try:
            response = requests.get(self.base_url, headers=self.headers)
            
            if response.status_code == 200:
                data = response.json()
                records = data['record']
                
                # Find matching member by ID
                member_record = next(
                    (record for record in records if record['memberID'] == member_id),
                    None
                )
                
                return member_record
            
            logger.error(f"Failed to retrieve data: HTTP {response.status_code}")
            return None
            
        except Exception as e:
            logger.error(f"Error accessing database API: {str(e)}")
            return None
    
    def get_child_account_details(self, child_ids_str: str) -> List[Dict[str, Any]]:
        """
        Retrieves details for child accounts based on comma-separated IDs.
        
        Args:
            child_ids_str: Comma-separated list of child member IDs
            
        Returns:
            List of dictionaries containing child account details
        """
        try:
            response = requests.get(self.base_url, headers=self.headers)
            
            if response.status_code == 200:
                data = response.json()
                records = data['record']
                
                child_ids = [id.strip() for id in child_ids_str.split(',')]
                child_details = []
                
                # Fetch details for each child account
                for child_id in child_ids:
                    child_record = next(
                        (record for record in records if record['memberID'] == child_id),
                        None
                    )
                    if child_record:
                        child_details.append({
                            'memberID': child_record['memberID'],
                            'name': child_record['name'],
                            'dob': child_record['dob'],
                            'policyEndDate': child_record['policyEndDate']
                        })
                
                return child_details
            
            return []
            
        except Exception as e:
            logger.error(f"Error retrieving child account details: {str(e)}")
            return []
    
    def get_all_members(self) -> List[Dict[str, Any]]:
        """
        Retrieves all members from the database.
        
        Returns:
            List of all member records
        """
        try:
            response = requests.get(self.base_url, headers=self.headers)
            
            if response.status_code == 200:
                data = response.json()
                records = data['record']
                return records
            
            logger.error(f"Failed to retrieve all members: HTTP {response.status_code}")
            return []
            
        except Exception as e:
            logger.error(f"Error accessing database API: {str(e)}")
            return []
    
    # Placeholder for future POST method
    def update_member_data(self, member_id: str, data: Dict[str, Any]) -> bool:
        """
        Updates member data in the database (placeholder for future implementation).
        
        Args:
            member_id: The member's unique identifier
            data: Dictionary containing data to update
            
        Returns:
            Boolean indicating success or failure
        """
        # This will be implemented in the future
        logger.info(f"Update member data called (not yet implemented)")
        return False 