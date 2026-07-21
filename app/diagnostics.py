from __future__ import annotations

import html
import json
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

from app.paths import DATA_DIR

FACTORS_PATH = DATA_DIR / "diagnostic_factors.json"
RULES_PATH = DATA_DIR / "diagnostic_rules.json"
SNAPSHOT_PATH = DATA_DIR / "diagnostics_snapshot.json"


@dataclass(frozen=True)
class DiagnosticResult:
    answers: list[str]
    labels: dict[str, str]
    scores: dict[str, int]
    tags: set[str]
    primary: dict[str, Any]
    alerts: list[dict[str, Any]]
    addons: list[dict[str, Any]]


def _load_json(path: Path) -> dict[str, Any]:
    try:
        with path.open(encoding="utf-8") as file:
            value = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return {}
    return value if isinstance(value, dict) else {}


def load_diagnostic_sources() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    """Read the last published diagnostic snapshot.

    Sources are deliberately loaded per calculation. A successfully published content
    update therefore becomes available without restarting the bot.
    """
    snapshot = _load_json(SNAPSHOT_PATH)
    content = snapshot.get("content", {})
    return (_load_json(FACTORS_PATH), _load_json(RULES_PATH), content)


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def _rule_matches(
    rule: dict[str, Any],
    answers: list[str],
    labels: dict[str, str],
    scores: dict[str, int],
    tags: set[str],
) -> bool:
    conditions = rule.get("conditions", {})

    for key, value in conditions.get("min_scores", {}).items():
        if scores.get(key, 0) < value:
            return False

    for key, value in conditions.get("max_scores", {}).items():
        if scores.get(key, 0) > value:
            return False

    for key, value in conditions.get("label_equals", {}).items():
        if labels.get(key) != value:
            return False

    for key, values in conditions.get("label_in", {}).items():
        if labels.get(key) not in set(_as_list(values)):
            return False

    if conditions.get("any_tags") and not tags.intersection(conditions["any_tags"]):
        return False

    if conditions.get("all_tags") and not set(conditions["all_tags"]).issubset(tags):
        return False

    answer_set = set(answers)
    if conditions.get("answers_any") and not answer_set.intersection(conditions["answers_any"]):
        return False

    if conditions.get("answers_all") and not set(conditions["answers_all"]).issubset(answer_set):
        return False

    if conditions.get("answers_none") and answer_set.intersection(conditions["answers_none"]):
        return False

    return True


def _active_modules(content: dict[str, Any]) -> dict[str, dict[str, Any]]:
    modules = content.get("modules", [])
    if not isinstance(modules, list):
        return {}
    return {
        module["id"]: module
        for module in modules
        if isinstance(module, dict)
        and isinstance(module.get("id"), str)
        and module.get("active", True)
    }


def analyze_answers_with_sources(
    answers: list[str],
    factors: dict[str, Any],
    rules_config: dict[str, Any],
    content: dict[str, Any],
) -> DiagnosticResult:
    answer_factors = factors.get("answers", {})
    labels: dict[str, str] = {}
    scores: Counter[str] = Counter()
    tags: set[str] = set()

    # Duplicate callbacks must never increase a score twice.
    unique_answers = list(dict.fromkeys(answers))
    for answer_id in unique_answers:
        factor = answer_factors.get(answer_id, {})
        if not isinstance(factor, dict):
            continue
        labels.update(factor.get("labels", {}))
        scores.update(factor.get("scores", {}))
        tags.update(factor.get("tags", []))

    modules = _active_modules(content)
    rules = sorted(
        rules_config.get("rules", []),
        key=lambda item: item.get("priority", 0),
        reverse=True,
    )
    matched = [
        rule
        for rule in rules
        if isinstance(rule, dict)
        and rule.get("module_id") in modules
        and _rule_matches(rule, unique_answers, labels, dict(scores), tags)
    ]

    primary_rule = next((rule for rule in matched if rule.get("role") == "primary"), None)
    primary_id = (
        primary_rule.get("module_id")
        if primary_rule
        else rules_config.get("fallback_primary_id")
    )
    primary = modules.get(primary_id, {})

    alerts = [modules[rule["module_id"]] for rule in matched if rule.get("role") == "alert"]
    max_addons = content.get("settings", {}).get("max_addons", 2)
    addons = [
        modules[rule["module_id"]]
        for rule in matched
        if rule.get("role") == "addon"
    ][:max_addons]

    return DiagnosticResult(
        answers=unique_answers,
        labels=labels,
        scores=dict(scores),
        tags=tags,
        primary=primary,
        alerts=alerts,
        addons=addons,
    )


def analyze_answers(answers: list[str]) -> DiagnosticResult:
    return analyze_answers_with_sources(answers, *load_diagnostic_sources())


def _escape(value: Any) -> str:
    return html.escape(value) if isinstance(value, str) else ""


def _unique_text(items: Iterable[Any], limit: int | None = None) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for item in items:
        if not isinstance(item, str):
            continue
        value = item.strip()
        normalized = value.casefold()
        if not value or normalized in seen:
            continue
        seen.add(normalized)
        result.append(value)
        if limit is not None and len(result) >= limit:
            break
    return result


def _bullets(items: Iterable[Any], limit: int | None = None) -> str:
    return "\n".join(f"• {_escape(item)}" for item in _unique_text(items, limit))


def _section(title: str, body: str) -> str:
    if not body:
        return ""
    return f"<b>{_escape(title)}</b>\n{body}" if title else body


def _fact_labels(content: dict[str, Any], labels: dict[str, str]) -> list[str]:
    facts = content.get("facts", {})
    result: list[str] = []
    for group, config in facts.items():
        if not isinstance(config, dict) or not config.get("visible", True):
            continue
        value = labels.get(group)
        label = config.get("values", {}).get(value)
        if isinstance(label, str) and label:
            result.append(label)
    return result


def _module_items(modules: Iterable[dict[str, Any]], field: str) -> list[str]:
    return [
        item
        for module in modules
        for item in module.get(field, [])
        if isinstance(item, str)
    ]


def build_recommendation_with_sources(
    answers: list[str],
    factors: dict[str, Any],
    rules_config: dict[str, Any],
    content: dict[str, Any],
) -> str:
    result = analyze_answers_with_sources(answers, factors, rules_config, content)
    primary = result.primary
    settings = content.get("settings", {})

    if not primary:
        return (
            "Я сохранила твои ответы 💛\n\n"
            "Сейчас диагностика не смогла собрать результат. "
            "Напиши в консультацию, и мастер разберет ситуацию вручную."
        )

    parts = [
        f"<b>{_escape(primary.get('title'))}</b>",
        _escape(primary.get("summary")),
        _section(
            settings.get("facts_title", "Что я учла:"),
            _bullets(_fact_labels(content, result.labels)),
        ),
    ]

    alert_summaries = [
        f"<b>{_escape(module.get('title'))}</b>\n{_escape(module.get('summary'))}"
        for module in result.alerts
        if module.get("title") or module.get("summary")
    ]
    parts.append(
        _section(
            settings.get("alerts_title", "На что важно обратить внимание:"),
            "\n\n".join(alert_summaries),
        )
    )

    parts.append(
        _section(
            settings.get("addons_title", "Дополнительно по твоим ответам:"),
            _bullets(module.get("summary") for module in result.addons),
        )
    )

    max_actions = settings.get("max_actions", 5)
    actions = _module_items(result.alerts, "actions")
    actions += _module_items([primary], "actions")
    actions += _module_items(result.addons, "actions")
    parts.append(
        _section(
            settings.get("actions_title", "Что можно попробовать:"),
            _bullets(actions, max_actions),
        )
    )

    max_cautions = settings.get("max_cautions", 3)
    cautions = _module_items(result.alerts, "cautions")
    cautions += _module_items([primary], "cautions")
    cautions += _module_items(result.addons, "cautions")
    parts.append(
        _section(
            settings.get("cautions_title", "С чем лучше аккуратнее:"),
            _bullets(cautions, max_cautions),
        )
    )

    cta = next(
        (
            module.get("cta")
            for module in result.alerts
            if isinstance(module.get("cta"), str) and module.get("cta").strip()
        ),
        primary.get("cta", ""),
    )
    parts.append(_escape(cta))

    footer = settings.get("footer")
    if isinstance(footer, str) and footer:
        parts.append(f"<i>{_escape(footer)}</i>")

    return "\n\n".join(part for part in parts if part)


def build_recommendation(answers: list[str]) -> str:
    return build_recommendation_with_sources(answers, *load_diagnostic_sources())
