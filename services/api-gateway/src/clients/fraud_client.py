"""
HTTP Client para Fraud Evaluation Service

Maneja la comunicación entre api-gateway y fraud-evaluation-service
"""
import httpx
from typing import Dict, Any, Optional


class FraudEvaluationClient:
    """Cliente HTTP para comunicarse con fraud-evaluation-service"""
    
    def __init__(self, base_url: str = "http://fraud-evaluation-service:8001"):
        """
        Inicializa el cliente
        
        Args:
            base_url: URL base del servicio de evaluación
        """
        self.base_url = base_url
        self.client = httpx.AsyncClient(base_url=base_url, timeout=30.0)
    
    async def evaluate_transaction(self, transaction_data: dict) -> Dict[str, Any]:
        """
        Evalúa una transacción llamando al servicio de evaluación
        
        Args:
            transaction_data: Datos de la transacción
        
        Returns:
            Dict con resultado de la evaluación
        
        Raises:
            httpx.HTTPError: Si falla la comunicación
        """
        try:
            response = await self.client.post(
                "/api/v1/evaluate",
                json=transaction_data,
                timeout=30.0,
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            # Manejar errores de comunicación
            raise Exception(f"Error calling fraud evaluation service: {str(e)}")
    
    async def get_evaluation_by_id(self, transaction_id: str) -> Dict[str, Any]:
        """
        Obtiene una evaluación específica por ID
        
        Args:
            transaction_id: ID de la transacción
        
        Returns:
            Dict con la evaluación
        
        Raises:
            httpx.HTTPError: Si falla la comunicación
        """
        try:
            response = await self.client.get(
                f"/api/v1/evaluations/{transaction_id}",
                timeout=10.0,
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            raise Exception(f"Error getting evaluation: {str(e)}")
    
    async def get_all_evaluations(self) -> Dict[str, Any]:
        """
        Obtiene todas las evaluaciones
        
        Returns:
            Dict con lista de evaluaciones
        
        Raises:
            httpx.HTTPError: Si falla la comunicación
        """
        try:
            response = await self.client.get(
                "/api/v1/evaluations",
                timeout=15.0,
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            raise Exception(f"Error getting evaluations: {str(e)}")
    
    async def review_transaction(
        self,
        transaction_id: str,
        decision: str,
        analyst_id: str,
    ) -> Dict[str, Any]:
        """
        Aplica una decisión manual a una transacción
        
        Args:
            transaction_id: ID de la transacción
            decision: APPROVED o REJECTED
            analyst_id: ID del analista
        
        Returns:
            Dict con confirmación
        
        Raises:
            httpx.HTTPError: Si falla la comunicación
        """
        try:
            response = await self.client.post(
                f"/api/v1/review/{transaction_id}",
                json={"decision": decision, "analyst_id": analyst_id},
                timeout=10.0,
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            raise Exception(f"Error reviewing transaction: {str(e)}")
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Verifica el estado del servicio de evaluación
        
        Returns:
            Dict con estado del servicio
        """
        try:
            response = await self.client.get("/health", timeout=5.0)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError:
            return {"status": "unhealthy"}
    
    async def close(self) -> None:
        """Cierra el cliente HTTP"""
        await self.client.aclose()


# Instancia global del cliente
fraud_client = FraudEvaluationClient()
