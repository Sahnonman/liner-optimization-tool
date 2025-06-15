
# 🚛 Transport Route Optimizer (Linear Programming)

A Streamlit app to optimize transport routes between cities using Linear Programming (PuLP).  
It calculates the most cost-effective distribution of trips between Company fleet and 3PL.

## Features
✅ Upload your Excel route file  
✅ Enter fleet size and work days  
✅ Automatic calculation of Company / 3PL trips  
✅ Full cost breakdown with justification  
✅ Clear English interface  

## How to run
```bash
pip install -r requirements.txt
streamlit run transport_route_optimizer_app.py
```

## Excel template
Fill in the Excel file `transport_route_clean_template.xlsx`:
- From, To: city codes
- Monthly_Demand: auto-calculated
- Company_Cost / Return_Empty_Cost: auto-calculated
- 3PL_Cost: enter manually

## Example decision logic
- Company trips cover at least 50% of demand on high-demand routes (>20 trips/month)
- Company trips cannot exceed fleet capacity
- Cost minimized across all routes
