import streamlit as st
import pandas as pd
import plotly.express as px
import os
import streamlit.components.v1 as components
import numpy as np
from datetime import date, datetime # For date slider

# --- Page Configuration ---
st.set_page_config(layout="wide", page_title="Swiss Mortality & Population Trends")

# --- Inject CSS to always show sidebar toggle ---
st.markdown("""
<style>
    button[kind="header"][aria-label="Menu"] {
        opacity: 1 !important; 
        visibility: visible !important; 
    }
</style>
""", unsafe_allow_html=True)


st.title("Swiss Mortality & Population Trends")

# --- Data Loading Functions ---
@st.cache_data
def load_weekly_deaths_data(file_path):
    try:
        df = pd.read_csv(file_path, delimiter=';')
        df['Ending_Date'] = pd.to_datetime(df['Ending'], format='%d.%m.%Y', errors='coerce')
        df['Date_Only'] = df['Ending_Date'].dt.date 
        numeric_cols = ['NoDeaths_EP', 'Expected', 'LowerB', 'UpperB']
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        df['Diff'] = df['Diff'].replace('.', pd.NA)
        df['Diff'] = pd.to_numeric(df['Diff'], errors='coerce')
        if 'Age' in df.columns:
            df['Age'] = df['Age'].str.strip()
        df.dropna(subset=['Ending_Date'], inplace=True)
        df = df.sort_values(by=['Ending_Date', 'Year', 'Week']).reset_index(drop=True)
        return df
    except FileNotFoundError:
        st.error(f"Error: Weekly deaths file not found at '{file_path}'.")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error loading weekly deaths data: {e}")
        return pd.DataFrame()

@st.cache_data
def load_absolute_deaths_data(file_path):
    try:
        df = pd.read_csv(file_path, delimiter=',')
        if 'X.1' in df.columns:
            df.rename(columns={'X.1': 'Year'}, inplace=True)
        elif df.columns[0].isdigit() or (df.columns[0].lower() == 'year' and len(df.columns[0])==4 ):
            df.rename(columns={df.columns[0]: 'Year'}, inplace=True)
        else:
            st.warning("Could not identify Year column in absolute deaths data. Please check column names.")
            return pd.DataFrame()

        df['Year'] = pd.to_numeric(df['Year'], errors='coerce').astype('Int64')
        numeric_cols_abs = ['Men', 'Women']
        for col in numeric_cols_abs:
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
def load_mortality_rate_per_100000_inhabitants(file_path):
    """Loads yearly mortality rate data per 100,000 by gender."""
    try:
        df = pd.read_csv(
            file_path, 
            delimiter=',',
            decimal=',' 
        ) 
        if 'X.1' in df.columns:
            df.rename(columns={'X.1': 'Year'}, inplace=True)
        elif df.columns[0].isdigit() or (df.columns[0].lower() == 'year' and len(df.columns[0])==4 ):
            df.rename(columns={df.columns[0]: 'Year'}, inplace=True)
        else:
            st.warning("Could not identify 'Year' column in mortality rate data.")
            return pd.DataFrame()

        df['Year'] = pd.to_numeric(df['Year'], errors='coerce').astype('Int64')
        rate_columns = ['Men', 'Women']
        for col in rate_columns:
            if col in df.columns:
                if df[col].dtype == 'object': # Should be handled by decimal=',' but for safety
                     df[col] = pd.to_numeric(df[col].str.replace(",","."), errors='coerce') 
                elif not pd.api.types.is_numeric_dtype(df[col]):
                     df[col] = pd.to_numeric(df[col], errors='coerce')
            else:
                st.warning(f"Rate column '{col}' not found in mortality rate data.")
                df[col] = pd.NA
        
        df.dropna(subset=['Year'], inplace=True)
        df = df.sort_values(by='Year').reset_index(drop=True)
        return df
    except FileNotFoundError:
        st.error(f"Error: Mortality rate file not found at '{file_path}'.")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"An error occurred while loading mortality rate data: {e}")
        return pd.DataFrame()


# --- Define File Paths ---
data_folder = "data"
file_weekly_deaths = os.path.join(data_folder, "Weekly_number_of_deaths.csv")
file_absolute_deaths = os.path.join(data_folder, "Deaths_Absolute_number.csv")
file_mortality_rate_per_100000_inhabitants = os.path.join(data_folder, "Mortality_rate_per_100000_inhabitants.csv")

# --- Load Data ---
df_weekly = load_weekly_deaths_data(file_weekly_deaths)
df_absolute_raw = load_absolute_deaths_data(file_absolute_deaths)
df_relative_csv = load_mortality_rate_per_100000_inhabitants(file_mortality_rate_per_100000_inhabitants)


# --- Helper function for axis range selectors (SIMPLIFIED - NO RESET, Y-MIN 0, Y-MAX +10%) ---
def get_axis_ranges(df, x_col, y_col, graph_key_prefix):
    # --- X-axis (Date/Year) Slider ---
    x_min_data_bound = df[x_col].min()
    x_max_data_bound = df[x_col].max()

    is_datetime_x = x_col == 'Date_Only' 

    # Default values for X-axis sliders (full range of the data for initial display)
    default_x_start = x_min_data_bound
    default_x_end = x_max_data_bound

    if is_datetime_x:
        min_slider_val_x = default_x_start if isinstance(default_x_start, date) else date(2000,1,1)
        max_slider_val_x = default_x_end if isinstance(default_x_end, date) else date(2025,12,31)
        if min_slider_val_x > max_slider_val_x: min_slider_val_x = max_slider_val_x 
        
        # The 'value' argument sets the initial position. Streamlit remembers subsequent user changes for this key.
        x_start_selected, x_end_selected = st.sidebar.slider(
            f"Date Range ({graph_key_prefix})",
            min_value=min_slider_val_x, max_value=max_slider_val_x,
            value=(min_slider_val_x, max_slider_val_x), 
            format="YYYY-MM-DD", key=f"{graph_key_prefix}_x_date_slider" 
        )
        x_start_final = pd.to_datetime(x_start_selected)
        x_end_final = pd.to_datetime(x_end_selected)
    else: 
        min_slider_val_x_num = int(default_x_start) if pd.notna(default_x_start) and np.isscalar(default_x_start) else 2000
        max_slider_val_x_num = int(default_x_end) if pd.notna(default_x_end) and np.isscalar(default_x_end) else 2023
        if min_slider_val_x_num >= max_slider_val_x_num: min_slider_val_x_num = max_slider_val_x_num - 1
        
        x_start_selected, x_end_selected = st.sidebar.slider(
            f"Year Range ({graph_key_prefix})", 
            min_slider_val_x_num, max_slider_val_x_num, 
            (min_slider_val_x_num, max_slider_val_x_num), 
            key=f"{graph_key_prefix}_x_year_slider"
        )
        x_start_final = x_start_selected
        x_end_final = x_end_selected

    # --- Y-axis (Value) Slider ---
    st.sidebar.markdown(f"**Y-Axis Range ({graph_key_prefix})**")

    y_data_max_val = df[y_col].max() if not df[y_col].empty else 1000.0
    y_data_max_val = float(y_data_max_val) if pd.notna(y_data_max_val) else 1000.0

    slider_min_bound_y = 0.0 
    slider_max_bound_y = y_data_max_val * 1.1 if y_data_max_val > 0 else 10.0
    if slider_max_bound_y <= slider_min_bound_y : 
        slider_max_bound_y = slider_min_bound_y + 100 

    default_y_start = slider_min_bound_y 
    default_y_end = slider_max_bound_y   

    data_range_y = slider_max_bound_y - slider_min_bound_y
    step_y = 1.0 
    if data_range_y > 0 :
        is_y_integer_like = (df[y_col].dropna()%1 == 0).all() if not df[y_col].dropna().empty and pd.api.types.is_numeric_dtype(df[y_col]) else False
        if is_y_integer_like and data_range_y < 1000 : step_y = 1.0
        else:
            step_y = data_range_y / 100.0
            if step_y < 0.01 and not is_y_integer_like : step_y = 0.01
            elif step_y < 1 and is_y_integer_like: step_y = 1.0
    if step_y <=0 : step_y = 0.01

    y_min_user, y_max_user = st.sidebar.slider(
        f"Y-Axis Values ({graph_key_prefix})",
        min_value=slider_min_bound_y, max_value=slider_max_bound_y,
        value=(default_y_start, default_y_end), 
        step=step_y if step_y > 0 else None, key=f"{graph_key_prefix}_y_slider" 
    )
    y_range_user = [y_min_user, y_max_user] if y_min_user < y_max_user else [y_min_user, y_max_user + (step_y if step_y > 0 else 0.1)]
    
    return x_start_final, x_end_final, y_range_user

# --- Graph 1: Weekly Deaths by Age Group ---
st.header("Weekly Deaths by Age Group (0-64 vs. 65+)")
if not df_weekly.empty:
    age_groups_to_plot_g1 = ["0-64", "65+"]
    data_for_g1_controls = df_weekly[df_weekly['Age'].isin(age_groups_to_plot_g1)]

    if not data_for_g1_controls.empty and 'Date_Only' in data_for_g1_controls.columns:
        st.sidebar.markdown("---")
        st.sidebar.subheader("Controls for Graph 1 (Weekly Deaths)")
        x_start_g1, x_end_g1, y_range_g1 = get_axis_ranges(data_for_g1_controls, 'Date_Only', 'NoDeaths_EP', "G1") 
        
        plot_df_g1 = data_for_g1_controls[
            (data_for_g1_controls['Ending_Date'] >= x_start_g1) & # pd.to_datetime() removed, x_start_g1 is already datetime
            (data_for_g1_controls['Ending_Date'] <= x_end_g1)  # pd.to_datetime() removed
        ]

        if not plot_df_g1.empty:
            fig_weekly = px.line(plot_df_g1, x='Ending_Date', y='NoDeaths_EP', color='Age',
                                 title='Weekly Deaths (NoDeaths_EP) by Age Group',
                                 labels={'Ending_Date': 'Date', 'NoDeaths_EP': 'Number of Deaths', 'Age': 'Age Group'})
            if y_range_g1:
                fig_weekly.update_layout(yaxis_range=y_range_g1)
            st.plotly_chart(fig_weekly, use_container_width=True, config={'displayModeBar': False})
        else:
            st.warning(f"No weekly data for selected range for Graph 1.")
    elif 'Date_Only' not in data_for_g1_controls.columns and not data_for_g1_controls.empty:
        st.warning("Helper column 'Date_Only' missing for Graph 1 controls. Please check data loading.")
    else:
        st.warning(f"No data for age groups '{', '.join(age_groups_to_plot_g1)}' in weekly data.")
else:
    st.info("Weekly deaths data unavailable for Graph 1.")


# --- Graph 2 ---
st.header("Absolute Yearly Deaths by Gender")
if not df_absolute_raw.empty:
    if 'Men' in df_absolute_raw.columns and 'Women' in df_absolute_raw.columns:
        data_for_g2_controls = df_absolute_raw.melt(id_vars=['Year'], value_vars=['Men', 'Women'],
                                                    var_name='Gender', value_name='Number_of_Deaths')
        data_for_g2_controls.dropna(subset=['Number_of_Deaths'], inplace=True)
        if not data_for_g2_controls.empty:
            st.sidebar.markdown("---")
            st.sidebar.subheader("Controls for Graph 2 (Absolute Yearly)")
            x_start_g2, x_end_g2, y_range_g2 = get_axis_ranges(data_for_g2_controls, 'Year', 'Number_of_Deaths', "G2")
            plot_df_g2 = data_for_g2_controls[
                (data_for_g2_controls['Year'] >= x_start_g2) & (data_for_g2_controls['Year'] <= x_end_g2)
            ]
            if not plot_df_g2.empty:
                fig_absolute = px.line(plot_df_g2, x='Year', y='Number_of_Deaths', color='Gender',
                                       title='Absolute Yearly Deaths: Men vs. Women',
                                       labels={'Year': 'Year', 'Number_of_Deaths': 'Number of Deaths', 'Gender': 'Gender'}, markers=True)
                if y_range_g2: fig_absolute.update_layout(yaxis_range=y_range_g2)
                st.plotly_chart(fig_absolute, use_container_width=True, config={'displayModeBar': False})
            else: st.warning(f"No absolute yearly data for selected range for Graph 2.")
        else: st.warning("No valid data for Graph 2 controls.")
    else: st.warning("Men/Women columns missing for Graph 2.")
else: st.info("Absolute yearly deaths data unavailable for Graph 2.")

# --- Graph 3 ---
st.header("Yearly Mortality Rate per 100,000 Inhabitants")
if not df_relative_csv.empty: # Use df_relative_csv (loaded mortality rates)
    # Assuming df_relative_csv has 'Year', 'Men', 'Women' columns with rates
    if 'Men' in df_relative_csv.columns and 'Women' in df_relative_csv.columns:
        data_for_g3_controls = df_relative_csv.melt(
            id_vars=['Year'], value_vars=['Men', 'Women'], # Use 'Men' and 'Women' as they contain the rates
            var_name='Gender', # Melt into a 'Gender' column
            value_name='Mortality_Rate'
        )
        data_for_g3_controls.dropna(subset=['Mortality_Rate'], inplace=True)
        
        if not data_for_g3_controls.empty:
            st.sidebar.markdown("---")
            st.sidebar.subheader("Controls for Graph 3 (Yearly Rates)")
            x_start_g3, x_end_g3, y_range_g3 = get_axis_ranges(data_for_g3_controls, 'Year', 'Mortality_Rate', "G3")
            
            plot_df_g3 = data_for_g3_controls[
                (data_for_g3_controls['Year'] >= x_start_g3) & (data_for_g3_controls['Year'] <= x_end_g3)
            ]
            if not plot_df_g3.empty:
                fig_rates = px.line(plot_df_g3, x='Year', y='Mortality_Rate', color='Gender', # Color by Gender
                                    title='Yearly Mortality Rate per 100,000: Men vs. Women',
                                    labels={'Year': 'Year', 'Mortality_Rate': 'Mortality Rate per 100,000', 'Gender': 'Gender'}, markers=True)
                if y_range_g3: fig_rates.update_layout(yaxis_range=y_range_g3)
                st.plotly_chart(fig_rates, use_container_width=True, config={'displayModeBar': False})
            else: st.warning(f"No rate data for selected range for Graph 3.")
        else: st.warning("No valid data for Graph 3 controls after melting direct rates.")
    else: st.warning("Required 'Men' or 'Women' columns (with rates) not found in the mortality rate file.")
else: st.info("Mortality rate data (Mortality_rate_per_100000_inhabitants.csv) unavailable for Graph 3.")
