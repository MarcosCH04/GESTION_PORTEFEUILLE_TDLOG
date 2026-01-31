# InvestTrack - Investment Backtester

A full-stack quantitative finance application with academic purposes for analyzing asset performance and simulating investment strategies (Buy & Hold, DCA). 

## Project Overview

This project implements a robust financial backtesting engine featuring a clear separation of concerns between data retrieval, calculation logic, and user interface. It is designed to handle historical market data efficiently using a "Gap Analysis" caching strategy and validates financial inputs using strict property-based testing.

### Key Technical Features

* **Gap Analysis Caching:** The system minimizes API calls to external providers (Yahoo Finance) by checking the local SQLite database first. It fetches only the specific dates missing from the requested range to optimize performance and reduce latency (`backend/app/data_fetcher.py`).
* **Session-Based Authentication:** Custom-built session management utilizing HTTP-only cookies and cryptographic hashing (Argon2), eliminating reliance on heavy third-party authentication services (`backend/app/auth.py`).
* **Property-Based Testing:** Utilizes the **Hypothesis** library to fuzz-test the financial engine against thousands of random scenarios, ensuring mathematical stability and handling of edge cases like zero-volatility assets (`backend/tests/test_random_calc.py`).
* **Strict Schema Validation:** Pydantic schemas enforce data integrity at the API boundary, ensuring invalid inputs (e.g., mismatched arrays or improper weight sums) are rejected before reaching the calculation engine.

---

## Architecture

The application follows a containerized microservices pattern managed via Docker.

### 1. Backend (FastAPI + SQLAlchemy)

* **API Layer (`api.py`):** Manages REST endpoints, handles dependency injection for database sessions, and executes Pydantic validation.
* **Financial Engine (`calc.py`):** Contains pure Python logic for computing CAGR, Volatility, Sharpe Ratio, and running Portfolio simulations.
* **Persistence (`db.py`):** SQLite database storing:
    * `DailyPrice`: Normalized historical time-series data.
    * `UserStrategy`: User-saved simulation parameters (JSON).
    * `Session`: Active user tokens and authentication state.

### 2. Frontend (React + Vite)

* **Orchestration (`App.jsx`):** Manages the global application state, handling the flow from Authentication to Asset Selection, Analysis, and finally Results.
* **Visualization:** Integrates `chart.js` for rendering interactive Asset Curves and Portfolio Growth charts.
* **Performance:** Implements React `useMemo` hooks to prevent unnecessary chart re-calculations during state updates.

---

## Quick Start

**Prerequisite:** [Docker Desktop](https://www.docker.com/products/docker-desktop/) must be installed and executed before running the code.

1.  **Build and Launch:**
    Run the following command from the root directory to build the containers:
    ```bash
    docker compose up --build
    ```

2.  **Access the Application:**
    * **Frontend Interface:** http://localhost:5173
    * **Backend Documentation (Swagger UI):** http://localhost:8000/docs

3.  **Run the Test Suite:**
    This project includes Unit, Integration, and Property-based tests with ```pytest```, cleaning right after with the ```--rm``` flag.
    ```bash
    docker compose run --rm backend python -m pytest
    ```

---

## Project Structure

```text
├── docker-compose.yml           # Orchestration for Backend + Frontend
├── backend
│   ├── Dockerfile               # Python Environment Definition
│   ├── requirements.txt         # Python Dependencies (FastAPI, Pandas, Hypothesis)
│   ├── app
│   │   ├── main.py              # App Entry Point & CORS Config
│   │   ├── api.py               # REST API Routes
│   │   ├── auth.py              # Session Management & Argon2 Security
│   │   ├── calc.py              # Financial Engine (CAGR, Volatility, Simulation)
│   │   ├── data_fetcher.py      # Yahoo Finance Integration & Gap Analysis
│   │   ├── db.py                # SQLite Models (User, Session, Strategy)
│   │   ├── schemas.py           # Pydantic Validation Models
│   │   └── assets.json          # Supported Asset List
│   ├── data
│   │   └── app.db               # SQLite DB
│   └── tests
│       ├── conftest.py          # Pytest Fixtures (In-Memory DB)
│       ├── test_api.py          # Integration Tests
│       ├── test_calc.py         # Property-Based Math Tests (Hypothesis)
│       ├── test_data.py         # Caching Logic Tests
│       └── test_session.py      # Auth & Persistence Tests
└── frontend
    ├── Dockerfile               # Node.js Environment Definition
    ├── package.json             # JS Dependencies (React, Chart.js, Tailwind)
    ├── vite.config.js           # Build Configuration
    ├── tailwind.config.js       # CSS Styling Configuration
    ├── index.html               # App Entry Point
    └── src
        ├── main.jsx             # React DOM Mounting
        ├── App.jsx              # Main Router & State Orchestrator
        ├── api.js               # Axios Wrapper (Cookies/Auth)
        ├── index.css            # Global Styles
        └── components
            ├── HomePage.jsx             # Landing Page
            ├── LoginForm.jsx            # Authentication UI
            ├── RegistrationForm.jsx     # User Onboarding
            ├── AssetSelector.jsx        # Multi-select Asset Grid
            ├── PeriodSelector.jsx       # Date Range Inputs
            ├── WeightAllocator.jsx      # Dynamic Percentage Inputs
            ├── StrategyForm.jsx         # Investment Parameters
            ├── Spinner.jsx              # Loading State UI
            ├── Charts.jsx               # Chart.js Visualizations
            ├── PortfolioTable.jsx       # Metrics Display
            ├── SavedStrategiesList.jsx  # Database Persistence UI
            └── Toast.jsx                # Notification System
```


## Testing Strategy

The project employs a comprehensive testing suite ensuring stability across the database, API, and math engine for a clear TDD approach.

1.  **Property-Based Math Tests (`test_calc.py`):**
    * **Tool:** Hypothesis
    * **Objective:** Fuzz-tests the financial engine with thousands of random inputs (e.g., zero prices, infinite lists) to prove the calculator never crashes.
    * *Coverage:* Volatility, CAGR, Drawdown, and weight validation logic.

2.  **API Integration Tests (`test_api.py`):**
    * **Objective:** Verifies the full request/response cycle for public and protected endpoints.
    * *Coverage:* User registration, login flows, and payload validation (422/400 errors).

3.  **Data Caching Tests (`test_data.py`):**
    * **Objective:** Validates the "Gap Analysis" engine.
    * *Coverage:* Ensures the system detects missing dates in the SQLite cache and only fetches the delta from Yahoo Finance.

4.  **Session & Security Tests (`test_session.py`):**
    * **Objective:** Verifies authentication persistence and isolation.
    * *Coverage:* Cookie handling, session expiration, and ensuring users cannot delete strategies owned by others.

---

## API Reference

| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| **GET** | `/api/assets` | List all available supported assets. | No |
| **POST** | `/api/register` | Register a new user account. | No |
| **POST** | `/api/login` | Authenticate and set the HttpOnly session cookie. | No |
| **POST** | `/api/logout` | Invalidate session and clear cookies. | Yes |
| **POST** | `/api/analyze` | Fetch historical metrics (CAGR, Vol) for specific assets. | Yes |
| **POST** | `/api/backtest` | Run a portfolio simulation and store as "Latest Draft". | Yes |
| **GET** | `/api/strategies` | Retrieve all saved strategies for the current user. | Yes |
| **POST** | `/api/strategies/save-current` | Persist the latest backtest draft as a named strategy. | Yes |
| **DELETE** | `/api/strategies/{id}` | Permanently remove a saved strategy. | Yes |

### Error Handling Standards
* **422 Unprocessable Entity:** Returned when inputs violate schema rules (e.g., missing a required JSON field in a request).
* **401 Unauthorized:** Returned when a session cookie is missing or expired.
* **400 Bad Request:** Returned for logic errors (e.g., "Username already taken" or "Strategy quota exceeded").
* **404 Not Found:** Returned when trying to delete or access a resource that doesn't exist.
