import os
import requests
import json
import time
from typing import List, Optional
try:
    from mlx_lm import load, generate
    MLX_AVAILABLE = True
except ImportError:
    MLX_AVAILABLE = False
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import BaseRetriever
from langchain.prompts import PromptTemplate
import chromadb


class MLXModel:
    def __init__(self, model_name: str = "mlx-community/Meta-Llama-3.1-70B-Instruct-4bit"):
        self.model_name = model_name
        self.model = None
        self.tokenizer = None
        self._load_model()
    
    def _load_model(self):
        """Load the MLX model"""
        try:
            print(f"Loading MLX model: {self.model_name}")
            self.model, self.tokenizer = load(self.model_name)
            print(f"MLX model loaded successfully")
        except Exception as e:
            print(f"Failed to load MLX model: {e}")
            self.model = None
            self.tokenizer = None
    
    def switch_model(self, model_name: str):
        """Switch to a different MLX model"""
        self.model_name = model_name
        self._load_model()
    
    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        if not self.model or not self.tokenizer:
            return "MLX model not loaded. Please check model availability."
        
        try:
            response = generate(
                self.model, 
                self.tokenizer, 
                prompt=prompt, 
                verbose=False,
                max_tokens=512
            )
            return response
        except Exception as e:
            return f"Error with MLX generation: {str(e)}"


class OllamaLLM:
    def __init__(self, model: str = "llama3.1:8b", base_url: str = "http://localhost:11434"):
        self.model = model
        self.base_url = base_url
    
    def switch_model(self, model: str):
        """Switch to a different model"""
        self.model = model
        print(f"Switched to Ollama model: {model}")
    
    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=120
            )
            response.raise_for_status()
            return response.json()["response"]
        except Exception as e:
            return f"Error connecting to Ollama: {str(e)}. Make sure Ollama is running with: ollama serve"


class HealthRAG:
    def __init__(self, data_path: str = "data/pdfs", persist_directory: str = "data/vectorstore", backend: str = "ollama"):
        self.data_path = data_path
        self.persist_directory = persist_directory
        self.backend = backend
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'}
        )
        self.vectorstore = None
        
        # Initialize LLM based on backend
        if backend == "mlx" and MLX_AVAILABLE:
            self.llm = MLXModel()
        else:
            self.llm = OllamaLLM()
        
        self._initialize_system()
    
    def switch_backend(self, backend: str, model: str = None):
        """Switch between Ollama and MLX backends"""
        self.backend = backend
        
        if backend == "mlx" and MLX_AVAILABLE:
            if model:
                self.llm = MLXModel(model)
            else:
                self.llm = MLXModel()
            print(f"Switched to MLX backend")
        else:
            if model:
                self.llm = OllamaLLM(model)
            else:
                self.llm = OllamaLLM()
            print(f"Switched to Ollama backend")
    
    def _initialize_system(self):
        """Initialize the RAG system with existing vectorstore or create new one"""
        try:
            # Try to load existing vectorstore
            self.vectorstore = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embeddings
            )
            
            # Check if vectorstore has documents
            if self.vectorstore._collection.count() == 0:
                self._load_documents()
            
        except Exception as e:
            print(f"Creating new vectorstore: {e}")
            self._load_documents()
        
        self._setup_qa_chain()
    
    def _load_documents(self):
        """Load and process PDF documents"""
        if not os.path.exists(self.data_path):
            os.makedirs(self.data_path)
            print(f"Created directory: {self.data_path}")
            return
        
        documents = []
        pdf_files = [f for f in os.listdir(self.data_path) if f.endswith('.pdf')]
        
        if not pdf_files:
            print("No PDF files found. Add PDFs to the data/pdfs directory.")
            return
        
        for pdf_file in pdf_files:
            pdf_path = os.path.join(self.data_path, pdf_file)
            try:
                loader = PyPDFLoader(pdf_path)
                docs = loader.load()
                documents.extend(docs)
                print(f"Successfully loaded: {pdf_file}")
            except Exception as e:
                print(f"Error loading {pdf_file}: {str(e)}")
                continue
        
        if documents:
            # Split documents into chunks
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                length_function=len
            )
            texts = text_splitter.split_documents(documents)
            
            # Create vectorstore
            self.vectorstore = Chroma.from_documents(
                documents=texts,
                embedding=self.embeddings,
                persist_directory=self.persist_directory
            )
            
            self.vectorstore.persist()
            print(f"Loaded {len(documents)} documents and created {len(texts)} chunks")
    
    def _setup_qa_chain(self):
        """Setup the QA chain with custom prompt for health and fitness"""
        if not self.vectorstore:
            return
        
        self.retriever = self.vectorstore.as_retriever(search_kwargs={"k": 5})
        
        # Custom prompt for health and fitness advice
        self.prompt_template = """
        You are a health and fitness advisor. IMPORTANT: Only use information from the provided context to answer questions. Do NOT make up information.
        
        Context from documents:
        {context}
        
        Question: {question}
        
        Rules:
        1. ONLY use information explicitly stated in the context above
        2. If the context doesn't contain the answer, say "I don't have information about that in the provided documents"
        3. Quote or reference specific parts of the context when possible
        4. Do NOT generate information not in the context
        5. Be clear when recommending to consult healthcare professionals
        
        Answer based only on the context:
        """
    
    def query(self, question: str) -> tuple[str, float]:
        """Query the RAG system and return response with timing"""
        if not self.vectorstore:
            return "System not properly initialized. Please add PDF documents to the data/pdfs directory and restart.", 0.0
        
        try:
            start_time = time.time()
            
            # Retrieve relevant documents
            docs = self.retriever.get_relevant_documents(question)
            context = "\n\n".join([doc.page_content for doc in docs])
            
            # Format prompt
            prompt = self.prompt_template.format(context=context, question=question)
            
            # Get response from Ollama
            response = self.llm._call(prompt)
            
            end_time = time.time()
            response_time = end_time - start_time
            
            return response, response_time
            
        except Exception as e:
            return f"Error processing query: {str(e)}", 0.0
    
    def add_documents(self, pdf_paths: List[str]):
        """Add new PDF documents to the vectorstore"""
        documents = []
        for pdf_path in pdf_paths:
            try:
                loader = PyPDFLoader(pdf_path)
                docs = loader.load()
                documents.extend(docs)
                print(f"Successfully loaded: {pdf_path}")
            except Exception as e:
                print(f"Error loading {pdf_path}: {str(e)}")
                continue
        
        if documents:
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                length_function=len
            )
            texts = text_splitter.split_documents(documents)
            
            if self.vectorstore:
                self.vectorstore.add_documents(texts)
                self.vectorstore.persist()
            else:
                self.vectorstore = Chroma.from_documents(
                    documents=texts,
                    embedding=self.embeddings,
                    persist_directory=self.persist_directory
                )
                self.vectorstore.persist()
                self._setup_qa_chain()
            
            print(f"Added {len(documents)} new documents")
    
    def get_document_count(self) -> int:
        """Get the number of documents in the vectorstore"""
        if self.vectorstore:
            return self.vectorstore._collection.count()
        return 0