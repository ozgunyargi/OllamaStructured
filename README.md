# Ollama Structured

Generate strongly typed, JSON-only responses from Ollama models by pairing
Pydantic schemas with a light wrapper around the `ollama` Python client. The
project demonstrates how to instruct Ollama Cloud to deliver structured product
reviews while automatically recovering from malformed outputs.

## Highlights
- `OllamaLLM` helper (in `src/utils/ollama_llm.py`) connects to Ollama Cloud or
  a local Ollama instance and handles chat history when needed.
- Enforces JSON that satisfies any Pydantic model, with retry-based recovery if
  the model drifts from the schema.
- `src/main.py` contains a runnable example that turns an unstructured review
  into the `ProductReview` data class.

## Prerequisites
- Python&nbsp;3.12 or later (as defined in `pyproject.toml`)
- The [uv](https://github.com/astral-sh/uv) Python packaging tool
- An Ollama Cloud API key.

## Environment configuration
1. Create a `.env` file in the repository root and add the credentials the code
   expects:
   ```bash
   PROJECT_DIR=${PWD}
   PYTHONPATH=${PROJECT_DIR}
   OLLAMA_API_KEY=replace-with-your-token
   ```
2. Tell uv to load that file whenever it runs in this project:
   ```bash
   export UV_ENV_FILE=.env
   ```
   Add the command to your shell profile if you want it to persist between
   sessions. (On Windows PowerShell, run `$env:UV_ENV_FILE=".env"` before using
   uv.)

## Install dependencies with uv
The repo already includes a `pyproject.toml` and `uv.lock`, so syncing the
environment is a single step once `UV_ENV_FILE` is exported:

```bash
uv sync
```

`uv sync` will create the virtual environment (cached under `~/.cache/uv`) and
ensure the dependencies listed in the lockfile are available.

## Run the structured output demo
With dependencies installed, execute the example script directly through uv so
that it can resolve the environment and automatically load `.env`:

```bash
uv run src/main.py
```

You should see a dictionary representation of the `ProductReview` model printed
to the console. Feel free to adjust the `SAMPLE` review text or replace the
model in `src/main.py` with your own Pydantic schema to capture other types of
structured data.

## Customizing the client
- **Choose a different model:** pass a `model` argument when calling
  `OllamaLLM.connect_to_ollama_cloud`.
- **Point to a local Ollama instance:** call `OllamaLLM.connect_to_local_ollama`
  with the desired host URL instead of `connect_to_ollama_cloud`.
- **Track chat history:** instantiate `OllamaLLM` with `track_chat_history=True`
  to keep the previous assistant replies in the prompt sequence.

## Troubleshooting
- `ValueError: 'OLLAMA_API_KEY' environment variable not found` &rarr; verify
  the `.env` file exists, contains the key, and that `UV_ENV_FILE=.env` was
  exported in the current shell.
- Schema validation errors after retries usually mean the model produced output
  that cannot be coerced into your Pydantic model. Tighten the schema or
  simplify the prompt.