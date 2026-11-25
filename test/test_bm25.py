
from rag.repository_ingestion import (
    get_repository_files,
    filter_repository_files,
    extract_file_contents
)
from rag.chunking import chunk_documents
from rag.bm25_search import BM25Search

owner = "HappyAdebayo"
repo = "backly-server"

result = get_repository_files(owner, repo)

if not isinstance(result, dict) or "error" in result:
    print(result)
    exit()

selected_files = filter_repository_files(result["files"])
documents = extract_file_contents(owner, repo, selected_files)

chunks = chunk_documents(
    documents,
    repository=f"{owner}/{repo}"
)

bm25 = BM25Search(chunks)

query = "const pool = new Pool connectionString process.env.DATABASE_URL"

results = bm25.search(query, k=5)

for index, (document, score) in enumerate(results, start=1):
    print(f"\nResult {index}")
    print(f"File: {document.metadata['file_path']}")
    print(f"BM25 Score: {score}")
    print(f"Content:\n{document.page_content}")
