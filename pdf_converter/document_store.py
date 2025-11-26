from typing import List
from streamlit.runtime.uploaded_file_manager import UploadedFile
from .chunking import Chunker
from .embeddings import EmbeddingGenerator
from .pdf_reader import PDFReader
from .vector_base import VectorBase

class DocumentStore:
    def __init__(self):
        
        self.pdf_reader = PDFReader()
        self.embedder = EmbeddingGenerator()
        self.chunker = Chunker()
        
        self.chunks = []
        self.pages = []
        self.vector_db = None
        self.chunk_id = 0
        
    def ingestion(self, files : List[UploadedFile]):
        
        print("started reading files 🤖🤖🤖🤖")
        
        pages = self.pdf_reader.read_pdf(files=files)
        self.pages.extend(pages)
        
        print("done reading files ✅✅✅✅")
        
        chunks = self.chunker.chunking(pages=pages)
        
        for c in chunks:
            c["chunk_id"] = self.chunk_id
            self.chunk_id += 1
        
        self.chunks.extend(chunks)
        print("done chunking files ✅✅✅✅")
        
        
        
        texts = [c["chunk"] for c in chunks]
        
        vectors  = self.embedder.embed_doc(texts=texts)
        
        print("done vectoring files ✅✅✅✅")
        
        
        if self.vector_db is None:
            self.vector_db = VectorBase(dim=len(vectors[0]))
            
        
        metadata = []
        
        for c in chunks:
            metadata.append({
                "file_name" : c["file_name"],
                "page" : c["page"],
                "text" : c["chunk"],
                "chunk_id" : c["chunk_id"]
            })
            
        print("done adding meta data ✅✅✅✅")
        
        
        self.vector_db.add_vectors(embeddings=vectors , metadata=metadata)
        
    
    def search(self , query , file_name : str | None = None ):
        print("query---->>>>>>✅✅✅", query)
        print("converting query to vectors ✅✅✅✅✅")
        query_vectors = self.embedder.embed_query(query)
        # print("query_vectors--------->>>> ✅✅✅✅" , query_vectors)
        print("started searching ✅✅✅")
        results = self.vector_db.search(query_embeds=query_vectors)
        if file_name is not None:
            results = [r for r in results if r["file_name"] == file_name]
            
        return results
            