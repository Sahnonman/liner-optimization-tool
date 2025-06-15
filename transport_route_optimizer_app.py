
import streamlit as st
import pandas as pd
from pulp import LpProblem, LpMinimize, LpVariable, lpSum, LpInteger, value

st.title("🚛 Transport Route Optimizer (Linear Programming)")

uploaded_file = st.file_uploader("Upload your transport route Excel file", type=["xlsx"])

if uploaded_file:
    data = pd.read_excel(uploaded_file, sheet_name="Routes")
    st.success("File loaded successfully!")
    st.write(data)

    fleet_size = st.number_input("Enter available company fleet size (trucks)", min_value=1, value=10)
    work_days = st.number_input("Enter number of working days per month", min_value=1, max_value=31, value=26)

    model = LpProblem("Transport_Cost_Minimization", LpMinimize)

    company_vars = {}
    pl3_vars = {}

    for _, row in data.iterrows():
        key = (row['From'], row['To'])
        company_vars[key] = LpVariable(f"Company_{row['From']}_{row['To']}", lowBound=0, cat=LpInteger)
        pl3_vars[key] = LpVariable(f"PL3_{row['From']}_{row['To']}", lowBound=0, cat=LpInteger)

    model += lpSum([
        company_vars[(row['From'], row['To'])] * (row['Company_Cost'] + row['Return_Empty_Cost']) +
        pl3_vars[(row['From'], row['To'])] * float(row['3PL_Cost'])
        for _, row in data.iterrows()
    ])

    for _, row in data.iterrows():
        key = (row['From'], row['To'])
        model += company_vars[key] + pl3_vars[key] >= row['Monthly_Demand'], f"Demand_{row['From']}_{row['To']}"

        if row['Monthly_Demand'] > 20:
            model += company_vars[key] >= 0.5 * row['Monthly_Demand'], f"HighDemand_{row['From']}_{row['To']}"

        max_trips = row['Max_Trips_per_Truck_Month'] * fleet_size
        model += company_vars[key] <= max_trips, f"MaxCompanyTrips_{row['From']}_{row['To']}"

    if st.button("Run Optimization"):
        model.solve()

        results = []
        for _, row in data.iterrows():
            key = (row['From'], row['To'])
            results.append({
                "From": row['From'],
                "To": row['To'],
                "Company_Trips": int(company_vars[key].varValue),
                "3PL_Trips": int(pl3_vars[key].varValue)
            })

        result_df = pd.DataFrame(results)
        st.subheader("Optimization Results")
        st.write(result_df)

        st.success(f"Total Cost: SAR {value(model.objective):,.2f}")
else:
    st.info("Please upload your Excel file to begin.")
