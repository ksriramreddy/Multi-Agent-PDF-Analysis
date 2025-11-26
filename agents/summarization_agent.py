class SummarizationAgent:
    def __init__(self, document_store , llm):
        self.llm = llm
        self.store  = document_store
        
    def summerize(self, file_name: str):
        
        chunks  =   [chunk for chunk in self.store.chunks if chunk["file_name"] == file_name]
        
        if not chunks:
            return {
                "answer": "No document found to summarize.",
                "metadata": {
                    "file_name": file_name,
                    "page": None,
                    "score": 0.0
                }
            }
            
        chunk_summary = []
        
        for chunk in chunks:
            prompt = f"""
            Summarize the given context only
            CONTEXT : {chunk} """
            
            summary = self.llm.invoke(prompt)
            
            chunk_summary.append(summary.content)
            
        prompt = f"""
        combine and summarize the following summeries in to single summary
        {"\n".join(chunk_summary)}
        """
        
        complete_summary = self.llm.invoke(prompt)
        # print("complete_summary->>>>>>",complete_summary)
        
        return {
            "answer" : complete_summary.content,
            "metadata" : {
                "file_name" : file_name,
                "page" : None,
                "score" : 1.0
            }
        }