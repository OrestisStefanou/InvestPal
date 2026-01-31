from enum import Enum
from typing import List, Union, Optional, Any, Dict
from pydantic import BaseModel, Field
import uuid


# ============================================================================
# ENUMS
# ============================================================================

class ComponentType(str, Enum):
    """Available UI component types for the investment advisor interface."""
    TEXT = "text"
    SECURITY_CARD = "security_card"
    METRICS_GRID = "metrics_grid"
    PORTFOLIO_HOLDINGS = "portfolio_holdings"
    SECTOR_PERFORMANCE = "sector_performance"
    ASSET_PERFORMANCE = "asset_performance"
    NEWS_FEED = "news_feed"
    COMPARISON_TABLE = "comparison_table"
    FINANCIAL_STATEMENT = "financial_statement"
    INVESTMENT_CALCULATOR = "investment_calculator"
    ALLOCATION_CHART = "allocation_chart"
    ECONOMIC_INDICATOR = "economic_indicator"
    ALERT = "alert"
    INSIGHTS = "insights"
    ACTION_SUGGESTIONS = "action_suggestions"


class TextFormat(str, Enum):
    """Text formatting options."""
    PLAIN = "plain"
    MARKDOWN = "markdown"


class AssetType(str, Enum):
    """Types of financial assets/securities."""
    STOCK = "stock"
    ETF = "etf"
    CRYPTO = "crypto"
    COMMODITY = "commodity"
    INDEX = "index"


class MetricFormat(str, Enum):
    """Formatting options for displaying metric values."""
    CURRENCY = "currency"
    PERCENTAGE = "percentage"
    NUMBER = "number"
    RATIO = "ratio"
    DATE = "date"


class ChartType(str, Enum):
    """Chart visualization types."""
    LINE = "line"
    AREA = "area"
    BAR = "bar"
    CANDLESTICK = "candlestick"
    PIE = "pie"
    DONUT = "donut"
    TREEMAP = "treemap"
    HEATMAP = "heatmap"


class SectorVisualization(str, Enum):
    """Visualization options for sector performance."""
    HEATMAP = "heatmap"
    BAR = "bar"
    TABLE = "table"


class ComparisonType(str, Enum):
    """Types of entity comparisons."""
    STOCKS = "stocks"
    ETFS = "etfs"
    SECTORS = "sectors"
    CRYPTOS = "cryptos"
    INVESTORS = "investors"


class FinancialStatementType(str, Enum):
    """Types of financial statements."""
    INCOME_STATEMENT = "income_statement"
    BALANCE_SHEET = "balance_sheet"
    CASH_FLOW = "cash_flow"


class AllocationType(str, Enum):
    """Types of portfolio/asset allocations."""
    SECTOR = "sector"
    ASSET_CLASS = "asset_class"
    GEOGRAPHY = "geography"
    HOLDINGS = "holdings"
    MARKET_CAP = "market_cap"


class AlertSeverity(str, Enum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    SUCCESS = "success"
    ERROR = "error"


class TrendDirection(str, Enum):
    """Trend direction indicators."""
    UP = "up"
    DOWN = "down"
    STABLE = "stable"


class SentimentType(str, Enum):
    """Sentiment classification for news and analysis."""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"


# ============================================================================
# BASE COMPONENT
# ============================================================================

class UIComponent(BaseModel):
    """Base class for all UI components."""
    type: ComponentType
    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique identifier for the component"
    )
    title: Optional[str] = Field(
        None,
        description="Optional title to display above the component"
    )
    loading: bool = Field(
        False,
        description="Indicates if the component is in a loading state"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        None,
        description="Additional metadata for extensibility"
    )


# ============================================================================
# TEXT COMPONENTS
# ============================================================================

class TextComponent(UIComponent):
    """Simple text/message component for explanations and narratives."""
    type: ComponentType = ComponentType.TEXT
    content: str = Field(
        ...,
        description="The text content to display"
    )
    format: TextFormat = Field(
        TextFormat.PLAIN,
        description="Text formatting type"
    )


class InsightComponent(UIComponent):
    """Component for displaying key insights and summary information."""
    type: ComponentType = ComponentType.INSIGHTS
    headline: str = Field(
        ...,
        description="Main headline or summary statement"
    )
    insights: List[str] = Field(
        ...,
        description="List of key insight bullet points"
    )
    context: Optional[str] = Field(
        None,
        description="Additional context or explanation"
    )


class AlertComponent(UIComponent):
    """Alert/notification banner for important information."""
    type: ComponentType = ComponentType.ALERT
    message: str = Field(
        ...,
        description="Alert message content"
    )
    severity: AlertSeverity = Field(
        AlertSeverity.INFO,
        description="Severity level of the alert"
    )
    actionable: bool = Field(
        False,
        description="Whether the alert has an associated action"
    )
    action_label: Optional[str] = Field(
        None,
        description="Label for the action button"
    )
    action_payload: Optional[Dict[str, Any]] = Field(
        None,
        description="Data payload for the action"
    )


# ============================================================================
# SECURITY/ASSET CARDS
# ============================================================================

class SecurityCardComponent(UIComponent):
    """Card displaying key information about a security (stock, ETF, etc.)."""
    type: ComponentType = ComponentType.SECURITY_CARD
    symbol: str = Field(
        ...,
        description="Trading symbol/ticker"
    )
    name: str = Field(
        ...,
        description="Full name of the security"
    )
    description: Optional[str] = Field(
        None,
        description="Description of the security"
    )
    price: float = Field(
        ...,
        description="Current price"
    )
    market_cap: Optional[float] = Field(
        None,
        description="Market capitalization"
    )
    sector: Optional[str] = Field(
        None,
        description="Sector the security belongs to"
    )
    industry: Optional[str] = Field(
        None,
        description="Industry the security belongs to"
    )
    asset_type: AssetType = Field(
        AssetType.STOCK,
        description="Type of asset"
    )


# ============================================================================
# METRICS & GRIDS
# ============================================================================

class MetricItem(BaseModel):
    """Individual metric item for display in a grid."""
    label: str = Field(
        ...,
        description="Display label for the metric"
    )
    value: Union[str, float] = Field(
        ...,
        description="The metric value"
    )
    change: Optional[float] = Field(
        None,
        description="Change value (can represent delta or percentage)"
    )
    format: Optional[MetricFormat] = Field(
        None,
        description="Formatting hint for displaying the value"
    )


class AssetPerformanceItem(BaseModel):
    """Performance data for an asset over a specific period."""
    period: str = Field(
        ...,
        description="Time period (e.g., '1D', '1M', '1Y', 'YTD')"
    )
    performance: float = Field(
        ...,
        description="Percentage return for the period"
    )


class MetricsGridComponent(UIComponent):
    """Grid layout for displaying multiple financial metrics."""
    type: ComponentType = ComponentType.METRICS_GRID
    metrics: List[MetricItem] = Field(
        ...,
        description="List of metrics to display"
    )
    columns: int = Field(
        2,
        description="Number of columns in the grid layout",
        ge=1,
        le=4
    )


class EconomicIndicatorComponent(UIComponent):
    """Component for displaying economic indicator data."""
    type: ComponentType = ComponentType.ECONOMIC_INDICATOR
    indicator_name: str = Field(
        ...,
        description="Name of the economic indicator (e.g., GDP, CPI)"
    )
    current_value: float = Field(
        ...,
        description="Current/latest value of the indicator"
    )
    previous_value: Optional[float] = Field(
        None,
        description="Previous period value for comparison"
    )
    change: Optional[float] = Field(
        None,
        description="Change from previous value"
    )
    as_of_date: str = Field(
        ...,
        description="Date of the current value (ISO format)"
    )
    trend: Optional[TrendDirection] = Field(
        None,
        description="Overall trend direction"
    )
    chart_data: Optional[List[Dict[str, Any]]] = Field(
        None,
        description="Historical time series data for visualization"
    )


# ============================================================================
# TABLES & HOLDINGS
# ============================================================================

class HoldingRow(BaseModel):
    """Individual holding/position in a portfolio."""
    symbol: str = Field(
        ...,
        description="Security symbol"
    )
    name: str = Field(
        ...,
        description="Security name"
    )
    shares: Optional[float] = Field(
        None,
        description="Number of shares held"
    )
    weight: float = Field(
        ...,
        description="Portfolio weight as a percentage"
    )
    value: Optional[float] = Field(
        None,
        description="Total value of the holding"
    )
    sector: Optional[str] = Field(
        None,
        description="Sector classification"
    )


class PortfolioHoldingsComponent(UIComponent):
    """Table displaying portfolio holdings."""
    type: ComponentType = ComponentType.PORTFOLIO_HOLDINGS
    holdings: List[HoldingRow] = Field(
        ...,
        description="List of portfolio holdings"
    )
    total_value: Optional[float] = Field(
        None,
        description="Total portfolio value"
    )
    as_of_date: Optional[str] = Field(
        None,
        description="Date the holdings data is from (ISO format)"
    )


class ComparisonRow(BaseModel):
    """Row in a comparison table showing a metric across entities."""
    metric: str = Field(
        ...,
        description="Name of the metric being compared"
    )
    values: Dict[str, Any] = Field(
        ...,
        description="Map of entity name/symbol to metric value"
    )
    format: Optional[MetricFormat] = Field(
        None,
        description="Formatting hint for the values"
    )


class ComparisonTableComponent(UIComponent):
    """Table for comparing multiple entities side-by-side."""
    type: ComponentType = ComponentType.COMPARISON_TABLE
    entities: List[str] = Field(
        ...,
        description="List of entity names/symbols being compared (column headers)"
    )
    rows: List[ComparisonRow] = Field(
        ...,
        description="Comparison metrics rows"
    )
    comparison_type: ComparisonType = Field(
        ComparisonType.STOCKS,
        description="Type of comparison being performed"
    )


class SectorPerformanceItem(BaseModel):
    """Performance data for a market sector."""
    sector: str = Field(
        ...,
        description="Sector name"
    )
    performance_data: List[AssetPerformanceItem] = Field(
        ...,
        description="List of performance returns for different periods"
    )


class SectorPerformanceComponent(UIComponent):
    """Component displaying sector performance data."""
    type: ComponentType = ComponentType.SECTOR_PERFORMANCE
    sectors: List[SectorPerformanceItem] = Field(
        ...,
        description="List of sectors with performance data"
    )
    visualization: SectorVisualization = Field(
        SectorVisualization.HEATMAP,
        description="Preferred visualization type"
    )


# ============================================================================
# FINANCIAL STATEMENTS
# ============================================================================

class FinancialStatementRow(BaseModel):
    """Row in a financial statement."""
    line_item: str = Field(
        ...,
        description="Name of the line item (e.g., 'Revenue', 'Net Income')"
    )
    values: Dict[str, float] = Field(
        ...,
        description="Map of period (e.g., '2024', '2023') to value"
    )
    category: Optional[str] = Field(
        None,
        description="Category for grouping rows (e.g., 'Operating Expenses')"
    )


class FinancialStatementComponent(UIComponent):
    """Component for displaying financial statements."""
    type: ComponentType = ComponentType.FINANCIAL_STATEMENT
    statement_type: FinancialStatementType = Field(
        ...,
        description="Type of financial statement"
    )
    periods: List[str] = Field(
        ...,
        description="List of time periods (e.g., ['2024', '2023', '2022'])"
    )
    rows: List[FinancialStatementRow] = Field(
        ...,
        description="Financial statement line items"
    )
    currency: str = Field(
        "USD",
        description="Currency code for the values"
    )


# ============================================================================
# CHARTS & VISUALIZATIONS
# ============================================================================




class AssetPerformanceComponent(UIComponent):
    """Component for displaying asset performance across different time periods."""
    type: ComponentType = ComponentType.ASSET_PERFORMANCE
    symbol: str = Field(
        ...,
        description="Asset symbol"
    )
    name: str = Field(
        ...,
        description="Asset name"
    )
    current_price: float = Field(
        ...,
        description="Current price of the asset"
    )
    performance_data: List[AssetPerformanceItem] = Field(
        ...,
        description="List of performance returns for different periods"
    )
    last_updated: str = Field(
        ...,
        description="Timestamp of the last data update"
    )


class AllocationItem(BaseModel):
    """Item in an allocation breakdown."""
    label: str = Field(
        ...,
        description="Label for the allocation category"
    )
    value: float = Field(
        ...,
        description="Absolute value of the allocation"
    )
    percentage: float = Field(
        ...,
        description="Percentage of total"
    )
    color: Optional[str] = Field(
        None,
        description="Hex color code for visualization"
    )


class AllocationChartComponent(UIComponent):
    """Chart showing allocation/distribution breakdown."""
    type: ComponentType = ComponentType.ALLOCATION_CHART
    allocations: List[AllocationItem] = Field(
        ...,
        description="List of allocation items"
    )
    chart_type: ChartType = Field(
        ChartType.PIE,
        description="Type of chart (pie, donut, treemap)"
    )
    allocation_type: AllocationType = Field(
        ...,
        description="What type of allocation is being shown"
    )
    total_value: Optional[float] = Field(
        None,
        description="Total value being allocated"
    )


# ============================================================================
# NEWS & CONTENT
# ============================================================================

class NewsItem(BaseModel):
    """Individual news article/item."""
    title: str = Field(
        ...,
        description="Article headline"
    )
    source: str = Field(
        ...,
        description="News source/publisher"
    )
    published_at: str = Field(
        ...,
        description="Publication date/time (ISO format)"
    )
    url: Optional[str] = Field(
        None,
        description="URL to the full article"
    )
    summary: Optional[str] = Field(
        None,
        description="Brief summary or excerpt"
    )
    sentiment: Optional[SentimentType] = Field(
        None,
        description="Sentiment classification of the article"
    )
    image_url: Optional[str] = Field(
        None,
        description="URL to article thumbnail/image"
    )


class NewsFeedComponent(UIComponent):
    """Feed of news articles."""
    type: ComponentType = ComponentType.NEWS_FEED
    articles: List[NewsItem] = Field(
        ...,
        description="List of news articles"
    )


# ============================================================================
# INVESTMENT CALCULATOR
# ============================================================================

class InvestmentProjection(BaseModel):
    """Yearly projection for an investment."""
    year: int = Field(
        ...,
        description="Year number in the projection"
    )
    value: float = Field(
        ...,
        description="Projected portfolio value"
    )
    contributions: float = Field(
        ...,
        description="Total contributions up to this year"
    )
    returns: float = Field(
        ...,
        description="Total returns/gains up to this year"
    )


class InvestmentCalculatorComponent(UIComponent):
    """Component showing investment growth calculations."""
    type: ComponentType = ComponentType.INVESTMENT_CALCULATOR
    initial_investment: float = Field(
        ...,
        description="Starting investment amount"
    )
    annual_return: float = Field(
        ...,
        description="Expected annual return rate (as percentage)"
    )
    years: int = Field(
        ...,
        description="Investment time horizon in years"
    )
    final_value: float = Field(
        ...,
        description="Projected final value"
    )
    total_return: float = Field(
        ...,
        description="Total dollar return/gain"
    )
    total_return_percent: float = Field(
        ...,
        description="Total percentage return"
    )
    projections: List[InvestmentProjection] = Field(
        ...,
        description="Year-by-year projections"
    )


# ============================================================================
# ACTION SUGGESTIONS
# ============================================================================

class SuggestedAction(BaseModel):
    """Suggested follow-up action or question."""
    label: str = Field(
        ...,
        description="Display text for the suggestion"
    )
    query: str = Field(
        ...,
        description="The actual query/action to execute when selected"
    )
    icon: Optional[str] = Field(
        None,
        description="Icon identifier for UI rendering"
    )


class ActionSuggestionsComponent(UIComponent):
    """Component showing suggested next actions/questions."""
    type: ComponentType = ComponentType.ACTION_SUGGESTIONS
    suggestions: List[SuggestedAction] = Field(
        ...,
        description="List of suggested actions"
    )


# ============================================================================
# API RESPONSE
# ============================================================================

class GenerativeUIResponseFormat(BaseModel):
    """Top-level response from the AI investment advisor."""
    components: List[
        Union[
            TextComponent,
            InsightComponent,
            AlertComponent,
            SecurityCardComponent,
            MetricsGridComponent,
            EconomicIndicatorComponent,
            PortfolioHoldingsComponent,
            ComparisonTableComponent,
            SectorPerformanceComponent,
            FinancialStatementComponent,
            AssetPerformanceComponent,
            AllocationChartComponent,
            NewsFeedComponent,
            InvestmentCalculatorComponent,
            ActionSuggestionsComponent,
        ]
    ] = Field(
        ...,
        description="Ordered list of UI components to render"
    )
