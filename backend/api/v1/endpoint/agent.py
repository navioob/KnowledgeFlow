from fastapi import FastAPI, HTTPException, UploadFile, Form, File, Body, Query, Header, Depends
from typing import Annotated, List
from fastapi import APIRouter
import itertools

from schema import UserSignupDetails, UserLoginDetails, UserCheckingDetails, FormulateQuestions
from utils import decrypt_text
from db import db_client, vectordb_client
from helper import parser, llm_agent, create_list_of_chunks

router = APIRouter(
    prefix="/agent",
    tags=["agent"],
    responses={404: {"description": "Not Found"}},
)

@router.get("/")
async def system_check():
    """Check if the agent functions are online and operational.

    Returns:
        dict: A dictionary with a message confirming the agent functions are online.
    """
    return {"message": "Agent Functions Online"}

@router.post("/formulate-question")
async def formulate_question(original_query: str = Body(...), list_summary: List[FormulateQuestions] = Body(...)):
    """Reformulate a user-provided query based on a list of summary data.

    Args:
        original_query (str): The original query string provided by the user.
        list_summary (List[FormulateQuestions]): A list of FormulateQuestions objects containing summary data.

    Returns:
        dict: A dictionary with a success flag and the reformulated question content.

    """
    reformulated_question = llm_agent.reformulate_query(original_query, list_summary)
    return {"success": True, "content": reformulated_question}

@router.post("/generate-answer")
async def generate_answer(query: str = Body(...), user_id: str = Body(...), list_summary: List[FormulateQuestions] = Body(...)):
    """Generate an answer to a query based on user ID and summary data if reformulation is needed.

    Args:
        query (str): The query string to generate an answer for.
        user_id (str): The ID of the user making the request.
        list_summary (List[FormulateQuestions]): A list of FormulateQuestions objects containing summary data.

    Returns:
        dict: A dictionary with a success flag and the generated answer content.

    Raises:
        HTTPException: If an error occurs during answer generation, with a 400 status code and error details.
    """
    list_of_document_ids = [document.document_id for document in list_summary]

    try:
        if len(list_summary) > 1:
            reformulated_question = llm_agent.reformulate_query(query, list_summary)
            # Based on the reformulated question, generate a response
            answer = llm_agent.process_query(query, reformulated_question, user_id, list_of_document_ids)
        else:
            answer = llm_agent.process_query(query, None, user_id, list_of_document_ids)

        return {"success": True, "content": answer}
    except Exception as error:
        raise HTTPException(400, detail=f"Error {error}. Unable to generate answers.")