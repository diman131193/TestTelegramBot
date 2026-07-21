from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.diagnostics import analyze_answers_with_sources, build_recommendation_with_sources

TELEGRAM_TEXT_LIMIT = 4096
VALID_ROLES = {"primary", "alert", "addon"}


@dataclass
class ValidationReport:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    terminal_paths: int = 0
    longest_result: int = 0

    @property
    def ok(self) -> bool:
        return not self.errors


def enumerate_paths(config: dict[str, Any]) -> list[list[str]]:
    questions = config.get("questions", {})
    start = config.get("start")
    paths: list[list[str]] = []

    def walk(question_id: str, answers: list[str], visited: set[str]) -> None:
        if question_id in visited:
            raise ValueError(f"Обнаружен цикл вопросов: {' -> '.join([*visited, question_id])}")
        question = questions.get(question_id)
        if not isinstance(question, dict):
            raise ValueError(f"Не найден вопрос {question_id}")
        options = question.get("options", [])
        if not options:
            raise ValueError(f"У вопроса {question_id} нет ответов")
        for option in options:
            answer_id = option.get("id")
            next_question = option.get("next")
            path = [*answers, answer_id]
            if next_question == "advice":
                paths.append(path)
            else:
                walk(next_question, path, visited | {question_id})

    if start:
        walk(start, [], set())
    return paths


def validate_sources(
    questions_config: dict[str, Any],
    factors: dict[str, Any],
    rules_config: dict[str, Any],
    content: dict[str, Any],
) -> ValidationReport:
    report = ValidationReport()
    questions = questions_config.get("questions", {})
    start = questions_config.get("start")

    if not start or start not in questions:
        report.errors.append("Стартовый вопрос не указан или отсутствует.")

    answer_ids: list[str] = []
    for question_id, question in questions.items():
        if not isinstance(question, dict) or not str(question.get("text", "")).strip():
            report.errors.append(f"У вопроса {question_id} нет текста.")
            continue
        options = question.get("options", [])
        if not options:
            report.errors.append(f"У вопроса {question_id} нет вариантов ответа.")
        for option in options:
            answer_id = str(option.get("id", "")).strip()
            answer_text = str(option.get("text", "")).strip()
            next_question = str(option.get("next", "")).strip()
            if not answer_id or not answer_text or not next_question:
                report.errors.append(f"В вопросе {question_id} есть незаполненный вариант ответа.")
                continue
            answer_ids.append(answer_id)
            if next_question != "advice" and next_question not in questions:
                report.errors.append(
                    f"Ответ {answer_id} ведет в несуществующий вопрос {next_question}."
                )

    duplicate_answers = sorted({item for item in answer_ids if answer_ids.count(item) > 1})
    if duplicate_answers:
        report.errors.append(f"Повторяются ID ответов: {', '.join(duplicate_answers)}.")

    factor_answers = factors.get("answers", {})
    missing_factors = sorted(set(answer_ids) - set(factor_answers))
    if missing_factors:
        report.errors.append(
            f"Не описан смысл ответов: {', '.join(missing_factors)}."
        )
    unused_factors = sorted(set(factor_answers) - set(answer_ids))
    if unused_factors:
        report.warnings.append(
            f"Есть неиспользуемые описания ответов: {', '.join(unused_factors)}."
        )

    modules_list = content.get("modules", [])
    module_ids = [
        module.get("id")
        for module in modules_list
        if isinstance(module, dict) and module.get("id")
    ]
    duplicate_modules = sorted({item for item in module_ids if module_ids.count(item) > 1})
    if duplicate_modules:
        report.errors.append(f"Повторяются ID рекомендаций: {', '.join(duplicate_modules)}.")
    modules = {
        module.get("id"): module
        for module in modules_list
        if isinstance(module, dict) and module.get("id")
    }
    for module_id, module in modules.items():
        role = module.get("role")
        if role not in VALID_ROLES:
            report.errors.append(f"У рекомендации {module_id} неизвестная роль {role}.")
        if module.get("active", True) and not str(module.get("summary", "")).strip():
            report.errors.append(f"У активной рекомендации {module_id} нет объяснения.")
        if role == "primary" and module.get("active", True):
            if not str(module.get("title", "")).strip():
                report.errors.append(f"У основной рекомендации {module_id} нет заголовка.")
            if not module.get("actions"):
                report.errors.append(f"У основной рекомендации {module_id} нет действий.")

    rules = rules_config.get("rules", [])
    for rule in rules:
        module_id = rule.get("module_id")
        if module_id not in modules:
            report.errors.append(f"Правило ссылается на неизвестную рекомендацию {module_id}.")
            continue
        if rule.get("role") != modules[module_id].get("role"):
            report.errors.append(
                f"Роль рекомендации {module_id} не совпадает с ролью в правиле."
            )
    fallback_id = rules_config.get("fallback_primary_id")
    if fallback_id not in modules or modules.get(fallback_id, {}).get("role") != "primary":
        report.errors.append("Резервная основная рекомендация отсутствует или имеет неверную роль.")

    facts = content.get("facts", {})
    used_label_values: dict[str, set[str]] = {}
    for factor in factor_answers.values():
        for group, value in factor.get("labels", {}).items():
            used_label_values.setdefault(group, set()).add(value)
    for group, values in used_label_values.items():
        if group not in facts or not facts.get(group, {}).get("visible", True):
            continue
        configured = set(facts.get(group, {}).get("values", {}))
        missing = sorted(values - configured)
        if missing:
            report.warnings.append(
                f"Для раздела {group} нет клиентских подписей: {', '.join(missing)}."
            )

    if report.errors:
        return report

    try:
        paths = enumerate_paths(questions_config)
    except (TypeError, ValueError) as error:
        report.errors.append(str(error))
        return report

    report.terminal_paths = len(paths)
    for path in paths:
        result = analyze_answers_with_sources(path, factors, rules_config, content)
        if not result.primary:
            report.errors.append(f"Путь {'|'.join(path)} не получил основную рекомендацию.")
            break
        text = build_recommendation_with_sources(path, factors, rules_config, content)
        report.longest_result = max(report.longest_result, len(text))
        if len(text) > TELEGRAM_TEXT_LIMIT:
            report.errors.append(
                f"Результат пути {'|'.join(path)} длиннее лимита Telegram: {len(text)} символов."
            )
            break

    if not paths:
        report.errors.append("В дереве вопросов нет ни одного завершающего пути.")
    return report
