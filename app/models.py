"""DocGen AI - Database models"""
import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, Text, DateTime, Enum as SQLEnum, Integer, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.sqlite import JSON
import enum

from app.database import Base


class UserTier(str, enum.Enum):
    FREE = "free"
    PRO = "pro"


class DocumentType(str, enum.Enum):
    PROPOSAL = "proposal"
    INVOICE = "invoice"
    REPORT = "report"
    SOP = "sop"
    CONTRACT = "contract"


class DocumentStatus(str, enum.Enum):
    DRAFT = "draft"
    GENERATING = "generating"
    COMPLETED = "completed"
    ERROR = "error"


class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    
    # Billing
    tier = Column(SQLEnum(UserTier), default=UserTier.FREE)
    stripe_customer_id = Column(String(255), nullable=True)
    stripe_subscription_id = Column(String(255), nullable=True)
    
    # Usage tracking
    document_count = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    documents = relationship("Document", back_populates="owner", cascade="all, delete-orphan")


class Document(Base):
    __tablename__ = "documents"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    
    title = Column(String(255), nullable=False)
    document_type = Column(SQLEnum(DocumentType), nullable=False)
    status = Column(SQLEnum(DocumentStatus), default=DocumentStatus.DRAFT)

    # User input
    user_input = Column(Text, nullable=False)
    additional_context = Column(Text, nullable=True)

    # Generated content
    generated_content = Column(Text, nullable=True)
    generated_html = Column(Text, nullable=True)

    # Metadata
    metadata_json = Column(JSON, nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    
    owner = relationship("User", back_populates="documents")

    def __repr__(self):
        return f"<Document(id={self.id}, title={self.title}, type={self.document_type})>"
