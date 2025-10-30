# app.py
import streamlit as st
import asyncio
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import nest_asyncio

# Apply nest_asyncio for async support in Streamlit
nest_asyncio.apply()

from src.models.schemas import StockRequest, TimePeriod
from src.main import StockAnalysisApp
from src.utils.helpers import format_analysis_output

# Configure page
st.set_page_config(
    page_title="Stock Trend Analyzer",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stock-card {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .positive-change {
        color: #00aa00;
        font-weight: bold;
    }
    .negative-change {
        color: #ff0000;
        font-weight: bold;
    }
    .analysis-section {
        background-color: white;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)


class StreamlitStockApp:
    def __init__(self):
        self.app = StockAnalysisApp()

    def setup_sidebar(self):
        """Setup the sidebar for user input"""
        st.sidebar.title("📊 Stock Analysis Configuration")

        # Stock symbol input
        symbol = st.sidebar.text_input(
            "Stock Symbol",
            value="AMZN",
            placeholder="e.g., AMZN, AAPL, GOOGL",
            help="Enter the stock ticker symbol"
        ).upper()

        # Analysis period
        period_options = {
            "1 Day": "1d",
            "1 Week": "1w",
            "1 Month": "1m",
            "3 Months": "3m",
            "6 Months": "6m",
            "1 Year": "1y",
            "2 Years": "2y",
            "5 Years": "5y"
        }

        selected_period = st.sidebar.selectbox(
            "Analysis Period",
            options=list(period_options.keys()),
            index=5  # Default to 1 Year
        )
        period = period_options[selected_period]

        # Custom date range option
        use_custom_dates = st.sidebar.checkbox("Use Custom Date Range")

        start_date = None
        end_date = None

        if use_custom_dates:
            col1, col2 = st.sidebar.columns(2)
            with col1:
                start_date = st.date_input(
                    "Start Date",
                    value=datetime.now() - timedelta(days=365),
                    max_value=datetime.now()
                )
            with col2:
                end_date = st.date_input(
                    "End Date",
                    value=datetime.now(),
                    max_value=datetime.now()
                )

            if start_date and end_date:
                if start_date >= end_date:
                    st.sidebar.error("Start date must be before end date")
                    return None, None, None, None

        # Analysis options
        st.sidebar.markdown("---")
        st.sidebar.subheader("Analysis Options")

        show_technical = st.sidebar.checkbox("Show Technical Indicators", value=True)
        show_volume = st.sidebar.checkbox("Show Volume Analysis", value=True)
        detailed_analysis = st.sidebar.checkbox("Detailed Trend Analysis", value=True)

        return symbol, period, start_date, end_date, show_technical, show_volume, detailed_analysis

    def create_price_chart(self, analysis_result):
        """Create interactive price chart"""
        if not analysis_result or not analysis_result.data_points:
            return None

        df = pd.DataFrame([point.dict() for point in analysis_result.data_points])
        df['date'] = pd.to_datetime(df['date'])

        # Create candlestick chart
        fig = go.Figure()

        # Candlestick
        fig.add_trace(go.Candlestick(
            x=df['date'],
            open=df['open'],
            high=df['high'],
            low=df['low'],
            close=df['close'],
            name='Price'
        ))

        fig.update_layout(
            title=f"{analysis_result.symbol} Stock Price - {analysis_result.period}",
            xaxis_title="Date",
            yaxis_title="Price ($)",
            height=500,
            showlegend=True
        )

        return fig

    def create_volume_chart(self, analysis_result):
        """Create volume analysis chart"""
        if not analysis_result or not analysis_result.data_points:
            return None

        df = pd.DataFrame([point.dict() for point in analysis_result.data_points])
        df['date'] = pd.to_datetime(df['date'])

        fig = px.bar(
            df,
            x='date',
            y='volume',
            title=f"{analysis_result.symbol} Trading Volume"
        )

        fig.update_layout(
            xaxis_title="Date",
            yaxis_title="Volume",
            height=300
        )

        return fig

    def create_performance_metrics(self, analysis_result):
        """Create performance metrics cards"""
        if not analysis_result or not analysis_result.statistics:
            return

        stats = analysis_result.statistics
        trends = analysis_result.trends

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            delta_color = "normal"
            if stats.get('percent_change', 0) > 0:
                delta_color = "normal"
            else:
                delta_color = "inverse"

            st.metric(
                label="Current Price",
                value=f"${stats.get('current_price', 0):.2f}",
                delta=f"{stats.get('percent_change', 0):.2f}%",
                delta_color=delta_color
            )

        with col2:
            st.metric(
                label="Period High",
                value=f"${stats.get('period_high', 0):.2f}"
            )

        with col3:
            st.metric(
                label="Period Low",
                value=f"${stats.get('period_low', 0):.2f}"
            )

        with col4:
            st.metric(
                label="Avg Volume",
                value=f"{stats.get('avg_volume', 0):,.0f}"
            )

    def display_trend_analysis(self, analysis_result, detailed=True):
        """Display trend analysis results"""
        if not analysis_result or not analysis_result.trends:
            return

        trends = analysis_result.trends

        st.markdown("### 📈 Trend Analysis")

        # Quick overview
        col1, col2 = st.columns(2)

        with col1:
            trend_direction = trends.get('trend_direction', 'unknown')
            trend_color = "🟢" if trend_direction == "bullish" else "🔴" if trend_direction == "bearish" else "⚪"
            st.markdown(f"**Trend Direction:** {trend_color} {trend_direction.upper()}")

        with col2:
            volatility = trends.get('volatility', 'unknown')
            st.markdown(f"**Volatility:** {volatility.upper()}")

        # Detailed analysis
        if detailed and trends.get('analysis'):
            with st.expander("Detailed Trend Analysis", expanded=True):
                st.markdown(trends['analysis'])

    def display_raw_data(self, analysis_result):
        """Display raw data in expandable section"""
        if not analysis_result or not analysis_result.data_points:
            return

        with st.expander("View Raw Data"):
            df = pd.DataFrame([point.dict() for point in analysis_result.data_points])
            st.dataframe(df, use_container_width=True)

            # Download option
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"{analysis_result.symbol}_{analysis_result.period}_data.csv",
                mime="text/csv"
            )

    async def run_analysis(self, symbol, period, start_date, end_date):
        """Run the stock analysis"""
        try:
            with st.spinner(f"Analyzing {symbol} for {period} period..."):
                result = await self.app.analyze_stock(
                    symbol=symbol,
                    period=period,
                    start_date=start_date.isoformat() if start_date else None,
                    end_date=end_date.isoformat() if end_date else None
                )
            return result
        except Exception as e:
            st.error(f"Analysis failed: {str(e)}")
            return None

    def run(self):
        """Main Streamlit application runner"""
        # Header
        st.markdown('<h1 class="main-header">📈 AI Stock Trend Analyzer</h1>', unsafe_allow_html=True)
        st.markdown("Analyze stock trends using AI-powered analysis with MCP Server integration")

        # Setup sidebar
        (symbol, period, start_date, end_date,
         show_technical, show_volume, detailed_analysis) = self.setup_sidebar()

        # Analysis button
        if st.sidebar.button("🚀 Analyze Stock", type="primary", use_container_width=True):
            if symbol:
                # Run analysis
                result = asyncio.run(self.run_analysis(symbol, period, start_date, end_date))

                if result and not result.get('error'):
                    analysis_result = result.get('analysis_result')

                    if analysis_result:
                        # Display results
                        st.markdown("---")

                        # Performance metrics
                        self.create_performance_metrics(analysis_result)

                        # Charts
                        col1, col2 = st.columns([2, 1])

                        with col1:
                            price_chart = self.create_price_chart(analysis_result)
                            if price_chart:
                                st.plotly_chart(price_chart, use_container_width=True)

                        with col2:
                            # Additional metrics
                            st.markdown("### 📊 Key Statistics")
                            stats = analysis_result.statistics

                            st.markdown(f"""
                            - **Data Points:** {stats.get('data_points', 0)}
                            - **Price Change:** ${stats.get('price_change', 0):.2f}
                            - **Percent Change:** {stats.get('percent_change', 0):.2f}%
                            - **Price Range:** ${stats.get('period_low', 0):.2f} - ${stats.get('period_high', 0):.2f}
                            """)

                        # Volume chart
                        if show_volume:
                            volume_chart = self.create_volume_chart(analysis_result)
                            if volume_chart:
                                st.plotly_chart(volume_chart, use_container_width=True)

                        # Trend analysis
                        self.display_trend_analysis(analysis_result, detailed_analysis)

                        # Raw data
                        self.display_raw_data(analysis_result)

                    else:
                        st.error("No analysis results available")
                else:
                    error_msg = result.get('error', 'Unknown error occurred') if result else 'Analysis failed'
                    st.error(f"Analysis failed: {error_msg}")
            else:
                st.error("Please enter a stock symbol")

        # Sample analysis section
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 💡 Quick Analysis")

        sample_col1, sample_col2 = st.sidebar.columns(2)

        with sample_col1:
            if st.button("Analyze AMZN"):
                st.session_state.quick_symbol = "AMZN"

        with sample_col2:
            if st.button("Analyze AAPL"):
                st.session_state.quick_symbol = "AAPL"

        # Instructions
        with st.expander("ℹ️ How to use this app"):
            st.markdown("""
            ### Getting Started

            1. **Enter Stock Symbol**: Input a valid stock ticker symbol (e.g., AMZN, AAPL, GOOGL)
            2. **Select Period**: Choose analysis timeframe or enable custom date range
            3. **Configure Options**: Toggle technical indicators and analysis depth
            4. **Run Analysis**: Click 'Analyze Stock' to generate insights

            ### Features

            - **Interactive Charts**: Candlestick price charts with volume analysis
            - **AI-Powered Insights**: GPT-4 powered trend analysis and recommendations
            - **Technical Metrics**: Key performance indicators and statistics
            - **Export Data**: Download analysis results as CSV

            ### Data Sources

            This app uses MCP Server integration with Vantage for real-time stock data and AI analysis for trend insights.
            """)


# Initialize and run the app
if __name__ == "__main__":
    app = StreamlitStockApp()
    app.run()