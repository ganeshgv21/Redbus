import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
from datetime import time

engine = create_engine('mysql+pymysql://root:12345678@localhost/red_bus')

try:
    bus_routes_query = "SELECT DISTINCT route_name FROM bus_routes"
    bus_route = pd.read_sql(bus_routes_query, engine)['route_name'].tolist()
    bus_routes_sidebar = st.sidebar.selectbox("Bus Routes", bus_route)
except Exception as e:
    st.error(f"Error loading bus routes: {e}")

bus_type_options = ['Sleeper', 'Seater', 'AC', 'Non-AC']
bus_type_sidebar = st.sidebar.multiselect('Select Bus Types:', bus_type_options)

departure_time_slider = st.sidebar.slider("Select departure time", value=(time(0, 0), time(23, 59)))
star_rating_slider = st.sidebar.slider("Select star rating", min_value=0.0, max_value=5.0, value=(0.0, 5.0), step=0.1)
price_sidebar_slider = st.sidebar.slider("Select price range", min_value=0, max_value=5000, value=(0, 5000), step=1)

params = {'route_name': bus_routes_sidebar}

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

where_clause = " OR ".join(bus_types_query)
query = f"""
    SELECT * FROM bus_routes 
    WHERE route_name = :route_name
    AND star_rating BETWEEN :min_rating AND :max_rating
    AND price BETWEEN :min_price AND :max_price
"""

if where_clause:
    query += f" AND ({where_clause})"

departure_from = departure_time_slider[0].strftime("%H:%M")
departure_upto = departure_time_slider[1].strftime("%H:%M")

query += " AND TIME_FORMAT(departing_time, '%H:%i') BETWEEN :departure_from AND :departure_upto"

params.update({
    'min_rating': star_rating_slider[0],
    'max_rating': star_rating_slider[1],
    'min_price': price_sidebar_slider[0],
    'max_price': price_sidebar_slider[1],
    'departure_from': departure_from,
    'departure_upto': departure_upto
})

if st.sidebar.button('Submit'):
    try:
        data = pd.read_sql(text(query), engine, params=params)
        
        # Format time fields
        def format_time(td):
            if pd.notnull(td):
                total_seconds = td.total_seconds()
                hours = int(total_seconds // 3600)
                minutes = int((total_seconds % 3600) // 60)
                return f"{hours:02}:{minutes:02}"
            return None

        data['departing_time'] = data['departing_time'].apply(format_time)
        data['reaching_time'] = data['reaching_time'].apply(format_time)
        
        st.write(data)
    except Exception as e:
        st.error(f"Error executing query: {e}")
