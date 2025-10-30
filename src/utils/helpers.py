# src/utils/helpers.py
from typing import Dict, Any
import pandas as pd
from ..models.schemas import StockAnalysis


def format_analysis_output(result: Dict[str, Any]) -> str:
    """Format the analysis result into a readable string"""
    if result.get("error"):
        return f"Error: {result['error']}"

    analysis: StockAnalysis = result.get("analysis_result")
    if not analysis:
        return "No analysis result available"

    stats = analysis.statistics
    trends = analysis.trends

    output = [
        f"📊 STOCK ANALYSIS REPORT",
        f"Symbol: {analysis.symbol}",
        f"Period: {analysis.period}",
        f"Data Points: {analysis.summary.get('total_data_points', 0)}",
        "",
        "📈 PRICE SUMMARY",
        f"Current Price: ${stats.get('current_price', 0):.2f}",
        f"Price Change: ${stats.get('price_change', 0):.2f} ({stats.get('percent_change', 0):.2f}%)",
        f"Period High: ${stats.get('period_high', 0):.2f}",
        f"Period Low: ${stats.get('period_low', 0):.2f}",
        f"Average Volume: {stats.get('avg_volume', 0):,.0f}",
        "",
        "📊 TREND ANALYSIS",
        f"Trend Direction: {trends.get('trend_direction', 'unknown').upper()}",
        f"Volatility: {trends.get('volatility', 'unknown').upper()}",
        "",
        "🔍 DETAILED ANALYSIS",
        trends.get('analysis', 'No detailed analysis available')
    ]

    return "\n".join(output)


def create_sample_data(symbol="AMZN", period="1y"):
    """Create sample data for demonstration"""
    import random
    from datetime import datetime, timedelta

    base_price = 100 + random.randint(-20, 20)
    data_points = []
    current_date = datetime.now() - timedelta(days=365)

    for i in range(250):  # Approx 1 year of trading days
        date = current_date + timedelta(days=i)
        if date.weekday() < 5:  # Only weekdays
            open_price = base_price + random.uniform(-2, 2)
            close_price = open_price + random.uniform(-5, 5)
            high_price = max(open_price, close_price) + random.uniform(0, 3)
            low_price = min(open_price, close_price) - random.uniform(0, 3)
            volume = random.randint(1000000, 5000000)

            data_points.append({
                "date": date.strftime("%Y-%m-%d"),
                "open": round(open_price, 2),
                "high": round(high_price, 2),
                "low": round(low_price, 2),
                "close": round(close_price, 2),
                "volume": volume,
                "adjusted_close": round(close_price, 2)
            })

    return {
        "symbol": symbol,
        "period": period,
        "data": data_points
    }