from fastapi import APIRouter, HTTPException, status
from app.models.schemas import ChatRequest, ChatResponse, ConversationResponse, CreateConversationResponse
from app.services.conversation_manager import ConversationManager
from app.services.transformer_model import CafeAdvisorModel

router = APIRouter(prefix="/api", tags=["chat"])
manager = ConversationManager()
advisor = CafeAdvisorModel()

@router.post("/conversations", response_model=CreateConversationResponse, status_code=status.HTTP_201_CREATED)
def create_conversation() -> CreateConversationResponse:
    return CreateConversationResponse(conversation_id=manager.create_conversation())

@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    message = request.message.strip()
    if not message:
        raise HTTPException(400, "Please enter a message.")
    try:
        manager.add_message(request.conversation_id, "user", message)
        response = advisor.generate_response(manager.get_messages(request.conversation_id))
        manager.add_message(request.conversation_id, "assistant", response)
        return ChatResponse(conversation_id=request.conversation_id, response=response)
    except KeyError:
        raise HTTPException(404, "Conversation not found. Please start a new conversation.")

@router.get("/conversations/{conversation_id}", response_model=ConversationResponse)
def get_conversation(conversation_id: str) -> ConversationResponse:
    try:
        return ConversationResponse(conversation_id=conversation_id, messages=manager.get_messages(conversation_id))
    except KeyError:
        raise HTTPException(404, "Conversation not found.")

@router.delete("/conversations/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_conversation(conversation_id: str) -> None:
    try:
        manager.delete_conversation(conversation_id)
    except KeyError:
        raise HTTPException(404, "Conversation not found.")
