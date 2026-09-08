from __future__ import annotations

# Actions that can communicate externally or change user data require explicit
# confirmation. This policy is intentionally conservative.
EXTERNAL_ACTIONS = {
    "send_whatsapp",
    "send_email",
    "reply_message",
    "delete_file",
    "delete_email",
    "submit_form",
    "purchase",
}


def needs_confirmation(action: str) -> bool:
    return action in EXTERNAL_ACTIONS
