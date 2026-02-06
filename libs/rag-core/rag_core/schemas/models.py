"""Pydantic models for RAG data structures."""

from datetime import datetime
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field, field_validator

from rag_core.config import EMBEDDING_DIM


class Chunk(BaseModel):
    """A chunk of text with embeddings and metadata."""

    id: str = Field(default_factory=lambda: f"chunk_{uuid4().hex[:12]}")
    document_id: str = Field(..., description="Parent document ID")
    text: str = Field(..., min_length=1, description="Chunk text content")
    embedding: list[float] = Field(..., description=f"Vector embedding ({EMBEDDING_DIM}-dim)")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Arbitrary metadata")

    # Positioning
    chunk_index: int = Field(0, ge=0, description="Position in document (0-indexed)")
    start_char: int | None = Field(None, ge=0, description="Start character position")
    end_char: int | None = Field(None, ge=0, description="End character position")

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    @field_validator("embedding")
    @classmethod
    def validate_embedding_dimension(cls, v: list[float]) -> list[float]:
        """Ensure embedding matches configured dimension."""
        if len(v) != EMBEDDING_DIM:
            raise ValueError(f"Expected {EMBEDDING_DIM}-dim embedding, got {len(v)}")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "id": "chunk_abc123",
                "document_id": "doc_xyz789",
                "text": "This is an example chunk of text.",
                "embedding": [0.1] * 1536,
                "metadata": {"source": "manual.pdf", "page": 5},
                "chunk_index": 0,
            }
        }


class Document(BaseModel):
    """A source document (e.g., PDF, webpage)."""

    id: str = Field(default_factory=lambda: f"doc_{uuid4().hex[:12]}")
    title: str = Field(..., min_length=1)
    source_uri: str = Field(..., description="Original location (file path, URL, etc.)")
    content: str | None = Field(None, description="Full text content (optional)")
    metadata: dict[str, Any] = Field(default_factory=dict)

    # Timestamps
    ingested_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "id": "doc_xyz789",
                "title": "Aeroknite Drone Manual",
                "source_uri": "s3://aeroknite-docs/manual.pdf",
                "metadata": {"category": "technical", "version": "2.0"},
            }
        }


class RetrievalResult(BaseModel):
    """Result from similarity search."""

    chunk: Chunk
    score: float = Field(..., ge=0.0, le=1.0, description="Similarity score (0-1)")
    rank: int = Field(..., ge=1, description="Rank in results (1-indexed)")

    class Config:
        json_schema_extra = {
            "example": {
                "chunk": Chunk.Config.json_schema_extra["example"],
                "score": 0.85,
                "rank": 1,
            }
        }


class Citation(BaseModel):
    """Citation referencing a source chunk."""

    chunk_id: str
    document_id: str
    text: str = Field(..., description="Cited text snippet")
    score: float = Field(..., ge=0.0, le=1.0)
    metadata: dict[str, Any] = Field(default_factory=dict)

    def format(self) -> str:
        """Format citation for display."""
        source = self.metadata.get("source", "Unknown")
        page = self.metadata.get("page")
        page_str = f", page {page}" if page else ""
        return f"[{source}{page_str}]: {self.text[:100]}..."


class GradingResult(BaseModel):
    """Result from LLM-based grading."""

    passed: bool = Field(..., description="Whether grading check passed")
    score: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    reason: str | None = Field(None, description="Explanation for grade")
    metadata: dict[str, Any] = Field(default_factory=dict)
