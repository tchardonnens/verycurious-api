from fastapi import FastAPI, File, UploadFile, HTTPException
import os
import re
from pymongo.mongo_client import MongoClient
from llama_index.vector_stores.mongodb import MongoDBAtlasVectorSearch
from llama_index.indices.vector_store.base import VectorStoreIndex
import pymongo
from llama_index.storage.storage_context import StorageContext
from llama_index.readers.file.base import SimpleDirectoryReader
from dotenv import load_dotenv
import shutil
import json
# Load environment variables
load_dotenv(override=True)

# Use environment variables for sensitive information
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MONGO_URI = os.getenv("MONGODB_URI")

# Initialize FastAPI app
app = FastAPI()

# Global MongoClient, reuse the connection
mongo_client = MongoClient(MONGO_URI)

# Configuration (consider using environment variables here too)
MONGODB_DB_NAME = "VeryCurious0"
MONGODB_COLLECTION_NAME = "Embeddings1"
ATLAS_VECTOR_SEARCH_INDEX_NAME = "default"

@app.get("/")
def read_root():
    return {"MongoDB Hack": "VeryCurious"}

@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile = File(...)):
    # Check file type
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=415, detail="Unsupported file type.")
    
    try:
        file_path = f"pdfs/{file.filename}"
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Use a context manager to write the file to the disk
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Load the PDF into LlamaIndex docs format
        store_doc_pdf = SimpleDirectoryReader(input_files=[file_path]).load_data()
        store = MongoDBAtlasVectorSearch(mongo_client, db_name=MONGODB_DB_NAME, collection_name=MONGODB_COLLECTION_NAME, index_name=ATLAS_VECTOR_SEARCH_INDEX_NAME)
        storage_context = StorageContext.from_defaults(vector_store=store)
        index = VectorStoreIndex.from_documents(store_doc_pdf, storage_context=storage_context)
        # Remove the file after processing
        os.remove(file_path)

        # Query for questions, assuming the index has a method 'as_query_engine()'
        response_beginner = index.as_query_engine().query("Create a set of 3 questions each for a beginner level about the topic of the document.")
        response_intermediate = index.as_query_engine().query("Create a set of 3 questions for an intermediate level about the topic of the document.")
        response_advanced = index.as_query_engine().query("Create a set of 3 questions for an expert level about the topic of the document.")
    
        def parse_questions(questions_str):

            # Split the string into individual questions using regular expression
            questions = re.split(r'\n\d+\.\s*', questions_str)

            # Remove the first entry if it's empty (happens if the string starts with a number and period)
            if questions[0] == '':
                questions = questions[1:]
            return questions

        return {"questions beginner": parse_questions(response_beginner.response), 
                "questions intermediate": parse_questions(response_intermediate.response), 
                "questions expert": parse_questions(response_advanced.response)} 
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
