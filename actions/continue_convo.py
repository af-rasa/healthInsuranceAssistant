# from typing import Any, Dict, Text, List
# from rasa_sdk import Action, Tracker
# from rasa_sdk.executor import CollectingDispatcher

# class ContinueConversationAction(Action):
#     def name(self) -> Text:
#         return "continue_conversation"

#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
#         # DEBUG ONLY - uncomment to see conversation context
#         # print(f"Debug - Tracker: {tracker.current_state()}")
        
#         return []  # Return empty list to avoid any automatic messages