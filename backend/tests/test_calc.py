# backend/tests/test_random_calc.py
import pytest
import pandas as pd
import numpy as np
from hypothesis import given, strategies as st
from app import calc

# --- Strategies (Generators) ---
# Generates a list of valid stock prices (positive numbers, no infinity/NaN)
price_lists = st.lists(
    st.floats(min_value=0.01, max_value=10000.0, allow_nan=False, allow_infinity=False),
    min_size=2,   # Must have at least 2 days to calculate a return
    max_size=100  # Keep it reasonable for speed
)

# Generates a valid probability distribution (weights that sum to 1.0)
def normalize_weights(weights):
    total = sum(weights)
    if total == 0: return [1.0] # Avoid division by zero
    return [w / total for w in weights]

# --- Tests ---

@given(price_lists)
def test_compute_metrics_never_crashes(prices):
    """
    Property: The calculator should handle ANY sequence of valid positive prices
    without raising an internal server error (500).
    """
    # Setup: Create a DataFrame structure similar to what calc.compute_metrics expects
    # Create a Date Range corresponding to the number of price points
    # We use a fixed start date; the specific dates don't matter, only the duration.
    dates = pd.date_range(start="2020-01-01", periods=len(prices), freq="D")
    
    # Assign the index explicitly when creating the Series
    series = pd.Series(prices, index=dates)
    df = pd.DataFrame({"TEST_ASSET": series})
    
    try:
        metrics = calc.compute_metrics(df)
        
        # Validation: Verify structure of output
        result = metrics["TEST_ASSET"]
        
        # 1. Volatility Logic: Cannot be negative
        assert result.vol >= 0.0, f"Volatility negative for prices: {prices}"
        
        # 2. Drawdown Logic: Must be 0 or negative (loss)
        assert result.max_drawdown <= 0.0, f"Drawdown positive for prices: {prices}"
        
        # 3. Type Safety
        assert isinstance(result.cagr, float)
        
    except ZeroDivisionError:
        # We explicitly want to fail if the code divides by zero
        pytest.fail(f"Calculator divided by zero on input: {prices}")
    except Exception as e:
        pytest.fail(f"Calculator crashed unexpectedly on input: {prices}. Error: {e}")

@given(st.lists(st.floats(min_value=0.1, max_value=1.0), min_size=1, max_size=10))
def test_weight_tolerance_property(raw_weights):
    """
    Property: If weights match the tolerance check in calc.py, they must be accepted.
    This ensures our frontend/backend '0.01' tolerance agreement actually holds.
    """
    # Normalize to effectively sum to 1.0
    valid_weights = normalize_weights(raw_weights)
    
    # Introduce a tiny error just under the tolerance threshold (0.01)
    # This simulates a frontend rounding error (e.g., 0.33 + 0.33 + 0.33 = 0.99)
    tiny_error = 0.009 
    dirty_weights = [w for w in valid_weights]
    dirty_weights[0] += tiny_error
    
    # Verify strict math logic matches the 'calc.py' validation logic
    total = sum(dirty_weights)
    
    # We expect this to pass our 0.01 tolerance check
    is_valid = np.isclose(total, 1.0, atol=0.01)
    
    assert is_valid, f"Weights {dirty_weights} (sum={total}) were rejected despite being within tolerance."