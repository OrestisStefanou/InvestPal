# InvestPal API Reference

Welcome to the InvestPal API reference. This document provides detailed information about the available endpoints, request/response models, and example usage.

**Base URL**: `http://localhost:8000` (default for development)

---

## Chat Service

### Post Message
`POST /chat`

Send a message to the AI investment advisor for a specific session.

#### Request Body
```json
{
  "session_id": "string",
  "message": "string"
}
```

#### Response Body
```json
{
  "response": "string"
}
```

#### Errors
- `404 Not Found`: Session not found.
- `500 Internal Server Error`: An error occurred during response generation.

### Post Generative UI Message
`POST /chat/gen-ui`

Send a message to the AI investment advisor for a specific session and receive a structured response containing various UI components (charts, data grids, text, etc.) for dynamic rendering.

#### Request Body
```json
{
  "session_id": "string",
  "message": "string"
}
```

#### Response Body
The response follows the `GenerativeUIResponseFormat`, returning a list of identifiable UI components.

```json
{
  "components": [
    {
      "type": "text | security_card | metrics_grid | ...",
      "id": "uuid-string",
      "title": "Optional Title",
      "loading": false,
      "metadata": {},
      "...": "component-specific-fields"
    }
  ],
  "metadata": {}
}
```

#### Component Types
The `type` field determines the schema of the component. Below are the available component types and their specific fields.

**1. Text (`text`)**
Basic text content.
- `content` (string): The text to display.
- `format` (string): `plain` or `markdown`.

**2. Insights (`insights`)**
Key insights and summary information.
- `headline` (string): Main headline.
- `insights` (array of strings): List of key insight bullet points.
- `context` (string): Additional context (optional).

**3. Alert (`alert`)**
Notification or warning banner.
- `message` (string): Alert content.
- `severity` (string): `info`, `warning`, `success`, `error`.
- `actionable` (bool): If the alert has an action.

**4. Security Card (`security_card`)**
Snapshot of a financial security.
- `symbol` (string): Ticker symbol.
- `name` (string): Security name.
- `price` (float): Current price.
- `market_cap` (float): Market capitalization (optional).
- `asset_type` (string): `stock`, `etf`, `crypto`, `commodity`, `index`.
- `sector` (string): Sector name (optional).

**5. Metrics Grid (`metrics_grid`)**
A grid of key financial metrics.
- `metrics` (array of objects):
    - `label` (string): Display label.
    - `value` (string | float): The metric value.
    - `change` (float): Change value (optional).
    - `format` (string): `currency`, `percentage`, `number`, `ratio`, `date` (optional).
- `columns` (int): Grid column count (default 2).

**6. Economic Indicator (`economic_indicator`)**
Macroeconomic data points.
- `indicator_name` (string): Name (e.g., GDP).
- `current_value` (float): Latest value.
- `previous_value` (float): Previous period value.
- `trend` (string): `up`, `down`, `stable`.
- `as_of_date` (string): Date of data.

**7. Portfolio Holdings (`portfolio_holdings`)**
Table of portfolio positions.
- `holdings` (array of objects):
    - `symbol` (string): Security symbol.
    - `name` (string): Security name.
    - `weight` (float): Portfolio weight percentage.
    - `value` (float): Total value of holding (optional).
    - `shares` (float): Number of shares (optional).
    - `sector` (string): Sector classification (optional).
- `total_value` (float): Total portfolio value.

**8. Comparison Table (`comparison_table`)**
Side-by-side comparison of entities.
- `entities` (array of strings): Names/symbols being compared (column headers).
- `rows` (array of objects):
    - `metric` (string): Name of the metric.
    - `values` (map<string, any>): Map of entity name/symbol to value.
    - `format` (string): Formatting hint `currency`, `percentage`, etc. (optional).
- `comparison_type` (string): `stocks`, `etfs`, `sectors`, etc.

**9. Sector Performance (`sector_performance`)**
Performance data across sectors.
- `sectors` (array of objects):
    - `sector` (string): Sector name.
    - `return_1d` (float): 1-day return % (optional).
    - `return_1w` (float): 1-week return % (optional).
    - `return_1m` (float): 1-month return % (optional).
    - `return_ytd` (float): YTD return % (optional).
- `visualization` (string): `heatmap`, `bar`, `table`.

**10. Financial Statement (`financial_statement`)**
Income statement, balance sheet, or cash flow.
- `statement_type` (string): `income_statement`, `balance_sheet`, `cash_flow`.
- `periods` (array of strings): List of time periods (e.g., `["2024", "2023"]`).
- `rows` (array of objects):
    - `line_item` (string): Name of the line item.
    - `values` (map<string, float>): Map of period to value.
    - `category` (string): Grouping category (optional).

**11. Time Series Chart (`time_series_chart`)**
Historical data visualization.
- `series` (array of objects):
    - `name` (string): Series name.
    - `data` (array of objects): List of `{ "timestamp": "ISO_DATE", "value": float }`.
    - `color` (string): Hex color code (optional).
- `chart_type` (string): `line`, `area`, `bar`, `candlestick`.

**12. Allocation Chart (`allocation_chart`)**
Distribution breakdown.
- `allocations` (array of objects):
    - `label` (string): Category label.
    - `value` (float): Absolute value.
    - `percentage` (float): Percentage of total.
    - `color` (string): Hex color code (optional).
- `chart_type` (string): `pie`, `donut`, `treemap`.
- `allocation_type` (string): `sector`, `asset_class`, `geography`, `holdings`, `market_cap`.

**13. News Feed (`news_feed`)**
Relevant news articles.
- `articles` (array of objects):
    - `title` (string): Article headline.
    - `source` (string): Publisher name.
    - `published_at` (string): ISO date string.
    - `url` (string): Link to full article (optional).
    - `summary` (string): Brief summary (optional).
    - `sentiment` (string): `positive`, `negative`, `neutral` (optional).
    - `image_url` (string): Thumbnail URL (optional).

**14. Investment Calculator (`investment_calculator`)**
Projected growth calculator.
- `initial_investment` (float): Starting amount.
- `annual_return` (float): Expected return %.
- `years` (int): Time horizon.
- `projections` (array of objects):
    - `year` (int): Year number.
    - `value` (float): Projected value.
    - `contributions` (float): Total contributions.
    - `returns` (float): Total returns.

**15. Action Suggestions (`action_suggestions`)**
Suggested follow-up actions.
- `suggestions` (array of objects):
    - `label` (string): Display text.
    - `query` (string): Action query to execute.
    - `icon` (string): Icon naming (optional).

#### Errors
- `404 Not Found`: Session not found.
- `500 Internal Server Error`: An error occurred during response generation.

---

## Session Service

### Create Session
`POST /session`

Create a new chat session for a user.

#### Request Body
```json
{
  "user_id": "string",
  "session_id": "string (optional)"
}
```
*If `session_id` is not provided, a new one will be generated.*

#### Response Body
```json
{
  "session_id": "string",
  "user_id": "string",
  "messages": []
}
```

#### Errors
- `409 Conflict`: Session already exists.
- `500 Internal Server Error`: An error occurred during session creation.

### Get Session
`GET /session/{session_id}`

Retrieve the details and message history of a specific session.

#### Parameters
- `session_id` (path): The unique identifier of the session.

#### Response Body
```json
{
  "session_id": "string",
  "user_id": "string",
  "messages": [
    {
      "role": "user | agent",
      "content": "string"
    }
  ]
}
```

#### Errors
- `404 Not Found`: Session not found.
- `500 Internal Server Error`: An error occurred during retrieval.

---

## User Context Service

### Create User Context
`POST /user_context`

Create initial context and portfolio for a user.

#### Request Body
```json
{
  "user_id": "string",
  "user_profile": {
    "key": "value"
  },
  "user_portfolio": [
    {
      "asset_class": "string",
      "symbol": "string",
      "name": "string",
      "quantity": 0.0
    }
  ]
}
```

#### Response Body
Same as request body.

#### Errors
- `409 Conflict`: User context already exists.
- `500 Internal Server Error`: An error occurred during creation.

### Get User Context
`GET /user_context/{user_id}`

Retrieve the context and portfolio for a specific user.

#### Parameters
- `user_id` (path): The unique identifier of the user.

#### Response Body
```json
{
  "user_id": "string",
  "user_profile": { ... },
  "user_portfolio": [ ... ]
}
```

#### Errors
- `404 Not Found`: User context not found.
- `500 Internal Server Error`: An error occurred during retrieval.

### Update User Context
`PUT /user_context`

Update existing context or portfolio for a user.

#### Request Body
Same as `POST /user_context`.

#### Response Body
Same as `POST /user_context`.

#### Errors
- `404 Not Found`: User context not found.
- `500 Internal Server Error`: An error occurred during update.
