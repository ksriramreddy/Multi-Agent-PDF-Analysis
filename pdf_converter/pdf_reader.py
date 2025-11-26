import pdfplumber
from streamlit.runtime.uploaded_file_manager import UploadedFile
from typing import List
class PDFReader:
    def read_pdf(self, files : List[UploadedFile]):
        
        pages = []
        
        for file in files:
            with pdfplumber.open(file) as f:
                for i , page in enumerate(f.pages , start=1):
                    text = page.extract_text() or ""
                    
                    pages.append({
                        "file_name" : file.name,
                        "page" : i,
                        "text" : text
                    })
                
        return pages