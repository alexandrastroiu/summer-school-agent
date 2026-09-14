from pathlib import Path

from app.knowledge import LocalKnowledgeProvider
from app.tools import AssistantTools


def main() -> None:
    """Demonstrate the local knowledge tools without using Google Cloud."""

    print("\n=== Milan City Guide AI Assistant ===\n")

    provider = LocalKnowledgeProvider(Path("knowledge"))
    tools = AssistantTools(provider)

    print("Available documents")
    print("-------------------")

    documents_result = tools.list_documents()

    for document in documents_result["documents"]:
        print(f"- {document}")

    print(f"\nTotal documents: {documents_result['document_count']}")

    print("\nReading milan_overview.md")
    print("-------------------")

    reading_result = tools.read_document("milan_overview.md")

    if reading_result["status"] == "success":
        print(reading_result["content"])
    else:
        print(reading_result["error_message"])

    print("\nSearching for 'Scala'")
    print("----------------------")

    search_result = tools.search_documents("Scala")

    if search_result["status"] == "error":
        print(search_result["error_message"])
        return

    if not search_result["matches"]:
        print("No documents found.")
        return

    for match in search_result["matches"]:
        print(f"\n{match['filename']}")

        for excerpt in match["excerpts"]:
            print(
                f"  line {excerpt['line_number']}: "
                f"{excerpt['text']}"
            )


if __name__ == "__main__":
    main()
