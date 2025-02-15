from fastapi import FastAPI, UploadFile, File, Depends, Query
from fastapi.responses import JSONResponse
import pytesseract
from PIL import Image
import io
import fitz  # PyMuPDF for PDF processing
import spacy
from transformers import pipeline, AutoModelForQuestionAnswering, AutoTokenizer
import psycopg2
from psycopg2.extras import RealDictCursor
import celery
from celery import Celery
from elasticsearch import Elasticsearch
import logging
import datasets
import torch
from sentence_transformers import SentenceTransformer, util
import faiss
import numpy as np
import openai
import os

# Configurar FastAPI
app = FastAPI()

# Configurar logs
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configurar modelos NLP
nlp = spacy.load("en_core_web_sm")
summarizer = pipeline("summarization")
retriever = SentenceTransformer("LexLM/legal-miniLM")  # Modelo legal
qa_model = AutoModelForQuestionAnswering.from_pretrained("deepset/roberta-base-squad2")
tokenizer = AutoTokenizer.from_pretrained("deepset/roberta-base-squad2")

# Configurar OpenAI API para GPT-4
openai.api_key = os.getenv("OPENAI_API_KEY")

def query_gpt4(context, question):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Eres un abogado experto que responde con base en los documentos proporcionados."},
            {"role": "user", "content": f"Contexto: {context}\n\nPregunta: {question}"}
        ]
    )
    return response['choices'][0]['message']['content']

# Configuración de Celery
celery_app = Celery(
    "tasks",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0"
)

# Configurar Elasticsearch
es = Elasticsearch(["http://localhost:9200"])

# Configurar PostgreSQL
DATABASE_URL = "postgresql://admin:securepassword@localhost/legal_docs"
def get_db():
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    return conn

def extract_text_from_pdf(contents: bytes) -> str:
    doc = fitz.open(stream=contents, filetype="pdf")
    text = "\n".join([page.get_text() for page in doc])
    return text

@app.post("/upload")
def upload_document(file: UploadFile = File(...)):
    contents = file.file.read()
    text = extract_text_from_pdf(contents)
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO documents (filename, content) VALUES (%s, %s) RETURNING id", (file.filename, text))
    doc_id = cursor.fetchone()["id"]
    conn.commit()
    cursor.close()
    conn.close()
    
    # Indexar en Elasticsearch
    es.index(index="documents", id=doc_id, body={"filename": file.filename, "content": text})
    
    return {"message": "Document uploaded", "document_id": doc_id}

@app.post("/ask")
def ask_question(question: str):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, content FROM documents")
    documents = cursor.fetchall()
    cursor.close()
    conn.close()
    
    if not documents:
        return {"error": "No documents available for search."}
    
    doc_texts = [doc["content"] for doc in documents]
    doc_ids = [doc["id"] for doc in documents]
    
    question_embedding = retriever.encode(question, convert_to_tensor=False).reshape(1, -1)
    doc_embeddings = retriever.encode(doc_texts, convert_to_tensor=False)
    faiss_index = faiss.IndexFlatL2(doc_embeddings.shape[1])
    faiss_index.add(np.array(doc_embeddings, dtype=np.float32))
    _, best_match_idx = faiss_index.search(question_embedding, 1)
    best_match_idx = best_match_idx[0][0]
    best_match_text = doc_texts[best_match_idx]
    best_match_id = doc_ids[best_match_idx]
    
    answer = query_gpt4(best_match_text, question)
    
    return {"question": question, "answer": answer, "document_id": best_match_id}

@app.get("/")
def root():
    return {"message": "Legal Document Analyzer API with GPT-4 is running."}
