from __future__ import annotations

from typing import Any, Dict, List, Optional

import httpx

from llm.schemas import LLMRequest, LLMResponse, ToolCall
from llm.tools import ToolSpec, execute_tool
from settings import get_settings


class LLMClient:
    def __init__(self, provider: Optional[str] = None, model: Optional[str] = None) -> None:
        settings = get_settings()
        self.provider = provider or settings.llm_provider
        if (provider or settings.llm_provider) == "dashscope" and settings.dashscope_model:
            self.model = model or settings.dashscope_model
        else:
            self.model = model or settings.llm_model
        self.api_key = settings.llm_api_key
        self.dashscope_api_key = settings.dashscope_api_key
        self.dashscope_base_url = settings.dashscope_base_url

    def complete(
        self,
        request: LLMRequest,
        tools: Optional[List[ToolSpec]] = None,
        tool_choice: Optional[str] = None,
        trace: Optional[List[Dict[str, Any]]] = None,
        trace_messages: Optional[List[Dict[str, Any]]] = None,
        trace_label: Optional[str] = None,
    ) -> LLMResponse:
        if trace_messages is not None:
            if not trace_messages:
                if request.system_prompt:
                    trace_messages.append({"role": "system", "content": request.system_prompt})
            trace_messages.append({"role": "user", "content": request.user_prompt})
        if trace is not None and self.provider != "dashscope":
            messages = []
            if request.system_prompt:
                messages.append({"role": "system", "content": request.system_prompt})
            messages.append({"role": "user", "content": request.user_prompt})
            trace.append(
                {
                    "label": trace_label or "llm_request",
                    "provider": self.provider,
                    "model": self.model,
                    "messages": messages,
                    "tools": [tool.as_openai() for tool in tools] if tools else None,
                    "tool_choice": tool_choice or "auto",
                }
            )
        if self.provider == "dashscope":
            return self._complete_dashscope(
                request,
                tools=tools,
                tool_choice=tool_choice,
                trace=trace,
                trace_messages=trace_messages,
                trace_label=trace_label,
            )
        content = f"[{self.provider}:{self.model}] {request.user_prompt}"
        if trace_messages is not None:
            trace_messages.append({"role": "assistant", "content": content})
        if trace is not None:
            trace.append(
                {
                    "label": trace_label or "llm_response",
                    "messages": [
                        {"role": "assistant", "content": content},
                    ],
                }
            )
        return LLMResponse(content=content)

    def _complete_dashscope(
        self,
        request: LLMRequest,
        tools: Optional[List[ToolSpec]] = None,
        tool_choice: Optional[str] = None,
        trace: Optional[List[Dict[str, Any]]] = None,
        trace_messages: Optional[List[Dict[str, Any]]] = None,
        trace_label: Optional[str] = None,
    ) -> LLMResponse:
        if not self.dashscope_api_key:
            if trace is not None:
                trace.append(
                    {
                        "label": trace_label or "llm_error",
                        "error": "missing_dashscope_api_key",
                    }
                )
            return LLMResponse(content="[dashscope] missing api key")
        url = f"{self.dashscope_base_url}/chat/completions"
        headers = {"Authorization": f"Bearer {self.dashscope_api_key}"}
        messages = []
        if request.system_prompt:
            messages.append({"role": "system", "content": request.system_prompt})
        messages.append({"role": "user", "content": request.user_prompt})

        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.2,
        }
        if tools:
            payload["tools"] = [tool.as_openai() for tool in tools]
            payload["tool_choice"] = tool_choice or "auto"

        if trace_messages is not None:
            if not trace_messages:
                if request.system_prompt:
                    trace_messages.append({"role": "system", "content": request.system_prompt})
            trace_messages.append({"role": "user", "content": request.user_prompt})
        if trace is not None:
            trace.append(
                {
                    "label": trace_label or "llm_request",
                    "provider": self.provider,
                    "model": self.model,
                    "messages": messages,
                    "tools": payload.get("tools"),
                    "tool_choice": payload.get("tool_choice"),
                }
            )

        try:
            with httpx.Client(timeout=30) as client:
                response = client.post(url, json=payload, headers=headers)
                response.raise_for_status()
                data = response.json()
        except httpx.HTTPError as exc:
            if trace is not None:
                trace.append(
                    {
                        "label": trace_label or "llm_error",
                        "error": str(exc),
                        "provider": self.provider,
                        "model": self.model,
                    }
                )
            return LLMResponse(content=f"[llm_error] {exc}")

        message = data["choices"][0]["message"]
        tool_calls_raw = message.get("tool_calls", []) or []
        tool_calls: List[ToolCall] = []
        tool_outputs: List[Dict[str, Any]] = []

        if tool_calls_raw:
            for call in tool_calls_raw:
                fn = call.get("function", {})
                name = fn.get("name")
                arguments = fn.get("arguments")
                if isinstance(arguments, str):
                    try:
                        import json

                        arguments = json.loads(arguments)
                    except Exception:
                        arguments = {}
                tool_call = ToolCall(id=call.get("id"), name=name, arguments=arguments or {})
                tool_calls.append(tool_call)
                output = execute_tool(name, tool_call.arguments)
                tool_outputs.append(output)

            if trace_messages is not None:
                trace_messages.append({"role": "assistant", "content": None, "tool_calls": tool_calls_raw})
                for call, output in zip(tool_calls_raw, tool_outputs):
                    trace_messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": call.get("id"),
                            "name": call.get("function", {}).get("name"),
                            "content": __import__("json").dumps(output, ensure_ascii=False),
                        }
                    )

            if trace is not None:
                trace.append(
                    {
                        "label": trace_label or "tool_calls",
                        "messages": [
                            {"role": "assistant", "content": None, "tool_calls": tool_calls_raw},
                            *[
                                {
                                    "role": "tool",
                                    "tool_call_id": call.get("id"),
                                    "name": call.get("function", {}).get("name"),
                                    "content": __import__("json").dumps(output, ensure_ascii=False),
                                }
                                for call, output in zip(tool_calls_raw, tool_outputs)
                            ],
                        ],
                    }
                )

            import json

            followup_messages = messages + [
                {
                    "role": "assistant",
                    "tool_calls": tool_calls_raw,
                    "content": None,
                }
            ]
            for call, output in zip(tool_calls_raw, tool_outputs):
                followup_messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": call.get("id"),
                        "name": call.get("function", {}).get("name"),
                        "content": json.dumps(output, ensure_ascii=False),
                    }
                )

            payload = {
                "model": self.model,
                "messages": followup_messages,
                "temperature": 0.2,
            }
            try:
                with httpx.Client(timeout=30) as followup_client:
                    response = followup_client.post(url, json=payload, headers=headers)
                    response.raise_for_status()
                    data = response.json()
            except httpx.HTTPError as exc:
                if trace is not None:
                    trace.append(
                        {
                            "label": trace_label or "llm_error",
                            "error": str(exc),
                            "provider": self.provider,
                            "model": self.model,
                        }
                    )
                return LLMResponse(content=f"[llm_error] {exc}", tool_calls=tool_calls, tool_outputs=tool_outputs)
            content = data["choices"][0]["message"].get("content", "") or ""
            if trace_messages is not None:
                trace_messages.append({"role": "assistant", "content": content})
            if trace is not None:
                trace.append(
                    {
                        "label": trace_label or "llm_followup",
                        "messages": followup_messages
                        + [{"role": "assistant", "content": content}],
                    }
                )
            return LLMResponse(content=content, tool_calls=tool_calls, tool_outputs=tool_outputs)

        content = message.get("content", "") or ""
        if trace_messages is not None:
            trace_messages.append({"role": "assistant", "content": content})
        if trace is not None:
            trace.append({"label": trace_label or "llm_response", "messages": [{"role": "assistant", "content": content}]})
        return LLMResponse(content=content)
