from fastapi import APIRouter, Depends

from api.deps import verify_auth
from semantic.store import list_dimensions, list_metrics

router = APIRouter()


@router.get("/metrics", dependencies=[Depends(verify_auth)])
def metrics():
    return [metric.__dict__ for metric in list_metrics()]


@router.get("/dimensions", dependencies=[Depends(verify_auth)])
def dimensions():
    return [dimension.__dict__ for dimension in list_dimensions()]


@router.get("/catalog", dependencies=[Depends(verify_auth)])
def catalog():
    return {
        "metrics": [metric.__dict__ for metric in list_metrics()],
        "dimensions": [dimension.__dict__ for dimension in list_dimensions()],
    }
