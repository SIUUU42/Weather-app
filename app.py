import streamlit as st
import requests
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
import os
import plotly.express as px

# CONFIG
load_dotenv() 
API_KEY = os.environ.get("API_KEY")
BASE_URL = "https://api.openweathermap.org/data/2.5/forecast"

# Data Fetcher (CACHED)
@st.cache_data(ttl=5)  # cache for 5 seconds
def fetch_weather_data(city, api_key):
    params = {"q": city, "appid": api_key, "units": "metric"}
    response = requests.get(BASE_URL, params=params)
    if response.status_code == 200:
        return response.json()
    return None

def render_weather(city, weather_report):
    current = weather_report["list"][0]
    temp = current["main"]["temp"]
    humidity = current["main"]["humidity"]
    wind = current["wind"]["speed"]
    condition = current["weather"][0]["description"].title()

    st.subheader(f"Current Weather in {city}")
    col1, col2, col3, col4 = st.columns([1,1,1,3])
    col1.metric("🌡 Temp (°C)", f"{temp}")        
    col2.metric("💧 Humidity (%)", f"{humidity}")
    col3.metric("💨 Wind (m/s)", f"{wind}")
    col4.metric("☁ Condition", condition)

    forecast_list = []
    for item in weather_report["list"]:
        dt = datetime.fromtimestamp(item["dt"])
        forecast_list.append({
            "datetime": dt,
            "date": dt.date(),
            "temp": item["main"]["temp"],
            "humidity": item["main"]["humidity"],
            "condition": item["weather"][0]["description"]
        })
    df = pd.DataFrame(forecast_list)

    st.divider()

    st.subheader("5-Day Forecast")

    # Temperature chart
    fig = px.line(
        df,
        x="datetime",
        y="temp",
        title="🌡 Temperature Trend",
        labels={"datetime": "","temp": "Temperature (°C)"}
    )
    fig.update_xaxes(dtick="D1", tickformat="%b %d")
    fig.update_traces(hovertemplate="Time: %{x|%b %d %H:%M}<br>Temp: %{y} °C")
    st.plotly_chart(fig, use_container_width=True)

    # Humidity chart
    fig2 = px.line(
        df,
        x="datetime",
        y="humidity",
        title="💧 Humidity Trend",
        labels={"datetime": "", "humidity": "Humidity (%)"}
    )
    fig2.update_xaxes(dtick="D1", tickformat="%b %d")
    fig2.update_traces(hovertemplate="Time: %{x|%b %d %H:%M}<br>Humidity: %{y} %")
    st.plotly_chart(fig2, use_container_width=True)




st.set_page_config(page_title="Weather App")

st.title("🌦 Weather Dashboard")
st.write("Check current weather and 5-day forecast for any city.")

with st.form(key="data"):
    city = st.text_input("Enter city name", "Kolkata")
    submit = st.form_submit_button(label="Fetch Weather")

if submit:
    data = fetch_weather_data(city, API_KEY)
    if data:
        render_weather(city, data)
    else:
        st.error("Invalid City Name or API error.")
