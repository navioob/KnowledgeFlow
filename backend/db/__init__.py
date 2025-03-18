from dotenv import load_dotenv
import os

from .mongo_atlas import *
from .pinecone import *

load_dotenv()  # take environment variables from .env.

ATLAS_URI = os.environ.get("ATLAS_URI")
PINECONE_API_KEY = os.environ.get("PINECONE_API_KEY")

db_client = AtlasClient(ATLAS_URI,'test')
vectordb_client = PineconeClient(api_key=PINECONE_API_KEY, index_name="index-knowledgeflow")

