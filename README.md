# cowork-file-automation

A Python file automation tool that watches a directory for new files and automatically classifies and organizes them using the Claude API.

Drop a file into the `watch/` folder — the tool reads its content, asks Claude to classify it, and moves it into the appropriate subfolder under `organized/`.

## How it works

```
watch/ (drop files here)
  └── file.txt
        │
        ▼
  Claude API (claude-haiku-4-5)
  classifies content
        │
        ▼
organized/
  ├── cv/
  ├── job_description/
  ├── invoice/
  ├── image/
  └── other/
```

1. A [watchdog](https://python-watchdog.readthedocs.io/) observer monitors `watch/` for new files.
2. On each new file, the content is read and sent to Claude with a classification prompt.
3. Claude returns one of five categories: `cv`, `job_description`, `invoice`, `image`, or `other`.
4. The file is moved to `organized/<category>/`. Filename collisions are resolved automatically (`report_1.txt`, `report_2.txt`, …).

## Requirements

- Python 3.10+
- An [Anthropic API key](https://console.anthropic.com/)

## Setup

```bash
# Clone the repo
git clone https://github.com/yangull/cowork-file-automation.git
cd cowork-file-automation

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set your API key
cp .env.example .env        # then edit .env and add your key
# or export directly:
export ANTHROPIC_API_KEY=sk-ant-...
```

**.env file:**
```
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

## Usage

```bash
python main.py
```

The watcher starts and prints its status:

```
Watching /path/to/cowork-file-automation/watch ...
```

Drop any text file into the `watch/` directory. The tool processes it immediately:

```
[done]  john_doe_cv.txt → cv → organized/cv/john_doe_cv.txt
[done]  invoice_feb.txt → invoice → organized/invoice/invoice_feb.txt
[skip]  photo.png — binary file
```

Press `Ctrl+C` to stop.

## File categories

| Category | Description |
|---|---|
| `cv` | Curriculum vitae or resume |
| `job_description` | Job posting or job description |
| `invoice` | Financial invoice or receipt |
| `image` | Image file (binary content) |
| `other` | Anything that does not fit the above |

## Project structure

```
cowork-file-automation/
├── main.py          # Entry point — loads env, starts watcher
├── watcher.py       # watchdog Observer setup and event handler
├── classifier.py    # Claude API call — returns a category string
├── organizer.py     # Moves the file to organized/<category>/
├── watch/           # Drop files here (created automatically)
├── organized/       # Output — subfolders per category
├── tests/
│   ├── test_classifier.py
│   └── test_organizer.py
└── requirements.txt
```

## Development

```bash
# Install dev dependencies
pip install -r requirements.txt  # includes pytest and pytest-mock

# Run tests
pytest

# Run a specific test file
pytest tests/test_classifier.py

# Lint and format (requires ruff)
ruff check .
ruff format .
```

## Claude API details

- **Model:** `claude-haiku-4-5` (fast and cost-efficient for classification)
- **Prompt caching:** The system prompt uses `cache_control: ephemeral` so repeated classifications reuse the cached prompt, reducing latency and cost.
- **Client:** A single `anthropic.Anthropic` client is instantiated at startup and reused across all events.

## License

MIT
