import re
from pathlib import Path
from typing import Any

import yaml


class RuleEngine:
    def __init__(self, path: str | Path = "config/rules.yaml") -> None:
        self.rules = yaml.safe_load(Path(path).read_text(encoding="utf-8"))["rules"]

    def handle(self, category: str, text: str, field: str | None = None) -> dict[str, Any] | None:
        for rule in self.rules:
            match = rule["match"]
            if match["category"] != category or ("field" in match and match["field"] != field):
                continue
            intent = match.get("intent")
            text_lower = text.lower()
            if intent == "salary" and not any(
                word in text_lower for word in ("salary", "annual", "monthly")
            ):
                continue
            if intent == "word_count" and not "word count" in text_lower:
                continue
            if intent == "yes_no" and text_lower.strip() not in {
                "yes",
                "no",
                "y",
                "n",
                "true",
                "false",
            }:
                continue
            if intent == "sentiment" and not any(
                word in text_lower for word in ("good", "bad", "great", "terrible")
            ):
                continue
            handler = rule["handler"]
            if handler == "regex_email":
                found = re.search(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}", text)
                return {"value": found.group(0) if found else None, "valid": found is not None}
            if handler == "deterministic_salary":
                values = [float(x) for x in re.findall(r"\d+(?:\.\d+)?", text)]
                return {"annual": values[0] * 12 if values else None}
            if handler == "exact_yes_no":
                return {"value": "yes" if text.strip().lower() in {"yes", "y", "true"} else "no"}
            if handler == "exact_sentiment":
                return {
                    "value": "positive"
                    if "good" in text.lower()
                    else "negative"
                    if "bad" in text.lower()
                    else "neutral"
                }
            if handler == "word_count":
                return {"value": len(text.split())}
        return None

    @staticmethod
    def billing_handler() -> dict[str, Any]:
        return {
            "category": "Billing",
            "refund_request": "Yes",
            "requires_followup": True,
            "handler": "billing_handler",
        }
