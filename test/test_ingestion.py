from rag.repository_ingestion import (
    get_repository_files,
    filter_repository_files,
    extract_file_contents
)
from rag.chunking import chunk_documents
from rag.vector_store import create_vector_store, store_chunks

owner = "HappyAdebayo"
repo = "backly-server"

result = get_repository_files(owner, repo)

if not isinstance(result, dict) or "error" in result:
    print(result)
    exit()

selected_files = filter_repository_files(result["files"])

print(f"Total files: {result['total_files']}")
print(f"Selected files: {len(selected_files)}")

documents = extract_file_contents(owner, repo, selected_files)

print(f"Successfully extracted: {len(documents)} files")

chunks = chunk_documents(
    documents,
    repository=f"{owner}/{repo}"
)

print(f"Total chunks generated: {len(chunks)}")

if chunks:
    print("\nFirst chunk:")
    print("Metadata:", chunks[0].metadata)
    print("Content:")
    print(chunks[0].page_content)

vector_store = create_vector_store()

stored_count = store_chunks(vector_store, chunks)

print(f"Successfully stored: {stored_count} chunks")
print(f"Total documents in database: {vector_store._collection.count()}")