from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
import requests
from datetime import datetime

class AuthenticateUser(Action):
    def name(self) -> Text:
        return "authenticate_user_action"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        member_id = tracker.get_slot("member_id")
        
        try:
            response = requests.get(
                'https://api.jsonbin.io/v3/b/67aa6b3aacd3cb34a8dd1abb',
                headers={'X-Master-Key': '$2a$10$j9N2X2cOS686Gk5IRXITw.8JhMMn9o/66t2N9h2twDPIkLse3uVHW'}
            )
            
            if response.status_code == 200:
                data = response.json()
                records = data['record']
                
                # Find matching member by ID
                member_record = next(
                    (record for record in records if record['memberID'] == member_id),
                    None
                )
                
                if member_record:
                    events = [
                        SlotSet("member_found", True),
                        SlotSet("member_name", member_record['name']),
                        SlotSet("member_dob", member_record['dob']),
                        SlotSet("policy_end_date", member_record['policyEndDate']),
                        SlotSet("has_child_accounts", member_record['has_child_accounts'])
                    ]

                    # Handle child accounts if they exist
                    if member_record['has_child_accounts'] and member_record['child_accounts']:
                        child_ids = [id.strip() for id in member_record['child_accounts'].split(',')]
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
                        
                        events.append(SlotSet("child_accounts", child_details))
                    
                    return events
                
            return [SlotSet("member_found", False)]
            
        except Exception as e:
            print(f"Error accessing JSONbin: {str(e)}")
            return [SlotSet("member_found", False)]


class AuthSuccessful(Action):
    def name(self) -> Text:
        return "auth_successful"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Set auth_status to true - user is now authenticated
        return [SlotSet("auth_status", True)]