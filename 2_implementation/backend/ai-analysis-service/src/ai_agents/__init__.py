"""
AI Analysis Service Agents

This module contains CrewAI agents for learning analysis and recommendations.
"""

from .analyst_agent import AnalystAgent
from .tutor_agent import TutorAgent
from .recommender_agent import RecommenderAgent
from .trend_analyzer_agent import TrendAnalyzerAgent

__all__ = [
    "AnalystAgent",
    "TutorAgent", 
    "RecommenderAgent",
    "TrendAnalyzerAgent"
] 