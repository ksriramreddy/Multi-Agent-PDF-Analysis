from typing import Dict , List
class Chunker:
    def chunking(self , pages : List[Dict]):
        chunks = []
        
        
        for page in pages:
            
            text = page["text"]
            
            start = 0
            
            while start < len(text):
                
                end = start + 600 #chunk size
                
                chunk = text[start : end]
                
                chunks.append({
                    "file_name" : page["file_name"],
                    "page" : page["page"],
                    "chunk" : chunk
                })
                
                start = start + (500 - 200) # 
                
        return chunks