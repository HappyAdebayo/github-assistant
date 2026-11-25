
from flashrank import Ranker, RerankRequest


class CrossEncoderReranker:
    def __init__(self):
        self.ranker = Ranker(
            model_name="ms-marco-MiniLM-L-12-v2"
        )

    def rerank(self, query, documents, top_n=5):
        passages = [
            {
                "id": index,
                "text": document.page_content,
                "meta": document.metadata
            }
            for index, (document, _) in enumerate(documents)
        ]

        request = RerankRequest(
            query=query,
            passages=passages
        )

        results = self.ranker.rerank(request)

        return [
            (
                documents[result["id"]][0],
                result["score"]
            )
            for result in results[:top_n]
        ]
