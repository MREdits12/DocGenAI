"""DocGen AI - Pydantic schemas for API validation"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from app.models import DocumentType, DocumentStatus


# --- Request schemas ---


class DocumentCreateRequest(BaseModel):
    """Request body for creating/generating a new document."""

    title: str = Field(..., min_length=1, max_length=255, description="Document title")
    document_type: DocumentType = Field(..., description="Type of document to generate")
    user_input: str = Field(
        ...,
        min_length=10,
        description="Raw input: notes, data, descriptions for the AI to work with",
    )
    additional_context: Optional[str] = Field(
        None,
        description="Extra context: company name, branding, tone, specific requirements",
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "title": "Website Redesign Proposal",
                    "document_type": "proposal",
                    "user_input": "Client: ABC Corp. Project: Redesign their e-commerce website. Budget: $15,000. Timeline: 8 weeks. Key features: mobile-first design, payment integration, inventory management.",
                    "additional_context": "My company is PixelPerfect Design Studio. Tone: professional but friendly.",
                }
            ]
        }
    }


class DocumentUpdateRequest(BaseModel):
    """Request body for updating a document's content."""

    title: Optional[str] = Field(None, max_length=255)
    generated_html: Optional[str] = None


# --- Response schemas ---


class DocumentResponse(BaseModel):
    """Response body for a single document."""

    id: str
    title: str
    document_type: DocumentType
    status: DocumentStatus
    user_input: str
    additional_context: Optional[str]
    generated_content: Optional[str]
    generated_html: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class DocumentListResponse(BaseModel):
    """Response body for listing documents."""

    documents: list[DocumentResponse]
    total: int


class GenerateResponse(BaseModel):
    """Response after AI generation completes."""

    id: str
    status: DocumentStatus
    generated_html: str
    message: str

# --- Auth Schemas ---

class UserCreate(BaseModel):
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class UserResponse(BaseModel):
    id: str
    email: str
    tier: str
    document_count: int
    
    model_config = {"from_attributes": True}
