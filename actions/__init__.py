from typing import List, Type
from rasa_sdk import Action

from .authentication.auth_actions import AuthenticateUserAction
from .authentication.auth_actions import AuthSuccessful
from .authentication.auth_actions import ActionAskSelectedAccountId
from .authentication.auth_actions import ActionTrackSelectedAccount
from .authentication.auth_actions import ActionClearSelectedAccount
from .policy_cancel.policy_cancel import CancelPolicy
__all__ = [
    'AuthenticateUserAction',
    'AuthSuccessful',
    'ActionAskSelectedAccountId',
    'ActionTrackSelectedAccount',
    'ActionClearSelectedAccount',
    'CancelPolicy'
]

def get_default_actions() -> List[Type[Action]]:
    """Return all actions for the bot."""
    return [
        AuthenticateUserAction,
        AuthSuccessful,
        ActionAskSelectedAccountId,
        ActionTrackSelectedAccount,
        ActionClearSelectedAccount,
        CancelPolicy
    ]
