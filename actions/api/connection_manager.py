import requests
from typing import Dict, List, Optional, Any
import logging

# Set up logging for this module
logger = logging.getLogger(__name__)

class ConnectionManager:
    """
    Manages all connections to the external database API.
    
    This class handles all external data operations:
    - Retrieving member information
    - Fetching account details 
    - Managing API authentication
    - Error handling for network/API issues
    
    Currently uses JSONbin.io as the backend database service.
    """
    
    def __init__(self):
        # Base URL for our JSONbin database
        # This is where all our member records are stored
        self.base_url = "https://api.jsonbin.io/v3/b/67aa6b3aacd3cb34a8dd1abb"
        
        # Authentication headers required by JSONbin
        # The master key allows read access to our data
        self.headers = {
            'X-Master-Key': '$2a$10$j9N2X2cOS686Gk5IRXITw.8JhMMn9o/66t2N9h2twDPIkLse3uVHW'
        }
    
    def get_member_data(self, member_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves complete member data from the database using member ID.
        
        How it works:
        1. Makes an API call to JSONbin
        2. Searches through all records for the matching member ID
        3. Returns the full member record if found, None otherwise
        
        Args:
            member_id: The member's unique identifier (e.g., "M12345")
            
        Returns:
            Dictionary containing complete member data if found, including:
            - name: Full name of the member
            - dob: Date of birth
            - memberID: Unique identifier 
            - policyEndDate: When their policy expires
            - has_child_accounts: Whether they have dependents
            - child_accounts: IDs of dependent accounts (if any)
            
            Returns None if member cannot be found or if API call fails
        """
        try:
            # Make API request to get all records from JSONbin
            response = requests.get(self.base_url, headers=self.headers)
            
            # Process successful responses only (HTTP 200)
            if response.status_code == 200:
                # Parse JSON response into Python dictionary
                data = response.json()
                # Extract the array of member records
                records = data['record']
                
                # Search for the specific member by ID
                # Using next() with a generator to efficiently find the first match
                member_record = next(
                    (record for record in records if record['memberID'] == member_id),
                    None  # Default value if no match is found
                )
                
                return member_record
            
            # Log any non-successful API responses
            logger.error(f"Failed to retrieve data: HTTP {response.status_code}")
            return None
            
        except Exception as e:
            # Handle any exceptions during the API call
            # This includes network errors, timeout issues, etc.
            logger.error(f"Error accessing database API: {str(e)}")
            return None
    
    def get_child_account_details(self, child_ids_str: str) -> List[Dict[str, Any]]:
        """
        Retrieves detailed information for all dependent (child) accounts.
        
        How it works:
        1. Takes a comma-separated string of child account IDs
        2. Makes an API call to get all member records
        3. Filters out just the records matching the child IDs
        4. Returns a list of simplified child account information
        
        Args:
            child_ids_str: Comma-separated string of child member IDs (e.g., "C12345,C12346")
            
        Returns:
            List of dictionaries containing essential child account details:
            - memberID: Unique identifier for the child account
            - name: Full name of the dependent
            - dob: Date of birth
            - policyEndDate: When their coverage expires
            
            Returns empty list if no children found or if API call fails
        """
        try:
            # Make API request to get all records
            response = requests.get(self.base_url, headers=self.headers)
            
            # Process successful responses only
            if response.status_code == 200:
                # Parse JSON response 
                data = response.json()
                records = data['record']
                
                # Split comma-separated IDs into a list and clean up any whitespace
                child_ids = [id.strip() for id in child_ids_str.split(',')]
                child_details = []
                
                # For each child ID, find its complete record and extract relevant details
                for child_id in child_ids:
                    child_record = next(
                        (record for record in records if record['memberID'] == child_id),
                        None
                    )
                    # If child record found, extract only the needed fields
                    if child_record:
                        child_details.append({
                            'memberID': child_record['memberID'],
                            'name': child_record['name'],
                            'dob': child_record['dob'],
                            'policyEndDate': child_record['policyEndDate']
                        })
                
                return child_details
            
            # Return empty list for any API failures
            return []
            
        except Exception as e:
            # Handle any exceptions that might occur
            logger.error(f"Error retrieving child account details: {str(e)}")
            return []
    
    # def get_all_members(self) -> List[Dict[str, Any]]:
    #     """
    #     Retrieves ALL member records from the database.
        
    #     How it works:
    #     1. Makes a single API call to get the complete dataset
    #     2. Returns the entire list of member records
        
    #     Use cases:
    #     - For data recovery when specific member ID is unknown
    #     - For searching across all members
    #     - For retrieving primary accounts (accounts with dependents)
        
    #     Returns:
    #         Complete list of all member records in the database
    #         Returns empty list if API call fails
    #     """
    #     try:
    #         # Make API request to get all records
    #         response = requests.get(self.base_url, headers=self.headers)
            
    #         # Process successful responses only
    #         if response.status_code == 200:
    #             data = response.json()
    #             # Return the full array of member records
    #             records = data['record']
    #             return records
            
    #         # Log any API failures
    #         logger.error(f"Failed to retrieve all members: HTTP {response.status_code}")
    #         return []
            
    #     except Exception as e:
    #         # Handle any exceptions during the API call
    #         logger.error(f"Error accessing database API: {str(e)}")
    #         return []
    
    def update_member_data(self, member_id: str, data: Dict[str, Any]) -> bool:
        """
        Updates member data in the database.
        
        This implementation:
        1. Gets the current full database
        2. Finds the member record by ID
        3. Updates the specified fields
        4. Writes the entire updated database back to JSONbin
        
        Args:
            member_id: The member's unique identifier
            data: Dictionary containing data fields to update
            
        Returns:
            Boolean indicating success (True) or failure (False)
        """
        try:
            logger.info(f"Updating member data for ID: {member_id}")
            
            # First, get the current full database content
            response = requests.get(self.base_url, headers=self.headers)
            
            if response.status_code != 200:
                logger.error(f"Failed to retrieve database: HTTP {response.status_code}")
                return False
            
            # Parse database content
            db_data = response.json()
            records = db_data['record']
            
            # Find the member record to update
            found = False
            for record in records:
                if record['memberID'] == member_id:
                    # Update specified fields in the record
                    for key, value in data.items():
                        record[key] = value
                    found = True
                    break
            
            if not found:
                logger.error(f"Member ID not found in database: {member_id}")
                return False
            
            # Prepare headers for update operation - need Content-Type for write operations
            update_headers = self.headers.copy()
            update_headers['Content-Type'] = 'application/json'
            
            # Write the entire updated database back to JSONbin
            update_response = requests.put(
                self.base_url,
                json=records,  # JSONbin expects the data directly, not wrapped
                headers=update_headers
            )
            
            # Check if update was successful
            if update_response.status_code == 200:
                logger.info(f"Successfully updated member data for ID: {member_id}")
                return True
            else:
                logger.error(f"Failed to update database: HTTP {update_response.status_code}")
                logger.error(f"Response: {update_response.text}")
                return False
                
        except Exception as e:
            # Handle any exceptions during the update process
            logger.error(f"Error updating member data: {str(e)}")
            return False 