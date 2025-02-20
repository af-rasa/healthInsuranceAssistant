from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, SessionStarted, ActionExecuted, EventType
import pendulum
import logging

# Add this near the top of the file
logger = logging.getLogger(__name__)

class ActionSessionStart(Action):
    # Class variable to store the date
    _current_date = None

    def name(self) -> Text:
        return "action_session_start"

    @staticmethod
    def fetch_slots(tracker: Tracker) -> List[EventType]:
        """Collect slots that should persist across sessions."""
        slots = []
        # Add any slots that should persist between sessions
        for key in ("current_date",):
            value = tracker.get_slot(key)
            if value is not None:
                slots.append(SlotSet(key=key, value=value))
        return slots

    @classmethod
    def get_current_date(cls) -> str:
        """Get current date using Pendulum."""
        if cls._current_date is None:
            # Get current UTC date in YYYY-MM-DD format
            cls._current_date = pendulum.now('UTC').format('YYYY-MM-DD')
            logger.info(f"Set current date to: {cls._current_date}")
        else:
            logger.debug(f"Using cached date: {cls._current_date}")
        
        return cls._current_date

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        # Start with session_started event
        events = [SessionStarted()]

        # Get the cached date using Pendulum
        current_date = self.get_current_date()
        events.append(SlotSet("current_date", current_date))

        # Add any slots that should persist
        events.extend(self.fetch_slots(tracker))

        # Add action_listen as the final event
        events.append(ActionExecuted("action_listen"))

        return events 