"""
Pydantic Schemas para API - Request/Response models

Separa los modelos de API de los modelos de dominio
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from decimal import Decimal
from datetime import datetime


class LocationSchema(BaseModel):
    """Schema para ubicación geográfica"""
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)


class TransactionRequest(BaseModel):
    """Schema para solicitud de evaluación de transacción"""
    id: str = Field(..., min_length=1)
    amount: Decimal = Field(..., gt=0)
    user_id: str = Field(..., min_length=1)
    location: LocationSchema
    timestamp: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "id": "txn_12345",
                "amount": 1200.50,
                "user_id": "user_001",
                "location": {
                    "latitude": 40.7128,
                    "longitude": -74.0060
                },
                "timestamp": "2024-01-08T10:30:00Z"
            }
        }


class EvaluationResponse(BaseModel):
    """Schema para respuesta de evaluación"""
    transaction_id: str
    risk_level: str
    reasons: List[str]
    status: str

    class Config:
        json_schema_extra = {
            "example": {
                "transaction_id": "txn_12345",
                "risk_level": "LOW_RISK",
                "reasons": [],
                "status": "APPROVED"
            }
        }


class ReviewRequest(BaseModel):
    """Schema para solicitud de revisión manual"""
    decision: str = Field(..., pattern="^(APPROVED|REJECTED)$")
    analyst_id: str = Field(..., min_length=1)

    class Config:
        json_schema_extra = {
            "example": {
                "decision": "APPROVED",
                "analyst_id": "analyst_123"
            }
        }


class HealthResponse(BaseModel):
    """Schema para health check"""
    status: str
    service: str
    version: str
