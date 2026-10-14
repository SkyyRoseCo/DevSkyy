"""Classification must never act on an invented confidence or a guessed label.

Mocks only the Groq client boundary; no network.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, Mock

import pytest

from llm.base import CompletionResponse, Message
from llm.classification import GroqFastClassifier
from llm.exceptions import LLMError
from llm.task_classifier import TaskCategory, TaskClassifier
from llm.unified_llm_client import LLMRequest, UnifiedLLMClient


def groq_returning(content: str) -> GroqFastClassifier:
    client = Mock()
    client.complete = AsyncMock(
        return_value=CompletionResponse(content=content, model="groq-model", provider="groq")
    )
    return GroqFastClassifier(groq_client=client)


@pytest.mark.parametrize(
    "content",
    [
        "This is not valid JSON",
        '{"label": "intent1"}',  # no confidence: never invent one
        '{"label": "refund", "confidence": 0.9}',  # label outside the allowed set
        '{"confidence": 0.9}',  # no label
        '{"label": "intent1", "confidence": 1.7}',  # out of range
    ],
)
async def test_unusable_responses_raise_instead_of_guessing(content):
    classifier = groq_returning(content)
    with pytest.raises(LLMError):
        await classifier.classify_intent("where is my order", intents=["intent1", "intent2"])


async def test_label_case_is_normalized_to_the_allowed_set():
    classifier = groq_returning('{"label": "Intent2", "confidence": 0.8}')
    result = await classifier.classify_intent("x", intents=["intent1", "intent2"])
    assert (result.label, result.confidence) == ("intent2", 0.8)


async def test_missing_scores_are_left_empty_not_fabricated():
    classifier = groq_returning('{"label": "intent1", "confidence": 0.8}')
    result = await classifier.classify_intent("x", intents=["intent1", "intent2"])
    assert result.all_scores == {}


async def test_task_classifier_returns_a_category():
    classifier = TaskClassifier(
        groq_classifier=groq_returning('{"label": "code", "confidence": 0.8}')
    )
    result = await classifier.classify("fix the failing pytest in api/")
    assert result.task_category is TaskCategory.CODE
    assert result.confidence == 0.8
    assert result.recommended_providers[0] == "openai"


async def test_task_classifier_raises_on_unusable_response():
    classifier = TaskClassifier(groq_classifier=groq_returning('{"label": "code"}'))
    with pytest.raises(LLMError):
        await classifier.classify("fix the failing pytest in api/")


async def test_unified_client_falls_back_to_default_routing_when_classification_fails():
    classifier = Mock()
    classifier.classify = AsyncMock(side_effect=LLMError("groq down", provider="groq"))
    router = Mock()
    router.complete = AsyncMock(
        return_value=CompletionResponse(content="ok", model="m", provider="anthropic")
    )
    client = UnifiedLLMClient(router=router, classifier=classifier)
    response = await client.complete(
        LLMRequest(
            messages=[Message.user("hi")],
            task_description="say hi",
            execution_mode="fast",
        )
    )
    assert response.content == "ok"
    assert response.task_classification is None
    assert router.complete.await_args.kwargs["provider"] is None
