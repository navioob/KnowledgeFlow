from .parser import *
from .llm import *

from llama_index.core.node_parser import SentenceSplitter
from llama_index.core import Document
import uuid

from dotenv import load_dotenv
import os

load_dotenv()  # take environment variables from .env.

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
RERANK_API_KEY = os.environ.get("RERANK_API_KEY")

llm_agent = LLMAgent(llm_model="gpt-4o-mini",embedding_model="text-embedding-3-large",embedding_dimensions=3072,api_key=OPENAI_API_KEY, rerank_api_key = RERANK_API_KEY)
parser = Parser()

def create_list_of_chunks(extracted_info, summary, document_title, document_id):
    #initialise with a summary chunk
    vector_chunks = [{
                "id":f"{document_id}-{str(uuid.uuid4())}",
                "values": llm_agent.create_embeddings(summary),
                "metadata":{
                    "text": summary,
                    "section":"AI Generated Summary",
                    "section_num":"Not Available",
                    "title":document_title,
                    "document_id":document_id
                }
            }]
    
    node_parser = SentenceSplitter(chunk_size=128, chunk_overlap=int(128*0.1))

    for section in extracted_info['body_text']:

        nodes = node_parser.get_nodes_from_documents([Document(text=section['text'])], show_progress=False)

        for node in nodes:
            vector_chunks.append({
                "id":f"{document_id}-{str(uuid.uuid4())}",
                "values": llm_agent.create_embeddings(node.text),
                "metadata":{
                    "text": node.text,
                    "section":section['section'],
                    "section_num":section['sec_num'],
                    "title":document_title,
                    "document_id":document_id
                }
            })
            
    return vector_chunks
