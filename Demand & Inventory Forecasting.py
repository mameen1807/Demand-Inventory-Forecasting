import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression

# -------------------------
# 1️⃣ Generate example past demand
# -------------------------
np.random.seed(42)
past_demand = np.random.poisson(lam=20, size=30)  # Example: last 30 days demand
print("Past demand:", past_demand)

# -------------------------
# 2️⃣ Forecast future demand
# -------------------------
def forecast_demand(past_demand, future_days=10, smoothing=0.3):
    df = pd.DataFrame({'day': np.arange(len(past_demand)), 'demand': past_demand})
    X = df[['day']]
    y = df['demand']
    model = LinearRegression()
    model.fit(X, y)

    future_X = pd.DataFrame({'day': np.arange(len(past_demand), len(past_demand)+future_days)})
    forecast = model.predict(future_X)

    # Blend regression forecast with historical mean (smoothing)
    avg_demand = np.mean(past_demand)
    forecast = (1 - smoothing) * forecast + smoothing * avg_demand

    # Ensure non-negative integers
    forecast = np.maximum(forecast, 0).astype(int)
    return forecast

forecast = forecast_demand(past_demand, future_days=10)
print("Forecasted demand for next 10 days:", forecast)

# -------------------------
# 3️⃣ Inventory Policy (s, S)
# -------------------------
def inventory_policy(forecast, s, S, initial_inventory=50, holding_cost=1, shortage_cost=5, order_cost=50):
    inventory = initial_inventory
    total_cost = 0
    for d in forecast:
        if inventory < s:  # Place order
            order_qty = S - inventory
            inventory += order_qty
            total_cost += order_cost
        if inventory >= d:  # Enough inventory
            inventory -= d
            total_cost += inventory * holding_cost
        else:  # Shortage
            total_cost += (d - inventory) * shortage_cost
            inventory = 0
    return total_cost

# -------------------------
# 4️⃣ Optimise (s, S) automatically
# -------------------------
def optimise_inventory_policy(forecast, s_range, S_range):
    best_s, best_S, best_cost = None, None, float('inf')
    for s in s_range:
        for S in S_range:
            if S > s:  # Valid policy
                cost = inventory_policy(forecast, s, S)
                if cost < best_cost:
                    best_s, best_S, best_cost = s, S, cost
    return best_s, best_S, best_cost

# Search for best policy in ranges
best_s, best_S, best_cost = optimise_inventory_policy(forecast, s_range=range(10,30), S_range=range(40,70))
print(f"Optimal policy: s={best_s}, S={best_S} with minimum expected cost={best_cost}")
