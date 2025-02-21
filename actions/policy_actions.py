from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
from datetime import datetime

# class GetCurrentAuthStatus(Action):
#     def name(self) -> Text:
#         return "get_current_auth_status"

#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#         auth_status = tracker.get_slot("auth_status")
#         return [SlotSet("auth_status", auth_status or False)]

class CheckSpecificPolicyStatus(Action):
    def name(self) -> Text:
        return "check_specific_policy_status"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        selected_id = tracker.get_slot("selected_account_id")
        child_accounts = tracker.get_slot("child_accounts") or []
        
        print(f"DEBUG: Selected ID: {selected_id}")
        print(f"DEBUG: Member ID: {tracker.get_slot('member_id')}")
        
        events = []
        # Get the member details - either primary account or child account
        if selected_id == tracker.get_slot("member_id"):
            # Primary account
            policy_end_date = tracker.get_slot("policy_end_date")
            events.append(SlotSet("is_child_account", False))
            print(f"DEBUG: Primary account selected - End date: {policy_end_date}")
        else:
            # Find matching child account
            child_account = next(
                (account for account in child_accounts if account['memberID'] == selected_id),
                None
            )
            if child_account:
                policy_end_date = child_account['policyEndDate']
                events.append(SlotSet("child_name", child_account['name']))
                events.append(SlotSet("is_child_account", True))
                print(f"DEBUG: Child account selected - End date: {policy_end_date}")
            else:
                print("DEBUG: No matching account found")
                return [SlotSet("is_policy_active", False)]

        try:
            end_date = datetime.strptime(policy_end_date, "%Y-%m-%d")
            current_date = datetime.now()
            is_active = end_date > current_date
            events.append(SlotSet("is_policy_active", is_active))
            return events
            
        except Exception as e:
            print(f"Error checking policy status: {str(e)}")
            return [SlotSet("is_policy_active", False)]

class AskSelectedAccountId(Action):
    def name(self) -> Text:
        return "action_ask_selected_account_id"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        print("DEBUG: Starting AskSelectedAccountId action")
        
        # Add primary account button
        buttons = []
        primary_id = tracker.get_slot("member_id")
        primary_name = tracker.get_slot("member_name")
        print(f"DEBUG: Primary account - ID: {primary_id}, Name: {primary_name}")
        
        buttons.append({
            "title": f"{primary_name} (Primary Account Holder)",
            "payload": f"SetSlots(selected_account_id='{primary_id}')"
        })
        
        # Add child account buttons
        child_accounts = tracker.get_slot("child_accounts") or []
        print(f"DEBUG: Child accounts = {child_accounts}")
        
        for child in child_accounts:
            print(f"DEBUG: Adding button for child - ID: {child['memberID']}, Name: {child['name']}")
            buttons.append({
                "title": f"{child['name']}",
                "payload": f"SetSlots(selected_account_id='{child['memberID']}')"
            })
        
        print(f"DEBUG: Final buttons list = {buttons}")
        
        dispatcher.utter_message(
            text="Which account's policy status would you like to check?",
            buttons=buttons
        )
        return []

class IsPolicyActiveAction(Action):
    def name(self) -> Text:
        return "is_policy_active_action"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        policy_end_date = tracker.get_slot("policy_end_date")
        if not policy_end_date:
            return [SlotSet("is_policy_active", False)]
        
        try:
            end_date = datetime.strptime(policy_end_date, "%Y-%m-%d")
            current_date = datetime.now()
            is_active = end_date > current_date
            return [SlotSet("is_policy_active", is_active)]
            
        except Exception as e:
            print(f"Error checking policy status: {str(e)}")
            return [SlotSet("is_policy_active", False)] 