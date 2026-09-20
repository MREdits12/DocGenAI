"""DocGen AI - Document API endpoints"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Document, DocumentStatus, User
from app.schemas import (
    DocumentCreateRequest,
    DocumentResponse,
    DocumentListResponse,
    DocumentUpdateRequest,
    GenerateResponse,
)
from app.services.ai_service import ai_service
from app.services.pdf_service import pdf_service
from app.dependencies import get_current_user, require_generation_credits

router = APIRouter(prefix="/api/documents", tags=["documents"])


@router.post("/generate", response_model=GenerateResponse)
async def generate_document(
    request: DocumentCreateRequest, 
    db: Session = Depends(get_db),
    current_user: User = Depends(require_generation_credits)
):
    """Generate a new professional document using AI."""
    # Create document record
    doc = Document(
        title=request.title,
        document_type=request.document_type,
        status=DocumentStatus.GENERATING,
        user_input=request.user_input,
        additional_context=request.additional_context,
        user_id=current_user.id
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    try:
        # Generate document using AI
        html_content = await ai_service.generate_document(
            document_type=request.document_type,
            user_input=request.user_input,
            additional_context=request.additional_context,
        )

        # Update document with generated content
        doc.generated_html = html_content
        doc.generated_content = html_content  # Store a copy
        doc.status = DocumentStatus.COMPLETED
        
        # Only increment usage if generation succeeds!
        current_user.document_count += 1
        
        db.commit()
        db.refresh(doc)

        return GenerateResponse(
            id=doc.id,
            status=doc.status,
            generated_html=html_content,
            message="Document generated successfully!",
        )

    except Exception as e:
        import traceback
        print(f"[ERROR] Document generation failed: {e}")
        traceback.print_exc()
        doc.status = DocumentStatus.ERROR
        db.commit()
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")


@router.get("/", response_model=DocumentListResponse)
async def list_documents(
    skip: int = 0, limit: int = 20, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all generated documents for the logged in user."""
    docs = (
        db.query(Document)
        .filter(Document.user_id == current_user.id)
        .order_by(Document.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    total = db.query(Document).filter(Document.user_id == current_user.id).count()
    return DocumentListResponse(documents=docs, total=total)


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: str, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific document by ID."""
    doc = db.query(Document).filter(Document.id == document_id, Document.user_id == current_user.id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc


@router.put("/{document_id}", response_model=DocumentResponse)
async def update_document(
    document_id: str, 
    request: DocumentUpdateRequest, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a document (e.g., after editing)."""
    doc = db.query(Document).filter(Document.id == document_id, Document.user_id == current_user.id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    if request.title is not None:
        doc.title = request.title
    if request.generated_html is not None:
        doc.generated_html = request.generated_html
        doc.generated_content = request.generated_html

    db.commit()
    db.refresh(doc)
    return doc


@router.delete("/{document_id}")
async def delete_document(
    document_id: str, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a document."""
    doc = db.query(Document).filter(Document.id == document_id, Document.user_id == current_user.id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    db.delete(doc)
    db.commit()
    return {"message": "Document deleted", "id": document_id}


@router.get("/{document_id}/pdf")
async def download_pdf(
    document_id: str, 
    db: Session = Depends(get_db) # Open route so the browser can print it directly in a new tab without sending Auth headers, we can secure this via a temporary token in a real production app, but for now we'll allow it if they know the ID.
):
    """Get a print-ready HTML page for saving as PDF via browser."""
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    if not doc.generated_html:
        raise HTTPException(status_code=400, detail="Document has no generated content")

    # Return print-optimized HTML
    printable = pdf_service.generate_printable_html(doc.generated_html)
    return Response(content=printable, media_type="text/html")


@router.get("/{document_id}/html")
async def get_html(
    document_id: str, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get raw HTML content of a document (for preview)."""
    doc = db.query(Document).filter(Document.id == document_id, Document.user_id == current_user.id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    if not doc.generated_html:
        raise HTTPException(status_code=400, detail="Document has no generated content")

    return Response(content=doc.generated_html, media_type="text/html")

