# from typing import Any, Text, Dict, List
# from rasa_sdk import Action, Tracker
# from rasa_sdk.executor import CollectingDispatcher
# from rasa_sdk.events import SlotSet
# from datetime import datetime

# class IsPolicyActiveAction(Action):
#     """
#     This action checks if a policy is active by comparing its end date with the current date.
#     It's used specifically for primary account holders (not child accounts).
#     """
    
#     def name(self) -> Text:
#         # The name that will be used to call this action from the Rasa flow
#         return "is_policy_active_action"

#     def _check_policy_status(self, policy_end_date: str) -> bool:
#         """
#         Helper function to check if a policy is active based on its end date.
        
#         Parameters:
#         - policy_end_date: The date the policy ends
        
#         Returns:
#         - True if policy is active, False if not
#         """
#         try:
#             end_date = datetime.strptime(policy_end_date, "%Y-%m-%d")
#             return end_date > datetime.now()
#         except Exception:
#             return False

#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#         """
#         This is the main function that checks if a primary account holder's policy is active
#         by comparing the policy end date with today's date.
        
#         Parameters:
#         - dispatcher: Like a messenger - helps the bot send messages to the user
#         - tracker: Like the bot's memory - keeps track of all conversation information
#         - domain: Like a rulebook - contains all the things the bot can say and do
        
#         Returns:
#         - A list with one update: whether the policy is active (true) or not (false)
#         """
#         policy_end_date = tracker.get_slot("policy_end_date")
#         is_active = policy_end_date and self._check_policy_status(policy_end_date)
#         return [SlotSet("is_policy_active", is_active)] 