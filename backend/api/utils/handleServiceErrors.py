import logging
from typing import Callable, TypeVar
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)

T = TypeVar("T")


def handle_service_errors(func: Callable[[], T]) -> T | JSONResponse:
    try:
        return func()
    except ValueError as e:
        logger.warning("Erreur de validation: %s", e)
        return JSONResponse(status_code=400, content={"detail": str(e)})
    except FileNotFoundError as e:
        logger.warning("Ressource introuvable: %s", e)
        return JSONResponse(status_code=404, content={"detail": str(e)})
    except Exception as e:
        logger.exception("Erreur inattendue: %s", e)
        return JSONResponse(status_code=500, content={"detail": "Erreur interne"})
