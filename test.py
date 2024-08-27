import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
from datetime import time

# SQLAlchemy connection string
engine = create_engine('mysql+pymysql://root:12345678@localhost/red_bus')

# Sidebar for bus route selection
bus_routes_query = "SELECT DISTINCT route_name FROM bus_routes"
bus_route = pd.read_sql(bus_routes_query, engine)['route_name'].tolist()
bus_routes_sidebar = st.sidebar.selectbox("Bus Routes", bus_route)

# Sidebar for bus type selection
bus_type_options = ['Sleeper', 'Seater', 'AC', 'Non-AC']
bus_type_sidebar = st.sidebar.multiselect('Select Bus Types:', bus_type_options)

# Sidebar for departure time selection
departure_time_slider = st.sidebar.slider(
    "Select departure time",
    value=(time(0, 0), time(23, 59))
)

# Sidebar for star rating selection
star_rating_slider = st.sidebar.slider(
    "Select star rating",
    min_value=0.0,
    max_value=5.0,
    value=(0.0, 5.0),
    step=0.1
)

# Sidebar for price range selection
price_sidebar_slider = st.sidebar.slider(
    "Select price range", 
    min_value=0, 
    max_value=5000, 
    value=(0, 5000),  # Default range
    step=1
)

# Define parameters for filtering
params = {'route_name': bus_routes_sidebar}

# Build the WHERE clause dynamically based on selected bus types
bus_types_query = []

if 'Sleeper' in bus_type_sidebar:
    bus_types_query.append("bustype LIKE '%Sleeper%' OR bustype LIKE '%SLEEPER%'")
if 'Seater' in bus_type_sidebar:
    bus_types_query.append("bustype LIKE '%Seater%' OR bustype LIKE '%SEATER%'")
if 'AC' in bus_type_sidebar:
    bus_types_query.append("""
        (bustype LIKE '%AC%' OR LOWER(bustype) LIKE '%a/c%' 
         OR bustype LIKE '%A.C%' OR bustype LIKE '%A/C%' OR bustype LIKE '%A/c%')
         AND bustype NOT LIKE '%Non-AC%' 
         AND bustype NOT LIKE '%NON-AC%' 
         AND bustype NOT LIKE '%NON A/C%' 
         AND bustype NOT LIKE '%Non A/C%' 
         AND bustype NOT LIKE '%Non AC%' 
         AND bustype NOT LIKE '%NON AC%'
    """)
if 'Non-AC' in bus_type_sidebar:
    bus_types_query.append("""
        (bustype LIKE '%Non-AC%' 
         OR bustype LIKE '%NON-AC%' 
         OR bustype LIKE '%NON A/C%' 
         OR bustype LIKE '%Non A/C%' 
         OR bustype LIKE '%Non AC%' 
         OR bustype LIKE '%NON AC%')
    """)

# Join the conditions with OR for bus types
where_clause = " OR ".join(bus_types_query)

# Base SQL query
query = f"""
    SELECT * FROM bus_routes 
    WHERE route_name = :route_name
    AND star_rating BETWEEN :min_rating AND :max_rating
    AND price BETWEEN :min_price AND :max_price
"""

if where_clause:
    query += f" AND ({where_clause})"

# Convert the selected times to strings for comparison
departure_from = departure_time_slider[0].strftime("%H:%M")
departure_upto = departure_time_slider[1].strftime("%H:%M")

# Add departure time filtering to the SQL query
query += " AND TIME_FORMAT(departing_time, '%H:%i') BETWEEN :departure_from AND :departure_upto"

# Adding the rest of the parameters
params.update({
    'min_rating': star_rating_slider[0],
    'max_rating': star_rating_slider[1],
    'min_price': price_sidebar_slider[0],
    'max_price': price_sidebar_slider[1],
    'departure_from': departure_from,
    'departure_upto': departure_upto
})

# Debug: Print the query to verify
st.write(f"SQL Query: {query}")
st.write(f"Params: {params}")

# Submit button
if st.sidebar.button('Submit'):
    # Load the filtered data on button press
    data = pd.read_sql(text(query), engine, params=params)
    
    # Function to convert time from Timedelta to 'H:M' format
    def format_time(td):
        if pd.notnull(td):
            total_seconds = td.total_seconds()
            hours = int(total_seconds // 3600)
            minutes = int((total_seconds % 3600) // 60)
            return f"{hours:02}:{minutes:02}"
        return None

    # Apply the function to the DataFrame columns
    data['departing_time'] = data['departing_time'].apply(format_time)
    data['reaching_time'] = data['reaching_time'].apply(format_time)
    
    # Display the filtered DataFrame
    st.write(data)
