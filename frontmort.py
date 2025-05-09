import streamlit as st
import pandas as pd
import plotly.express as px


st.set_page_config(page_title="Mortality in Switzerland", layout="wide")


# injects custom CSS rules
st.markdown("""
<style>
body {
    font-family: Arial, sans-serif;
}
.stApp > header {
    background-color: transparent;
}
.st-emotion-cache-16txtl3 {
    padding-top: 2rem; # Adjust top padding of main content area
}
</style>
""", unsafe_allow_html=True)


# Load and prepare datasets
@st.cache_data 
def load_absolute_data(file_path):
    """Loads and preprocesses absolute death number data."""
    data = pd.read_csv(file_path)
    data["Datum"] = pd.to_datetime(data["X.1"], format="%Y") 
    data["Total"] = data["Men"] + data["Women"]
    return data

@st.cache_data
def load_rate_data(file_path):
    """Loads and preprocesses mortality rate data."""
    data = pd.read_csv(
        file_path,
        sep=",",
        quotechar='"',
        decimal=",",
        encoding="utf-8"
    )
    data["Datum"] = pd.to_datetime(data["X.1"], format="%Y")
    data["Men"] = pd.to_numeric(data["Men"], errors="coerce")
    data["Women"] = pd.to_numeric(data["Women"], errors="coerce")
    data["Total"] = data["Men"] + data["Women"] 
    return data

# Initial Loading
absolute_data_df = load_absolute_data("data/Deaths_Absolute_number.csv")
rate_data_df = load_rate_data("data/Mortality_rate_per_100000_inhabitants.csv")

#Sidebar naviation 
st.sidebar.header(" Chart Controls")

chart_names = [
    "Absolute Mortality Over Time",
    "Mortality Rate per 100,000 Over Time",
    "Absolute Mortality: Men vs. Women",
    "Mortality Rate per 100,000: Men vs. Women"
]
selected_charts = st.sidebar.multiselect("Select Charts to Display:", chart_names, default=[chart_names[0]]) # Default to one chart

st.sidebar.header(" Global Date Filter")
min_date_overall = absolute_data_df["Datum"].min()
max_date_overall = absolute_data_df["Datum"].max()

global_start_date = pd.to_datetime(st.sidebar.date_input(
    "Start Date",
    min_date_overall,
    min_value=min_date_overall,
    max_value=max_date_overall,
    key="global_start_date"
))
global_end_date = pd.to_datetime(st.sidebar.date_input(
    "End Date",
    max_date_overall,
    min_value=min_date_overall,
    max_value=max_date_overall,
    key="global_end_date"
))

if global_start_date > global_end_date:
    st.sidebar.error("Error: End date must be after start date.")
    st.stop()


# Main Page Title and Introduction
st.title("Mortality Trends in Switzerland")
st.markdown("Explore various mortality metrics over time. Use the sidebar to select charts and filter by date.")
st.markdown("---")



#Style Configurations for consistency and Layout
COMMON_LAYOUT_ARGS = {
    "font": dict(family="Arial, sans-serif", size=12, color="#333333"),
    "title_x": 0.5,
    "title_font_size": 18,
    "legend_title_text": "Category",
    "hovermode": "x unified"
}

GENDER_COLOR_MAP = {"Men": "#1f77b4", "Women": "#ff7f0e"}


# Add Annotation
def add_covid_annotation_if_in_range(fig, year_to_annotate, data_series, date_column, value_column_for_positioning):
    """Adds an annotation for a specific year if it's within the filtered data's range."""
    if data_series.empty or date_column not in data_series.columns:
        return

    min_data_year = data_series[date_column].min().year
    max_data_year = data_series[date_column].max().year
    
    if not (min_data_year <= year_to_annotate <= max_data_year):
        return

    y_val = None
    if value_column_for_positioning in data_series.columns and pd.api.types.is_numeric_dtype(data_series[value_column_for_positioning]):
        year_data = data_series[data_series[date_column].dt.year == year_to_annotate]
        if not year_data.empty:
            y_val = year_data[value_column_for_positioning].mean()
        else:
            y_val = data_series[value_column_for_positioning].quantile(0.75)
    else:
        numeric_cols = data_series.select_dtypes(include=pd.np.number).columns
        if len(numeric_cols) > 0:
             y_val = data_series[numeric_cols[0]].quantile(0.75)


    if y_val is not None:
        fig.add_annotation(
            x=pd.to_datetime(f"{year_to_annotate}-01-01"),
            y=y_val,
            text=f"COVID-19 Pandemic Impact (from {year_to_annotate})",
            showarrow=True,
            arrowhead=2,
            ax=0,
            ay=-60,
            font=dict(size=10, color="black"),
            bgcolor="rgba(255,235,59,0.7)",
            bordercolor="grey",
            borderwidth=1
        )

if not selected_charts:
    st.info("Please select at least one chart from the sidebar to display data.")

#Render Each Graph if in selected Charts
if "Absolute Mortality Over Time" in selected_charts:
    st.subheader("Absolute Mortality Over Time")
    filtered_df = absolute_data_df[
        (absolute_data_df["Datum"] >= global_start_date) &
        (absolute_data_df["Datum"] <= global_end_date)
    ].copy()

    if not filtered_df.empty:
        min_yr = filtered_df["Datum"].dt.year.min()
        max_yr = filtered_df["Datum"].dt.year.max()

        fig = px.line(
            filtered_df,
            x="Datum",
            y="Total",
            labels={"Datum": "Year", "Total": "Total Number of Deaths"}
        )
        fig.update_layout(
            title_text=f"<b>Total Absolute Deaths ({min_yr}–{max_yr})</b>",
            **COMMON_LAYOUT_ARGS
        )
        fig.update_traces(line=dict(color="#0072B2", width=2.5))
        add_covid_annotation_if_in_range(fig, 2020, filtered_df, "Datum", "Total")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning(f"No data available for 'Absolute Mortality Over Time' in the selected date range ({global_start_date.year}–{global_end_date.year}).")


if "Mortality Rate per 100,000 Over Time" in selected_charts:
    st.subheader("Mortality Rate per 100,000 Over Time")
    filtered_df = rate_data_df[
        (rate_data_df["Datum"] >= global_start_date) &
        (rate_data_df["Datum"] <= global_end_date)
    ].copy()

    if not filtered_df.empty:
        min_yr = filtered_df["Datum"].dt.year.min()
        max_yr = filtered_df["Datum"].dt.year.max()

        fig = px.line(
            filtered_df,
            x="Datum",
            y="Total",
            labels={"Datum": "Year", "Total": "Deaths per 100,000 Inhabitants"}
        )
        fig.update_layout(
            title_text=f"<b>Mortality Rate per 100,000 Inhabitants ({min_yr}–{max_yr})</b>",
            yaxis_rangemode='tozero',
            **COMMON_LAYOUT_ARGS
        )
        fig.update_traces(line=dict(color="#D55E00", width=2.5))
        add_covid_annotation_if_in_range(fig, 2020, filtered_df, "Datum", "Total")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning(f"No data available for 'Mortality Rate per 100,000' in the selected date range ({global_start_date.year}–{global_end_date.year}).")


if "Absolute Mortality: Men vs. Women" in selected_charts:
    st.subheader("Absolute Mortality: Men vs. Women")
    filtered_df = absolute_data_df[
        (absolute_data_df["Datum"] >= global_start_date) &
        (absolute_data_df["Datum"] <= global_end_date)
    ].copy()

    if not filtered_df.empty:
        min_yr = filtered_df["Datum"].dt.year.min()
        max_yr = filtered_df["Datum"].dt.year.max()

        fig = px.line(
            filtered_df,
            x="Datum",
            y=["Men", "Women"],
            labels={"Datum": "Year", "value": "Number of Deaths", "variable": "Gender"},
            color_discrete_map=GENDER_COLOR_MAP
        )
        specific_layout_args = COMMON_LAYOUT_ARGS.copy()
        specific_layout_args["legend_title_text"] = "Gender"

        fig.update_layout(
            title_text=f"<b>Absolute Deaths by Gender ({min_yr}–{max_yr})</b>",
            **specific_layout_args
        )
        add_covid_annotation_if_in_range(fig, 2020, filtered_df, "Datum", "Men")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning(f"No data available for 'Absolute Mortality: Men vs. Women' in the selected date range ({global_start_date.year}–{global_end_date.year}).")


if "Mortality Rate per 100,000: Men vs. Women" in selected_charts:
    st.subheader("Mortality Rate per 100,000: Men vs. Women")
    filtered_df = rate_data_df[
        (rate_data_df["Datum"] >= global_start_date) &
        (rate_data_df["Datum"] <= global_end_date)
    ].copy()

    if not filtered_df.empty:
        min_yr = filtered_df["Datum"].dt.year.min()
        max_yr = filtered_df["Datum"].dt.year.max()

        fig = px.line(
            filtered_df,
            x="Datum",
            y=["Men", "Women"],
            labels={"Datum": "Year", "value": "Deaths per 100,000 Inhabitants", "variable": "Gender"},
            color_discrete_map=GENDER_COLOR_MAP
        )
        specific_layout_args = COMMON_LAYOUT_ARGS.copy()
        specific_layout_args["legend_title_text"] = "Gender"
        
        fig.update_layout(
            title_text=f"<b>Mortality Rate per 100,000 by Gender ({min_yr}–{max_yr})</b>",
            yaxis_rangemode='tozero',
            **specific_layout_args
        )
        add_covid_annotation_if_in_range(fig, 2020, filtered_df, "Datum", "Men")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning(f"No data available for 'Mortality Rate per 100,000: Men vs. Women' in the selected date range ({global_start_date.year}–{global_end_date.year}).")


#Footer
st.markdown("---")
st.caption("Data Source: Bundesamt für Statistik (BFS).")
st.caption("Dashboard created for HSLU Data Visualization for AI and ML course.")
