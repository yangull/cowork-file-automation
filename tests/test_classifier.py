import os
import types
import pytest
import classifier


def _make_response(text: str):
    content_block = types.SimpleNamespace(text=text)
    return types.SimpleNamespace(content=[content_block])


@pytest.fixture(autouse=True)
def reset_client():
    # Ensure each test gets a fresh client slot and a dummy API key
    original = classifier._client
    os.environ.setdefault("ANTHROPIC_API_KEY", "test-key")
    yield
    classifier._client = original


@pytest.fixture
def mock_client(mocker):
    client = mocker.MagicMock()
    mocker.patch.object(classifier, "_get_client", return_value=client)
    return client


@pytest.mark.parametrize("api_response,expected", [
    ("cv",               "cv"),
    ("job_description",  "job_description"),
    ("invoice",          "invoice"),
    ("image",            "image"),
    ("other",            "other"),
    ("CV\n",             "cv"),           # stripped + lowercased
    ("INVOICE",          "invoice"),      # uppercase normalised
    ("gibberish",        "other"),        # unknown → other
    ("  cv  ",           "cv"),           # whitespace stripped
])
def test_classify_file_categories(mock_client, api_response, expected):
    mock_client.messages.create.return_value = _make_response(api_response)
    assert classifier.classify_file("file.txt", "some content") == expected


def test_classify_file_calls_correct_model(mock_client):
    mock_client.messages.create.return_value = _make_response("cv")
    classifier.classify_file("resume.pdf", "experience...")
    call_kwargs = mock_client.messages.create.call_args.kwargs
    assert call_kwargs["model"] == "claude-haiku-4-5"


def test_classify_file_includes_filename_in_prompt(mock_client):
    mock_client.messages.create.return_value = _make_response("invoice")
    classifier.classify_file("invoice_jan.txt", "Total: $100")
    call_kwargs = mock_client.messages.create.call_args.kwargs
    user_content = call_kwargs["messages"][0]["content"]
    assert "invoice_jan.txt" in user_content


def test_classify_file_includes_content_in_prompt(mock_client):
    mock_client.messages.create.return_value = _make_response("cv")
    classifier.classify_file("doc.txt", "unique-marker-xyz")
    call_kwargs = mock_client.messages.create.call_args.kwargs
    user_content = call_kwargs["messages"][0]["content"]
    assert "unique-marker-xyz" in user_content


def test_classify_file_system_prompt_has_cache_control(mock_client):
    mock_client.messages.create.return_value = _make_response("other")
    classifier.classify_file("x.txt", "")
    system = mock_client.messages.create.call_args.kwargs["system"]
    assert isinstance(system, list)
    assert system[0]["cache_control"] == {"type": "ephemeral"}
