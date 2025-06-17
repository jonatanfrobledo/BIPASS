from typing import Any, Dict, Optional
from fastapi import HTTPException, status
from pydantic import BaseModel

class ProblemDetail(BaseModel):
    """Implementación del estándar RFC 9457 para detalles de problemas."""
    type: str
    title: str
    status: int
    detail: str
    instance: Optional[str] = None
    additional_data: Optional[Dict[str, Any]] = None

class APIException(HTTPException):
    """Excepción base para errores de la API."""
    def __init__(
        self,
        status_code: int,
        detail: str,
        type: str = "about:blank",
        title: Optional[str] = None,
        instance: Optional[str] = None,
        additional_data: Optional[Dict[str, Any]] = None
    ):
        self.problem_detail = ProblemDetail(
            type=type,
            title=title or self._get_default_title(status_code),
            status=status_code,
            detail=detail,
            instance=instance,
            additional_data=additional_data
        )
        super().__init__(status_code=status_code, detail=self.problem_detail.dict())

    @staticmethod
    def _get_default_title(status_code: int) -> str:
        """Obtiene el título por defecto según el código de estado."""
        return {
            status.HTTP_400_BAD_REQUEST: "Bad Request",
            status.HTTP_401_UNAUTHORIZED: "Unauthorized",
            status.HTTP_403_FORBIDDEN: "Forbidden",
            status.HTTP_404_NOT_FOUND: "Not Found",
            status.HTTP_409_CONFLICT: "Conflict",
            status.HTTP_422_UNPROCESSABLE_ENTITY: "Unprocessable Entity",
            status.HTTP_500_INTERNAL_SERVER_ERROR: "Internal Server Error"
        }.get(status_code, "Unknown Error")

class ResourceNotFoundException(APIException):
    """Excepción para recursos no encontrados."""
    def __init__(self, resource_type: str, resource_id: Any):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            type="https://api.bipass.com/errors/resource-not-found",
            title="Resource Not Found",
            detail=f"{resource_type} with id {resource_id} not found",
            additional_data={"resource_type": resource_type, "resource_id": resource_id}
        )

class ValidationException(APIException):
    """Excepción para errores de validación."""
    def __init__(self, detail: str, errors: Dict[str, Any]):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            type="https://api.bipass.com/errors/validation-error",
            title="Validation Error",
            detail=detail,
            additional_data={"errors": errors}
        )

class AuthenticationException(APIException):
    """Excepción para errores de autenticación."""
    def __init__(self, detail: str = "Invalid authentication credentials"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            type="https://api.bipass.com/errors/authentication-error",
            title="Authentication Error",
            detail=detail
        )

class AuthorizationException(APIException):
    """Excepción para errores de autorización."""
    def __init__(self, detail: str = "Not enough permissions"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            type="https://api.bipass.com/errors/authorization-error",
            title="Authorization Error",
            detail=detail
        ) 