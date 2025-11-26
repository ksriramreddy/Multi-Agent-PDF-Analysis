import json

class PlannerAgent:
    def __init__(self, rag_agent, summarizer_agent, comparator_agent, aggregator_agent, llm):
        self.rag = rag_agent
        self.summary = summarizer_agent
        self.compare = comparator_agent
        self.aggregate = aggregator_agent
        self.llm = llm

    def decide(self, query: str):
        # collect all document names for grounding
        docs = list({p["file_name"] for p in self.rag.store.pages})

        prompt = f"""
        You are a ROUTING AGENT. Your job is to classify the user's intent.
        DO NOT ANSWER THE QUESTION.

        User Query:
        "{query}"

        Available documents:
        {docs}

        You must choose one action from below:

        ----------------------------
        ### 1️⃣ "summary"
        When the user asks for:
        - overview
        - what this document is about
        - general explanation
        - introduction
        - high level understanding

        Examples:
        - "Tell me about this pdf"
        - "What is this document about?"
        - "Give me an overview"
        - "Explain what this paper discusses"

        ----------------------------
        ### 2️⃣ "rag"
        When the user needs:
        - factual answers
        - content lookup
        - specific information
        - page-level context

        Examples:
        - "What is the refund policy"
        - "Who is the author?"
        - "Give me the formula in chapter 3"

        ----------------------------
        ### 3️⃣ "compare"
        When user asks to compare OR contrast
        - two documents
        - two concepts
        - performance
        - skills

        Keywords:
        compare, vs, difference between, contrast

        Examples:
        - "Compare resume A.pdf and resume B.pdf"
        - "Difference between CNN and RNN?"

        ----------------------------
        ### 4️⃣ "aggregate"
        User asks to gather **ALL** evidence about a topic
        - collect everything
        - merge all mentions
        - assemble all content
        - bring together
        - show every reference

        Keywords:
        all, aggregate, collect, everything, gather, compile, merge

        Examples:
        - "Collect all information about neural networks"
        - "Show every place that mentions data preprocessing"
        - "Aggregate all text across documents about AI"

        ----------------------------
        
        ### 5️⃣ "timeline"
        When the user wants chronological order, history, or progression:
        - arrange events by year
        - sort steps in order
        - build chronological narrative

        Keywords:
        timeline, history, evolution, chronological, sequence, progression,
        stages, phases, order of events

        Examples:
        - "Show the history of AI across these PDFs"
        - "Arrange these findings in chronological order"
        - "Give me a timeline of methodology steps"
        - "How did this technology evolve over time?"
        ------------------------------------

        Your output must STRICTLY be JSON:
        {{
            "action": "<summary|rag|compare|aggregate|timeline>",
            "file_name": "<string|null|[string,string,...]>"
        }}

        Notes:
        - If user mentions 2 document names → return list
        - If no document name → return null
        - NEVER mention explanations
        - NO natural language
        - ONLY JSON
        """

        resp = self.llm.invoke(prompt)
        # print("🧠 PLANNER RAW:", resp)

        try:
            return json.loads(resp.content)
        except:
            return {"action": "rag", "file_name": None}


    def run(self, query: str):
        plan = self.decide(query)
        print("🧠 PLAN:", plan)

        action = plan.get("action", "rag")
        files = plan.get("file_name")

        if files is None:
            files = []

        if isinstance(files, str):
            files = [files]


        # SUMMARY
        if action == "summary":
            print("📘 EXEC: SUMMARIZER")
            
            file_for_summary = files[0] if files else None
            return self.summary.summerize(file_for_summary)

        # COMPARISON
        if action == "compare":
            print("⚖️ EXEC: COMPARATOR")
            return self.compare.compare(query, files)

        # AGGREGATOR
        if action == "aggregate":
            print("🧩 EXEC: AGGREGATOR")
            return self.aggregate.aggregate(query, files)
        
        if action == "timeline":
            print("📅 EXEC: TIMELINE AGENT")
            return self.timeline.build_timeline(query, files)


        # DEFAULT = RAG
        print("🔍 EXEC: RAG")
        return self.rag.answer(query)
