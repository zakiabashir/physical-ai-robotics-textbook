"""
Chat Router - Handles chat interactions with the Physical AI assistant
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field
import logging

from ..services.chatbot import PhysicalAIChatbot
from ..models.chat import ChatMessage, ChatResponse, ChatRequest
from ..core.dependencies import get_chatbot

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    chatbot: PhysicalAIChatbot = Depends(get_chatbot)
):
    """
    Send a message to the Physical AI chatbot

    - **message**: The message from the user
    - **context**: Optional context about the current page or selection
    - **conversation_id**: Optional conversation ID for session tracking
    """
    try:
        # Process the message through the chatbot
        response = await chatbot.process_message(
            message=request.message,
            context=request.context,
            conversation_id=request.conversation_id
        )

        return ChatResponse(
            message=response["message"],
            sources=response.get("sources", []),
            related_concepts=response.get("related_concepts", []),
            code_examples=response.get("code_examples", []),
            suggestions=response.get("suggestions", [])
        )

    except Exception as e:
        logger.error(f"Error processing chat message: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process message"
        )


@router.get("/history/{conversation_id}", response_model=List[ChatMessage])
async def get_conversation_history(
    conversation_id: str,
    chatbot: PhysicalAIChatbot = Depends(get_chatbot),
    limit: int = Query(default=50, le=100, description="Maximum number of messages to return")
):
    """
    Get conversation history for a given conversation ID

    - **conversation_id**: The ID of the conversation
    - **limit**: Maximum number of messages to return
    """
    try:
        history = await chatbot.get_conversation_history(
            conversation_id=conversation_id,
            limit=limit
        )

        return [
            ChatMessage(
                role=msg["role"],
                content=msg["content"],
                timestamp=msg["timestamp"]
            )
            for msg in history
        ]

    except Exception as e:
        logger.error(f"Error getting conversation history: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    chatbot: PhysicalAIChatbot = Depends(get_chatbot)
):
    """
    Delete a conversation and its history

    - **conversation_id**: The ID of the conversation to delete
    """
    try:
        success = await chatbot.delete_conversation(conversation_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )

        return {"message": "Conversation deleted successfully"}

    except Exception as e:
        logger.error(f"Error deleting conversation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete conversation"
        )


@router.get("/conversations", response_model=List[Dict])
async def list_conversations(
    chatbot: PhysicalAIChatbot = Depends(get_chatbot),
    limit: int = Query(default=20, le=50, description="Maximum number of conversations to return")
):
    """
    List all conversations for the user

    - **limit**: Maximum number of conversations to return
    """
    try:
        conversations = await chatbot.list_conversations(limit=limit)
        return conversations

    except Exception as e:
        logger.error(f"Error listing conversations: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list conversations"
        )


@router.post("/feedback")
async def submit_feedback(
    conversation_id: str,
    message_id: str,
    feedback: Dict[str, Any],
    chatbot: PhysicalAIChatbot = Depends(get_chatbot)
):
    """
    Submit feedback on a chat response

    - **conversation_id**: The conversation ID
    - **message_id**: The ID of the message
    - **feedback**: Feedback object containing rating and comments
    """
    try:
        # Validate feedback
        if "rating" not in feedback:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Rating is required in feedback"
            )

        rating = feedback["rating"]
        if rating < 1 or rating > 5:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Rating must be between 1 and 5"
            )

        # Submit feedback
        await chatbot.submit_feedback(
            conversation_id=conversation_id,
            message_id=message_id,
            rating=rating,
            comment=feedback.get("comment", ""),
            category=feedback.get("category", "general")
        )

        return {"message": "Feedback submitted successfully"}

    except Exception as e:
        logger.error(f"Error submitting feedback: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to submit feedback"
        )


@router.get("/suggestions/{lesson_id}")
async def get_lesson_suggestions(
    lesson_id: str,
    chatbot: PhysicalAIChatbot = Depends(get_chatbot)
):
    """
    Get contextual suggestions based on the current lesson

    - **lesson_id**: The ID of the current lesson
    """
    try:
        suggestions = await chatbot.get_lesson_suggestions(lesson_id)
        return {"suggestions": suggestions}

    except Exception as e:
        logger.error(f"Error getting lesson suggestions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get suggestions"
        )


@router.post("/highlight/ask")
async def ask_about_highlight(
    selected_text: str,
    lesson_id: str,
    section: Optional[str] = None,
    chatbot: PhysicalAIChatbot = Depends(get_chatbot)
):
    """
    Ask a question about highlighted text

    - **selected_text**: The highlighted text from the user
    - **lesson_id**: The current lesson ID
    - **section**: Optional section within the lesson
    """
    try:
        response = await chatbot.ask_about_highlight(
            text=selected_text,
            lesson_id=lesson_id,
            section=section
        )

        return {
            "response": response["response"],
            "related_content": response.get("related_content", []),
            "can_explain_code": response.get("can_explain_code", False)
        }

    except Exception as e:
        logger.error(f"Error processing highlight question: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process question"
        )


@router.get("/search")
async def search_content(
    query: str,
    lesson_id: Optional[str] = None,
    chatbot: PhysicalAIChatbot = Depends(get_chatbot),
    limit: int = Query(default=10, le=20, description="Maximum number of results")
):
    """
    Search for content within the textbook

    - **query**: Search query string
    - **lesson_id**: Optional lesson ID to restrict search to
    - **limit**: Maximum number of results to return
    """
    try:
        results = await chatbot.search_content(
            query=query,
            lesson_id=lesson_id,
            limit=limit
        )

        return {
            "results": results,
            "total": len(results)
        }

    except Exception as e:
        logger.error(f"Error searching content: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to search content"
        )