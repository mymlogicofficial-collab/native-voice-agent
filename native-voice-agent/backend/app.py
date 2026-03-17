
import os
import re
from datetime import datetime
import json
import urllib.request
import urllib.error
from typing import Any, Dict, Optional

from flask import Flask, jsonify, request
from flask_socketio import SocketIO, emit


def _normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").strip().lower())


def _rule_based_reply(text: str) -> str:
    normalized = _normalize_text(text)
    if not normalized:
        return "Say something and I’ll reply." 

    if normalized in {"hi", "hello", "hey"}:
        return "Hello. How can I help?"

    if "help" in normalized:
        return "Try: 'hello', 'time', 'date', or ask a simple question."

    if "time" in normalized:
        return f"Local time is {datetime.now().strftime('%H:%M:%S')}."

    if "date" in normalized or "day" in normalized:
        return f"Local date is {datetime.now().strftime('%Y-%m-%d')}."

    if normalized.startswith("echo "):
        return normalized[5:].strip() or "(empty echo)"

    return f"You said: {text}"


def _is_command_like(text: str) -> bool:
    normalized = _normalize_text(text)
    if not normalized:
        return True
    if normalized in {"hi", "hello", "hey"}:
        return True
    if "help" in normalized:
        return True
    if "time" in normalized:
        return True
    if "date" in normalized or "day" in normalized:
        return True
    if normalized.startswith("echo "):
        return True
    return False


def _ollama_generate(prompt: str) -> str:
    base_url = os.environ.get("OLLAMA_URL", "http://127.0.0.1:11434").rstrip("/")
    model = os.environ.get("OLLAMA_MODEL", "gemma3:12b")
    timeout_s = float(os.environ.get("OLLAMA_TIMEOUT_S", "60"))

    url = f"{base_url}/api/generate"
    body = {
        "model": model,
        "prompt": prompt,
        "stream": False,
    }

    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=timeout_s) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, ValueError) as e:
        return f"Ollama error: {e}"

    response_text = data.get("response")
    if isinstance(response_text, str) and response_text.strip():
        return response_text.strip()
    return "Ollama returned an empty response."


app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev")

socketio = SocketIO(
    app,
    cors_allowed_origins=os.environ.get("CORS_ALLOWED_ORIGINS", "*"),
    async_mode=os.environ.get("SOCKETIO_ASYNC_MODE"),
)


@app.get("/health")
def health() -> Any:
    ollama_enabled = os.environ.get("OLLAMA_ENABLED", "0") in {"1", "true", "True"}
    return jsonify({"status": "ok", "ollama_enabled": ollama_enabled})


@app.post("/chat")
def chat() -> Any:
    data = request.get_json(silent=True) or {}
    text = str(data.get("text", ""))
    session_id = data.get("session_id")

    ollama_enabled = os.environ.get("OLLAMA_ENABLED", "0") in {"1", "true", "True"}
    if ollama_enabled and not _is_command_like(text):
        reply = _ollama_generate(text)
    else:
        reply = _rule_based_reply(text)

    payload: Dict[str, Any] = {"text": reply}
    if session_id is not None:
        payload["session_id"] = session_id
    return jsonify(payload)


@socketio.on("connect")
def on_connect(auth: Optional[Dict[str, Any]] = None) -> None:
    emit("server_status", {"status": "connected"})


@socketio.on("disconnect")
def on_disconnect() -> None:
    return


@socketio.on("user_message")
def on_user_message(data: Any) -> None:
    payload = data if isinstance(data, dict) else {}
    text = str(payload.get("text", ""))
    session_id = payload.get("session_id")

    ollama_enabled = os.environ.get("OLLAMA_ENABLED", "0") in {"1", "true", "True"}
    if ollama_enabled and not _is_command_like(text):
        reply = _ollama_generate(text)
    else:
        reply = _rule_based_reply(text)

    out: Dict[str, Any] = {"text": reply}
    if session_id is not None:
        out["session_id"] = session_id

    emit("bot_message", out)


if __name__ == "__main__":
    host = os.environ.get("HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", "5000"))
    debug = os.environ.get("DEBUG", "1") not in {"0", "false", "False"}

    socketio.run(app, host=host, port=port, debug=debug)
