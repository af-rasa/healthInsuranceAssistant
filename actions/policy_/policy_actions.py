# from typing import Any, Text, Dict, List
# from rasa_sdk import Action, Tracker
# from rasa_sdk.executor import CollectingDispatcher
# from rasa_sdk.events import SlotSet
# from datetime import datetime


# class CheckSpecificPolicyStatus(Action):
#     def name(self) -> Text:
#         return "check_specific_policy_status"

#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
#         selected_id = tracker.get_slot("selected_account_id")
#         member_id = tracker.get_slot("member_id")
#         child_accounts = tracker.get_slot("child_accounts") or []
        
#         events = []
#         # Get the member details - either primary account or child account
#         if not member_id:
#             # If member_id is cleared but we have the selected_id matching original primary
#             if selected_id == '101':  # Or whatever your primary ID pattern is
#                 policy_end_date = tracker.get_slot("policy_end_date")
#                 events.append(SlotSet("is_child_account", False))
#             else:
#                 # Find matching child account
#                 child_account = next(
#                     (account for account in child_accounts if account['memberID'] == selected_id),
#                     None
#                 )
#                 if child_account:
#                     policy_end_date = child_account['policyEndDate']
#                     events.append(SlotSet("child_name", child_account['name']))
#                     events.append(SlotSet("is_child_account", True))
#                 else:
#                     return [SlotSet("is_policy_active", False)]
#         else:
#             # Normal flow when member_id is present
#             if selected_id == member_id:
#                 policy_end_date = tracker.get_slot("policy_end_date")
#                 events.append(SlotSet("is_child_account", False))
#             else:
#                 # Find matching child account
#                 child_account = next(
#                     (account for account in child_accounts if account['memberID'] == selected_id),
#                     None
#                 )
#                 if child_account:
#                     policy_end_date = child_account['policyEndDate']
#                     events.append(SlotSet("child_name", child_account['name']))
#                     events.append(SlotSet("is_child_account", True))
#                 else:
#                     return [SlotSet("is_policy_active", False)]

#         try:
#             end_date = datetime.strptime(policy_end_date, "%Y-%m-%d")
#             current_date = datetime.now()
#             is_active = end_date > current_date
#             events.append(SlotSet("is_policy_active", is_active))
#             return events
            
#         except Exception as e:
#             return [SlotSet("is_policy_active", False)]

# class AskSelectedAccountId(Action):
#     def name(self) -> Text:
#         return "action_ask_selected_account_id"

#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
#         # Add primary account button
#         buttons = []
#         primary_id = tracker.get_slot("member_id")
#         primary_name = tracker.get_slot("member_name")
        
#         # If primary_id is None but we have auth_status, restore from slots
#         if (not primary_id or primary_id == 'None') and tracker.get_slot("auth_status"):
#             all_slots = tracker.current_slot_values()
#             # Get the first successful member_id from history
#             for event in reversed(tracker.events):
#                 if event.get('event') == 'slot' and event.get('name') == 'member_id' and event.get('value'):
#                     primary_id = event.get('value')
#                     break
        
#         buttons.append({
#             "title": f"{primary_name} (Primary Account Holder)",
#             "payload": f"SetSlots(selected_account_id='{primary_id}')"
#         })
        
#         # Add child account buttons
#         child_accounts = tracker.get_slot("child_accounts") or []
        
#         for child in child_accounts:
#             buttons.append({
#                 "title": f"{child['name']}",
#                 "payload": f"SetSlots(selected_account_id='{child['memberID']}')"
#             })
        
#         dispatcher.utter_message(
#             text="Which account's policy status would you like to check?",
#             buttons=buttons
#         )
#         return []

# class IsPolicyActiveAction(Action):
#     def name(self) -> Text:
#         return "is_policy_active_action"

#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
#         policy_end_date = tracker.get_slot("policy_end_date")
#         if not policy_end_date:
#             return [SlotSet("is_policy_active", False)]
        
#         try:
#             end_date = datetime.strptime(policy_end_date, "%Y-%m-%d")
#             current_date = datetime.now()
#             is_active = end_date > current_date
#             return [SlotSet("is_policy_active", is_active)]
            
#         except Exception as e:
#             return [SlotSet("is_policy_active", False)] 