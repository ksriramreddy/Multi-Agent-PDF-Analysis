
class RAGAgent:
    def __init__(self , document_store , llm):
        self.store = document_store
        self.llm = llm
    
    def answer(self , query : str):
        
        result = self.store.search(query)
        
        print("resultsssss->>🤖🤖🤖",result)
        
        context = "\n\n".join([
            f"[file_name : {res["file_name"]} \n page_no : {res["page"]} \n text : {res["text"]} ]"
            for res in result
        ])
        
        prompt = f"""
        you are a Q/A system
        Answer the query with given context only.
        CONTEXT : {context}
        QUERY : {query}
        RUELS : No External sources, No factual Ans"""
        
        answer = self.llm.invoke(prompt)
        
        top = result[0]
        
        retur = {
            "answer" : answer.content,
            "metadata" : {
                "file_name" : top["file_name"],
                "page" : top["page"],
                "score" : top["score"]
            }
                          
        }
        print("answer->>>>>>",retur)
        # print(retur)
        return retur
        