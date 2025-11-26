import re

class TimelineAgent:
    def __init__(self, document_store, llm):
        self.store = document_store
        self.llm = llm

    def build_timeline(self, query: str, files: list[str]):
        print("⏳ TIMELINE AGENT ACTIVATED")

        if not files:
            return {
                "answer": "⚠️ Timeline requires at least one document.",
                "metadata": {"file_name": None, "page": None, "score": 0.0},
            }

        contexts = []
        for f in files:
            res = self.store.search(query, f)
            if res:
                contexts.extend(res)

        if not contexts:
            return {
                "answer": "No timeline-related events found.",
                "metadata": {"file_name": " | ".join(files), "page": None, "score": 0.0},
            }

        entries = []
        year_pattern = r"(?:19|20)\d{2}"

        for c in contexts:
            years = re.findall(year_pattern, c["text"])
            if years:
                for y in years:
                    entries.append((int(y), c))
            else:
                entries.append((None, c))


        dated = [e for e in entries if e[0] is not None]
        undated = [e for e in entries if e[0] is None]

        dated.sort(key=lambda x: x[0])

        merged_context = []
        for year, c in dated:
            merged_context.append(
                f"[{c['file_name']} | p.{c['page']} | {year}]\n{c['text']}\n"
            )
        for _, c in undated:
            merged_context.append(
                f"[{c['file_name']} | p.{c['page']}]\n{c['text']}\n"
            )

        prompt = f"""
You are a TIMELINE extraction AI.

You will receive unordered passages about a topic.
Extract key events and arrange them chronologically.

CONTEXT:
{''.join(merged_context)}

RULES:
- Use ONLY the given context.
- DO NOT hallucinate dates.
- If no explicit year, infer order from phrases:
  "first", "later", "then", "eventually", "finally".
- Prefer YYYY format if available.
- Be clean, short, and well formatted.

OUTPUT FORMAT:
YYYY — short event
YYYY — short event
...
"""

        resp = self.llm.invoke(prompt)

        return {
            "answer": resp.content,
            "metadata": {
                "file_name": " | ".join(files),
                "page": None,
                "score": 1.0,
            }
        }
