# Investment Backtester Prototype

A full-stack application for analyzing asset performance and simulating investment strategies (Buy & Hold, DCA) with persistent user sessions.

## Project Architecture

The project is split into two main services managed via Docker:

### 1. Backend (FastAPI + SQLAlchemy)
* **Location:** `/backend`
* **Core Logic:**
    * `app/calc.py`: The financial engine. It calculates metrics like CAGR, Volatility, Max Drawdown, and Sharpe Ratio.
    * `app/api.py`: REST API handling public data (assets) and protected user actions (backtests, strategy saving).
    * `app/db.py`: Database schema utilizing SQLite. It stores daily price caches, user credentials, and strategy parameters.
    * `app/data_fetcher.py`: Manages historical data retrieval and local caching to minimize API hits.

### 2. Frontend (React + Vite)
* **Location:** `/frontend`
* **Key Features:**
    * **Authentication:** Uses HTTP-only session cookies via Axios (`withCredentials: true`) to ensure security.
    * **Strategy Management:** Users can run backtests, which creates a "Dernière stratégie" entry. These can be promoted to "Saved" status.
    * **State Management:** Explicitly resets all local variables on logout to prevent data leaking between user sessions in the same browser.



---

## Key Workflows

### Investment Strategies
The system currently supports two economic methods in `calc.py`:
* **Buy and Hold:** A single investment made at the start of the simulation period.
* **DCA (Dollar-Cost Averaging):** Fixed monthly contributions throughout the simulation period.

### Data Persistence
1.  **Backtest:** When a user runs a simulation, parameters are saved in the `user_strategy` table with `is_saved = False` and the name "Dernière stratégie".
2.  **Save:** Users can "save" the current run, which creates a permanent record (`is_saved = True`) and prompts for a custom name.
3.  **Loading:** Saved strategies can be reloaded into the UI, which re-populates all inputs (assets, weights, dates) for a new run.

---

## Security & Constraints
* **Session-Based:** Authentication is handled by the backend `Session` model; sessions are deleted upon logout.
* **Ownership:** The API enforces that users can only fetch, or delete strategies where `user_id` matches their own session.
* **Quota:** Each user is limited to **5 saved strategies** (enforced in `api.py`).

---

## Setup & Development
* **Docker:** Run `docker-compose up --build` from the root directory to launch the environment.
* **Database:** The SQLite database is persisted in `/backend/data/app.db`.

# Technical API & Schema Specification

This document serves as the "Source of Truth" for the Investment Backtester's data structures and communication protocols.

---

## 1. Core Data Schemas (Models)
These schemas define the Pydantic models used for API validation and the JSON structure stored in the database.

### **Financial Metrics (`Metrics`)**
Computed in `calc.py` and returned in analysis and backtest responses.
- **cagr**: Compound Annual Growth Rate (float).
- **vol**: Annualized Volatility (float).
- **max_drawdown**: Maximum peak-to-trough loss (float).
- **sharpe_ratio**: Risk-adjusted return relative to risk-free rate (float).
- **best_year / worst_year**: Highest and lowest annual returns (float).

### **Strategy Parameters (`BacktestRequest`)**
The "Recipe" for a simulation, stored in the `parameters` JSON column of the `user_strategy` table.
- **assets**: List of ticker strings (e.g., `["AAPL", "SPY"]`).
- **start_date / end_date**: Date range for historical metrics calculation.
- **invest_amount**: Initial or monthly investment amount (float).
- **weights**: List of floats representing allocation (must sum to 1.0).
- **strategy**: Either `"buy_and_hold"` or `"dca"`.
- **strat_start / strat_end**: Date range for the portfolio simulation.

---

## 2. Public API Endpoints
*Accessible without an active session.*

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| **GET** | `/api/assets` | Returns available tickers from `assets.json`. |
| **POST** | `/api/register` | Creates a new user in the database. |
| **POST** | `/api/login` | Authenticates user and sets the `session_token` cookie. |

---

## 3. Protected API Endpoints
*Requires a valid `session_token` cookie. All data is scoped to the `current_user`.*

### **POST** `/api/analyze` (Newly Protected)
**Purpose:** Fetch historical data and performance metrics for specific assets.
- **Request:** `AnalyzeRequest` (assets, start_date, end_date).
- **Response:** - `prices`: `{ "YYYY-MM-DD": { "TICKER": price } }`
  - `metrics`: `{ "TICKER": MetricsObject }`

### **POST** `/api/backtest`
**Purpose:** Run a simulation and record it as the user's latest "draft" (unsaved) run.
- **Response:** Includes `portfolio` time-series data and calculated metrics.

### **POST** `/api/strategies/save-current`
**Purpose:** Persist the most recent backtest with a custom name.
- **Request:** `{ "name": "string" }`
- **Constraint:** Limited to 5 saved strategies per user.

### **GET** `/api/strategies`
**Purpose:** Fetch all strategies (saved and unsaved) belonging to the session user.

### **DELETE** `/api/strategies/{id}`
**Purpose:** Remove a saved strategy. Ownership is verified before deletion.

### **POST** `/api/logout`
**Purpose:** Destroys the session in the DB and clears the browser cookie.

---

## 4. Error Reference Table

| Status Code | Meaning | Typical Cause |
| :--- | :--- | :--- |
| **400** | Bad Request | Logic error (e.g., weights don't sum to 1). |
| **401** | Unauthorized | Session cookie missing or expired. |
| **422** | Unprocessable Entity | Missing required JSON field or wrong data type. |
| **404** | Not Found | Attempting to access a strategy that does not exist. |