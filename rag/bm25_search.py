
from rank_bm25 import BM25Okapi


class BM25Search:
    def __init__(self, chunks):
        self.chunks = chunks

        tokenized_documents = [
            chunk.page_content.lower().split()
            for chunk in chunks
        ]

        self.bm25 = BM25Okapi(tokenized_documents)

    def search(self, query, k=5):
        tokenized_query = query.lower().split()

        scores = self.bm25.get_scores(tokenized_query)

        ranked_indices = scores.argsort()[::-1][:k]

        return [
            (self.chunks[index], scores[index])
            for index in ranked_indices
        ]
