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
                    return [
                        SlotSet("member_found", True),
                        SlotSet("member_name", member_record['name']),
                        SlotSet("member_dob", member_record['dob']),
                        SlotSet("policy_end_date", member_record['policyEndDate'])
                    ]
                
            return [SlotSet("member_found", False)]
            
        except Exception as e:
            print(f"Error accessing JSONbin: {str(e)}")
            return [SlotSet("member_found", False)]



# class CompareDOB(Action):
#     def name(self) -> Text:
#         return "compare_dob"

#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
#         dob_input = tracker.get_slot("dob_input")
#         stored_dob = tracker.get_slot("member_dob")
        
#         # Simple string comparison for now
#         # In production, you might want to parse and compare actual dates
#         return []  # The flow will handle the comparison

class AuthSuccessful(Action):
    def name(self) -> Text:
        return "auth_successful"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # dispatcher.utter_message(response="utter_auth_successful")
        return [SlotSet("auth_status", True)] 

