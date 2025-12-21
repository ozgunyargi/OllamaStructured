# Ollama Structured

Generate strongly typed, JSON-only responses from Ollama models by pairing
Pydantic schemas with a light wrapper around the `ollama` Python client. The
project demonstrates how to instruct Ollama Cloud to deliver structured outputs
for both **text** and **vision** tasks while automatically recovering from
malformed outputs.

## Highlights
- `OllamaLLM` helper (in `src/OllamaStructured/utils/ollama_llm.py`) connects to
  Ollama Cloud or a local Ollama instance and handles chat history when needed.
- Enforces JSON that satisfies any Pydantic model, with retry-based recovery if
  the model drifts from the schema.
- **Multimodal support**: pass an image path or raw bytes to
  `ask_w_structured_output` for vision model inference.
- `src/main.py` contains runnable examples:
  - `text_sample()` – turns an unstructured product review into a
    `ProductReview` data class.
  - `image_sample()` – extracts structured metadata from an image using the
    `ImageReview` schema and a vision model.

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

By default the script runs `image_sample()`. To run the text example instead,
edit `src/main.py` and call `text_sample()` in the `if __name__` block.

You should see a dictionary representation of the Pydantic model printed to the
console. Feel free to adjust the sample data or replace the schemas in
`src/main.py` with your own Pydantic models to capture other types of
structured data.

## Customizing the client
- **Choose a different model:** pass a `model` argument when calling
  `OllamaLLM.connect_to_ollama_cloud` (default: `gpt-oss:20b-cloud`).
- **Use a vision model:** supply a vision-capable model such as
  `qwen3-vl:235b-cloud` and provide an image to `ask_w_structured_output`.
- **Point to a local Ollama instance:** call `OllamaLLM.connect_to_local_ollama`
  with the desired host URL instead of `connect_to_ollama_cloud`.
- **Track chat history:** instantiate `OllamaLLM` with `track_chat_history=True`
  to keep the previous assistant replies in the prompt sequence.

## Project structure
```
src/
├── main.py                          # Entry point with sample functions
└── OllamaStructured/
    ├── __init__.py                  # Re-exports OllamaLLM
    └── utils/
        ├── __init__.py
        ├── exceptions.py            # Custom exceptions
        ├── ollama_llm.py            # OllamaLLM class
        └── prompts.py               # System & recovery prompts
```

## Troubleshooting
- `ValueError: 'OLLAMA_API_KEY' environment variable not found` &rarr; verify
  the `.env` file exists, contains the key, and that `UV_ENV_FILE=.env` was
  exported in the current shell.
- `OllamaLLMStructuredOutputException` after retries usually means the model
  produced output that cannot be coerced into your Pydantic model even after
  recovery attempts. Tighten the schema or simplify the prompt.
- For vision tasks, ensure you are using a model that supports images (e.g.,
  `qwen3-vl:235b-cloud`).