import streamlit as st
import pandas as pd
import plotly.express as px
import os
import numpy as np
from datetime import date, datetime  # For date slider
from pandas.api.types import is_datetime64_any_dtype, is_numeric_dtype

# ==========================
# 1) Page Configuration
# ==========================
st.set_page_config(
    page_title="Swiss Mortality & Population Trends",
    page_icon="🔬",      
    layout="wide"
)

# ==========================
# 2) Inject Global CSS for Dark Theme & Styling
# ==========================
st.markdown(
    """
    <style>
    /* Use a modern sans-serif font everywhere */
    html, body, [class*="css"] {
        font-family: 'Helvetica Neue', Arial, sans-serif;
    }

    /* Give Plotly charts rounded corners and a subtle shadow */
    .js-plotly-plot .plot-container .svg-container {
        border-radius: 12px !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.3) !important;
    }

    /* Style the sidebar background, add padding, rounded edges */
    [data-testid="stSidebar"] {
        background-color: #262730 !important;  /* Dark secondary background */
        padding-top: 1rem;
        border-top-right-radius: 12px;
        border-bottom-right-radius: 12px;
    }

    /* Header (h1) styling */
    .css-10trblm h1 {
        font-weight: 700;
        font-size: 2.8rem;
        letter-spacing: -1px;
        color: #FFFFFF;  /* White text */
    }

    /* Subheaders (h2, h3) styling */
    .css-10trblm h2, .css-10trblm h3 {
        font-weight: 600;
        color: #DDDDDD;
    }

    /* Make horizontal separators slightly lighter */
    .css-1lcbmhc {
        border-color: rgba(255,255,255,0.1) !important;
    }

    /* Increase tick label size in Plotly charts */
    .plotly .xtick text,
    .plotly .ytick text {
        font-size: 12px !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ==========================
# 3) Force Plotly to Use Dark Template
# ==========================
px.defaults.template = "plotly_dark"

# ==========================
# 4) Page Title & Intro
# ==========================
st.title("Swiss Mortality & Population Trends")
st.write(
    """
    This interactive dashboard visualizes both weekly and yearly mortality data for Switzerland.  
    Use the controls in the sidebar to zoom into specific date or year ranges, and explore trends 
    by age group, gender, mortality rates, and a seasonal heatmap of weekly deaths.
    """
)

# ==========================
# 5) Data Loading Functions
# ==========================
@st.cache_data
def load_weekly_deaths_data(file_path: str) -> pd.DataFrame:
    """
    Loads the weekly number of deaths CSV (semicolon-delimited), parses dates,
    converts numeric columns, and returns a cleaned DataFrame.
    """
    try:
        df = pd.read_csv(file_path, delimiter=';')
        # Parse the "Ending" column into a datetime; german format day.month.year
        df['Ending_Date'] = pd.to_datetime(df['Ending'], format='%d.%m.%Y', errors='coerce')
        df['Date_Only'] = df['Ending_Date'].dt.date  # Extract date for slider
        
        # Convert numeric columns safely
        numeric_cols = ['NoDeaths_EP', 'Expected', 'LowerB', 'UpperB']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        # "Diff" column might contain "." as placeholder; coerce to numeric
        if 'Diff' in df.columns:
            df['Diff'] = df['Diff'].replace('.', pd.NA)
            df['Diff'] = pd.to_numeric(df['Diff'], errors='coerce')

        # Clean up "Age" column by stripping whitespace
        if 'Age' in df.columns:
            df['Age'] = df['Age'].astype(str).str.strip()

        # Drop rows where the date parsing failed
        df.dropna(subset=['Ending_Date'], inplace=True)

        # Sort by date (and Year/Week for safety)
        df = df.sort_values(by=['Ending_Date', 'Year', 'Week']).reset_index(drop=True)
        return df

    except FileNotFoundError:
        st.error(f"Error: Weekly deaths file not found at '{file_path}'.")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error loading weekly deaths data: {e}")
        return pd.DataFrame()


@st.cache_data
def load_absolute_deaths_data(file_path: str) -> pd.DataFrame:
    """
    Loads the absolute yearly deaths CSV (comma-delimited), normalizes the 'Year' column,
    and converts 'Men'/'Women' to numeric. Returns a sorted DataFrame.
    """
    try:
        df = pd.read_csv(file_path, delimiter=',')
        # Identify and rename the Year column if necessary
        if 'X.1' in df.columns:
            df.rename(columns={'X.1': 'Year'}, inplace=True)
        elif df.columns[0].isdigit() or (df.columns[0].lower() == 'year' and len(df.columns[0]) == 4):
            df.rename(columns={df.columns[0]: 'Year'}, inplace=True)
        else:
            st.warning("Could not identify 'Year' column in absolute deaths data. Please check column names.")
            return pd.DataFrame()

        df['Year'] = pd.to_numeric(df['Year'], errors='coerce').astype('Int64')

        # Convert 'Men' and 'Women' columns to numeric if they exist
        for col in ['Men', 'Women']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            else:
                df[col] = pd.NA

        df.dropna(subset=['Year'], inplace=True)
        df = df.sort_values(by='Year').reset_index(drop=True)
        return df

    except FileNotFoundError:
        st.error(f"Error: Absolute deaths file not found at '{file_path}'.")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error loading absolute deaths data: {e}")
        return pd.DataFrame()


@st.cache_data
def load_mortality_rate_per_100000_inhabitants(file_path: str) -> pd.DataFrame:
    """
    Loads the yearly mortality rate per 100,000 inhabitants CSV (comma-delimited, decimal=','),
    normalizes the 'Year' column, converts rate columns to numeric, and returns the DataFrame.
    """
    try:
        df = pd.read_csv(file_path, delimiter=',', decimal=',')
        # Identify and rename the Year column if necessary
        if 'X.1' in df.columns:
            df.rename(columns={'X.1': 'Year'}, inplace=True)
        elif df.columns[0].isdigit() or (df.columns[0].lower() == 'year' and len(df.columns[0]) == 4):
            df.rename(columns={df.columns[0]: 'Year'}, inplace=True)
        else:
            st.warning("Could not identify 'Year' column in mortality rate data.")
            return pd.DataFrame()

        df['Year'] = pd.to_numeric(df['Year'], errors='coerce').astype('Int64')

        # Convert 'Men'/'Women' rate columns to numeric (they might use comma as decimal)
        for col in ['Men', 'Women']:
            if col in df.columns:
                if df[col].dtype == 'object':
                    df[col] = pd.to_numeric(df[col].str.replace(",", "."), errors='coerce')
                else:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            else:
                df[col] = pd.NA

        df.dropna(subset=['Year'], inplace=True)
        df = df.sort_values(by='Year').reset_index(drop=True)
        return df

    except FileNotFoundError:
        st.error(f"Error: Mortality rate file not found at '{file_path}'.")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error loading mortality rate data: {e}")
        return pd.DataFrame()


# ==========================
# 6) Define File Paths & Load Data
# ==========================
data_folder = "data"
file_weekly_deaths = os.path.join(data_folder, "Weekly_number_of_deaths.csv")
file_absolute_deaths = os.path.join(data_folder, "Deaths_Absolute_number.csv")
file_mortality_rate = os.path.join(data_folder, "Mortality_rate_per_100000_inhabitants.csv")

df_weekly = load_weekly_deaths_data(file_weekly_deaths)
df_absolute_raw = load_absolute_deaths_data(file_absolute_deaths)
df_relative_csv = load_mortality_rate_per_100000_inhabitants(file_mortality_rate)


# ==========================
# 7) Helper Function: Axis Range Selectors
# ==========================


def get_axis_ranges(df: pd.DataFrame, x_col: str, y_col: str, graph_key_prefix: str):
    """
    Returns (x_start, x_end, [y_min, y_max]) based on the data in df[x_col]/df[y_col].
    - If x_col is a datetime64 column, uses a date slider.
    - If x_col is numeric (e.g. Year), uses an integer slider.
    - y_col always yields a 0–110% numeric slider.
    """

    # --- 1) X-Achse (Datum vs. Numeric) ---
    x_vals = df[x_col].dropna()

    # Fall: datetime-Spalte
    if is_datetime64_any_dtype(x_vals):
        # Min/Max als python.date extrahieren
        x_min = x_vals.min().date() if isinstance(x_vals.min(), pd.Timestamp) else x_vals.min()
        x_max = x_vals.max().date() if isinstance(x_vals.max(), pd.Timestamp) else x_vals.max()
        if x_min > x_max:
            x_min, x_max = x_max, x_min

        x_start, x_end = st.sidebar.slider(
            f"Date Range ({graph_key_prefix})",
            min_value=x_min,
            max_value=x_max,
            value=(x_min, x_max),
            format="YYYY-MM-DD",
            key=f"{graph_key_prefix}_x_date_slider"
        )
        x_start_final = pd.to_datetime(x_start)
        x_end_final   = pd.to_datetime(x_end)

    # Fall: numerische Spalte (z.B. Year)
    elif is_numeric_dtype(x_vals):
        try:
            x_min = int(x_vals.min())
            x_max = int(x_vals.max())
        except:
            x_min = float(x_vals.min())
            x_max = float(x_vals.max())

        if x_min >= x_max:
            x_min, x_max = (x_max-1, x_max) if isinstance(x_max, (int, np.integer)) else (x_max-1, x_max)

        x_start, x_end = st.sidebar.slider(
            f"Year Range ({graph_key_prefix})",
            min_value=x_min,
            max_value=x_max,
            value=(x_min, x_max),
            step=1 if isinstance(x_min, (int, np.integer)) and isinstance(x_max, (int, np.integer)) else None,
            key=f"{graph_key_prefix}_x_year_slider"
        )
        x_start_final = x_start
        x_end_final   = x_end

    else:
        st.error(f"Column '{x_col}' is neither numeric nor datetime.")
        return None, None, None

    # --- 2) Y-Achse (Numeric von 0 bis ca. 110% max) ---
    y_vals = df[y_col].dropna()
    if not y_vals.empty and is_numeric_dtype(y_vals):
        y_max = float(y_vals.max())
        y_min = 0.0
        y_upper_bound = y_max * 1.1 if y_max > 0 else 1.0

        data_range = y_upper_bound - y_min
        if pd.api.types.is_integer_dtype(y_vals) and (data_range < 1000):
            y_step = 1
        else:
            y_step = max(data_range / 100.0, 0.01)

        y_start, y_end = st.sidebar.slider(
            f"Y-Axis Range ({graph_key_prefix})",
            min_value=y_min,
            max_value=y_upper_bound,
            value=(y_min, y_upper_bound),
            step=y_step,
            key=f"{graph_key_prefix}_y_slider"
        )
        y_range_final = [y_start, y_end]
    else:
        y_range_final = [0.0, 1.0]

    return x_start_final, x_end_final, y_range_final


    if is_datetime:
        # Convert to Python date objects if needed
        if isinstance(x_min_data, pd.Timestamp):
            x_min_data = x_min_data.date()
        if isinstance(x_max_data, pd.Timestamp):
            x_max_data = x_max_data.date()

        min_slider_val = x_min_data
        max_slider_val = x_max_data
        if min_slider_val > max_slider_val:
            min_slider_val, max_slider_val = max_slider_val, min_slider_val

        x_start_sel, x_end_sel = st.sidebar.slider(
            f"Date Range ({graph_key_prefix})",
            min_value=min_slider_val,
            max_value=max_slider_val,
            value=(min_slider_val, max_slider_val),
            format="YYYY-MM-DD",
            key=f"{graph_key_prefix}_x_date_slider"
        )
        x_start_final = pd.to_datetime(x_start_sel)
        x_end_final = pd.to_datetime(x_end_sel)
    else:
        # Numeric (Year) slider
        try:
            min_num = int(x_min_data) if pd.notna(x_min_data) else 2000
            max_num = int(x_max_data) if pd.notna(x_max_data) else 2023
        except:
            min_num, max_num = 2000, 2023

        if min_num >= max_num:
            min_num, max_num = max_num - 1, max_num

        x_start_sel, x_end_sel = st.sidebar.slider(
            f"Year Range ({graph_key_prefix})",
            min_value=min_num,
            max_value=max_num,
            value=(min_num, max_num),
            key=f"{graph_key_prefix}_x_year_slider"
        )
        x_start_final = x_start_sel
        x_end_final = x_end_sel

    # --- Determine Y-axis range & slider ---
    y_vals = df[y_col].dropna()
    y_max_data = float(y_vals.max()) if not y_vals.empty else 1000.0
    y_min_bound = 0.0
    y_max_bound = y_max_data * 1.1 if y_max_data > 0 else 10.0
    if y_max_bound <= y_min_bound:
        y_max_bound = y_min_bound + 1.0

    # Determine a reasonable step for the slider
    data_range_y = y_max_bound - y_min_bound
    if data_range_y <= 0:
        step_y = 0.1
    else:
        is_integer_like = False
        if pd.api.types.is_numeric_dtype(df[y_col]) and not y_vals.empty:
            is_integer_like = (y_vals % 1 == 0).all() and data_range_y < 1000
        if is_integer_like:
            step_y = 1.0
        else:
            step_y = data_range_y / 100.0
            if step_y < 0.01:
                step_y = 0.01

    y_start_sel, y_end_sel = st.sidebar.slider(
        f"Y-Axis Range ({graph_key_prefix})",
        min_value=y_min_bound,
        max_value=y_max_bound,
        value=(y_min_bound, y_max_bound),
        step=step_y,
        key=f"{graph_key_prefix}_y_slider"
    )
    y_range_final = [y_start_sel, y_end_sel]

    return x_start_final, x_end_final, y_range_final


# ==========================
# 8) Graph 1: Weekly Deaths by Age Group (0-64 vs. 65+)
# ==========================
st.header("Weekly Deaths by Age Group (0–64 vs. 65+)")
if not df_weekly.empty:
    # Restrict to the two age groups
    age_groups_to_plot = ["0-64", "65+"]
    df_g1 = df_weekly[df_weekly['Age'].isin(age_groups_to_plot)].copy()

    if not df_g1.empty and 'Ending_Date' in df_g1.columns:
        st.sidebar.markdown("---")
        st.sidebar.subheader("Controls for Graph 1 (Weekly Deaths)")
        x_start_g1, x_end_g1, y_range_g1 = get_axis_ranges(df_g1, 'Ending_Date', 'NoDeaths_EP', "G1")


        # Filter by date range
        df_g1_filtered = df_g1[
            (df_g1['Ending_Date'] >= x_start_g1) &
            (df_g1['Ending_Date'] <= x_end_g1)
        ]

        if not df_g1_filtered.empty:
            fig_g1 = px.line(
                df_g1_filtered,
                x='Ending_Date',
                y='NoDeaths_EP',
                color='Age',
                title='Weekly Deaths by Age Group',
                labels={
                    'Ending_Date': 'Date',
                    'NoDeaths_EP': 'Number of Deaths',
                    'Age': 'Age Group'
                },
                template="plotly_dark"
            )
            if y_range_g1:
                fig_g1.update_layout(yaxis_range=y_range_g1)
            st.plotly_chart(fig_g1, use_container_width=True, config={'displayModeBar': False})
        else:
            st.warning("No weekly data available for the selected date range (Graph 1).")
    else:
        st.warning("Required data for Graph 1 is missing or 'Date_Only' column is not present.")
else:
    st.info("Weekly deaths data unavailable for Graph 1.")


# ==========================
# 9) Graph 2: Absolute Yearly Deaths by Gender
# ==========================
st.header("Absolute Yearly Deaths by Gender")
if not df_absolute_raw.empty:
    if 'Men' in df_absolute_raw.columns and 'Women' in df_absolute_raw.columns:
        # Melt to long form for plotting
        df_g2 = df_absolute_raw.melt(
            id_vars=['Year'],
            value_vars=['Men', 'Women'],
            var_name='Gender',
            value_name='Number_of_Deaths'
        )
        df_g2.dropna(subset=['Number_of_Deaths'], inplace=True)

        if not df_g2.empty:
            st.sidebar.markdown("---")
            st.sidebar.subheader("Controls for Graph 2 (Absolute Yearly)")

            x_start_g2, x_end_g2, y_range_g2 = get_axis_ranges(df_g2, 'Year', 'Number_of_Deaths', "G2")

            df_g2_filtered = df_g2[
                (df_g2['Year'] >= x_start_g2) &
                (df_g2['Year'] <= x_end_g2)
            ]

            if not df_g2_filtered.empty:
                fig_g2 = px.line(
                    df_g2_filtered,
                    x='Year',
                    y='Number_of_Deaths',
                    color='Gender',
                    title='Absolute Yearly Deaths: Men vs. Women',
                    labels={
                        'Year': 'Year',
                        'Number_of_Deaths': 'Number of Deaths',
                        'Gender': 'Gender'
                    },
                    markers=True,
                    template="plotly_dark"
                )
                # set x- and y-axis ranges and remove left padding
                fig_g2.update_layout(
                    xaxis=dict(
                        range=[x_start_g2, x_end_g2],    # start exactly bei erstem Jahr, Ende beim letzten
                        autorange=False
                    ),
                    margin=dict(l=10, r=20, t=50, b=50)  # l=10 reduziert den linken Rand auf 10px
                )

                if y_range_g2:
                    fig_g2.update_layout(yaxis_range=y_range_g2)
                st.plotly_chart(fig_g2, use_container_width=True, config={'displayModeBar': False})
            else:
                st.warning("No absolute yearly data available for the selected range (Graph 2).")
        else:
            st.warning("No valid data after processing for Graph 2.")
    else:
        st.warning("Columns 'Men' or 'Women' missing in absolute deaths data (Graph 2).")
else:
    st.info("Absolute yearly deaths data unavailable for Graph 2.")


# ==========================
# 10) Graph 3: Yearly Mortality Rate per 100,000 Inhabitants
# ==========================
st.header("Yearly Mortality Rate per 100,000 Inhabitants")
if not df_relative_csv.empty:
    if 'Men' in df_relative_csv.columns and 'Women' in df_relative_csv.columns:
        df_g3 = df_relative_csv.melt(
            id_vars=['Year'],
            value_vars=['Men', 'Women'],
            var_name='Gender',
            value_name='Mortality_Rate'
        )
        df_g3.dropna(subset=['Mortality_Rate'], inplace=True)

        if not df_g3.empty:
            st.sidebar.markdown("---")
            st.sidebar.subheader("Controls for Graph 3 (Yearly Rates)")

            x_start_g3, x_end_g3, y_range_g3 = get_axis_ranges(df_g3, 'Year', 'Mortality_Rate', "G3")

            df_g3_filtered = df_g3[
                (df_g3['Year'] >= x_start_g3) &
                (df_g3['Year'] <= x_end_g3)
            ]

            if not df_g3_filtered.empty:
                fig_g3 = px.line(
                    df_g3_filtered,
                    x='Year',
                    y='Mortality_Rate',
                    color='Gender',
                    title='Yearly Mortality Rate per 100,000: Men vs. Women',
                    labels={
                        'Year': 'Year',
                        'Mortality_Rate': 'Mortality Rate per 100,000',
                        'Gender': 'Gender'
                    },
                    markers=True,
                    template="plotly_dark"
                )
                fig_g3.update_layout(
                    xaxis=dict(
                        range=[x_start_g3, x_end_g3],
                        autorange=False
                    ),
                    margin=dict(l=10, r=20, t=50, b=50)
                )

                if y_range_g3:
                    fig_g3.update_layout(yaxis_range=y_range_g3)
                st.plotly_chart(fig_g3, use_container_width=True, config={'displayModeBar': False})
            else:
                st.warning("No rate data available for the selected range (Graph 3).")
        else:
            st.warning("No valid data after melting for Graph 3.")
    else:
        st.warning("Columns 'Men' or 'Women' missing in mortality rate data (Graph 3).")
else:
    st.info("Mortality rate data unavailable for Graph 3.")


# ==========================
# 11) Graph 4: Heatmap of Weekly Deaths by Year & Calendar Week (Total)
# ==========================
st.header("Heatmap: Weekly Deaths by Year and Calendar Week (Total)")

@st.cache_data(show_spinner=False)
def load_weekly_totals(path: str) -> pd.DataFrame:
    """
    Reads 'Weekly_number_of_deaths.csv' (semicolon-delimited, skips lines beginning with '#'),
    cleans 'NoDeaths_EP', groups by Year & Week, and returns a pivot table (index=Year, columns=Week).
    """
    try:
        df = pd.read_csv(
            path,
            delimiter=";",
            comment="#",
            parse_dates=["Ending"],
            dayfirst=True,
            dtype={"Year": "Int64", "Week": "Int64"}
        )

        # Clean up 'NoDeaths_EP': strip whitespace, coerce to numeric
        df["NoDeaths_EP"] = df["NoDeaths_EP"].astype(str).str.strip()
        df["NoDeaths_EP"] = pd.to_numeric(df["NoDeaths_EP"], errors="coerce")

        # Drop rows that didn't convert to a valid number
        df = df.dropna(subset=["NoDeaths_EP"])
        df["NoDeaths_EP"] = df["NoDeaths_EP"].astype(int)

        # Group by Year + Week and sum
        df_grouped = (
            df
            .groupby(["Year", "Week"], as_index=False)["NoDeaths_EP"]
            .sum()
            .rename(columns={"NoDeaths_EP": "Deaths"})
        )

        # Pivot so that index=Year, columns=Week
        pivot = df_grouped.pivot(index="Year", columns="Week", values="Deaths")
        pivot = pivot.sort_index(axis=1)  # Sort columns (weeks) ascending
        return pivot

    except FileNotFoundError:
        st.error(f"Error: 'Weekly_number_of_deaths.csv' not found at '{path}'.")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error processing 'Weekly_number_of_deaths.csv': {e}")
        return pd.DataFrame()


# Load the pivoted DataFrame
pivot = load_weekly_totals(file_weekly_deaths)

if (pivot is not None) and (not pivot.empty):
    min_year = int(pivot.index.min())
    max_year = int(pivot.index.max())

    st.sidebar.markdown("---")
    st.sidebar.subheader("Controls for Graph 4 (Heatmap)")

    year_start, year_end = st.sidebar.slider(
        label="Year Range (G4)",
        min_value=min_year,
        max_value=max_year,
        value=(min_year, max_year),
        step=1,
        key="G4_year_slider"
    )

    pivot_filtered = pivot.loc[year_start:year_end]

    if not pivot_filtered.empty:
        fig_g4 = px.imshow(
            pivot_filtered,
            labels={"x": "Calendar Week", "y": "Year", "color": "Deaths"},
            x=pivot_filtered.columns,
            y=pivot_filtered.index,
            aspect="auto",
            origin="lower",
            color_continuous_scale="Turbo",
            title="Seasonal Heatmap: Weekly Deaths (Switzerland)",
            template="plotly_dark"
        )
        fig_g4.update_layout(
            title_font_size=18,
            xaxis_title_font_size=14,
            yaxis_title_font_size=14,
            font_color="white",
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            coloraxis_colorbar=dict(title_font_size=14, tickfont_size=12)
        )
        st.plotly_chart(fig_g4, use_container_width=True, config={"displayModeBar": False})
    else:
        st.warning("No data available for the selected year range (Graph 4).")
else:
    st.info("Weekly_number_of_deaths.csv could not be loaded or is empty (Graph 4).")
