# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

A Python file automation tool that watches directories for filesystem events using [watchdog](https://python-watchdog.readthedocs.io/) and processes files via the Claude API (Anthropic SDK). Intended for coworking/collaboration workflows where file changes trigger AI-powered processing pipelines.

## Commands

```bash
# Install in editable mode with dev dependencies
pip install -e ".[dev]"

# Run the watcher (main entry point)
python -m cowork_file_automation

# Run all tests
pytest

# Run a single test file
pytest tests/test_watcher.py

# Run a single test by name
pytest tests/test_processor.py::test_on_created

# Lint and format
ruff check .
ruff format .
```

## Architecture

The tool is event-driven: a long-running `Observer` thread (watchdog) emits filesystem events that are dispatched to handlers, which call the Claude API to process file content.

### Key components

**`cowork_file_automation/watcher.py`** — Sets up the watchdog `Observer` and registers `FileSystemEventHandler` subclasses for configured watch paths. The observer runs in a background thread; the main thread blocks on a signal handler for clean shutdown.

**`cowork_file_automation/handlers.py`** — `FileSystemEventHandler` subclasses that filter events by file pattern (e.g., `*.md`, `*.txt`) and delegate to the processor. Handlers are stateless; debounce logic lives here to avoid duplicate events on rapid saves.

**`cowork_file_automation/processor.py`** — Receives a file path, reads its content, builds a prompt, and calls the Claude API via the Anthropic SDK. Returns structured output. Uses prompt caching (`cache_control`) on the system prompt to reduce latency and cost on repeated invocations.

**`cowork_file_automation/config.py`** — Loads configuration from a YAML/TOML file and environment variables. Key settings: watched directories, file glob patterns, Claude model, output directory.

### Claude API usage

- Client is instantiated once at startup and reused across events.
- System prompts are marked with `cache_control: {"type": "ephemeral"}` for prompt caching.
- The model in use is `claude-haiku-4-5` by default; override via `ANTHROPIC_MODEL` env var.
- `ANTHROPIC_API_KEY` must be set in the environment.

### Event flow

```
filesystem change
  → watchdog Observer (background thread)
  → Handler.on_created / on_modified
  → debounce / filter by pattern
  → Processor.process(path)
  → Claude API call
  → write output file or callback
```

## Dependencies

Core: `anthropic`, `watchdog`, `pyyaml`  
Dev: `pytest`, `pytest-mock`, `ruff`
