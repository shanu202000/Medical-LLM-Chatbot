from langchain.document_loaders import PyPDFLoader, DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from typing import List
from langchain.schema import Document


#Extract Data From the PDF File
def load_pdf_file(data):
    loader= DirectoryLoader(data,
                            glob="*.pdf",
                            loader_cls=PyPDFLoader)

    documents=loader.load()

    return documents

#function to filter the documents to only contain source as metadata and the original page_content

def filter_to_minimal_docs(docs: List[Document])-> List[Document]:

    
    "Given a list of documemts, return a list of document objects that contain only source as metadata and the original page_content."
    minimal_docs: List[Document] = []
    for doc in docs:
        src=doc.metadata.get("source")
        minimal_docs.append(
            Document(page_content=doc.page_content, metadata={"source": src})
        )

    return minimal_docs    


#spilit the documents into chunks of 1000 characters with an overlap of 200 characters
def text_split(minimal_docs):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=20,
        length_function=len
    )
    docs_chunk = text_splitter.split_documents(minimal_docs)
    return docs_chunk

#Function to download the embeddings from the huggingface model
def download_embeddings():

    "Download and return higgingface embedding model."
    model_name = "sentence-transformers/all-MiniLM-L6-v2"

    embeddings = HuggingFaceEmbeddings(
        model_name=model_name,
        
    )
    return embeddings

embeddings = download_embeddings()

