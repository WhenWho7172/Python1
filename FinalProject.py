"""
Class: CS230--Section 003 
Name: Wenbin Wu
Description: (Give a brief description for Exercise name--See below)
I pledge that I have completed the programming assignment independently. 
I have not copied the code from a student or any source.
I have not given my code to any student. 
"""
from datetime import datetime
import pandas as pd
import streamlit as st
import numpy as np
from streamlit_player import st_player
import re
import matplotlib.pyplot as plt
import pydeck as pdk

REGEX = "^(\w|\.|\_|\-)+[@](\w|\_|\-|\.)+[.]\w{2,3}$"

INDEX = []
KEY = []
FARE_AMOUNT = []
PICKUP_DATETIME = []
PICKUP_LONGITUDE = []
PICKUP_LATITUDE = []
DROPOFF_LONGITUDE = []
DROPOFF_LATITUDE = []
PASSENGER_COUNT = []
defalt_people_count = ["1", "2", "3", "4", "5", "6"]
defalt_price = 20

def read_Data():
    rawdata = pd.read_csv("uber.csv", delimiter=",")
    for data in rawdata.values:
        INDEX.append(data[0])
        KEY.append(data[1])
        FARE_AMOUNT.append(data[2])
        PICKUP_DATETIME.append(data[3])
        PICKUP_LONGITUDE.append(data[4])
        PICKUP_LATITUDE.append(data[5])
        DROPOFF_LONGITUDE.append(data[6])
        DROPOFF_LATITUDE.append(data[7])
        PASSENGER_COUNT.append(data[8])

def df():  # Create Dataframe
    data = {'key': KEY,
            'fare_amount': FARE_AMOUNT,
            'pickup_datetime': PICKUP_DATETIME,
            'pickup_longitude': PICKUP_LONGITUDE,
            'pickup_latitude': PICKUP_LATITUDE,
            'dropoff_longitude': DROPOFF_LONGITUDE,
            'dropoff-latitude': DROPOFF_LATITUDE,
            'passenger_count': PASSENGER_COUNT}
    df = pd.DataFrame(data)
    return df

def page0(df):  # Home page
    st.image('im.png')
    st.title('\nPython Final Project (UBER)')
    st.write('')
    st.markdown(
        'Within this assignment, we are expected to develop an interactive data-driven Python-based web application. This application represents a culmination of topics learned throughout this course in spring 2022. The dataset chosen for this project is Uber for its variety of data on ride fares, pick up and drop off locations, and the number of passengers per ride.')
    st.write('\n')
    st.subheader('Not familiar with Uber? Get started with the video below!')
    st.write('\n')

    st_player("https://www.youtube.com/watch?v=tQlgavP5cmo")
    st.write('\n')

    st.subheader('Stay Connected')
    st.markdown('Enjoy your experience? Help us build our next dataset and fill in the following:')

    # for shits and giggles
    name = st.text_input(f'Enter your name ')
    email = st.text_input('Enter your email to join our mailing list')
    consent = st.checkbox('Do you consent to receiving emails')
    if consent:
        if email != "":
            with open('Uber_subdata_collection', 'a') as f:
                f.writelines(f'{email}, ')
        else:
            st.error("Error! Please enter an Email. ")

    if name and email:
        st.write(f'Thank you {name}, your email is {email}')

def page1(df):
    st.title('Where is Uber Used? 🛫🌎️\n')
    map_df = df.filter(['Index', 'pickup_longitude', 'pickup_latitude', 'Fare_Amount'])
    view_area = pdk.ViewState(latitude=map_df["pickup_latitude"].mean(),
                              longitude=map_df["pickup_longitude"].mean(),
                              zoom=2)
    layer = pdk.Layer('ScatterplotLayer',
                      data=map_df, get_position='[pickup_longitude, pickup_latitude]',
                      get_radius=7000,
                      get_color=[255, 0, 255],
                      pickable=True)
    tool_tip = {'html': f'Fare:<br/> <b>{"Pickup_Location"}</b>',
                'style': {'backgroundColor': 'blue', 'color': 'white'}}
    map = pdk.Deck(map_style='mapbox://styles/mapbox/light-v9',
                   initial_view_state=view_area,
                   layers=[layer],
                   tooltip=tool_tip)

    st.pydeck_chart(map)

def page2(df):
    st.title(f'{"Quantity traveled Data Charts"}')
    rawdata = df
    del rawdata['key']
    print(rawdata.keys())

    date_st = [dates.strip("UTC ") for dates in rawdata['pickup_datetime']]
    rawdata['pickup_datetime'] = [datetime.strptime(dates, '%Y-%m-%d %H:%M:%S') for dates in date_st]
    rawdata['pickup_datetime'] = rawdata['pickup_datetime'].dt.date

    rawdata.sort_values(by='pickup_datetime', ascending=True, inplace=True, ignore_index=True)
    rawdata.head(10)

    lat_pickup = rawdata['pickup_latitude']
    lon_pickup = rawdata['pickup_longitude']
    lat2_dropoff = rawdata['dropoff-latitude']
    lon2_dropoff = rawdata['dropoff_longitude']
    rawdata['distance'] = np.sqrt((lat_pickup - lat2_dropoff) ** 2 + (lon_pickup - lon2_dropoff) ** 2)
    rawdata.tail(10)

    print(rawdata)

    start = pd.to_datetime("2014-01-01").date()
    end = pd.to_datetime("2014-01-31").date()
    trip = rawdata.loc[(rawdata['pickup_datetime'] >= start) & (rawdata['pickup_datetime'] <= end)]

    print(trip)
    count = rawdata['passenger_count']
    print(count)
    print(len(count))

    dst1 = list(filter(lambda num: num == 1, count))
    dst2 = list(filter(lambda num: num == 2, count))
    dst3 = list(filter(lambda num: num == 3, count))
    dst4 = list(filter(lambda num: num == 4, count))
    dst5 = list(filter(lambda num: num == 5, count))
    dst6 = list(filter(lambda num: num == 6, count))

    dta = [len(dst1), len(dst2),len(dst3), len(dst4), len(dst5), len(dst6)]

    print(dta)
    print("after")

    chart_data = pd.DataFrame(
     dta,
     columns=["Count"])

    st.bar_chart(chart_data)

    fare_low = trip['fare_amount'].quantile(0.05)
    fare_hi = trip['fare_amount'].quantile(0.95)
    dist_low = trip['distance'].quantile(0.05)
    dist_hi = trip['distance'].quantile(0.95)

    trip_outliers = trip[(trip["distance"] < dist_hi) & (trip["distance"] > dist_low) & (
                trip['fare_amount'] < fare_hi) & (trip['fare_amount'] > fare_low)]
    trip_filtered = trip_outliers

    print(trip_filtered)
    width = st.slider('Width', min_value=8, max_value=15)
    length = st.slider('Length', min_value=6, max_value=15)
    fig, ax1 = plt.subplots(1, 2, figsize=(width, length))
    trip_filtered.plot.scatter(x='distance',
                               y='fare_amount',
                               s=5,
                               ax=ax1[0],
                               title="Outliers excluded",
                               xlabel="Distance(km)",
                               ylabel="Fare amount (USD)")
    trip.plot.scatter(x='distance',
                            y='fare_amount',
                            s=5,
                            ax=ax1[1],
                            title="With Outliers",
                            xlabel="Distance(km)",
                            ylabel="Fare amount (USD)")
    plt.suptitle("Fare amount vs. Travel distance", fontsize=14)
    st.pyplot(fig)

    cost = df['fare_amount']
    print(cost)

def page3():
    st.header("Download Data Form")
    st.markdown("Please complete the following fields to access the form. Thank you!")
    field_1 = st.text_input("Your Name")
    if field_1 != '':
        field_2 = st.text_input("Your Email Address", help="example@mail.com")
        if (re.search(REGEX, field_2)):
            field_3 = st.slider('Your Age:', min_value=1, max_value=100)
            if field_3 < 18:
                st.error("Error! You are too young to receive access. Come back when you are older.")
            elif field_3 >= 18:
                st.write(
                    'Thank you for your cooperation below is https://www.kaggle.com/datasets/yasserh/uber-fares-dataset')


read_Data()
df()
# ---------------------------------------------------------
# Streamlit Navigation
# ---------------------------------------------------------
st.sidebar.title("Navigation")
selection = st.sidebar.radio("Go to:", ["🏠 Home", "🗺️ Map", "📈 Chart", "📁 Access Data"])
if selection == "🏠 Home":
    page0(df)
if selection == "🗺️ Map":
    page1(df())
if selection == "📈 Chart":
    page2(df())
if selection == "📁 Access Data":
    page3()

st.sidebar.markdown('---')
st.sidebar.markdown(':information_source: Details')
with st.sidebar:
    data_des = st.checkbox('📃 Dataset Description')
    if data_des:
        st.write(
            f"The project is about on world's largest taxi company Uber inc. Uber delivers service to hundreds-of thousands of customers daily. With its assounding growth it has become really important to manage their data properly to come up with new business ideas to get best results. Eventually, it becomes really important to analysis the fare prices and determine if this dominating company is worth it.")
    data_dic = st.checkbox('📕 Data Dictionary')
    if data_dic:
        st.write({'key': 'KEY',
                  'fare_amount': 'FARE_AMOUNT',
                  'pickup_datetime': 'PICKUP_DATETIME',
                  'longitude': 'PICKUP_LONGITUDE',
                  'latitude': 'PICKUP_LATITUDE',
                  'dropoff_longitude': 'DROPOFF_LONGITUDE',
                  'dropoff-latitude': 'DROPOFF_LATITUDE',
                  'passenger_count': 'PASSENGER_COUNT'})
