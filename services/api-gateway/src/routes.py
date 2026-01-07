"""
FastAPI - Rutas de la API REST
Endpoints para evaluación, auditoría, revisión y configuración

Cumple Single Responsibility: Cada endpoint tiene una responsabilidad única

Nota del desarrollador (María Gutiérrez):
La IA sugirió poner toda la lógica en las rutas. La moví a los casos de uso
para cumplir con Separation of Concerns - las rutas solo manejan HTTP.
"""
from fastapi import APIRouter, HTTPException, Header, status
from typing import List, Optional, Callable, Any
from pydantic import BaseModel, Field
from decimal import Decimal


# DTOs para request/response
class TransactionRequest(BaseModel):
    """DTO para solicitud de evaluación de transacción"""

    id: str = Field(..., description="Transaction ID")
    amount: float = Field(..., gt=0, description="Transaction amount")
    user_id: str = Field(..., description="User ID")
    location: dict = Field(..., description="Transaction location")
    timestamp: Optional[str] = None


class ReviewRequest(BaseModel):
    """DTO para decisión manual de revisión"""

    decision: str = Field(..., pattern="^(APPROVED|REJECTED)$")
    analyst_comment: Optional[str] = None


class ThresholdConfigRequest(BaseModel):
    """DTO para actualización de configuración"""

    amount_threshold: float = Field(..., gt=0)
    location_radius_km: float = Field(..., gt=0)


# Router principal
router = APIRouter()

# Variables globales para las factories de dependencias
_repository_factory = None
_cache_factory = None
_publisher_factory = None
_evaluate_use_case_factory = None
_review_use_case_factory = None

def configure_dependencies(
    repository_factory,
    cache_factory,
    evaluate_use_case_factory,
    review_use_case_factory,
    publisher_factory=None
):
    """Configura las factories de dependencias desde main.py"""
    global _repository_factory, _cache_factory, _evaluate_use_case_factory, _review_use_case_factory, _publisher_factory
    _repository_factory = repository_factory
    _cache_factory = cache_factory
    _evaluate_use_case_factory = evaluate_use_case_factory
    _review_use_case_factory = review_use_case_factory
    _publisher_factory = publisher_factory


@router.post("/transaction", status_code=status.HTTP_202_ACCEPTED)
async def submit_transaction(transaction: TransactionRequest):
    """
    HU-001: Recibe transacción y responde 202 Accepted
    El procesamiento es asíncrono vía RabbitMQ
    
    Nota del desarrollador:
    La IA sugirió 200 OK. Lo cambié a 202 Accepted porque el procesamiento
    es asíncrono - esto comunica mejor la semántica al cliente.
    """
    try:
        # Instanciar directamente con las factories
        repository = _repository_factory()
        cache = _cache_factory()
        publisher = _publisher_factory()
        
        # Crear estrategias
        from decimal import Decimal
        from shared.config import settings
        from shared.domain.strategies.amount_threshold import AmountThresholdStrategy
        from shared.domain.strategies.location_check import LocationStrategy
        
        strategies = [
            AmountThresholdStrategy(Decimal(str(settings.amount_threshold))),
            LocationStrategy(settings.location_radius_km),
        ]
        
        # Crear e invocar use case
        from shared.application.use_cases import EvaluateTransactionUseCase
        evaluate_use_case = EvaluateTransactionUseCase(repository, publisher, cache, strategies)
        
        result = await evaluate_use_case.execute(transaction.model_dump())
        return {
            "status": "accepted",
            "transaction_id": transaction.id,
            "risk_level": result["risk_level"],
        }
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.get("/audit/all")
async def get_all_evaluations():
    """
    HU-002: Consulta todas las evaluaciones para auditoría
    """
    repository = _repository_factory()
    evaluations = await repository.get_all_evaluations()
    return [
        {
            "transaction_id": e.transaction_id,
            "risk_level": e.risk_level.name,
            "reasons": e.reasons,
            "timestamp": e.timestamp.isoformat(),
            "status": e.status,
            "reviewed_by": e.reviewed_by,
            "reviewed_at": e.reviewed_at.isoformat() if e.reviewed_at else None,
        }
        for e in evaluations
    ]


@router.get("/audit/transaction/{transaction_id}")
async def get_evaluation_by_id(transaction_id: str):
    """
    Consulta una evaluación específica por ID
    """
    repository = _repository_factory()
    evaluation = await repository.get_evaluation_by_id(transaction_id)
    if evaluation is None:
        raise HTTPException(status_code=404, detail="Transaction not found")

    return {
        "transaction_id": evaluation.transaction_id,
        "risk_level": evaluation.risk_level.name,
        "reasons": evaluation.reasons,
        "timestamp": evaluation.timestamp.isoformat(),
        "status": evaluation.status,
        "reviewed_by": evaluation.reviewed_by,
        "reviewed_at": evaluation.reviewed_at.isoformat()
        if evaluation.reviewed_at
        else None,
    }


@router.get("/audit/user/{user_id}")
async def get_user_transactions(user_id: str):
    """
    Consulta todas las transacciones de un usuario específico
    
    Returns:
        Lista de evaluaciones de transacciones del usuario
    """
    repository = _repository_factory()
    evaluations = repository.get_evaluations_by_user(user_id)
    
    if not evaluations:
        return []
    
    return [
        {
            "transaction_id": e.transaction_id,
            "user_id": user_id,
            "risk_level": e.risk_level.name,
            "reasons": e.reasons,
            "status": e.status,
            "evaluated_at": e.evaluated_at.isoformat() if hasattr(e, 'evaluated_at') and e.evaluated_at else e.timestamp.isoformat(),
            "reviewed_by": e.reviewed_by,
            "reviewed_at": e.reviewed_at.isoformat() if e.reviewed_at else None,
        }
        for e in evaluations
    ]


@router.put("/transaction/review/{transaction_id}")
async def review_transaction(
    transaction_id: str,
    review: ReviewRequest,
    analyst_id: str = Header(..., alias="X-Analyst-ID"),
):
    """
    HU-010: Analista toma decisión final sobre transacción
    
    Nota del desarrollador:
    La IA sugirió recibir analyst_id en el body. Lo moví a un header
    para separar datos de autenticación de datos de negocio.
    """
    try:
        review_use_case = _review_use_case_factory()
        await review_use_case.execute(transaction_id, review.decision, analyst_id)
        return {"status": "reviewed", "decision": review.decision}
    except ValueError as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail=str(e))
        raise HTTPException(status_code=422, detail=str(e))


@router.get("/config/thresholds")
async def get_thresholds():
    """
    HU-009: Consulta configuración actual de umbrales
    """
    cache = _cache_factory()
    config = await cache.get_threshold_config()
    if config is None:
        # Valores por defecto desde settings
        from src.infrastructure.config import settings

        return {
            "amount_threshold": settings.amount_threshold,
            "location_radius_km": settings.location_radius_km,
            "source": "default",
        }

    config["source"] = "cache"
    return config


@router.put("/config/thresholds")
async def update_thresholds(
    config: ThresholdConfigRequest,
    analyst_id: str = Header(..., alias="X-Analyst-ID"),
):
    """
    HU-008: Actualiza umbrales sin redespliegue
    
    Nota del desarrollador:
    La IA no contempló auditoría de cambios. Agregué analyst_id
    para saber quién modificó la configuración (compliance requirement).
    """
    cache = _cache_factory()
    await cache.set_threshold_config(
        amount_threshold=config.amount_threshold,
        location_radius_km=config.location_radius_km,
    )

    # TODO: Guardar en MongoDB para auditoría (futura iteración)
    return {
        "status": "updated",
        "updated_by": analyst_id,
        "config": config.model_dump(),
    }
