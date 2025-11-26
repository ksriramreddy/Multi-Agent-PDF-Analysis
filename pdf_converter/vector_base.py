import faiss
import numpy as np

class VectorBase:
    def __init__(self , dim):
        self.index = faiss.IndexFlatL2(dim)
        self.metadata = {}
        
    def add_vectors(self , embeddings , metadata):
        
        embeddings = np.array(embeddings).astype("float32")
        
        start = len(self.metadata)
        
        self.index.add(embeddings)
        
        for i , data in enumerate(metadata):
            self.metadata[start + i] = data
            
    
    def search(self , query_embeds , k = 5):
        print("query_embeds to np array ✅✅✅")
        querry = np.array(query_embeds,dtype="float32")
        
        if querry.ndim == 1:
            querry = querry.reshape(1, -1)
        # print("querry--->>>>" , querry)
        # print(querry.shape)
        D , I  = self.index.search(querry , k)
        print("Done searching ✅✅✅")
        results = []
        
        for dist ,index  in zip(D[0] , I[0]):
            meta = self.metadata.get(index)
            
            if meta:
                results.append({
                    **meta ,
                    "score" : float(dist)
                })
        print("done creating ans and metadata")
        
        return results