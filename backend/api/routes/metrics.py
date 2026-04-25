from fastapi import APIRouter
from services.metrics_service import (
    get_summary,
    get_by_class,
    get_tokens_by_day,
    get_latency,
    get_cost
)

router = APIRouter(prefix="/metrics", tags=["Metrics"])


@router.get("/summary")
def summary():
    return get_summary()


@router.get("/by-class")
def by_class():
    return get_by_class()


@router.get("/tokens-by-day")
def tokens_by_day():
    return get_tokens_by_day()


@router.get("/latency")
def latency():
    return get_latency()


@router.get("/cost")
def cost():
    return get_cost()