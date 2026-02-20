"""Utilitaires API (gestion d'erreurs, etc.)."""
from typing import Callable, TypeVar

from fastapi import HTTPException

T = TypeVar("T")


def handle_service_errors(func: Callable[[], T]) -> T:
    """Exécute une fonction et convertit les erreurs de service en HTTPException.
    
    ValueError -> 400
    RuntimeError -> 503
    """
    try:
        return func()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e
