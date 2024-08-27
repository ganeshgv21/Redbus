# Redbus
## Overview
This projects aims to scrape bus deatails using 'SELENIUM' ,store it in the database and display it by using  'STREAMLIT' web app applying filters  

###  Objects
The main objective of my project is to:  
1.Scrape Bus Details: Use Selenium to collect bus information
2.Store Data: Save the collected data into a SQL database. 
3.Display Data: Present the stored bus details using filters in a Streamlit web application.

### Tools
- Excel - Pandas - Data Cleaning
- MySql - Store data
- Streamlit -  Display the stored data using filters

# CODE EXPLANATION
#### 1.code for scrape:
```py
import time
import numpy as np
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException, TimeoutException
# above modules  are required to do the project 

driver = webdriver.Chrome()   # Initialize the Chrome WebDriver

driver.get("https://www.redbus.in/")
driver.maximize_window()   # navigate to the RedBus website

wait = WebDriverWait(driver, 10)   # define the explicit wait in "wait" variable

bus_data = []   #initialize an empty list to store bus data


try:
    # Try to click on the RTC section link
    try:
        rtc_section_link = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[@href='https://www.redbus.in/online-booking/rtc-directory']"))).click()
    except ElementClickInterceptedException:
        print("ERROR while clicking RTC section")   #this snippet is used to navigate to rtc section page by clicking xpath of it

    try:
        main_window = driver.current_window_handle
        for window in driver.window_handles:
            if window != main_window:
                driver.switch_to.window(window)
                break  

        APSRTC_LINK = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "APSRTC"))).click()
    except ElementClickInterceptedException:
        print("ERROR while switching windows or clicking APSRTC link:")  #this snippet is helps to open rtc page in second window  by looping through all windows ,then it will get into apsrtc by clicking link txt of it

    
    route_names = []
    route_links = []     # initialize two empty lists to store route names,links
    
    def collect_data():
        try:
            route_containers = driver.find_elements(By.CLASS_NAME, "route")
            for route_container in route_containers:
                title = route_container.get_attribute('title')
                href = route_container.get_attribute('href')
                route_names.append(title)
                route_links.append(href)
        except NoSuchElementException:
            print("ERROR while collecting route data")     # collect_data() snippet helps to find & store it in route_name,route_link lists by container in apstrs page 


    def collect_route_details():
        try:
            for i in range(1, 6):
                if i > 1:
                    x_path = f'/html/body/div[1]/div/div[4]/div[12]/div[{i}]'
                    element = driver.find_element(By.XPATH, x_path)
                    driver.execute_script("arguments[0].scrollIntoView(true);", element)
                    driver.execute_script("arguments[0].click();", element)
                    time.sleep(4)
                collect_data()
        except NoSuchElementException:
            print("ERROR while collecting route details")    #this snippet do scroll upto down of page and itrate in apsrtc page using manual xpath and call the collect_data() to do its work 


    def collect_bus_elements(route_name, route_link):
        try:
            wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'clearfix.bus-item')))
            print('found container')
            time.sleep(3)

            bus_elements = driver.find_elements(By.CLASS_NAME, 'clearfix.bus-item')

            for bus in bus_elements:
                bus_info = {}
                bus_info['Route_Name'] = route_name
                bus_info['Route_Link'] = route_link

                try:
                    bus_info['Bus_Name'] = bus.find_element(By.CLASS_NAME, "travels.lh-24.f-bold.d-color").text
                except NoSuchElementException:
                    bus_info['Bus_Name'] = np.nan

                try:
                    bus_info['Bus_Type'] = bus.find_element(By.CLASS_NAME, "bus-type.f-12.m-top-16.l-color.evBus").text
                except NoSuchElementException:
                    bus_info['Bus_Type'] = np.nan

                try:
                    bus_info['Departing_Time'] = bus.find_element(By.CLASS_NAME, "dp-time.f-19.d-color.f-bold").text
                except NoSuchElementException:
                    bus_info['Departing_Time'] = np.nan

                try:
                    bus_info['Duration'] = bus.find_element(By.CLASS_NAME, "dur.l-color.lh-24").text
                except NoSuchElementException:
                    bus_info['Duration'] = np.nan

                try:
                    bus_info['Reaching_Time'] = bus.find_element(By.CLASS_NAME, "bp-time.f-19.d-color.disp-Inline").text
                except NoSuchElementException:
                    bus_info['Reaching_Time'] = np.nan

                try:
                    bus_info['Star_Rating'] = bus.find_element(By.CLASS_NAME, "rating-sec.lh-24").text
                except NoSuchElementException:
                    bus_info['Star_Rating'] = np.nan

                try:
                    bus_info['Price'] = bus.find_element(By.CLASS_NAME, "fare.d-block").text.replace('INR ', '')
                except NoSuchElementException:
                    bus_info['Price'] = np.nan

                try:
                    seats_available_text = bus.find_element(By.CLASS_NAME, "column-eight.w-15.fl").text
                    bus_info['Seats_Available'] = seats_available_text.split()[0].strip()
                except NoSuchElementException:
                    bus_info['Seats_Available'] = np.nan

                bus_data.append(bus_info)
                print(bus_info)

            print('Bus details collected')

        except NoSuchElementException:
            print("ERROR while collecting bus elements")


    collect_route_details()
    
    print('Collected route names')
    print('Collected route links')   #The function collects bus details for a each route by first finding all bus elements in the page. It then iterates through each bus element, extracting information such as bus name, type, departure time, and price, and stores these details in a list. also, it initializes lists to keep track of route names and their corresponding links and calls a function to gather and process route details, including collecting bus data for each route.


    def scroll_upto_down():
        scrolling = True
        while scrolling:
            old_page_source = driver.page_source
            body = driver.find_element(By.TAG_NAME, "body")
            for _ in range(10): 
                body.send_keys(Keys.PAGE_DOWN)
                time.sleep(1)  
            new_page_source = driver.page_source
            if new_page_source == old_page_source:
                scrolling = False       # Function to scroll down the page we can where we need

    if route_links:
        try:
            for route_name, route_link in zip(route_names, route_links):
                driver.get(route_link)
                print(f"get in to: {route_link}")
                time.sleep(5)
                
                next_day_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "icon.icon-right"))).click()
                time.sleep(10)
                print('Clicked next day button')
                
                viewbuses_button = driver.find_elements(By.CLASS_NAME, "p-left-10.icon.icon-down")
                if len(viewbuses_button) == 2: 
                    print('Found two buttons')
                    viewbuses_button2 = wait.until(EC.element_to_be_clickable((By.XPATH,'//*[@id="result-section"]/div[2]/div/div[2]/div/div[4]/div[2]'))).click()
                    time.sleep(10)
                    print('Clicked button 2')
                    viewbuses_button1 = wait.until(EC.presence_of_element_located((By.XPATH, "//div[contains(@class,'clearfix srp-data')]//div//div[1]//div[1]//div[2]//div[1]//div[4]//div[2]"))).click()
                    print('Clicked button 1')
                    time.sleep(2)
                    scroll_upto_down()
                    print('Scrolled up to down')
                    collect_bus_elements(route_name, route_link)
                    print('Collected bus elements')
                elif len(viewbuses_button) == 1:
                    print('Found only one button')
                    time.sleep(10)
                    a_viewbuses_button = wait.until(EC.element_to_be_clickable((By.XPATH,"//div[@class='button']"))).click()
                    print('Clicked only one button')
                    scroll_upto_down()
                    print('Scrolled up to down')
                    collect_bus_elements(route_name, route_link)
                    print('Collected bus elements')
                else:
                    len(viewbuses_button) == 0
                    print('Found no button')
                    time.sleep(10)
                    next_day_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "icon.icon-right"))).click()
                    print('Clicked next day button')
                    time.sleep(2)
                    scroll_upto_down()
                    print('Scrolled up to down')
                    collect_bus_elements(route_name, route_link)
                    print('Collected bus elements')
        except:
            print(f"ERROR get in to link {route_links}:") # this snippets main work is get into every link in route_link click next day then only we will get lots of bus data then checks how many view_buses button are there in link if viewbuses are 2 firstly it clicks second button and wait for 10 seconds and click first view_buses button after called scroll_upto_down it will do its part of work  after that we have to call collect_bus_elements(route_name, route_link)
,  likewise it will do if there is only one link click it then do scroll function then collect_bus_elements(route_name, route_link)  and if there is no view buses button it'll do scroll and collect_bus_elements(route_name, route_link) .   

    try:
        df = pd.DataFrame(bus_data)
        df.to_csv('APSRTC.csv', index=False)
        print("data saved to APSRTC.csv")
    except:
        print("ERROR WHILE CSV TO DF")      # convert the list of dictionaries to a DataFrame and save it to a CSV file


finally:
    # Close the browser after a delay
    time.sleep(21)
    driver.quit()  # final error check 
```

#### 2.code for push csv to sql 
Sqlalchamy  is used  For pushing data to sql here. 
```py
import pandas as pd
from sqlalchemy import create_engine, Table, Column, Integer, String, Float, Time, MetaData
from sqlalchemy.sql import text  # these are required packages  & modules 

engine = create_engine('mysql+mysqlconnector://root:12345678@localhost/')   # create the sqlalchamy engine to connect to mysql db

with engine.connect() as conn:
    conn.execute(text("CREATE DATABASE IF NOT EXISTS red_bus"))   # connect to the mysql db and create a new database if it doesn't exist

engine = create_engine('mysql+mysqlconnector://root:12345678@localhost/red_bus')   # Update the engine to connect to the newly created 'red_bus' database

df = pd.read_csv(r"C:\Users\GANESH\OneDrive\Desktop\Red_Bus\APSRTC.csv")   # Read the CSV file containing bus data into a Pandas DataFrame


df_cleaned = df.dropna()   # Drop rows if the row has 'NONE' in the DataFrame


df_cleaned.columns = [
    'route_name',  
    'route_link',  
    'busname',    
    'bustype',     
    'departing_time', 
    'duration',   
    'reaching_time',
    'star_rating', 
    'price',     
    'seats_available'
]    # Rename the columns of the DataFrame same like database columns  


metadata = MetaData()   # initialize the metadata object, which will contain table definitions


bus_routes_table = Table(
    'bus_routes', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('route_name', String(255)),
    Column('route_link', String(255)), 
    Column('busname', String(255)),   
    Column('bustype', String(50)),    
    Column('departing_time', Time),    
    Column('duration', String(50)),  
    Column('reaching_time', Time),    
    Column('star_rating', Float),     
    Column('price', Float),           
    Column('seats_available', Integer) 
)   # defining the 'bus_routes' table with columns matching the cleaned DataFrame


with engine.connect() as conn:
    metadata.create_all(conn)   # Create the 'bus_routes' table in the 'red_bus' database if it doesn't already exist


df_cleaned.to_sql('bus_routes', con=engine, if_exists='append', index=False)   # inserting the cleaned DataFrame data into the 'bus_routes' table, appending to existing data


with engine.connect() as conn:
    result = conn.execute(text('SELECT * FROM bus_routes LIMIT 10'))
    rows = result.fetchall()
    for row in rows:   # to check the data inserting by printing the first 10 rows from the 'bus_routes' table

        print(row)  # Print 10 rows from the database to check

print("Data insert is done")  # Print a confirmation message after data insertion

```
```py

```



