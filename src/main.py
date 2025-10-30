# src/main.py
import asyncio
import json
from typing import Dict, Any
from .models.schemas import StockRequest, TimePeriod
from .graph.stock_analysis_graph import stock_analysis_graph
from .utils.helpers import format_analysis_output


class StockAnalysisApp:
    def __init__(self):
        self.graph = stock_analysis_graph.compile()

    async def analyze_stock(self, symbol: str, period: str = "1y",
                            start_date: str = None, end_date: str = None) -> Dict[str, Any]:
        """Main method to analyze stock"""
        try:
            # Create stock request
            stock_request = StockRequest(
                symbol=symbol.upper(),
                period=TimePeriod(period),
                start_date=start_date,
                end_date=end_date
            )

            # Initialize state
            initial_state = {
                "stock_request": stock_request,
                "raw_data": None,
                "processed_data": None,
                "analysis_result": None,
                "error": None
            }

            # Execute the graph
            result = await self.graph.ainvoke(initial_state)

            return result

        except Exception as e:
            return {"error": f"Analysis failed: {str(e)}"}

    def format_output(self, result: Dict[str, Any]) -> str:
        """Format the analysis result for display"""
        return format_analysis_output(result)