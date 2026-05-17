import os
import anthropic

CATEGORIES = {"cv", "job_description", "invoice", "image", "other"}

SYSTEM_PROMPT = """You are a file classifier. Given a filename and its text content, classify the file into exactly one of these categories:

- cv: a curriculum vitae or resume
- job_description: a job posting or job description
- invoice: a financial invoice or receipt
- image: an image file (content will typically be empty or binary)
- other: anything that does not fit the above

Respond with only the category name, nothing else."""

_client = None


def _get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    return _client


def classify_file(filename: str, content: str) -> str:
    client = _get_client()

    message = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=16,
        system=[{"type": "text", "text": SYSTEM_PROMPT, "cache_control": {"type": "ephemeral"}}],
        messages=[
            {
                "role": "user",
                "content": f"Filename: {filename}\n\nContent:\n{content}",
            }
        ],
    )

    category = message.content[0].text.strip().lower()
    return category if category in CATEGORIES else "other"
