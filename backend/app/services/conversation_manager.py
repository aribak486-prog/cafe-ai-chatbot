from uuid import uuid4
from app.models.schemas import Message


class ConversationManager:
    def __init__(self) -> None:
        # Temporary in-memory conversation storage.
        # No permanent database is intentionally used.
        self.conversations: dict[str, list[Message]] = {}

    def create_conversation(self) -> str:
        conversation_id = str(uuid4())
        self.conversations[conversation_id] = []
        return conversation_id

    def add_message(self, conversation_id: str, role: str, content: str) -> None:
        if conversation_id not in self.conversations:
            raise KeyError(conversation_id)
        self.conversations[conversation_id].append(Message(role=role, content=content))

    def get_messages(self, conversation_id: str) -> list[Message]:
        if conversation_id not in self.conversations:
            raise KeyError(conversation_id)
        return self.conversations[conversation_id]

    def delete_conversation(self, conversation_id: str) -> None:
        if conversation_id not in self.conversations:
            raise KeyError(conversation_id)
        del self.conversations[conversation_id]
