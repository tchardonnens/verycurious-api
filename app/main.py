from fastapi import FastAPI, File, UploadFile

import os
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from llama_index.vector_stores.mongodb import MongoDBAtlasVectorSearch
from llama_index.indices.vector_store.base import VectorStoreIndex

OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
#MONGO_URI = os.environ["MONGO_URI"]

app = FastAPI()

# Create a new client and connect to the server
# client = MongoClient(os.getenv("MONGODB_URI"), server_api=ServerApi('1'))

# connect to Atlas as a vector store
# store = MongoDBAtlasVectorSearch(
#     client,
#     db_name=os.getenv('MONGODB_DATABASE'), # this is the database where you stored your embeddings
#     collection_name=os.getenv('MONGODB_VECTORS'), # this is where your embeddings were stored in 2_load_and_index.py
#     index_name=os.getenv('MONGODB_VECTOR_INDEX') # this is the name of the index you created after loading your data
# )
# index = VectorStoreIndex.from_vector_store(store)

@app.get("/")
def read_root():
    return {"MongoDB Hack": "VeryCurious"}


#PDF files only
# store the file in a folder called "pdfs"
@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile = File(...)):
    with open(f"pdfs/{file.filename}", "wb") as buffer:
        buffer.write(file.file.read())
    return {"filename": file.filename}
