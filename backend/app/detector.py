from __future__ import annotations

import asyncio
import re
from dataclasses import dataclass
from typing import Callable
from uuid import uuid4

from faker import Faker

fake = Faker()


@dataclass(slots=True)
class DetectionRule:
    label: str
    pattern: re.Pattern[str]
    synthesizer: Callable[[str], str]


def _fake_email(_: str) -> str:
    return fake.safe_email()


def _fake_phone(_: str) -> str:
    return fake.phone_number()


def _fake_name(_: str) -> str:
    return fake.name()


def _mask_secret(_: str) -> str:
    return f"SECRET-{uuid4().hex[:8]}"


DETECTION_RULES: tuple[DetectionRule, ...] = (
    DetectionRule("PII_EMAIL", re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"), _fake_email),
    DetectionRule("PII_PHONE", re.compile(r"(?:\+?\d[\s-]?){7,15}"), _fake_phone),
    DetectionRule("PII_NAME", re.compile(r"\b[A-Z][a-z]+\s[A-Z][a-z]+\b"), _fake_name),
    DetectionRule("BUSINESS_SECRET", re.compile(r"ACME-(?:DOC|PLAN)-\d{4}"), _mask_secret),
)


async def detect_and_tokenize(text: str) -> tuple[str, dict[str, dict[str, str]]]:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _run_detection, text)


def _run_detection(text: str) -> tuple[str, dict[str, dict[str, str]]]:
    token_map: dict[str, dict[str, str]] = {}
    spans: list[tuple[int, int, DetectionRule, str]] = []

    for rule in DETECTION_RULES:
        for match in rule.pattern.finditer(text):
            start, end = match.span()
            spans.append((start, end, rule, match.group()))

    spans.sort(key=lambda item: item[0])
    merged_spans: list[tuple[int, int, DetectionRule, str]] = []
    for span in spans:
        if merged_spans and span[0] < merged_spans[-1][1]:
            continue
        merged_spans.append(span)

    masked_parts: list[str] = []
    cursor = 0
    for index, (start, end, rule, original) in enumerate(merged_spans, start=1):
        masked_parts.append(text[cursor:start])
        placeholder = f"<{rule.label}_{index:03d}>"
        synthetic = rule.synthesizer(original)
        masked_parts.append(placeholder)
        token_map[placeholder] = {
            "label": rule.label,
            "original": original,
            "synthetic": synthetic,
        }
        cursor = end
    masked_parts.append(text[cursor:])

    return "".join(masked_parts), token_map
