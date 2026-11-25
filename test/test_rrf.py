
from rag.repository_ingestion import (
    get_repository_files,
    filter_repository_files,
    extract_file_contents
)
from rag.chunking import chunk_documents
from rag.vector_store import create_vector_store
from rag.retrieval import (
    semantic_search,
    reciprocal_rank_fusion,
    filter_by_metadata
)
from rag.bm25_search import BM25Search
from rag.reranking import CrossEncoderReranker

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

vector_store = create_vector_store()
bm25 = BM25Search(chunks)

query = "Where is the pg Pool instantiated with connectionString set to process.env.DATABASE_URL?"
semantic_results = semantic_search(vector_store, query, k=5)
bm25_results = bm25.search(query, k=5)

fused_results = reciprocal_rank_fusion(
    [semantic_results, bm25_results]
)

reranker = CrossEncoderReranker()

reranked_results = reranker.rerank(
    query=query,
    documents=fused_results,
    top_n=5
)

filtered_results = filter_by_metadata(
    reranked_results,
    repository="HappyAdebayo/backly-server",
    file_path="core/database/"
)

for index, (document, score) in enumerate(filtered_results, start=1):
    print(f"\nResult {index}")
    print(f"File: {document.metadata['file_path']}")
    print(f"Reranking Score: {score}")
    print(f"Content:\n{document.page_content}")