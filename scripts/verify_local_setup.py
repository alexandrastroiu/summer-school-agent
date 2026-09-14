"""
Verify the local Day 4 project setup.

This script does not contact Google Cloud and does not call Gemini.
"""

from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from app.agent import root_agent
from app.config import load_config
from app.knowledge import LocalKnowledgeProvider
from app.tools import AssistantTools


def print_check(message: str) -> None:
    """Print a successful verification step."""
    print(f"✓ {message}")


def main() -> None:
    """Run all local verification checks."""

    print("\n=== Local Setup Verification ===\n")

    config = load_config()

    assert config.knowledge_source == "local"
    assert config.model
    assert config.local_knowledge_directory

    print_check("Configuration loaded")
    print(f"  Model: {config.model}")
    print(f"  Knowledge source: {config.knowledge_source}")

    knowledge_directory = Path(config.local_knowledge_directory)

    if not knowledge_directory.is_absolute():
        knowledge_directory = PROJECT_ROOT / knowledge_directory

    assert knowledge_directory.exists(), (
        f"Knowledge directory does not exist: {knowledge_directory}"
    )
    assert knowledge_directory.is_dir(), (
        f"Knowledge path is not a directory: {knowledge_directory}"
    )

    print_check("Knowledge directory found")
    print(f"  Path: {knowledge_directory}")

    provider = LocalKnowledgeProvider(knowledge_directory)
    documents = provider.list_documents()

    assert documents, "No Markdown documents were found."

    print_check("Knowledge documents found")
    print(f"  Documents: {', '.join(documents)}")

    tools = AssistantTools(provider)

    list_result = tools.list_documents()
    assert list_result["status"] == "success"
    assert list_result["document_count"] == len(documents)
    print_check("list_documents works")

    first_document = documents[0]
    read_result = tools.read_document(first_document)
    assert read_result["status"] == "success"
    assert read_result["filename"] == first_document
    assert read_result["content"].strip()
    print_check("read_document works")

    search_result = tools.search_documents("Docker")
    assert search_result["status"] == "success"
    assert isinstance(search_result["matches"], list)
    assert all("filename" in match for match in search_result["matches"])
    assert all("excerpts" in match for match in search_result["matches"])
    print_check("search_documents returns excerpts")

    missing_result = tools.read_document("missing-document.md")
    assert missing_result["status"] == "error"
    print_check("Missing-document handling works")

    empty_search_result = tools.search_documents("")
    assert empty_search_result["status"] == "error"
    print_check("Empty-search handling works")

    assert root_agent.name == "summer_school_assistant"
    assert len(root_agent.tools) == 4
    print_check("ADK agent loaded")
    print(f"  Agent: {root_agent.name}")
    print(f"  Tools: {len(root_agent.tools)}")

    print("\nAll local checks passed.")
    print("No Google Cloud request or Gemini request was made.\n")


if __name__ == "__main__":
    main()
