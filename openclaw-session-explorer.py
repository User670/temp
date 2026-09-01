#!/usr/bin/env python3
"""OpenClaw Session Explorer - Interactive CLI to explore openclaw sessions."""

try:
    from rich.console import Console
    from rich.markup import escape as rich_escape
except ImportError:
    import sys
    print("This app requires the 'rich' library.")
    print("Install it with: pip install rich")
    sys.exit(1)

import argparse
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from io import StringIO
from pathlib import Path

try:
    import msvcrt
    _IS_WINDOWS = True
except ImportError:
    _IS_WINDOWS = False

try:
    import tty
    import termios
    _HAS_TERMIOS = True
except ImportError:
    _HAS_TERMIOS = False

CONFIG_PATH = Path.home() / ".openclaw-session-explorer.json"
PAGE_SIZE = 5
TOOL_CALL_TRUNCATE = 300
TOOL_RESULT_TRUNCATE = 500
PREVIEW_LENGTH = 200

_preview_cache = {}

console = Console()


# --- Mouse wheel support for vertical scrolling ---

if _IS_WINDOWS:
    import ctypes
    from ctypes import wintypes

    _kernel32 = ctypes.windll.kernel32
    _STD_INPUT_HANDLE = -10
    _ENABLE_MOUSE_INPUT = 0x0010
    _ENABLE_EXTENDED_FLAGS = 0x0080
    _ENABLE_QUICK_EDIT_MODE = 0x0040
    _MOUSE_WHEELED = 0x0004

    class _COORD(ctypes.Structure):
        _fields_ = [("X", ctypes.c_short), ("Y", ctypes.c_short)]

    class _MOUSE_EVENT_RECORD(ctypes.Structure):
        _fields_ = [
            ("dwMousePosition", _COORD),
            ("dwButtonState", wintypes.DWORD),
            ("dwControlKeyState", wintypes.DWORD),
            ("dwEventFlags", wintypes.DWORD),
        ]

    class _KEY_EVENT_RECORD(ctypes.Structure):
        _fields_ = [
            ("bKeyDown", wintypes.BOOL),
            ("wRepeatCount", wintypes.WORD),
            ("wVirtualKeyCode", wintypes.WORD),
            ("wVirtualScanCode", wintypes.WORD),
            ("uChar", wintypes.WCHAR),
            ("dwControlKeyState", wintypes.DWORD),
        ]

    class _INPUT_RECORD(ctypes.Structure):
        class _Event(ctypes.Union):
            _fields_ = [
                ("KeyEvent", _KEY_EVENT_RECORD),
                ("MouseEvent", _MOUSE_EVENT_RECORD),
                ("_padding", ctypes.c_byte * 16),
            ]
        _fields_ = [
            ("EventType", wintypes.WORD),
            ("Event", _Event),
        ]

    _mouse_console_handle = None
    _mouse_old_mode = None

    def enable_mouse():
        """Enable mouse wheel input on Windows console."""
        global _mouse_console_handle, _mouse_old_mode
        _mouse_console_handle = _kernel32.GetStdHandle(_STD_INPUT_HANDLE)
        mode = wintypes.DWORD()
        _kernel32.GetConsoleMode(_mouse_console_handle, ctypes.byref(mode))
        _mouse_old_mode = mode.value
        new_mode = (_mouse_old_mode | _ENABLE_MOUSE_INPUT | _ENABLE_EXTENDED_FLAGS) & ~_ENABLE_QUICK_EDIT_MODE
        _kernel32.SetConsoleMode(_mouse_console_handle, new_mode)

    def disable_mouse():
        """Restore console mode."""
        global _mouse_console_handle, _mouse_old_mode
        if _mouse_console_handle is not None and _mouse_old_mode is not None:
            _kernel32.SetConsoleMode(_mouse_console_handle, _mouse_old_mode)
            _mouse_console_handle = None
            _mouse_old_mode = None

    def _read_key_windows_mouse():
        """Read key or mouse wheel event via ReadConsoleInputW."""
        buf = _INPUT_RECORD()
        count = wintypes.DWORD()
        while True:
            _kernel32.ReadConsoleInputW(_mouse_console_handle, ctypes.byref(buf), 1, ctypes.byref(count))
            if buf.EventType == 1:  # KEY_EVENT
                if not buf.Event.KeyEvent.bKeyDown:
                    continue
                ch = buf.Event.KeyEvent.uChar
                vk = buf.Event.KeyEvent.wVirtualKeyCode
                if ch == '\x03':
                    raise KeyboardInterrupt
                if ch == '\x04':
                    return "q"
                if vk == 13 or ch == '\r':
                    return "enter"
                if vk == 27:
                    return "escape"
                if vk == 37:
                    return "left"
                if vk == 38:
                    return "up"
                if vk == 39:
                    return "right"
                if vk == 40:
                    return "down"
                if ch and ch != '\x00' and ch != '\xe0':
                    return ch
            elif buf.EventType == 2:  # MOUSE_EVENT
                if buf.Event.MouseEvent.dwEventFlags & _MOUSE_WHEELED:
                    high_word = ctypes.c_short((buf.Event.MouseEvent.dwButtonState >> 16) & 0xFFFF).value
                    if high_word > 0:
                        return "wheel_up"
                    else:
                        return "wheel_down"
else:
    _unix_mouse_enabled = False

    def enable_mouse():
        """Enable mouse tracking on Unix terminals."""
        global _unix_mouse_enabled
        sys.stdout.write("\x1b[?1000h\x1b[?1006h")
        sys.stdout.flush()
        _unix_mouse_enabled = True

    def disable_mouse():
        """Disable mouse tracking on Unix terminals."""
        global _unix_mouse_enabled
        sys.stdout.write("\x1b[?1000l\x1b[?1006l")
        sys.stdout.flush()
        _unix_mouse_enabled = False


def load_config():
    try:
        if CONFIG_PATH.exists():
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return {}


def save_config(cfg):
    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2)
    except Exception:
        pass


def detect_openclaw_dir():
    if shutil.which("openclaw"):
        try:
            result = subprocess.run(
                ["openclaw", "config", "path"],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0 and result.stdout.strip():
                p = Path(result.stdout.strip())
                if p.exists():
                    return str(p)
        except Exception:
            pass
    default = Path.home() / ".openclaw"
    if default.exists():
        return str(default)
    return None


def prompt_openclaw_dir(cfg):
    saved = cfg.get("openclaw_dir")
    detected = detect_openclaw_dir()
    default = saved or detected or str(Path.home() / ".openclaw")

    while True:
        console.print(f"\nOpenClaw directory [bold]{default}[/]: ", end="")
        user_input = input().strip()
        path = user_input if user_input else default

        if not Path(path).exists():
            console.print(f"[red]Directory does not exist: {path}[/]")
            continue
        if not (Path(path) / "agents").exists():
            console.print(f"[red]No 'agents' subdirectory found in: {path}[/]")
            continue

        cfg["openclaw_dir"] = path
        save_config(cfg)
        return path


def _parse_timestamp_to_ms(ts):
    """Parse a timestamp (ISO string or epoch number) to milliseconds."""
    if ts is None:
        return None
    if isinstance(ts, (int, float)):
        ts_num = float(ts)
        if ts_num > 1e12:
            return ts_num
        else:
            return ts_num * 1000
    if isinstance(ts, str):
        ts = ts.strip()
        # Try numeric first
        try:
            ts_num = float(ts)
            if ts_num > 1e12:
                return ts_num
            else:
                return ts_num * 1000
        except ValueError:
            pass
        # Try ISO 8601
        try:
            s = ts.replace("Z", "+00:00")
            dt = datetime.fromisoformat(s)
            return dt.timestamp() * 1000
        except ValueError:
            pass
    return None


def _extract_session_meta_from_jsonl(jsonl_path):
    """Extract basic metadata from a JSONL file by scanning its lines."""
    session_id = Path(jsonl_path).stem
    started_at = 0
    last_active = 0
    model = ""
    channel = ""

    first_ts = None
    last_ts = None
    for obj in iter_jsonl_lines(jsonl_path):
        ts = _parse_timestamp_to_ms(obj.get("timestamp"))
        if ts is not None:
            if first_ts is None:
                first_ts = ts
            last_ts = ts

        if not model and obj.get("type") == "session":
            spr = obj.get("systemPromptReport", {})
            provider = spr.get("provider", "")
            model_id = spr.get("model", "")
            if provider and model_id:
                model = f"{provider}/{model_id}"
            elif model_id:
                model = model_id

        if not channel and obj.get("type") == "session":
            dc = obj.get("deliveryContext", {})
            channel = dc.get("channel", "")
            if not channel:
                channel = obj.get("lastChannel", "")

    if first_ts:
        started_at = int(first_ts)
    if last_ts:
        last_active = int(last_ts)

    return {
        "session_id": session_id,
        "model": model,
        "channel": channel,
        "started_at": started_at,
        "last_active": last_active,
    }


def load_sessions(openclaw_dir):
    sessions = []
    agents_dir = Path(openclaw_dir) / "agents"
    if not agents_dir.exists():
        return sessions

    for agent_path in sorted(agents_dir.iterdir()):
        if not agent_path.is_dir():
            continue
        agent_name = agent_path.name
        sessions_dir = agent_path / "sessions"
        sessions_file = sessions_dir / "sessions.json"

        seen_ids = set()

        if sessions_file.exists():
            try:
                with open(sessions_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except (json.JSONDecodeError, OSError) as e:
                console.print(f"[red]Error reading {sessions_file}: {e}[/]")
                data = {}
            else:
                for key, entry in data.items():
                    session_file = entry.get("sessionFile", "")
                    session_id = entry.get("sessionId", "")
                    if not session_id:
                        continue
                    seen_ids.add(session_id)
                    jsonl_path = None
                    if session_file and Path(session_file).exists():
                        jsonl_path = session_file
                    else:
                        candidate = sessions_dir / f"{session_id}.jsonl"
                        if candidate.exists():
                            jsonl_path = str(candidate)

                    spr = entry.get("systemPromptReport", {})
                    model_str = ""
                    provider = spr.get("provider", "")
                    model_id = spr.get("model", "")
                    if provider and model_id:
                        model_str = f"{provider}/{model_id}"
                    elif model_id:
                        model_str = model_id

                    channel = entry.get("lastChannel") or ""
                    if not channel:
                        dc = entry.get("deliveryContext", {})
                        channel = dc.get("channel", "")

                    status = entry.get("status", "unknown")
                    aborted = entry.get("abortedLastRun", False)

                    started_at = entry.get("sessionStartedAt") or entry.get("startedAt") or 0
                    last_active = entry.get("lastInteractionAt") or entry.get("updatedAt") or 0

                    origin = entry.get("origin", {})
                    origin_label = origin.get("label", "")

                    sessions.append({
                        "agent": agent_name,
                        "session_key": key,
                        "session_id": session_id,
                        "jsonl_path": jsonl_path,
                        "status": status,
                        "aborted": aborted,
                        "model": model_str,
                        "channel": channel,
                        "started_at": started_at,
                        "last_active": last_active,
                        "origin_label": origin_label,
                        "raw_entry": entry,
                    })

        # Scan for JSONL files not in sessions.json
        if sessions_dir.exists():
            for jsonl_file in sessions_dir.glob("*.jsonl"):
                if jsonl_file.name == "sessions.jsonl":
                    continue
                file_session_id = jsonl_file.stem
                if file_session_id in seen_ids:
                    continue
                meta = _extract_session_meta_from_jsonl(str(jsonl_file))
                sessions.append({
                    "agent": agent_name,
                    "session_key": file_session_id,
                    "session_id": meta["session_id"],
                    "jsonl_path": str(jsonl_file),
                    "status": "unknown",
                    "aborted": False,
                    "model": meta["model"],
                    "channel": meta["channel"],
                    "started_at": meta["started_at"],
                    "last_active": meta["last_active"],
                    "origin_label": "",
                    "raw_entry": {},
                })

    sessions.sort(key=lambda s: s["last_active"], reverse=True)
    return sessions


def format_relative_time(epoch_ms):
    if not epoch_ms:
        return "N/A"
    try:
        dt = datetime.fromtimestamp(epoch_ms / 1000, tz=timezone.utc)
        now = datetime.now(tz=timezone.utc)
        diff = now - dt
        seconds = int(diff.total_seconds())
        if seconds < 60:
            return "just now"
        minutes = seconds // 60
        if minutes < 60:
            return f"{minutes}m ago"
        hours = minutes // 60
        if hours < 24:
            return f"{hours}h ago"
        days = hours // 24
        if days < 30:
            return f"{days}d ago"
        months = days // 30
        if months < 12:
            return f"{months}mo ago"
        years = months // 12
        return f"{years}y ago"
    except Exception:
        return "N/A"


def format_timestamp(epoch_ms):
    if not epoch_ms:
        return "N/A"
    try:
        dt = datetime.fromtimestamp(epoch_ms / 1000, tz=timezone.utc)
        return dt.strftime("%Y-%m-%d %H:%M:%S UTC")
    except Exception:
        return "N/A"


def get_status_display(status, aborted):
    if aborted:
        return "[red]aborted[/]"
    if status == "done":
        return "[green]done[/]"
    return f"[yellow]{status}[/]"


def unescape_text(text):
    if not isinstance(text, str):
        text = str(text)
    _PH = "\x00BS\x00"
    text = text.replace("\\\\", _PH)
    text = text.replace("\\n", "\n")
    text = text.replace("\\t", "\t")
    text = text.replace("\\r", "\r")
    text = text.replace(_PH, "\\")
    return text


def truncate_text(text, max_len):
    if len(text) <= max_len:
        return text
    return text[:max_len] + "..."


def extract_text_from_content(content_list):
    texts = []
    for item in content_list:
        if not isinstance(item, dict):
            continue
        ctype = item.get("type", "")
        if ctype == "text":
            texts.append(item.get("text", ""))
    return texts


def iter_jsonl_lines(jsonl_path):
    if not jsonl_path or not Path(jsonl_path).exists():
        return
    try:
        with open(jsonl_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.rstrip("\n\r")
                if not line:
                    continue
                try:
                    yield json.loads(line)
                except json.JSONDecodeError:
                    yield {"_raw": line, "_parse_error": True}
    except OSError as e:
        yield {"_error": str(e), "_io_error": True}


def get_first_user_message(jsonl_path):
    cache_key = ("first_user", jsonl_path)
    if cache_key in _preview_cache:
        return _preview_cache[cache_key]
    result = None
    for obj in iter_jsonl_lines(jsonl_path):
        if obj.get("type") == "message" and obj.get("message", {}).get("role") == "user":
            content = obj["message"].get("content", [])
            if isinstance(content, str):
                if content:
                    result = unescape_text(content)
                    break
            else:
                texts = extract_text_from_content(content)
                if texts:
                    result = unescape_text(texts[0])
                    break
    _preview_cache[cache_key] = result
    return result


def get_last_assistant_message(jsonl_path):
    cache_key = ("last_asst", jsonl_path)
    if cache_key in _preview_cache:
        return _preview_cache[cache_key]
    last = None
    for obj in iter_jsonl_lines(jsonl_path):
        if obj.get("type") == "message" and obj.get("message", {}).get("role") == "assistant":
            texts = []
            for item in obj["message"].get("content", []):
                if isinstance(item, dict) and item.get("type") == "text":
                    texts.append(item.get("text", ""))
            if texts:
                last = unescape_text(texts[0])
    _preview_cache[cache_key] = last
    return last


def get_filtered_blocks(jsonl_path, verbose=False):
    blocks = []
    for obj in iter_jsonl_lines(jsonl_path):
        if obj.get("_parse_error") or obj.get("_io_error"):
            blocks.append(obj)
            continue
        btype = obj.get("type", "")
        if verbose:
            blocks.append(obj)
        else:
            if btype == "session":
                blocks.append(obj)
            elif btype == "message":
                blocks.append(obj)
    return blocks


def search_in_sessions(sessions, query):
    if not query:
        return sessions
    q = query.lower()
    results = []
    for s in sessions:
        jsonl_path = s.get("jsonl_path")
        if not jsonl_path:
            if q in s.get("session_id", "").lower() or q in s.get("model", "").lower() or q in s.get("channel", "").lower():
                results.append(s)
            continue
        found = False
        for obj in iter_jsonl_lines(jsonl_path):
            if found:
                break
            if obj.get("type") != "message":
                continue
            role = obj.get("message", {}).get("role", "")
            if role not in ("user", "assistant"):
                continue
            content = obj.get("message", {}).get("content", [])
            if isinstance(content, str):
                if q in content.lower():
                    results.append(s)
                    continue
            for item in content if not isinstance(content, str) else []:
                if not isinstance(item, dict):
                    continue
                if item.get("type") in ("text", "thinking"):
                    text = item.get("text", "")
                    if q in text.lower():
                        results.append(s)
                        found = True
                        break
    return results


def search_in_blocks(blocks, query):
    if not query:
        return []
    q = query.lower()
    indices = []
    for i, obj in enumerate(blocks):
        if obj.get("type") != "message":
            continue
        role = obj.get("message", {}).get("role", "")
        if role not in ("user", "assistant"):
            continue
        content = obj.get("message", {}).get("content", [])
        if isinstance(content, str):
            if q in content.lower():
                indices.append(i)
                continue
        for item in content if not isinstance(content, str) else []:
            if not isinstance(item, dict):
                continue
            if item.get("type") in ("text", "thinking"):
                text = item.get("text", "")
                if q in text.lower():
                    indices.append(i)
                    break
        else:
            continue
        continue
    return indices


def read_key(mouse=False):
    if mouse and _IS_WINDOWS and _mouse_console_handle is not None:
        return _read_key_windows_mouse()
    if _IS_WINDOWS:
        ch = msvcrt.getwch()
        if ch == "\r" or ch == "\n":
            return "enter"
        if ch == "\x00" or ch == "\xe0":
            ch2 = msvcrt.getwch()
            if ch2 == "H":
                return "up"
            elif ch2 == "P":
                return "down"
            elif ch2 == "M":
                return "right"
            elif ch2 == "K":
                return "left"
            return "unknown"
        if ch == "\x1b":
            return "escape"
        if ch == "\x03":
            raise KeyboardInterrupt
        if ch == "\x04":
            return "q"
        return ch
    else:
        if _HAS_TERMIOS:
            fd = sys.stdin.fileno()
            old = termios.tcgetattr(fd)
            try:
                tty.setraw(fd)
                ch = sys.stdin.read(1)
                if ch == "\r" or ch == "\n":
                    return "enter"
                if ch == "\x1b":
                    ch2 = sys.stdin.read(1)
                    if ch2 == "[":
                        ch3 = sys.stdin.read(1)
                        if ch3 == "<":
                            # SGR mouse event: \x1b[<button;col;rowM
                            mouse_data = ""
                            while True:
                                c = sys.stdin.read(1)
                                if c in ("M", "m"):
                                    break
                                mouse_data += c
                            parts = mouse_data.split(";")
                            if parts:
                                try:
                                    button = int(parts[0])
                                    if button == 64:
                                        return "wheel_up"
                                    elif button == 65:
                                        return "wheel_down"
                                except ValueError:
                                    pass
                            return "unknown"
                        elif ch3 == "A":
                            return "up"
                        elif ch3 == "B":
                            return "down"
                        elif ch3 == "C":
                            return "right"
                        elif ch3 == "D":
                            return "left"
                    return "escape"
                if ch == "\x03":
                    raise KeyboardInterrupt
                if ch == "\x04":
                    return "q"
                return ch
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old)
        else:
            try:
                return input().strip()
            except EOFError:
                return "q"


def prompt_input(label):
    console.print(f"\n[bold]{label}[/]: ", end="")
    try:
        return input().strip()
    except (EOFError, KeyboardInterrupt):
        return ""


def save_jsonl(jsonl_path):
    if not jsonl_path or not Path(jsonl_path).exists():
        console.print("[red]No session file to save.[/]")
        return
    dest = prompt_input("Save to [path]")
    if not dest:
        console.print("[dim]Cancelled.[/]")
        return
    dest_path = Path(dest)
    if not dest_path.is_absolute():
        dest_path = Path.cwd() / dest_path
    if dest_path.exists():
        console.print(f"[yellow]File already exists: {dest_path}[/]")
        confirm = prompt_input("Overwrite? (y/n)")
        if confirm.lower() != "y":
            console.print("[dim]Cancelled.[/]")
            return
    try:
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(jsonl_path, dest_path)
        size = dest_path.stat().st_size
        console.print(f"[green]Saved to {dest_path} ({size} bytes)[/]")
    except OSError as e:
        console.print(f"[red]Error saving file: {e}[/]")


def render_block_content(obj, verbose=False, expanded=False, search_query=None):
    if obj.get("_io_error"):
        return f"[red][IO error: {obj['_error']}][/]"
    if obj.get("_parse_error"):
        raw = obj.get("_raw", "")
        if len(raw) > 200:
            raw = raw[:200] + "..."
        return f"[red][parse error][/]\n{rich_escape(unescape_text(raw))}"

    btype = obj.get("type", "")

    if btype == "session":
        sid = obj.get("id", "unknown")
        ts = obj.get("timestamp", "")
        cwd = obj.get("cwd", "")
        return f"[dim][session] {sid[:8]}... | {ts} | {cwd}[/]"

    if btype == "model_change":
        provider = obj.get("provider", "")
        model_id = obj.get("modelId", "")
        return f"[dim][model_change] {provider}/{model_id}[/]"

    if btype == "thinking_level_change":
        level = obj.get("thinkingLevel", "")
        return f"[dim][thinking_level_change] {level}[/]"

    if btype == "custom":
        custom_type = obj.get("customType", "")
        data = obj.get("data", {})
        data_str = json.dumps(data) if data else ""
        if len(data_str) > 100:
            data_str = data_str[:100] + "..."
        return f"[dim][custom: {custom_type}] {rich_escape(data_str)}[/]"

    if btype == "custom_message":
        custom_type = obj.get("customType", "")
        display = obj.get("display", True)
        if not display and not verbose:
            return None
        content = obj.get("content", "")
        if len(content) > 200:
            content = content[:200] + "..."
        return f"[dim][custom_message: {custom_type}] {rich_escape(unescape_text(content))}[/]"

    if btype == "message":
        msg = obj.get("message", {})
        role = msg.get("role", "")
        content_list = msg.get("content", [])

        if role == "user":
            parts = []
            if isinstance(content_list, str):
                text = unescape_text(content_list)
                if text:
                    parts.append(f"[bold cyan]User:[/]\n{rich_escape(text)}")
            else:
                for item in content_list:
                    if not isinstance(item, dict):
                        continue
                    ctype = item.get("type", "")
                    if ctype == "text":
                        text = unescape_text(item.get("text", ""))
                        parts.append(f"[bold cyan]User:[/]\n{rich_escape(text)}")
            return "\n".join(parts) if parts else "[bold cyan]User:[/] [dim](empty)[/]"

        if role == "assistant":
            parts = []
            for item in content_list:
                if not isinstance(item, dict):
                    continue
                ctype = item.get("type", "")
                if ctype == "thinking":
                    text = unescape_text(item.get("thinking", item.get("text", "")))
                    parts.append(f"[dim italic]Thinking:\n{rich_escape(text)}[/]")
                elif ctype == "text":
                    text = unescape_text(item.get("text", ""))
                    parts.append(f"[bold magenta]Assistant:[/]\n{rich_escape(text)}")
                elif ctype == "toolCall":
                    tool_name = item.get("name", "unknown")
                    args = item.get("arguments", {})
                    if isinstance(args, dict):
                        args_str = json.dumps(args, ensure_ascii=False)
                    else:
                        args_str = str(args)
                    args_str = unescape_text(args_str)
                    if expanded:
                        parts.append(f"[bold yellow]Tool Call: {rich_escape(tool_name)}[/]\n{rich_escape(args_str)}")
                    else:
                        truncated = truncate_text(args_str, TOOL_CALL_TRUNCATE)
                        if len(args_str) > TOOL_CALL_TRUNCATE:
                            parts.append(f"[bold yellow]Tool Call: {rich_escape(tool_name)}[/] [dim][+] expand[/]\n{rich_escape(truncated)}")
                        else:
                            parts.append(f"[bold yellow]Tool Call: {rich_escape(tool_name)}[/]\n{rich_escape(truncated)}")
            return "\n".join(parts) if parts else "[bold magenta]Assistant:[/] [dim](empty)[/]"

        if role == "toolResult":
            tool_name = msg.get("toolName", "unknown")
            exit_code = None
            duration = None
            is_error = msg.get("isError", False)
            details = msg.get("details", {})
            if isinstance(details, dict):
                exit_code = details.get("exitCode")
                duration = details.get("durationMs")

            text_parts = []
            for item in content_list:
                if not isinstance(item, dict):
                    continue
                ctype = item.get("type", "")
                if ctype == "text":
                    text_parts.append(item.get("text", ""))

            full_text = unescape_text("\n".join(text_parts))
            status_info = ""
            if exit_code is not None:
                status_info += f" exit={exit_code}"
            if duration is not None:
                status_info += f" {duration}ms"
            if is_error:
                status_info += " [red]ERROR[/]"

            if expanded:
                return f"[bold green]Tool Result: {rich_escape(tool_name)}[/]{status_info}\n{rich_escape(full_text)}"
            else:
                truncated = truncate_text(full_text, TOOL_RESULT_TRUNCATE)
                if len(full_text) > TOOL_RESULT_TRUNCATE:
                    return f"[bold green]Tool Result: {rich_escape(tool_name)}[/]{status_info} [dim][+] expand[/]\n{rich_escape(truncated)}"
                else:
                    return f"[bold green]Tool Result: {rich_escape(tool_name)}[/]{status_info}\n{rich_escape(truncated)}"

    return f"[dim][{btype}] {rich_escape(json.dumps(obj, ensure_ascii=False)[:200])}[/]"


def get_block_label(obj):
    if obj.get("_parse_error"):
        return "parse_error"
    if obj.get("_io_error"):
        return "io_error"
    btype = obj.get("type", "")
    if btype == "message":
        role = obj.get("message", {}).get("role", "")
        return role or btype
    return btype


def render_to_lines(content_str):
    """Render a rich markup string to a list of pre-wrapped lines (with ANSI codes if color is on)."""
    if not content_str:
        return []
    buf = StringIO()
    cap = Console(
        file=buf,
        width=console.width,
        force_terminal=bool(console.color_system),
        color_system=console.color_system,
        legacy_windows=False,
    )
    cap.print(content_str)
    text = buf.getvalue()
    lines = text.split('\n')
    while lines and lines[-1] == '':
        lines.pop()
    return lines


def session_detail_page(session, verbose=False):
    jsonl_path = session.get("jsonl_path")
    if not jsonl_path or not Path(jsonl_path).exists():
        console.print("[red]Session file not found.[/]")
        prompt_input("Press Enter to go back")
        return

    blocks = get_filtered_blocks(jsonl_path, verbose=verbose)
    total = len(blocks)

    if total == 0:
        _clear_screen()
        console.print("[yellow]Empty session.[/]")
        prompt_input("Press Enter to go back")
        return

    current = 0
    expanded = False
    show_raw = False
    scroll_offset = 0
    search_query = None
    search_matches = []

    enable_mouse()
    try:
        while True:
            _clear_screen()

            console.print(f"[bold]Session {session['session_id'][:8]}...[/] | {session['agent']} | {session['model']} | {get_status_display(session['status'], session['aborted'])}")
            console.print(f"[dim]Started {format_timestamp(session['started_at'])} | Last {format_timestamp(session['last_active'])} | {total} blocks[/]")
            console.print()

            obj = blocks[current]
            label = get_block_label(obj)

            expand_hint = " [-] collapse" if expanded else (" [+] expand" if _has_expandable(obj) else "")
            raw_hint = " [raw]" if show_raw else ""
            header = f"── Block {current + 1}/{total} [{label}]{expand_hint}{raw_hint} ── ←→ block | ↑↓/wheel scroll | e expand | r raw | v verbose | / search | n next match | s save | b back | q quit ──"

            console.print(header)
            console.print()

            # Render content to pre-wrapped lines
            if show_raw:
                content_str = rich_escape(json.dumps(obj, indent=2, ensure_ascii=False))
            else:
                content_str = render_block_content(obj, verbose=verbose, expanded=expanded, search_query=search_query)

            content_lines = render_to_lines(content_str)

            # Calculate viewport
            term_height = shutil.get_terminal_size().lines
            fixed_lines = 7  # session(2) + blank(1) + header(1) + blank(1) + indicator/blank(1) + footer(1)
            viewport_height = max(1, term_height - fixed_lines)

            max_offset = max(0, len(content_lines) - viewport_height)
            scroll_offset = max(0, min(scroll_offset, max_offset))

            # Display visible lines
            visible = content_lines[scroll_offset:scroll_offset + viewport_height]
            for line in visible:
                sys.stdout.write(line + "\n")
            sys.stdout.flush()

            # Scroll indicator or blank
            if len(content_lines) > viewport_height:
                end_line = min(scroll_offset + viewport_height, len(content_lines))
                pct = int((scroll_offset / max_offset) * 100) if max_offset > 0 else 0
                console.print(f"[dim]── lines {scroll_offset + 1}-{end_line}/{len(content_lines)} ({pct}%) ↑↓/wheel scroll ──[/]")
            else:
                console.print()

            console.print(header)

            key = read_key(mouse=True)

            if key == "up":
                scroll_offset = max(0, scroll_offset - 1)
            elif key == "down":
                scroll_offset = min(max_offset, scroll_offset + 1)
            elif key == "wheel_up":
                scroll_offset = max(0, scroll_offset - 3)
            elif key == "wheel_down":
                scroll_offset = min(max_offset, scroll_offset + 3)
            elif key in ("right", "l"):
                if current < total - 1:
                    current += 1
                    expanded = False
                    show_raw = False
                    scroll_offset = 0
                else:
                    console.print("[dim](last block)[/]")
            elif key in ("left", "h"):
                if current > 0:
                    current -= 1
                    expanded = False
                    show_raw = False
                    scroll_offset = 0
                else:
                    console.print("[dim](first block)[/]")
            elif key == "e":
                expanded = not expanded
                scroll_offset = 0
            elif key == "r":
                show_raw = not show_raw
                scroll_offset = 0
            elif key == "v":
                verbose = not verbose
                blocks = get_filtered_blocks(jsonl_path, verbose=verbose)
                total = len(blocks)
                if current >= total:
                    current = max(0, total - 1)
                expanded = False
                scroll_offset = 0
                search_matches = []
                console.print(f"[dim]Verbose mode: {'ON' if verbose else 'OFF'} ({total} blocks)[/]")
            elif key == "/":
                disable_mouse()
                query = prompt_input("Search in session")
                enable_mouse()
                if query:
                    search_query = query
                    search_matches = search_in_blocks(blocks, query)
                    if search_matches:
                        current = search_matches[0]
                        expanded = False
                        scroll_offset = 0
                        console.print(f"[green]Found {len(search_matches)} match(es)[/]")
                    else:
                        console.print("[yellow]No matches found.[/]")
                        search_query = None
            elif key == "n":
                if search_matches:
                    try:
                        idx = search_matches.index(current)
                        if idx < len(search_matches) - 1:
                            current = search_matches[idx + 1]
                            expanded = False
                            scroll_offset = 0
                        else:
                            current = search_matches[0]
                            expanded = False
                            scroll_offset = 0
                            console.print("[dim](wrapped to first match)[/]")
                    except ValueError:
                        current = search_matches[0]
                        expanded = False
                        scroll_offset = 0
                else:
                    console.print("[dim]No active search. Press / to search.[/]")
            elif key == "s":
                disable_mouse()
                save_jsonl(jsonl_path)
                enable_mouse()
            elif key in ("b", "escape"):
                return
            elif key == "q":
                raise SystemExit(0)
    finally:
        disable_mouse()


def _has_expandable(obj):
    if obj.get("type") != "message":
        return False
    msg = obj.get("message", {})
    role = msg.get("role", "")
    content_list = msg.get("content", [])

    if role == "assistant":
        for item in content_list:
            if isinstance(item, dict) and item.get("type") == "toolCall":
                args = item.get("arguments", {})
                args_str = json.dumps(args, ensure_ascii=False) if isinstance(args, dict) else str(args)
                if len(args_str) > TOOL_CALL_TRUNCATE:
                    return True

    if role == "toolResult":
        text_parts = []
        for item in content_list:
            if isinstance(item, dict) and item.get("type") == "text":
                text_parts.append(item.get("text", ""))
        full_text = "\n".join(text_parts)
        if len(full_text) > TOOL_RESULT_TRUNCATE:
            return True

    return False


def _clear_screen():
    if _IS_WINDOWS:
        os.system("cls")
    else:
        os.system("clear")


def session_list_page(sessions, verbose=False):
    if not sessions:
        console.print("[yellow]No sessions found.[/]")
        return

    filtered = list(sessions)
    page = 0
    selected = 0
    search_query = None

    while True:
        total_pages = max(1, (len(filtered) + PAGE_SIZE - 1) // PAGE_SIZE)
        if page >= total_pages:
            page = total_pages - 1

        start = page * PAGE_SIZE
        end = min(start + PAGE_SIZE, len(filtered))
        page_sessions = filtered[start:end]

        if selected >= len(page_sessions):
            selected = max(0, len(page_sessions) - 1)

        _clear_screen()

        console.print("[bold]OpenClaw Session Explorer[/]")
        if search_query:
            console.print(f"[dim]Search: \"{rich_escape(search_query)}\" — {len(filtered)} result(s) | / new search | Esc clear[/]")
        console.print()

        for i, s in enumerate(page_sessions):
            is_sel = i == selected
            sid = s["session_id"][:8] + "..."
            status = get_status_display(s["status"], s["aborted"])
            model = s["model"] or "-"
            channel = s["channel"] or "-"
            started = format_relative_time(s["started_at"])
            last_active = format_relative_time(s["last_active"])

            if is_sel:
                marker = "▶"
                line_style = ""
            else:
                marker = " "
                line_style = "dim"

            header_parts = [
                f"Session {sid}",
                f"model: {model}",
                f"status: {status}",
                f"channel: {channel}",
                f"created: {started}",
                f"active: {last_active}",
            ]
            header_line = f" {marker} " + " | ".join(header_parts)

            if line_style:
                console.print(f"[{line_style}]{header_line}[/]")
            else:
                console.print(header_line)

            jsonl_path = s.get("jsonl_path")
            if jsonl_path:
                first_msg = get_first_user_message(jsonl_path)
                last_msg = get_last_assistant_message(jsonl_path)
                if first_msg:
                    preview = truncate_text(first_msg.replace("\n", " "), PREVIEW_LENGTH)
                    detail = f"   First: {rich_escape(preview)}"
                    if line_style:
                        console.print(f"[{line_style}]{detail}[/]")
                    else:
                        console.print(detail)
                if last_msg:
                    preview = truncate_text(last_msg.replace("\n", " "), PREVIEW_LENGTH)
                    detail = f"   Last:  {rich_escape(preview)}"
                    if line_style:
                        console.print(f"[{line_style}]{detail}[/]")
                    else:
                        console.print(detail)
            else:
                detail = "   [dim][no session file][/]"
                if line_style:
                    console.print(f"[{line_style}]{detail}[/]")
                else:
                    console.print(detail)

            console.print()

        console.print(f"Page {page + 1}/{total_pages} — ↑↓ navigate | ←→ page | Enter view | / search | s save | v verbose | q quit")

        key = read_key()

        if key == "up":
            if selected > 0:
                selected -= 1
        elif key == "down":
            if selected < len(page_sessions) - 1:
                selected += 1
        elif key == "right":
            if page < total_pages - 1:
                page += 1
                selected = 0
        elif key == "left":
            if page > 0:
                page -= 1
                selected = 0
        elif key == "enter":
            sel_session = page_sessions[selected] if page_sessions else None
            if sel_session:
                try:
                    session_detail_page(sel_session, verbose=verbose)
                except SystemExit:
                    raise
        elif key == "/":
            query = prompt_input("Search sessions")
            if query:
                search_query = query
                filtered = search_in_sessions(sessions, query)
                page = 0
                selected = 0
                console.print(f"[green]Found {len(filtered)} matching session(s)[/]")
        elif key == "escape":
            if search_query:
                search_query = None
                filtered = list(sessions)
                page = 0
                selected = 0
            else:
                return
        elif key == "s":
            sel_session = page_sessions[selected] if page_sessions else None
            if sel_session:
                save_jsonl(sel_session.get("jsonl_path"))
        elif key == "v":
            verbose = not verbose
            console.print(f"[dim]Verbose mode: {'ON' if verbose else 'OFF'}[/]")
        elif key == "q":
            return


def main():
    parser = argparse.ArgumentParser(description="OpenClaw Session Explorer")
    parser.add_argument("--dir", help="OpenClaw directory path")
    parser.add_argument("--session", help="Jump directly to session ID")
    parser.add_argument("--no-color", action="store_true", help="Disable colors")
    parser.add_argument("--verbose", action="store_true", help="Start in verbose mode")
    args = parser.parse_args()

    if args.no_color:
        os.environ["NO_COLOR"] = "1"

    cfg = load_config()
    verbose = args.verbose or cfg.get("verbose", False)

    if args.dir:
        openclaw_dir = args.dir
        if not Path(openclaw_dir).exists():
            console.print(f"[red]Directory does not exist: {openclaw_dir}[/]")
            sys.exit(1)
        cfg["openclaw_dir"] = openclaw_dir
        save_config(cfg)
    else:
        openclaw_dir = prompt_openclaw_dir(cfg)

    console.print(f"\n[bold]OpenClaw Session Explorer[/]")
    console.print(f"  Directory: {openclaw_dir}")

    sessions = load_sessions(openclaw_dir)
    console.print(f"  Found {len(sessions)} session(s)")

    if not sessions:
        console.print("[yellow]No sessions found. Check your openclaw directory.[/]")
        sys.exit(0)

    if args.session:
        target = None
        for s in sessions:
            if s["session_id"].startswith(args.session):
                target = s
                break
        if target:
            try:
                session_detail_page(target, verbose=verbose)
            except SystemExit:
                pass
        else:
            console.print(f"[red]Session not found: {args.session}[/]")
            sys.exit(1)
    else:
        try:
            session_list_page(sessions, verbose=verbose)
        except SystemExit:
            pass


if __name__ == "__main__":
    main()
