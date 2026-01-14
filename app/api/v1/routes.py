from fastapi import APIRouter, HTTPException
from app.api.v1.schemas import OptimizeRequest, OptimizeResponse
from app.services.load_optimizer import optimize_load
from app.core.exceptions import ValidationError

router = APIRouter()

@router.post("/load-optimizer/optimize", response_model=OptimizeResponse)
def optimize(request: OptimizeRequest):
    try:
        return optimize_load(request)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
