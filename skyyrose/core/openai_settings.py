"""Small, endpoint-specific OpenAI settings contract (Chat Completions only).

Source-verified 2026-09-28: developers.openai.com/api/docs/guides/
{latest-model,reasoning,structured-outputs}. Unknown capabilities fail closed;
this is an allowlist for these adapters, not a claim that other models do not exist.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal


@dataclass(frozen=True)
class ChatCapabilities:
    structured_output: bool = False
    reasoning_efforts: tuple[str, ...] = ()
    verbosity: bool = False
    token_parameter: str = "max_tokens"
    tools: bool = True
    sampling: bool = True


def capabilities(model: str) -> ChatCapabilities:
    if model in {
        "gpt-4o",
        "gpt-4o-mini",
        "gpt-4o-2024-05-13",
        "gpt-4o-2024-08-06",
        "gpt-4o-2024-11-20",
        "gpt-4o-mini-2024-07-18",
    }:
        return ChatCapabilities(structured_output=model != "gpt-4o-2024-05-13")
    if model in {"gpt-4", "gpt-4-turbo", "gpt-4-turbo-preview", "gpt-3.5-turbo"}:
        return ChatCapabilities()
    if model in {"o1-preview", "o1-mini"}:
        return ChatCapabilities(
            token_parameter="max_completion_tokens", tools=False, sampling=False
        )
    if model in {"gpt-6-astra", "gpt-6-sol", "gpt-6-luna"}:
        efforts = ("low", "medium", "high", "xhigh", "max")
        if model != "gpt-6-astra":
            efforts = ("none", *efforts)
        return ChatCapabilities(True, efforts, True, "max_completion_tokens", False, False)
    raise ValueError(f"Chat Completions capabilities not registered for {model!r}")


@dataclass(frozen=True)
class OpenAIChatSettings:
    """None means omitted; explicit incompatible values are rejected, never dropped."""

    max_tokens: int = 1024
    temperature: float | None = None
    response_format: dict[str, Any] | None = None
    reasoning_effort: Literal["none", "minimal", "low", "medium", "high", "xhigh", "max"] | None = (
        None
    )
    verbosity: Literal["low", "medium", "high"] | None = None
    top_p: float | None = None
    frequency_penalty: float | None = None
    presence_penalty: float | None = None
    stop: str | list[str] | None = None
    tool_choice: str | dict[str, Any] | None = None
    parallel_tool_calls: bool | None = None

    def to_request(self, model: str, *, tools: list[dict] | None = None) -> dict[str, Any]:
        cap = capabilities(model)
        if type(self.max_tokens) is not int or self.max_tokens <= 0:
            raise ValueError("max_tokens must be a positive integer")
        if self.reasoning_effort is not None and self.reasoning_effort not in cap.reasoning_efforts:
            raise ValueError(f"reasoning_effort unsupported for {model}")
        if self.verbosity is not None and (
            not cap.verbosity or self.verbosity not in ("low", "medium", "high")
        ):
            raise ValueError(f"verbosity unsupported for {model}")
        sampling = cap.sampling or (
            model in {"gpt-6-sol", "gpt-6-luna"} and self.reasoning_effort == "none"
        )
        tool_support = cap.tools or (
            model in {"gpt-6-sol", "gpt-6-luna"} and self.reasoning_effort == "none"
        )
        result: dict[str, Any] = {cap.token_parameter: self.max_tokens}
        for name, bounds in (
            ("temperature", (0, 2)),
            ("top_p", (0, 1)),
            ("frequency_penalty", (-2, 2)),
            ("presence_penalty", (-2, 2)),
        ):
            value = getattr(self, name)
            if value is not None:
                if (
                    not sampling
                    or isinstance(value, bool)
                    or not isinstance(value, (int, float))
                    or not bounds[0] <= value <= bounds[1]
                ):
                    raise ValueError(f"{name} unsupported or invalid for {model}")
                result[name] = value
        if self.stop is not None:
            if not cap.sampling:
                raise ValueError(f"stop unsupported by this adapter for {model}")
            result["stop"] = self.stop
        if self.response_format is not None:
            kind = self.response_format.get("type")
            if kind not in {"text", "json_object", "json_schema"}:
                raise ValueError("Invalid response_format type")
            if kind == "json_schema" and not cap.structured_output:
                raise ValueError(f"json_schema unsupported for {model}")
            if kind == "json_schema" and not isinstance(
                self.response_format.get("json_schema"), dict
            ):
                raise ValueError("json_schema definition required")
            if kind == "json_schema":
                schema = self.response_format["json_schema"]
                if not schema.get("name") or not isinstance(schema.get("schema"), dict):
                    raise ValueError("json_schema requires name and schema")
            if not cap.sampling and not cap.structured_output:
                raise ValueError(f"response_format not supported by this adapter for {model}")
            result["response_format"] = self.response_format
        if tools or self.tool_choice is not None or self.parallel_tool_calls is not None:
            if not tool_support:
                raise ValueError(
                    f"Tools require a different endpoint/settings for {model}; use Responses"
                )
            if not tools:
                raise ValueError("tool_choice/parallel_tool_calls require tools")
            if self.parallel_tool_calls is not None and type(self.parallel_tool_calls) is not bool:
                raise ValueError("parallel_tool_calls must be boolean")
            if (
                self.tool_choice is not None
                and not isinstance(self.tool_choice, dict)
                and self.tool_choice not in ("auto", "none", "required")
            ):
                raise ValueError("Invalid tool_choice")
            result["tools"] = tools
            if self.tool_choice is not None:
                result["tool_choice"] = self.tool_choice
            if self.parallel_tool_calls is not None:
                result["parallel_tool_calls"] = self.parallel_tool_calls
        for name in ("reasoning_effort", "verbosity"):
            if getattr(self, name) is not None:
                result[name] = getattr(self, name)
        return result


def chat_settings(
    model: str,
    max_tokens: int,
    temperature: float | None,
    options: dict[str, Any],
    *,
    tools: list[dict] | None = None,
    default_temperature: float | None = 0.7,
) -> dict[str, Any]:
    """Compatibility bridge for existing **kwargs APIs. Typos raise before I/O."""
    allowed = set(OpenAIChatSettings.__dataclass_fields__) - {"max_tokens", "temperature"}
    unknown = set(options) - allowed
    if unknown:
        raise ValueError(f"Unsupported OpenAI settings: {', '.join(sorted(unknown))}")
    if temperature is None and capabilities(model).sampling:
        temperature = default_temperature
    return OpenAIChatSettings(max_tokens=max_tokens, temperature=temperature, **options).to_request(
        model, tools=tools
    )
