class ComparatorAgent:
    def __init__(self, document_store, llm):
        self.llm = llm
        self.store = document_store

    def compare(self, query: str, files: list[str]):
        print("🚀 Comparator Agent activated")

        if not files or len(files) < 2:
            return {
                "answer": "⚠️ Please provide at least TWO documents to compare.",
                "metadata": {
                    "file_name": None,
                    "page": None,
                    "score": 0.0
                }
            }

        # 1️⃣ Retrieve evidence for each document
        evidence_map = {}
        for file_name in files:
            findings = self.store.search(query, file_name)
            evidence_map[file_name] = findings

        print("🔍 Evidence mapping:", evidence_map.keys())

        # 2️⃣ If absolutely no evidence found
        if all(len(v) == 0 for v in evidence_map.values()):
            return {
                "answer": "No relevant content found in any documents for this comparison.",
                "metadata": {
                    "file_name": " | ".join(files),
                    "page": None,
                    "score": 0.0
                }
            }

        # 3️⃣ ✨ Format context for LLM
        blocks = []
        for file_name, passages in evidence_map.items():

            if not passages:
                blocks.append(f"[{file_name}] No relevant passages found.\n")
                continue

            block = "\n".join(
                f"[{file_name} | p.{p['page']}]\n{p['text']}"
                for p in passages
            )
            blocks.append(block)

        context = "\n\n------------------\n\n".join(blocks)

        # 4️⃣ Send comparison prompt to model
        prompt = f"""
You are a multi-document comparison agent.

You are given excerpts from multiple documents.
Each block corresponds to a document.

CONTEXT:
{context}

TASK:
- Compare how these documents relate to the user query.
- List similarities across all documents.
- List differences between them.
- Identify which document contains stronger coverage.
- If one document lacks information, mention that.
- Be objective. Do NOT invent facts.
- Write in clean bullet points.

USER QUERY:
"{query}"

Return clear, structured analysis in plain text.
"""

        print("➡️ Sending to LLM")
        resp = self.llm.invoke(prompt)
        print("🔁 Comparison complete")

        return {
            "answer": resp.content,
            "metadata": {
                "file_name": " | ".join(files),
                "page": None,
                "score": 1.0
            }
        }
