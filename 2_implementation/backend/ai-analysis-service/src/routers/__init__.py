"""
AI Analysis Service Routers

This module contains all API routes for the AI analysis service.
"""

from .weakness_analysis import router as weakness_analysis_router
from .learning_recommendation import router as learning_recommendation_router
from .trend_analysis import router as trend_analysis_router
from .vector_search import router as vector_search_router

__all__ = [
    "weakness_analysis_router",
    "learning_recommendation_router",
    "trend_analysis_router",
    "vector_search_router"
] 