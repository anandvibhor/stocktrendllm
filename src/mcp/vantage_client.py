# src/mcp/vantage_client.py
import requests
import json
from typing import Dict, Any, Optional
import asyncio
from ..models.schemas import StockRequest, StockDataPoint
from config import config
from ..utils.helpers import create_sample_data


class VantageMCPServer:
    def __init__(self):
        self.base_url = config.MCP_SERVER_URL
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {config.MCP_API_KEY}"
        }
        self.use_mock_data = config.MCP_SERVER_URL == "mock"

    async def get_stock_data(self, stock_request: StockRequest) -> Dict[str, Any]:
        """Fetch stock data from Vantage MCP server or use mock data"""
        if self.use_mock_data:
            # Use mock data for demonstration
            await asyncio.sleep(1)  # Simulate API delay
            return create_sample_data(stock_request.symbol, stock_request.period)

        try:
            payload = {
                "symbol": stock_request.symbol,
                "period": stock_request.period,
                "start_date": stock_request.start_date,
                "end_date": stock_request.end_date
            }

            response = requests.post(
                f"{self.base_url}/stock/data",
                headers=self.headers,
                json=payload,
                timeout=30
            )

            if response.status_code == 200:
                return response.json()
            else:
                # Fallback to mock data if API fails
                print(f"MCP Server error, using mock data: {response.status_code}")
                return create_sample_data(stock_request.symbol, stock_request.period)

        except requests.exceptions.RequestException as e:
            # Fallback to mock data
            print(f"MCP Server connection failed, using mock data: {str(e)}")
            return create_sample_data(stock_request.symbol, stock_request.period)

    async def get_technical_indicators(self, symbol: str, data: List[StockDataPoint]) -> Dict[str, Any]:
        """Get technical indicators for the stock"""
        if self.use_mock_data:
            return {
                "rsi": 45.6,
                "macd": 1.2,
                "moving_averages": {
                    "sma_20": sum([point.close for point in data[-20:]]) / 20 if len(data) >= 20 else 0,
                    "sma_50": sum([point.close for point in data[-50:]]) / 50 if len(data) >= 50 else 0
                }
            }

        try:
            payload = {
                "symbol": symbol,
                "data": [point.dict() for point in data]
            }

            response = requests.post(
                f"{self.base_url}/technical/indicators",
                headers=self.headers,
                json=payload,
                timeout=30
            )

            if response.status_code == 200:
                return response.json()
            else:
                return {}

        except:
            return {}


vantage_client = VantageMCPServer()