# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Serve the reasoning_engine ``{class_method, input}`` contract over HTTP.

Exists to guarantee support for the Google Cloud console playground and Gemini
(via ADK registration), which both invoke the engine through this contract.
Agent Runtime forwards calls to ``/api/reasoning_engine`` (sync) and
``/api/stream_reasoning_engine`` (streaming); dispatch is limited to the
:class:`AdkApp` ``register_operations()`` methods so the wire output matches an
agent packaged for Agent Runtime.
"""

import inspect
import json
from typing import Any

from agentplatform.agent_engines.templates.adk import AdkApp
from fastapi import FastAPI, HTTPException, Request, encoders, responses
from starlette.concurrency import iterate_in_threadpool, run_in_threadpool

from app.app_utils import services


def _no_op_instrumentor_builder(project_id: str) -> None:
    """No-op so set_up() keeps the startup instrumentor and generate_content spans."""
    return None


def attach_reasoning_engine_routes(app: FastAPI) -> None:
    """Register reasoning_engine routes that dispatch to an AdkApp."""
    runtime: AdkApp | None = None
    streaming_methods: set[str] = set()
    sync_methods: set[str] = set()

    def get_runtime() -> AdkApp:
        nonlocal runtime, streaming_methods, sync_methods
        if runtime is None:
            from app.agent import app as adk_app

            # Reuse the process-wide services so sessions created here are
            # visible to the adk_api and A2A paths, and vice versa (see services.py).
            runtime = AdkApp(
                app=adk_app,
                session_service_builder=services.get_session_service,
                artifact_service_builder=services.get_artifact_service,
                instrumentor_builder=_no_op_instrumentor_builder,
            )
            runtime.set_up()
            operations = runtime.register_operations()
            streaming_methods = set(operations.get("stream", [])) | set(
                operations.get("async_stream", [])
            )
            sync_methods = set(operations.get("", [])) | set(
                operations.get("async", [])
            )
        return runtime

    def resolve_method(class_method: str, *, streaming: bool):
        rt = get_runtime()
        allowed = streaming_methods if streaming else sync_methods
        if class_method not in allowed:
            raise HTTPException(
                status_code=404,
                detail=f"Unsupported reasoning_engine method: {class_method!r}",
            )
        return getattr(rt, class_method)

    def _normalize_kwargs(raw_input: Any) -> dict[str, Any]:
        if raw_input is None:
            return {"message": "", "user_id": "default_user"}
        if isinstance(raw_input, str):
            return {"message": raw_input, "user_id": "default_user"}
        if isinstance(raw_input, dict):
            res = dict(raw_input)
            if "message" not in res and "input" in res:
                res["message"] = res.pop("input")
            if "message" not in res and "prompt" in res:
                res["message"] = res.pop("prompt")
            res.setdefault("user_id", "default_user")
            return res
        return {"message": str(raw_input), "user_id": "default_user"}

    def _prepare_args(method_name: str, raw_input: Any) -> dict[str, Any]:
        if method_name == "streaming_agent_run_with_events":
            if isinstance(raw_input, str):
                try:
                    parsed = json.loads(raw_input)
                    if isinstance(parsed, dict):
                        return _prepare_args(method_name, parsed)
                except Exception:
                    pass
                return {"request_json": raw_input}
            if isinstance(raw_input, dict):
                if "request_json" in raw_input and isinstance(raw_input["request_json"], str):
                    return {"request_json": raw_input["request_json"]}
                req_dict = dict(raw_input)
                msg = req_dict.get("message") or req_dict.get("input") or req_dict.get("prompt") or ""
                if isinstance(msg, str):
                    req_dict["message"] = {"parts": [{"text": msg}], "role": "user"}
                elif isinstance(msg, dict) and "parts" not in msg:
                    req_dict["message"] = {"parts": [{"text": str(msg)}], "role": "user"}
                req_dict.setdefault("user_id", "default_user")
                return {"request_json": json.dumps(req_dict)}
            return {
                "request_json": json.dumps({
                    "message": {"parts": [{"text": str(raw_input)}], "role": "user"},
                    "user_id": "default_user",
                })
            }
        return _normalize_kwargs(raw_input)

    @app.post("/api/stream_reasoning_engine")
    async def stream_query(request: Request) -> responses.StreamingResponse:
        body = await request.json()
        get_runtime()
        class_method = body.get("class_method")
        if not class_method:
            class_method = (
                "async_stream_query"
                if "async_stream_query" in streaming_methods
                else "stream_query"
            )
        method = resolve_method(class_method, streaming=True)
        kwargs = _prepare_args(class_method, body.get("input"))
        stream = (
            await method(**kwargs)
            if inspect.iscoroutinefunction(method)
            else method(**kwargs)
        )

        async def generator():
            if hasattr(stream, "__aiter__"):
                async for event in stream:
                    yield json.dumps(encoders.jsonable_encoder(event)) + "\n"
            else:
                async for event in iterate_in_threadpool(stream):
                    yield json.dumps(encoders.jsonable_encoder(event)) + "\n"

        return responses.StreamingResponse(
            content=generator(), media_type="application/json"
        )

    @app.post("/api/reasoning_engine")
    async def query(request: Request) -> responses.JSONResponse:
        body = await request.json()
        get_runtime()
        class_method = body.get("class_method")

        if class_method and class_method in sync_methods:
            method = getattr(get_runtime(), class_method)
            kwargs = _prepare_args(class_method, body.get("input"))
            if inspect.iscoroutinefunction(method):
                output = await method(**kwargs)
            else:
                output = await run_in_threadpool(method, **kwargs)
            return responses.JSONResponse(
                content=encoders.jsonable_encoder({"output": output})
            )

        stream_method_name = (
            class_method
            if (class_method and class_method in streaming_methods)
            else (
                "async_stream_query"
                if "async_stream_query" in streaming_methods
                else "stream_query"
            )
        )
        method = getattr(get_runtime(), stream_method_name)
        kwargs = _prepare_args(stream_method_name, body.get("input"))
        stream = (
            await method(**kwargs)
            if inspect.iscoroutinefunction(method)
            else method(**kwargs)
        )
        collected = []
        if hasattr(stream, "__aiter__"):
            async for event in stream:
                collected.append(event)
        else:
            for event in stream:
                collected.append(event)
        return responses.JSONResponse(
            content=encoders.jsonable_encoder({"output": collected})
        )
