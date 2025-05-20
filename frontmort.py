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

# --- Define Age Mappings (from your provided images) ---
AGE_LABELS_EN = {
    '_T': 'Total (all ages)', # This specific label might be filtered out later for age distribution
    'Y0T4': '0 to 4 years',
    'Y5T9': '5 to 9 years',
    'Y10T14': '10 to 14 years',
    'Y15T19': '15 to 19 years',
    'Y20T24': '20 to 24 years',
    'Y25T29': '25 to 29 years',
    'Y30T34': '30 to 34 years',
    'Y35T39': '35 to 39 years',
    'Y40T44': '40 to 44 years',
    'Y45T49': '45 to 49 years',
    'Y50T54': '50 to 54 years',
    'Y55T59': '55 to 59 years',
    'Y60T64': '60 to 64 years',
    'Y65T69': '65 to 69 years',
    'Y70T74': '70 to 74 years',
    'Y75T79': '75 to 79 years',
    'Y80T84': '80 to 84 years',
    'Y85T89': '85 to 89 years',
    'Y_GE90': '90 and over',
    '__U': 'Unknown'
}

# Define the desired order of age groups for the chart
# This order will be used for the x-axis of the new bar chart
ORDERED_AGE_GROUP_LABELS = [
    AGE_LABELS_EN[code] for code in [
        'Y0T4', 'Y5T9', 'Y10T14', 'Y15T19', 'Y20T24', 'Y25T29', 'Y30T34',
        'Y35T39', 'Y40T44', 'Y45T49', 'Y50T54', 'Y55T59', 'Y60T64',
        'Y65T69', 'Y70T74', 'Y75T79', 'Y80T84', 'Y85T89', 'Y_GE90', '__U'
    ] if code in AGE_LABELS_EN
]


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

# --- New function to load age-specific data ---
@st.cache_data
def load_deaths_by_age_data(file_path):
    """Loads and preprocesses deaths by age, sex, geo, and time period."""
    try:
        data = pd.read_csv(file_path)
        data["OBS_VALUE"] = pd.to_numeric(data["OBS_VALUE"], errors="coerce")
        data.dropna(subset=["OBS_VALUE"], inplace=True) # Remove rows where OBS_VALUE couldn't be converted

        # Map AGE codes to human-readable labels
        data["Age Group"] = data["AGE"].map(AGE_LABELS_EN)
        
        # Filter out rows where Age Group could not be mapped, if any
        data.dropna(subset=["Age Group"], inplace=True)

        # Convert 'Age Group' to a categorical type with a specific order for plotting
        data["Age Group"] = pd.Categorical(data["Age Group"], categories=ORDERED_AGE_GROUP_LABELS, ordered=True)
        
        # Sort TIME_PERIOD for the slider
        data = data.sort_values("TIME_PERIOD")
        return data
    except FileNotFoundError:
        st.error(f"Error: The data file {file_path} was not found. Please ensure it's in the correct location.")
        return pd.DataFrame() # Return empty DataFrame on error
    except Exception as e:
        st.error(f"An error occurred while loading or processing {file_path}: {e}")
        return pd.DataFrame()


# Initial Loading
absolute_data_df = load_absolute_data("data/Deaths_Absolute_number.csv")
rate_data_df = load_rate_data("data/Mortality_rate_per_100000_inhabitants.csv")
# --- Load the new dataset ---
deaths_by_age_df = load_deaths_by_age_data("data/deaths_by_age_sex_geo_timeperiod.csv")


#Sidebar naviation
st.sidebar.header("Chart Controls")

chart_names = [
    "Absolute Mortality Over Time",
    "Mortality Rate per 100,000 Over Time",
    "Absolute Mortality: Men vs. Women",
    "Mortality Rate per 100,000: Men vs. Women",
    "Age Distribution of Deaths by Week" # <-- New chart name
]
# Default to show the first chart and the new age distribution chart if data is available
default_selection = [chart_names[0]]
if not deaths_by_age_df.empty:
    default_selection.append("Age Distribution of Deaths by Week")

selected_charts = st.sidebar.multiselect(
    "Select Charts to Display:",
    chart_names,
    default=default_selection
)

st.sidebar.header("Global Date Filter (Yearly Data)")
min_date_overall = absolute_data_df["Datum"].min() if not absolute_data_df.empty else pd.to_datetime("2000-01-01")
max_date_overall = absolute_data_df["Datum"].max() if not absolute_data_df.empty else pd.to_datetime("2024-01-01")


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
            # Fallback if the specific year has no data but is in range (e.g. single point)
            y_val = data_series[value_column_for_positioning].quantile(0.75) if not data_series.empty else 0
    else:
        # Fallback if specified value_column is not numeric or not present
        numeric_cols = data_series.select_dtypes(include='number').columns
        if len(numeric_cols) > 0:
             y_val = data_series[numeric_cols[0]].quantile(0.75) if not data_series.empty else 0


    if y_val is not None: # Ensure y_val was set
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
    if not absolute_data_df.empty:
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
    else:
        st.warning("Absolute mortality data is not available.")


if "Mortality Rate per 100,000 Over Time" in selected_charts:
    st.subheader("Mortality Rate per 100,000 Over Time")
    if not rate_data_df.empty:
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
    else:
        st.warning("Mortality rate data is not available.")


if "Absolute Mortality: Men vs. Women" in selected_charts:
    st.subheader("Absolute Mortality: Men vs. Women")
    if not absolute_data_df.empty:
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
            add_covid_annotation_if_in_range(fig, 2020, filtered_df, "Datum", "Men") # Position based on Men's data
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning(f"No data available for 'Absolute Mortality: Men vs. Women' in the selected date range ({global_start_date.year}–{global_end_date.year}).")
    else:
        st.warning("Absolute mortality data is not available.")


if "Mortality Rate per 100,000: Men vs. Women" in selected_charts:
    st.subheader("Mortality Rate per 100,000: Men vs. Women")
    if not rate_data_df.empty:
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
            add_covid_annotation_if_in_range(fig, 2020, filtered_df, "Datum", "Men") # Position based on Men's data
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning(f"No data available for 'Mortality Rate per 100,000: Men vs. Women' in the selected date range ({global_start_date.year}–{global_end_date.year}).")
    else:
        st.warning("Mortality rate data is not available.")


# --- New Chart: Age Distribution of Deaths by Week ---
if "Age Distribution of Deaths by Week" in selected_charts:
    st.subheader("Age Distribution of Deaths by Week")

    if deaths_by_age_df.empty:
        st.warning("Data for age distribution of deaths is not available. Please check the data file.")
    else:
        # Slider for TIME_PERIOD
        # Ensure unique time periods are sorted for the slider
        unique_time_periods = sorted(deaths_by_age_df["TIME_PERIOD"].unique())
        
        if not unique_time_periods:
            st.warning("No time periods available in the age distribution data.")
        else:
            selected_time_period = st.select_slider(
                "Select Time Period (Week):",
                options=unique_time_periods,
                value=unique_time_periods[-1] if unique_time_periods else None # Default to the latest week
            )

            if selected_time_period:
                # Filter data for the selected time period, GEO='CH', SEX='T', and specific age groups (exclude overall total '_T')
                age_dist_data = deaths_by_age_df[
                    (deaths_by_age_df["TIME_PERIOD"] == selected_time_period) &
                    (deaths_by_age_df["GEO"] == "CH") &
                    (deaths_by_age_df["SEX"] == "T") &
                    (deaths_by_age_df["AGE"] != "_T") # Exclude the 'Total' age code, we want distribution
                ].copy() # Use .copy() to avoid SettingWithCopyWarning

                # Ensure 'Age Group' is categorical with the defined order after filtering
                # This is important if filtering reduces the available categories temporarily
                if not age_dist_data.empty:
                    age_dist_data["Age Group"] = pd.Categorical(
                        age_dist_data["Age Group"],
                        categories=ORDERED_AGE_GROUP_LABELS,
                        ordered=True
                    )
                    age_dist_data.sort_values("Age Group", inplace=True)


                if not age_dist_data.empty:
                    fig_age_dist = px.bar(
                        age_dist_data,
                        x="Age Group",
                        y="OBS_VALUE",
                        labels={"Age Group": "Age Group", "OBS_VALUE": "Number of Deaths"},
                        # category_orders={"Age Group": ORDERED_AGE_GROUP_LABELS} # Already handled by pd.Categorical
                    )
                    fig_age_dist.update_layout(
                        title_text=f"<b>Age Distribution of Deaths in Switzerland (CH) - Week {selected_time_period}</b>",
                        xaxis_title="Age Group",
                        yaxis_title="Number of Deaths",
                        **COMMON_LAYOUT_ARGS
                    )
                    fig_age_dist.update_xaxes(tickangle=45) # Improve readability of age group labels
                    st.plotly_chart(fig_age_dist, use_container_width=True)
                else:
                    st.warning(f"No data available for Switzerland (CH), Total Sex (T) for age groups in week {selected_time_period}.")
            else:
                st.info("Please select a time period to display the age distribution.")

#Footer
st.markdown("---")
st.caption("Data Source: Bundesamt für Statistik (BFS).")
st.caption("Dashboard created for HSLU Data Visualization for AI and ML course.")