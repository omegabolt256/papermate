"""Persistent chat management with search."""
from typing import List, Optional
from datetime import datetime
from app.database import get_session
from app.database.models import Chat, Message
from app.models import get_model_provider
import json

class ChatManager:
    def __init__(self):
        self.session = get_session()
        self.model = get_model_provider("ollama")
    
    # ==================== CHAT CRUD ====================
    
    def create_chat(self, project_id: str, title: str = "New Chat", context_type: str = "project") -> Chat:
        chat = Chat(
            project_id=project_id,
            title=title,
            context_type=context_type
        )
        self.session.add(chat)
        self.session.commit()
        return chat
    
    def get_chat(self, chat_id: str) -> Optional[Chat]:
        return self.session.query(Chat).filter(Chat.id == chat_id).first()
    
    def get_project_chats(self, project_id: str) -> List[Chat]:
        return self.session.query(Chat)\
            .filter(Chat.project_id == project_id)\
            .order_by(Chat.updated_at.desc()).all()
    
    def get_recent_chats(self, project_id: str, limit: int = 5) -> List[Chat]:
        return self.session.query(Chat)\
            .filter(Chat.project_id == project_id)\
            .order_by(Chat.updated_at.desc()).limit(limit).all()
    
    def rename_chat(self, chat_id: str, new_title: str) -> Optional[Chat]:
        chat = self.get_chat(chat_id)
        if chat:
            chat.title = new_title
            chat.updated_at = datetime.utcnow()
            self.session.commit()
        return chat
    
    def delete_chat(self, chat_id: str) -> bool:
        chat = self.get_chat(chat_id)
        if chat:
            self.session.delete(chat)
            self.session.commit()
            return True
        return False
    
    # ==================== MESSAGES ====================
    
    def add_message(self, chat_id: str, role: str, content: str, sources: List[dict] = None) -> Message:
        msg = Message(
            chat_id=chat_id,
            role=role,
            content=content,
            sources=sources or []
        )
        self.session.add(msg)
        
        # Update chat timestamp
        chat = self.get_chat(chat_id)
        if chat:
            chat.updated_at = datetime.utcnow()
            # Auto-rename chat based on first user message
            if role == "user" and chat.title == "New Chat":
                chat.title = content[:60] + ("..." if len(content) > 60 else "")
        
        self.session.commit()
        return msg
    
    def get_messages(self, chat_id: str) -> List[Message]:
        return self.session.query(Message)\
            .filter(Message.chat_id == chat_id)\
            .order_by(Message.timestamp).all()
    
    def get_last_messages(self, chat_id: str, limit: int = 10) -> List[Message]:
        return self.session.query(Message)\
            .filter(Message.chat_id == chat_id)\
            .order_by(Message.timestamp.desc()).limit(limit)[::-1]
    
    # ==================== CHAT WITH AI ====================
    
    def send_message(self, chat_id: str, user_message: str, context_papers: List[dict] = None) -> Message:
        """Send a message and get AI response with context."""
        
        # Save user message
        self.add_message(chat_id, "user", user_message)
        
        # Get recent messages for context
        recent = self.get_last_messages(chat_id, limit=10)
        
        # Build prompt with chat history
        history_parts = []
        for msg in recent:
            role_name = "User" if msg.role == "user" else "Assistant"
            history_parts.append(f"{role_name}: {msg.content}")
        
        history = "\n".join(history_parts)
        
        # Build full prompt
        prompt = f"""You are a medical research assistant. Continue this conversation.

CHAT HISTORY:
{history}

RULES:
- Cite sources when referencing papers
- If discussing a paper, mention title and year
- Be precise and evidence-based

User: {user_message}
Assistant:"""
        
        # Get AI response
        response = self.model.generate(prompt, max_tokens=600)
        
        # Save AI response
        return self.add_message(chat_id, "assistant", response)
    
    # ==================== SEARCH ====================
    
    def search_chats(self, project_id: str, query: str) -> List[dict]:
        """Search across all chat messages in a project."""
        results = self.session.query(Message, Chat)\
            .join(Chat, Message.chat_id == Chat.id)\
            .filter(Chat.project_id == project_id)\
            .filter(Message.content.ilike(f"%{query}%"))\
            .order_by(Message.timestamp.desc())\
            .limit(20).all()
        
        return [
            {
                "message_id": msg.id,
                "chat_id": chat.id,
                "chat_title": chat.title,
                "content": msg.content[:200],
                "role": msg.role,
                "timestamp": msg.timestamp.isoformat() if msg.timestamp else None,
            }
            for msg, chat in results
        ]
    
    def search_chat_titles(self, project_id: str, query: str) -> List[Chat]:
        """Search chat titles."""
        return self.session.query(Chat)\
            .filter(Chat.project_id == project_id)\
            .filter(Chat.title.ilike(f"%{query}%"))\
            .order_by(Chat.updated_at.desc()).all()
    
    def close(self):
        self.session.close()