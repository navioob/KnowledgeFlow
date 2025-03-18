from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from typing import List, Dict, Set
import json
import re
from concurrent.futures import ThreadPoolExecutor
from itertools import chain
from .prompt import *
import requests
from collections import defaultdict
from db import vectordb_client


def create_chain(llm, instruction_prompt, context_prompt):

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    instruction_prompt,
                ),
                (
                    "human", 
                    context_prompt
                ),
            ]
        )
        chain = prompt | llm

        return chain

def format_contexts(contexts: List[Dict]) -> str:
    """Format contexts with document IDs for the prompt"""
    documents = defaultdict(list)

    for doc in contexts:
        documents[doc['title']].append(doc)

    # return "\n\n ---".join(
    #     f"Document ID: {doc['document_id']}\nDocument Title({doc['title']})\n{doc['text']} \n ---)"
    #     for doc in contexts
    # )

    return documents

class CitationParser:
    def __init__(self):
        # Match both (1) and (doc1) style citations
        self.pattern = r'\(([a-f0-9]{24})\)'
    
    def parse(self, text: str) -> Set[str]:
        # Return unique citations as strings to match document_id type
        return set(re.findall(self.pattern, text))


class LLMAgent:
    def __init__(self, llm_model, embedding_model, embedding_dimensions, api_key, rerank_api_key):
        self.llm = ChatOpenAI(model=llm_model, temperature=0, api_key = api_key)
        self.rerank_api_key = rerank_api_key
        self.embeddings = OpenAIEmbeddings(model=embedding_model, api_key = api_key, dimensions = embedding_dimensions)
        self.summary_chain = create_chain(self.llm, prompt_summary_instructions, prompt_summary_context)
        self.query_reformulation_chain = create_chain(self.llm, prompt_query_reformulation_instructions, prompt_query_reformulation_input)

        self.citation_parser = CitationParser()

    def create_embeddings(self, text):
         vectors = self.embeddings.embed_query(text)

         return vectors

    def generate_summary(self, title, authors, abstract, content):
        response = self.summary_chain.invoke(
                        {
                            "title":title,
                            "author_details": authors,
                            "abstract": abstract,
                            "paper_content": content
                        }
                    )
        return response.content
    
    def reformulate_query(self, original_query, list_of_paper_summaries):
        response = self.query_reformulation_chain.invoke(
                        {
                            "original_query":original_query,
                            "list_of_paper_summaries":list_of_paper_summaries,
                        }
                    )
        return response.content
    
    def rerank(self, query, context):
        url = 'https://api.jina.ai/v1/rerank'
        api_key = self.rerank_api_key
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}'
        }
        data = {
            "model": "jina-reranker-v2-base-multilingual",
            "query": query,
            "top_n": 3,
            "documents": context
        }

        response = requests.post(url, headers=headers, json=data)
        selected_context = [result["document"]["text"] for result in response.json()["results"]]

        return selected_context
    
    def retrieve_context(self, query, user_id, document_id):

        vector_query = self.create_embeddings(query)

        filter = { "document_id": { "$eq": document_id } }


        response = vectordb_client.index.query(
            namespace = user_id,
            vector = vector_query,
            top_k = 10,
            include_values = True,
            include_metadata = True,
            filter=filter
        )

        print('vector_query:', vector_query)
        print('response:', response)

        # Store retrieved texts with metadata
        retrieved_contexts = {chunk['metadata']['text']: chunk['metadata'] for chunk in response['matches']}
        print('Retrieved Context:', retrieved_contexts)

        # Rerank based on query
        reranked_contexts = self.rerank(query, list(retrieved_contexts.keys()))

        print('Reranked Context:', reranked_contexts)

        # Map reranked contexts back to metadata
        final_contexts = [retrieved_contexts[text]for text in reranked_contexts]

        return final_contexts
    
    def process_query(self, query, reformulated_query, user_id, document_ids):

        if reformulated_query is not None:
            with ThreadPoolExecutor() as executor:
                contexts = list(executor.map(lambda args: self.retrieve_context(*args), 
                                        [(reformulated_query, user_id, document_id) for document_id in document_ids]))
        
        else:
            with ThreadPoolExecutor() as executor:
                contexts = list(executor.map(lambda args: self.retrieve_context(*args), 
                                        [(query, user_id, document_id) for document_id in document_ids]))
        # with ThreadPoolExecutor() as executor:
        #         contexts = list(executor.map(lambda args: self.retrieve_context(*args), 
        #                                 [(query, user_id, document_id) for document_id in document_ids]))

        llm_chain = ChatPromptTemplate.from_messages(qa_prompt) | self.llm | JsonOutputParser()
        contexts = list(chain(*contexts))
        formatted_contexts = format_contexts(contexts)

        print("Query: ", query)
        print("Reformulated Query: ", reformulated_query)
        print("Context: ", contexts)

        # Ensure the LLM includes references in output
        result = llm_chain.invoke({
            "question": query,
            "contexts": formatted_contexts
        })

        # # Extract citations
        # parser = CitationParser()
        # cited_ids = parser.parse(result["answer"])

        # print("Generated Answer:", result["answer"])
        # print("Generated References:", result["references"])

        # # Validate citations against provided contexts
        # valid_ids = [str(ctx["document_id"]) for ctx in contexts]
        # print("Valid IDs:", valid_ids)
        # print("Cited IDs:", cited_ids)

        # # Validate citations
        # if len(cited_ids) != 0:
        #     for cid in cited_ids:
        #         if str(cid) not in valid_ids:
        #             raise ValueError(f"Invalid citation to document {cid}")

            # Create references for all cited documents
        #     result["references"] = [
        #         {
        #             "document_id": ctx["document_id"],
        #             "title": ctx.get("title", f"Document {ctx['document_id']}"),
        #             "section": ctx.get("section", ""),
        #             "section_num": ctx.get("section_num", ""),
        #             "text": ctx.get("text", ""),  # Include the relevant text
        #         }
        #         for ctx in contexts 
        #         if str(ctx["document_id"]) in cited_ids
        #     ]
        # else:
        #     result["references"] = []

        # # Validate references exist
        # if not result.get("references"):
        #     raise ValueError("No references found in the response. Each citation must have a corresponding reference.")

        print("Generated Answer: ", result['answer'])

        return result


        

    
         
    





    

        

    

