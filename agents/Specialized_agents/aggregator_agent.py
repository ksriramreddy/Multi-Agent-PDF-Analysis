class AggregatorAgent:
    def __init__(self, document_store, llm):
        self.store = document_store
        self.llm = llm

    def aggregate(self, query, files=None):
        print("🚀 Aggregator Agent activated")

        if files is None:
            files = []
        if isinstance(files, str):
            files = [files]

        evidence = []

        for file_name in files:
            chunks = self.store.search(query, file_name)
            evidence.extend(chunks)

        if not files:
            evidence = self.store.search(query)

        if not evidence:
            return {
                "answer": "No relevant information found.",
                "metadata": {
                    "file_name": None,
                    "page": None,
                    "score": 0.0
                }
            }

        context = "\n\n".join([
            f"[{ev['file_name']} | p.{ev['page']} | score={ev['score']:.4f}]\n{ev['text']}"
            for ev in evidence
        ])

        prompt = f"""
You are an aggregation agent.

CONTEXT:
{context}

TASK:
- Collect and merge all information relevant to the query.
- Remove redundancy.
- Group similar ideas.
- Produce a clear cohesive answer.
- Use bullet points or short paragraphs.
- DO NOT invent facts.

USER QUERY:
"{query}"

Return a clean, structured response.
"""

        resp = self.llm.invoke(prompt)

        # Best single metadata record = highest score
        top = max(evidence, key=lambda x: x["score"])

        return {
            "answer": resp.content,
            "metadata": {
                "file_name": top["file_name"],
                "page": top["page"],
                "score": top["score"]
            }
        }
