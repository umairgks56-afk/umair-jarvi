"""Runtime behavior rules for JARVIS.

Rules are intentionally simple and deterministic: they shape routing and safety before
an LLM gets a chance to act. This is the foundation for a future visual rule builder.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict


@dataclass(frozen=True)
class BehaviorRule:
    id: str
    name: str
    description: str
    enabled: bool = True


RULES = [
    BehaviorRule("confirm_external_send", "Confirm external sends", "Require explicit confirmation before email or WhatsApp messages are sent."),
    BehaviorRule("confirm_destructive", "Confirm destructive actions", "Require explicit confirmation before delete, submit, purchase, shutdown, or restart actions."),
    BehaviorRule("local_first", "Local-first privacy", "Prefer local files, local memory, and Ollama before sending content to external services."),
    BehaviorRule("never_fake_completion", "Never fake completion", "Never claim an action succeeded unless the underlying tool reports success."),
    BehaviorRule("cite_research_sources", "Research source traceability", "Keep source URLs with saved research notes so findings can be inspected later."),
    BehaviorRule("protect_credentials", "Protect credentials", "Never place passwords, OAuth tokens, or session secrets into memory or prompts."),
]


def list_rules() -> list[dict]:
    return [asdict(rule) for rule in RULES]


def enabled_rules() -> list[BehaviorRule]:
    return [rule for rule in RULES if rule.enabled]
