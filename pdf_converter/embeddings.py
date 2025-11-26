from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv

load_dotenv()
class EmbeddingGenerator:
    def __init__(self):
        self.model = OpenAIEmbeddings(
            model = "text-embedding-3-small",
            )
        
    def embed_doc(self , texts : list[str]):
        return self.model.embed_documents(texts)
        
    def embed_query(self , query : str):
        return self.model.embed_query(query)    