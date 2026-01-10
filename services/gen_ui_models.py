from enum import Enum
from typing import List, Union, Optional, Any, Dict
from pydantic import BaseModel, Field


class ComponentType(str, Enum):
    TEXT = "text"
    CHART = "chart"
    TABLE = "table"
    METRIC_CARD = "metric_card"
    STOCK_CARD = "stock_card"
    ALERT = "alert"
    COMPARISON = "comparison"
    TIMELINE = "timeline"


class UIComponent(BaseModel):
    type: ComponentType
    title: Optional[str] = None


class TextComponent(UIComponent):
    type: ComponentType = ComponentType.TEXT
    content: str


class ChartType(str, Enum):
    PIE = "pie"
    LINE = "line"
    BAR = "bar"


class ChartDataPoint(BaseModel):
    label: str
    value: float
    metadata: Optional[Dict[str, Any]] = None


class ChartComponent(UIComponent):
    type: ComponentType = ComponentType.CHART
    chart_type: ChartType
    data: List[ChartDataPoint]
    x_axis_label: Optional[str] = None
    y_axis_label: Optional[str] = None


class TableRow(BaseModel):
    values: Dict[str, Any]  # Maps column key to value


class TableColumn(BaseModel):
    key: str
    label: str


class TableComponent(UIComponent):
    type: ComponentType = ComponentType.TABLE
    columns: List[TableColumn]
    rows: List[TableRow]


class MetricCardComponent(UIComponent):
    type: ComponentType = ComponentType.METRIC_CARD
    label: str
    value: str | float
    change: Optional[float] = None
    change_direction: Optional[str] = None  # "up", "down", "neutral"


class StockCardComponent(UIComponent):
    type: ComponentType = ComponentType.STOCK_CARD
    symbol: str
    name: str
    price: float
    change: float
    change_percent: float


class AlertSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    SUCCESS = "success"


class AlertComponent(UIComponent):
    type: ComponentType = ComponentType.ALERT
    message: str
    severity: AlertSeverity = AlertSeverity.INFO


class ComparisonItem(BaseModel):
    name: str
    metrics: Dict[str, Any]


class ComparisonComponent(UIComponent):
    type: ComponentType = ComponentType.COMPARISON
    items: List[ComparisonItem]


class TimelineEvent(BaseModel):
    date: str
    title: str
    description: Optional[str] = None


class TimelineComponent(UIComponent):
    type: ComponentType = ComponentType.TIMELINE
    events: List[TimelineEvent]


class GenerativeUIResponse(BaseModel):
    components: List[
        Union[
            TextComponent,
            ChartComponent,
            TableComponent,
            MetricCardComponent,
            StockCardComponent,
            AlertComponent,
            ComparisonComponent,
            TimelineComponent,
        ]
    ] = Field(..., description="A list of UI components to render on the client side.")
