import os
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

Chroma_dir="vector_db"
collection_name="meeting_transcript"
embedding_model="all-MiniLM-L6-v2"

def get_embeddings():
    return HuggingFaceEmbeddings(model_name=embedding_model,
                                 model_kwargs={"device":"cpu"})

def build_vector_store(transcript:str)->Chroma:
    print("Creating Vector Store...")
    # chunking
    splitter=RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )
    chunks=splitter.split_text(transcript)
    docs=[
        Document(page_content=chunk, metadata={"chunk_index":i})
        for i,chunk in enumerate(chunks)
    ]
    embeddings=get_embeddings()
    vector_store=Chroma.from_documents(
        documents=docs,
        embedding=embeddings,
        collection_name=collection_name,
        persist_directory=Chroma_dir
    )
    return vector_store

def load_vector_store()->Chroma:
    embeddings=get_embeddings()
    vector_store=Chroma(
        collection_name=collection_name,
        embedding_function=embeddings,
        persist_directory=Chroma_dir
    )
    return vector_store

def get_retriever(vector_store:Chroma,k:int=4):
    return vector_store.as_retriever(
        # Prefer distinct transcript passages over near-duplicate chunks. This
        # helps questions that ask for several items spread across a video.
        search_type="mmr",
        search_kwargs={"k":max(k, 8), "fetch_k":max(k * 4, 24), "lambda_mult":0.5}
    )


# Keep the original misspelled name working for existing imports.
get_retreiver = get_retriever




