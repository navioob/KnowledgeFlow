from fastapi import FastAPI, HTTPException, UploadFile, Form, File, Body, Query, Header, Depends
from typing import Annotated
from fastapi import APIRouter
import itertools

from schema import UserSignupDetails, UserLoginDetails, UserCheckingDetails
from utils import decrypt_text
from db import db_client, vectordb_client
from helper import parser, llm_agent, create_list_of_chunks

router = APIRouter(
    prefix="/document",
    tags=["document"],
    responses={404: {"description": "Not Found"}},
)

@router.get("/")
async def system_check():
    """Check if the document-related functions are online and operational.

    Returns:
        dict: A dictionary with a message confirming the document functions are online.
    """
    return {"message": "User Functions Online"}

@router.post("/upload")
async def upload_document(user_id: str = Form(...), file: UploadFile = File(...)):
    """Upload a document, extract its content, generate a summary, and store it in the database.

    Args:
        user_id (str): The ID of the user uploading the document.
        file (UploadFile): The file to be uploaded (expected to be a PDF).

    Returns:
        dict: A dictionary with a success flag and a confirmation message.

    Raises:
        HTTPException: If an error occurs during file processing, database upload, or vector storage.
    """
    # Read PDF file bytes
    file_bytes = await file.read()
    # Pass the file bytes into the Parser to extract text
    extracted_info = parser.extract_text(file.filename, file_bytes)
    paper_title = extracted_info['title']

    # Generate summary chunk
    summary = llm_agent.generate_summary(
        extracted_info["title"],
        extracted_info['authors'],
        extracted_info['abstract'],
        extracted_info['all_text']
    )

    # Upload document into MongoDB and get inserted document id
    inserted_id = db_client.upload_document(
        user_id=user_id,
        document_title=paper_title,
        document_summary=summary
    )
    # Create a list of chunks that's vectorized to be upserted in batch
    list_of_chunks = create_list_of_chunks(
        extracted_info=extracted_info,
        summary=summary,
        document_title=paper_title,
        document_id=str(inserted_id)
    )

    # Upload the vectorized chunks into the VectorDB
    vectordb_client.upload_vectors(list_of_chunks=list_of_chunks, namespace=str(user_id))

    return {
        "success": True,
        "message": "Document Upload Successful."
    }

@router.delete("/delete")
async def delete_document(user_id: str, document_id: str):
    """Delete a document from both the NoSQL database and the vector database.

    Args:
        user_id (str): The ID of the user who owns the document.
        document_id (str): The ID of the document to delete.

    Returns:
        dict: A dictionary with a success flag and a confirmation message.

    Raises:
        HTTPException: If deletion fails in either the NoSQL database (status 400) or vector database (status 400).
    """
    try:
        db_client.delete_document(user_id=user_id, document_id=document_id)
    except Exception as error:
        raise HTTPException(status_code=400, detail=f"NoSQL DB - Delete document failed. Error: {error}.")

    try:
        vectordb_client.delete_vectors(user_id=user_id, document_id=document_id)
    except Exception as error:
        raise HTTPException(status_code=400, detail=f"Vector DB - Delete document failed. Error: {error}.")

    return {
        "success": True,
        "message": "Document Upload Successful."  # Note: Should this be "Document Deletion Successful"?
    }

@router.get("/list")
async def get_documents(user_id: str):
    """Retrieve a list of documents associated with a user.

    Args:
        user_id (str): The ID of the user whose documents are to be retrieved.

    Returns:
        dict: A dictionary with a success flag, a message, and the list of documents.
    """
    list_of_documents = db_client.get_documents(user_id=user_id)
    print(list_of_documents)

    return {
        "success": True,
        "message": "List of Documents extracted.",
        "content": list_of_documents
    }