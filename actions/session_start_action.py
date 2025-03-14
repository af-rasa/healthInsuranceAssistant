from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, SessionStarted, ActionExecuted
from datetime import datetime
import logging

# Add this near the top of the file
logger = logging.getLogger(__name__)

class ActionSessionStart(Action):
    def name(self) -> Text:
        return "action_session_start"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        # Start with session_started event
        events = [SessionStarted()]

        # Set current date using the same simple method as policy_actions
        current_date = datetime.now().strftime('%Y-%m-%d')
        events.append(SlotSet("current_date", current_date))

        # Add action_listen as the final event
        events.append(ActionExecuted("action_listen"))

        return events 