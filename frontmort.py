import streamlit as st
import numpy as np
import pandas as pd
import matplotlib as mp
import plotly.express as px

st.set_page_config(page_title="Mortality", page_icon=":bar_chart:", layout="wide")

st.title(":bar_chart: Mortality in switzerland")

#List of all possible Charts

chartnames = ["Absolute Mortality", "Mortality per 100'000", "Mortality Men vs Women", "Men vs Women Mortality per 100'000"]



chart = st.sidebar.multiselect("Pick the chart",chartnames)

#Auskommentiert weil noch nicht funktional

if "Absolute Mortality" in chart:
    data = pd.read_csv("data/Deaths_Absolute_number.csv")
    data["Datum"] = pd.to_datetime(data["X.1"], format="%Y")
    startDate = data["Datum"].min()
    endDate = data["Datum"].max()

    col1, col2 = st.columns(2)
    with col1:
        date1 = pd.to_datetime(st.date_input("Start Date", startDate, key="abs_start"))
    with col2:
        date2 = pd.to_datetime(st.date_input("End Date", endDate, key="abs_end"))

    #data = data[(data["Datum"] >= date1) & (data["Datum"] <= date2)].copy()
    
    # Daten filtern
    filtered = data[(data["Datum"] >= date1) & (data["Datum"] <= date2)].copy()

    # Gesamt-Sterblichkeit berechnen
    filtered["Total"] = filtered["Men"] + filtered["Women"]

    # Liniendiagramm erstellen
    fig = px.line(filtered, x="Datum", y="Total", title="Absolute Mortality per Year", labels={
        "Datum": "Year",
        "Total": "Total Deaths"
    })

    st.plotly_chart(fig, use_container_width=True)


if "Mortality per 100'000" in chart:
    data = pd.read_csv(
    "data/Mortality_rate_per_100000_inhabitants.csv",
    sep=",",            # explizit: Komma ist Trennzeichen
    quotechar='"',      # die Zahlen sind in Anführungszeichen
    decimal=",",        # das Komma ist Dezimaltrennzeichen
    encoding="utf-8"    # optional – wenn nötig
    )


    data["Datum"] = pd.to_datetime(data["X.1"], format="%Y")
    startDate = data["Datum"].min()
    endDate = data["Datum"].max()

    col1, col2 = st.columns(2)
    with col1:
        date3 = pd.to_datetime(st.date_input("Start Date", startDate, key="rate_start"))
    with col2:
        date4 = pd.to_datetime(st.date_input("End Date", endDate, key="rate_end"))

    filtered = data[(data["Datum"] >= date3) & (data["Datum"] <= date4)].copy()
    data["Men"] = pd.to_numeric(data["Men"], errors="coerce")
    data["Women"] = pd.to_numeric(data["Women"], errors="coerce")

    filtered["Total"] = filtered["Men"] + filtered["Women"]

    fig = px.line(filtered, x="Datum", y="Total", title="Mortality Rate per 100,000", labels={
        "Datum": "Year",
        "Total": "Deaths per 100,000"
    }, range_y=[0, None])

    st.plotly_chart(fig, use_container_width=True)
    





if "Mortality Men vs Women" in chart:
    data = pd.read_csv("data/Deaths_Absolute_number.csv")
    data["Datum"] = pd.to_datetime(data["X.1"], format="%Y")
    startDate = data["Datum"].min()
    endDate = data["Datum"].max()

    col1, col2 = st.columns(2)
    with col1:
        date5 = pd.to_datetime(st.date_input("Start Date", startDate, key="menvswomen_start"))
    with col2:
        date6 = pd.to_datetime(st.date_input("End Date", endDate, key="menvswomen_end"))

    # Daten filtern
    filtered = data[(data["Datum"] >= date5) & (data["Datum"] <= date6)].copy()

    # Liniendiagramm mit zwei Linien: Männer und Frauen
    fig = px.line(
        filtered,
        x="Datum",
        y=["Men", "Women"],
        title="Mortality Men vs Women",
        labels={
            "Datum": "Year",
            "value": "Deaths",
            "variable": "Gender"
        }
    )

    st.plotly_chart(fig, use_container_width=True)

if "Men vs Women Mortality per 100'000" in chart:
    # CSV einlesen – beachte Trennzeichen & Dezimaltrennung
    data = pd.read_csv(
        "data/Mortality_rate_per_100000_inhabitants.csv",
        sep=",",
        quotechar='"',
        decimal=",",
        encoding="utf-8"
    )

    data["Datum"] = pd.to_datetime(data["X.1"], format="%Y")
    data["Men"] = pd.to_numeric(data["Men"], errors="coerce")
    data["Women"] = pd.to_numeric(data["Women"], errors="coerce")

    startDate = data["Datum"].min()
    endDate = data["Datum"].max()

    col1, col2 = st.columns(2)
    with col1:
        date7 = pd.to_datetime(st.date_input("Start Date", startDate, key="rate_gender_start"))
    with col2:
        date8 = pd.to_datetime(st.date_input("End Date", endDate, key="rate_gender_end"))

    # Daten filtern
    filtered = data[(data["Datum"] >= date7) & (data["Datum"] <= date8)].copy()

    # Liniendiagramm: Männer vs Frauen
    fig = px.line(
        filtered,
        x="Datum",
        y=["Men", "Women"],
        title="Men vs Women Mortality Rate per 100,000",
        labels={
            "Datum": "Year",
            "value": "Deaths per 100,000",
            "variable": "Gender"
        },
        range_y=[0, None]
    )

    st.plotly_chart(fig, use_container_width=True)

