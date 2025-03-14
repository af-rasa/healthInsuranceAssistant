from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
import requests
from datetime import datetime
import logging
from .db_service import DBService

# Add logger at top of file
logger = logging.getLogger(__name__)

class AuthenticateUser(Action):
    def name(self) -> Text:
        return "authenticate_user_action"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        member_id = tracker.get_slot("member_id")
        logger.info("Authenticating user with ID: %s", member_id)
        
        member_record = DBService.find_account_by_id(member_id)
        
        if member_record:
            events = [
                SlotSet("member_found", True),
                SlotSet("member_id", member_record['memberID']),
                SlotSet("member_name", member_record['name']),
                SlotSet("member_dob", member_record['dob']),
                SlotSet("policy_end_date", member_record['policyEndDate']),
                SlotSet("has_child_accounts", member_record['has_child_accounts'])
            ]

            if member_record['has_child_accounts'] and member_record['child_accounts']:
                child_details = DBService.get_child_accounts(member_record['child_accounts'])
                events.append(SlotSet("child_accounts", child_details))
            
            return events
            
        return [SlotSet("member_found", False)]


class AuthSuccessful(Action):
    def name(self) -> Text:
        return "auth_successful"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # For accounts without children, set selected account details to main account
        has_child_accounts = tracker.get_slot("has_child_accounts")
        events = [SlotSet("auth_status", True)]
        
        if not has_child_accounts:
            logger.info("No child accounts - setting selected account details to main account")
            events.extend([
                SlotSet("selected_account_id", tracker.get_slot("member_id")),
                SlotSet("selected_account_name", tracker.get_slot("member_name")),
                SlotSet("selected_account_dob", tracker.get_slot("member_dob")),
                SlotSet("selected_policy_end_date", tracker.get_slot("policy_end_date"))
            ])
            
            # Add debug log
            logger.info("Set selected account details: ID=%s, Name=%s, DOB=%s, Policy End=%s",
                       tracker.get_slot("member_id"),
                       tracker.get_slot("member_name"),
                       tracker.get_slot("member_dob"),
                       tracker.get_slot("policy_end_date"))
        
        return events

class ActionTrackSelectedAccount(Action):
    def name(self) -> Text:
        return "action_track_selected_account"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        selected_id = tracker.get_slot("selected_account_id")
        if selected_id:
            selected_id = selected_id.strip("'")
        
        logger.info("=== Selected Account Tracking ===")
        logger.info("selected_account_id after cleaning: %s", selected_id)

        selected_record = DBService.find_account_by_id(selected_id)
        
        if selected_record:
            events = [
                SlotSet("selected_account_id", selected_id),
                SlotSet("selected_account_name", selected_record['name']),
                SlotSet("selected_account_dob", selected_record['dob']),
                SlotSet("selected_policy_end_date", selected_record['policyEndDate'])
            ]
            
            # debug_msg = (
            #     "Debug - Selected Account Details:\n"
            #     f"Name: {selected_record['name']}\n"
            #     f"ID: {selected_id}\n"
            #     f"DOB: {selected_record['dob']}\n"
            #     f"Policy End: {selected_record['policyEndDate']}"
            # )
            # dispatcher.utter_message(text=debug_msg)
            
            return events
            
        logger.warning("No match found for ID: %s", selected_id)
        return []

class ActionClearSelectedAccount(Action):
    def name(self) -> Text:
        return "action_clear_selected_account"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        logger.info("=== Clearing Selected Account Details ===")
        
        # Clear all selected_ slots but maintain member_ slots
        events = [
            SlotSet("selected_account_id", None),
            SlotSet("selected_account_name", None),
            SlotSet("selected_account_dob", None),
            SlotSet("selected_policy_end_date", None)
        ]
        
        logger.info("Cleared selected account slots")
        return events