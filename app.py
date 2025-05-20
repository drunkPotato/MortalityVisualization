import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- Page Configuration ---
st.set_page_config(layout="wide", page_title="Swiss Mortality Trends")

st.title("Swiss Mortality Trends")

# --- Data Loading Functions ---

@st.cache_data
def load_weekly_deaths_data(file_path):
    try:
        df = pd.read_csv(file_path, delimiter=';')
        df['Ending_Date'] = pd.to_datetime(df['Ending'], format='%d.%m.%Y', errors='coerce')
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
def load_population_data(file_path):
    """Loads yearly population data."""
    try:
        df = pd.read_csv(file_path, delimiter=';')
        if len(df.columns) >= 2:
            df.rename(columns={df.columns[0]: 'Year', df.columns[1]: 'Population'}, inplace=True)
        else:
            st.error("Population data CSV does not have at least two columns.")
            return pd.DataFrame()

        if df['Year'].dtype == 'object':
            df['Year'] = df['Year'].str.replace('"', '', regex=False)
        df['Year'] = pd.to_numeric(df['Year'], errors='coerce').astype('Int64')

        if df['Population'].dtype == 'object':
            df['Population'] = df['Population'].str.replace('"', '', regex=False)
        df['Population'] = pd.to_numeric(df['Population'], errors='coerce')

        df.dropna(subset=['Year', 'Population'], inplace=True)
        df = df.sort_values(by='Year').reset_index(drop=True)
        return df
    except FileNotFoundError:
        st.error(f"Error: Population file not found at '{file_path}'.")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error loading population data: {e}")
        return pd.DataFrame()

# --- Define File Paths ---
data_folder = "data"
file_weekly_deaths = os.path.join(data_folder, "Weekly_number_of_deaths.csv")
file_absolute_deaths = os.path.join(data_folder, "Deaths_Absolute_number.csv")
file_population = os.path.join(data_folder, "Switzerland_Population.csv")

# --- Load Data ---
df_weekly = load_weekly_deaths_data(file_weekly_deaths)
df_absolute_raw = load_absolute_deaths_data(file_absolute_deaths)
df_population = load_population_data(file_population)

# --- Process Data for Mortality Rates ---
df_absolute_with_rates = pd.DataFrame()

if not df_absolute_raw.empty and not df_population.empty:
    df_merged = pd.merge(df_absolute_raw, df_population, on='Year', how='left')
    if 'Men' in df_merged.columns and 'Women' in df_merged.columns:
        df_merged['Total_Deaths'] = df_merged['Men'].fillna(0) + df_merged['Women'].fillna(0)
    else:
        df_merged['Total_Deaths'] = pd.NA

    if 'Population' in df_merged.columns:
        if 'Men' in df_merged.columns:
            df_merged['Rate_Men'] = df_merged.apply(
                lambda row: (row['Men'] / row['Population']) * 100000 if pd.notna(row['Men']) and pd.notna(row['Population']) and row['Population'] != 0 else pd.NA,
                axis=1
            )
        if 'Women' in df_merged.columns:
            df_merged['Rate_Women'] = df_merged.apply(
                lambda row: (row['Women'] / row['Population']) * 100000 if pd.notna(row['Women']) and pd.notna(row['Population']) and row['Population'] != 0 else pd.NA,
                axis=1
            )
        if 'Total_Deaths' in df_merged.columns:
            df_merged['Rate_Total'] = df_merged.apply(
                lambda row: (row['Total_Deaths'] / row['Population']) * 100000 if pd.notna(row['Total_Deaths']) and pd.notna(row['Population']) and row['Population'] != 0 else pd.NA,
                axis=1
            )
        df_absolute_with_rates = df_merged.copy()
    else:
        st.warning("Population column missing after merge or in population data, cannot calculate rates.")
elif df_absolute_raw.empty:
    st.info("Absolute deaths data could not be loaded. Rates cannot be calculated.")
elif df_population.empty:
    st.info("Population data could not be loaded. Rates cannot be calculated.")


# --- Graph 1: Weekly Deaths by Age Group ---
st.header("Weekly Deaths by Age Group (0-64 vs. 65+)")
if not df_weekly.empty:
    age_groups_to_plot = ["0-64", "65+"]
    plot_df_weekly_combined = df_weekly[df_weekly['Age'].isin(age_groups_to_plot)]
    if not plot_df_weekly_combined.empty:
        fig_weekly = px.line(plot_df_weekly_combined, x='Ending_Date', y='NoDeaths_EP', color='Age',
                             title='Weekly Deaths (NoDeaths_EP) by Age Group',
                             labels={'Ending_Date': 'Date', 'NoDeaths_EP': 'Number of Deaths', 'Age': 'Age Group'})
        st.plotly_chart(fig_weekly, use_container_width=True, config={'displayModeBar': False}) # Modebar hidden
    else:
        st.warning(f"No data for age groups '{', '.join(age_groups_to_plot)}' in weekly data.")
else:
    st.info("Weekly deaths data unavailable for Graph 1.")


# --- Graph 2: Absolute Yearly Deaths by Gender ---
st.header("Absolute Yearly Deaths by Gender")
if not df_absolute_raw.empty:
    if 'Men' in df_absolute_raw.columns and 'Women' in df_absolute_raw.columns:
        df_abs_melted = df_absolute_raw.melt(id_vars=['Year'], value_vars=['Men', 'Women'],
                                            var_name='Gender', value_name='Number_of_Deaths')
        df_abs_melted.dropna(subset=['Number_of_Deaths'], inplace=True)
        if not df_abs_melted.empty:
            fig_absolute = px.line(df_abs_melted, x='Year', y='Number_of_Deaths', color='Gender',
                                   title='Absolute Yearly Deaths: Men vs. Women',
                                   labels={'Year': 'Year', 'Number_of_Deaths': 'Number of Deaths', 'Gender': 'Gender'},
                                   markers=True)
            st.plotly_chart(fig_absolute, use_container_width=True, config={'displayModeBar': False}) # Modebar hidden
        else:
            st.warning("No valid data to plot for absolute yearly deaths (after processing).")
    else:
        st.warning("Required 'Men' or 'Women' columns missing for absolute deaths plot.")
else:
    st.info("Absolute yearly deaths data unavailable for Graph 2.")


# --- Graph 3: Yearly Mortality Rates per 100,000 by Gender ---
st.header("Yearly Mortality Rate per 100,000 Inhabitants")
if not df_absolute_with_rates.empty:
    rate_columns = []
    if 'Rate_Men' in df_absolute_with_rates.columns: rate_columns.append('Rate_Men')
    if 'Rate_Women' in df_absolute_with_rates.columns: rate_columns.append('Rate_Women')
    if 'Rate_Total' in df_absolute_with_rates.columns: rate_columns.append('Rate_Total')

    if rate_columns:
        df_rates_melted = df_absolute_with_rates.melt(
            id_vars=['Year'],
            value_vars=rate_columns,
            var_name='Rate_Category',
            value_name='Mortality_Rate'
        )
        df_rates_melted['Rate_Category'] = df_rates_melted['Rate_Category'].str.replace('Rate_', '')
        df_rates_melted.dropna(subset=['Mortality_Rate'], inplace=True)

        if not df_rates_melted.empty:
            fig_rates = px.line(
                df_rates_melted,
                x='Year',
                y='Mortality_Rate',
                color='Rate_Category',
                title='Yearly Mortality Rate per 100,000: Men, Women, and Total',
                labels={'Year': 'Year', 'Mortality_Rate': 'Mortality Rate per 100,000', 'Rate_Category': 'Category'},
                markers=True
            )
            st.plotly_chart(fig_rates, use_container_width=True, config={'displayModeBar': False}) # Modebar hidden
        else:
            st.warning("No valid rate data to plot (after processing and melting).")
    else:
        st.warning("No rate columns (Rate_Men, Rate_Women, Rate_Total) available in the processed data for plotting rates.")
else:
    st.info("Data for mortality rates (absolute deaths or population) could not be fully processed or is unavailable for Graph 3.")