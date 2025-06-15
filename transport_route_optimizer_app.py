import streamlit as st
import pandas as pd
import math
from pulp import LpProblem, LpMinimize, LpVariable, lpSum, LpInteger, value

st.title("🚛 Transport Route Optimizer (Linear Programming)")

uploaded_file = st.file_uploader("Upload your transport route Excel file", type=["xlsx"])

if uploaded_file:
    data = pd.read_excel(uploaded_file, sheet_name="Routes")
    st.success("File loaded successfully!")
    st.write(data)

    # User inputs
    fleet_size = st.number_input("Enter available company fleet size (trucks)", min_value=1, value=10)
    work_days = st.number_input("Enter number of working days per month", min_value=1, max_value=31, value=26)

    # Build LP model
    model = LpProblem("Transport_Cost_Minimization", LpMinimize)

    # Decision variables
    company_vars = {}
    pl3_vars = {}
    trucks_vars = {}

    for _, row in data.iterrows():
        route_key = (row['From'], row['To'])
        # Number of trucks assigned to this route
        trucks_vars[route_key] = LpVariable(f"Trucks_{row['From']}_{row['To']}", lowBound=0, upperBound=fleet_size, cat=LpInteger)
        # Number of trips by company
        company_vars[route_key] = LpVariable(f"CompanyTrips_{row['From']}_{row['To']}", lowBound=0, cat=LpInteger)
        # Number of trips by 3PL
        pl3_vars[route_key] = LpVariable(f"PL3Trips_{row['From']}_{row['To']}", lowBound=0, cat=LpInteger)

    # Objective: minimize total cost
    model += lpSum([
        company_vars[key] * (row['Company_Cost'] + row['Return_Empty_Cost']) +
        pl3_vars[key] * float(row['3PL_Cost'])
        for _, row in data.iterrows()
        for key in [(row['From'], row['To'])]
    ])

    # Constraints
    # 1. Sum of trucks assigned ≤ total fleet size
    model += lpSum([trucks_vars[key] for key in trucks_vars]) <= fleet_size, "Total_Truck_Limit"

    for _, row in data.iterrows():
        key = (row['From'], row['To'])
        demand = row['Monthly_Demand']
        duration = row['Trip_Duration_Days']

        # a) Satisfy demand
        model += company_vars[key] + pl3_vars[key] >= demand, f"Demand_{row['From']}_{row['To']}"

        # b) High-demand coverage (≥50% by company if demand > 20)
        if demand > 20:
            model += company_vars[key] >= 0.5 * demand, f"HighDemand_{row['From']}_{row['To']}"

        # c) Company trips limited by assigned trucks capacity
        max_trips_per_truck = math.floor(work_days / duration)
        model += company_vars[key] <= trucks_vars[key] * max_trips_per_truck, f"Capacity_{row['From']}_{row['To']}"

    # Solve
    if st.button("Run Optimization"):
        model.solve()

        # Collect results
        results = []
        for _, row in data.iterrows():
            key = (row['From'], row['To'])
            results.append({
                "From": row['From'],
                "To": row['To'],
                "Trucks_Assigned": int(trucks_vars[key].varValue),
                "Company_Trips": int(company_vars[key].varValue),
                "3PL_Trips": int(pl3_vars[key].varValue)
            })

        result_df = pd.DataFrame(results)
        st.subheader("Optimization Results")
        st.write(result_df)
        st.success(f"Total Cost: SAR {value(model.objective):,.2f}")
else:
    st.info("Please upload your Excel file to begin.")
