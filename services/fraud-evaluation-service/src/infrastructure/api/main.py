"""
FastAPI Main Application - Fraud Evaluation Service

Implementa API REST para evaluación de transacciones
Puerto 8001 - Microservicio independiente
"""
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from decimal import Decimal
from typing import List
from ...application.use_cases import EvaluateTransactionUseCase, ReviewTransactionUseCase
from ...application.interfaces import TransactionRepository, MessagePublisher, CacheService
from ...domain.strategies.amount_threshold import AmountThresholdStrategy
from ...domain.strategies.location_check import LocationStrategy
from ...domain.strategies.device_validation import DeviceValidationStrategy
from ..adapters.mongodb import MongoDBAdapter
from ..adapters.redis import RedisAdapter
from ..adapters.rabbitmq import RabbitMQAdapter
from ..config import settings
from .schemas import (
    TransactionRequest,
    EvaluationResponse,
    ReviewRequest,
    HealthResponse,
)

# Crear aplicación FastAPI
app = FastAPI(
    title="Fraud Evaluation Service",
    description="Microservicio de evaluación de fraude con Clean Architecture",
    version="1.0.0",
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializar adaptadores (Dependency Injection)
mongodb_adapter = MongoDBAdapter(
    connection_string=settings.mongodb_url,
    database_name=settings.mongodb_database,
)

redis_adapter = RedisAdapter(
    redis_url=settings.redis_url,
    ttl=settings.redis_ttl,
)

rabbitmq_adapter = RabbitMQAdapter(
    rabbitmq_url=settings.rabbitmq_url,
    transactions_queue=settings.rabbitmq_transactions_queue,
    manual_review_queue=settings.rabbitmq_manual_review_queue,
)

# Inicializar estrategias de fraude
fraud_strategies = [
    AmountThresholdStrategy(threshold=Decimal(str(settings.amount_threshold))),
    LocationStrategy(radius_km=settings.location_radius_km),
    # DeviceValidationStrategy se puede agregar cuando tengamos device_id en las transacciones
]


# Dependency Injection Factory para Use Cases
def get_evaluate_use_case() -> EvaluateTransactionUseCase:
    """Factory para crear EvaluateTransactionUseCase con sus dependencias"""
    return EvaluateTransactionUseCase(
        repository=mongodb_adapter,
        publisher=rabbitmq_adapter,
        cache=redis_adapter,
        strategies=fraud_strategies,
    )


def get_review_use_case() -> ReviewTransactionUseCase:
    """Factory para crear ReviewTransactionUseCase con sus dependencias"""
    return ReviewTransactionUseCase(repository=mongodb_adapter)


# ============================================================================
# ENDPOINTS
# ============================================================================

@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "fraud-evaluation-service",
        "version": "1.0.0",
    }


@app.post(
    "/api/v1/evaluate",
    response_model=EvaluationResponse,
    tags=["Fraud Evaluation"],
    summary="Evaluar transacción",
    description="Evalúa una transacción usando estrategias de detección de fraude",
)
async def evaluate_transaction(
    request: TransactionRequest,
    use_case: EvaluateTransactionUseCase = Depends(get_evaluate_use_case),
):
    """
    Evalúa una transacción y retorna el nivel de riesgo
    
    - **id**: ID único de la transacción
    - **amount**: Monto de la transacción
    - **user_id**: ID del usuario
    - **location**: Ubicación geográfica (lat, lon)
    - **timestamp**: Timestamp de la transacción (opcional)
    """
    try:
        # Convertir request a dict para el use case
        transaction_data = request.model_dump()
        
        # Ejecutar caso de uso
        result = await use_case.execute(transaction_data)
        
        return EvaluationResponse(**result)
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.post(
    "/api/v1/review/{transaction_id}",
    tags=["Manual Review"],
    summary="Revisar transacción manualmente",
    description="Permite a un analista aprobar o rechazar una transacción",
)
async def review_transaction(
    transaction_id: str,
    request: ReviewRequest,
    use_case: ReviewTransactionUseCase = Depends(get_review_use_case),
):
    """
    Aplica una decisión manual a una transacción
    
    - **transaction_id**: ID de la transacción a revisar
    - **decision**: APPROVED o REJECTED
    - **analyst_id**: ID del analista que toma la decisión
    """
    try:
        await use_case.execute(
            transaction_id=transaction_id,
            decision=request.decision,
            analyst_id=request.analyst_id,
        )
        
        return {"message": "Review applied successfully", "transaction_id": transaction_id}
    
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get(
    "/api/v1/evaluations",
    tags=["Fraud Evaluation"],
    summary="Obtener todas las evaluaciones",
    description="Retorna el historial de todas las evaluaciones de fraude",
)
async def get_all_evaluations(
    use_case: EvaluateTransactionUseCase = Depends(get_evaluate_use_case),
):
    """
    Obtiene todas las evaluaciones históricas
    """
    try:
        evaluations = await use_case.repository.get_all_evaluations()
        
        # Convertir a dict para serialización
        result = []
        for evaluation in evaluations:
            result.append({
                "transaction_id": evaluation.transaction_id,
                "user_id": evaluation.user_id,
                "risk_level": evaluation.risk_level.name,
                "reasons": evaluation.reasons,
                "status": evaluation.status,
                "timestamp": evaluation.timestamp.isoformat(),
                "amount": float(evaluation.amount) if evaluation.amount else None,
                "reviewed_by": evaluation.reviewed_by,
                "reviewed_at": evaluation.reviewed_at.isoformat() if evaluation.reviewed_at else None,
            })
        
        return {"evaluations": result, "total": len(result)}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get(
    "/api/v1/evaluations/{transaction_id}",
    tags=["Fraud Evaluation"],
    summary="Obtener evaluación específica",
    description="Retorna la evaluación de una transacción específica",
)
async def get_evaluation_by_id(
    transaction_id: str,
    use_case: EvaluateTransactionUseCase = Depends(get_evaluate_use_case),
):
    """
    Obtiene una evaluación específica por ID de transacción
    """
    try:
        evaluation = await use_case.repository.get_evaluation_by_id(transaction_id)
        
        if evaluation is None:
            raise HTTPException(status_code=404, detail=f"Transaction {transaction_id} not found")
        
        return {
            "transaction_id": evaluation.transaction_id,
            "user_id": evaluation.user_id,
            "risk_level": evaluation.risk_level.name,
            "reasons": evaluation.reasons,
            "status": evaluation.status,
            "timestamp": evaluation.timestamp.isoformat(),
            "amount": float(evaluation.amount) if evaluation.amount else None,
            "location": {
                "latitude": evaluation.location.latitude,
                "longitude": evaluation.location.longitude,
            } if evaluation.location else None,
            "reviewed_by": evaluation.reviewed_by,
            "reviewed_at": evaluation.reviewed_at.isoformat() if evaluation.reviewed_at else None,
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


# Startup event
@app.on_event("startup")
async def startup_event():
    """Inicializar conexiones al arrancar"""
    await redis_adapter.connect()
    rabbitmq_adapter.connect()
    print(f"✅ Fraud Evaluation Service started on port {settings.service_port}")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cerrar conexiones al apagar"""
    await redis_adapter.disconnect()
    rabbitmq_adapter.disconnect()
    print("✅ Fraud Evaluation Service shutdown complete")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=settings.service_port)
