# vis2.py - Simplified after fixing data loading
import pandas as pd
import plotly.express as px
import streamlit as st # Keep for st.error/st.exception if needed

def create_absolute_deaths_plot(dataframe):
    """
    Generates a line plot showing the absolute number of deaths for men and women over the years.
    Expects columns 'X.1' (Year), 'Men', 'Women'.
    """
    if dataframe is None or dataframe.empty:
        print("Warning in create_absolute_deaths_plot: Received empty or None data.")
        return None

    try:
        # --- Data Preparation ---
        df_processed = dataframe.copy()

        # 1. Check for and rename the 'X.1' column (should exist now)
        if 'X.1' in df_processed.columns:
             df_processed = df_processed.rename(columns={'X.1': 'Year'})
        elif 'Year' not in df_processed.columns:
             st.error("Error creating plot: Column 'X.1' or 'Year' not found after loading.")
             print("Columns found:", df_processed.columns.tolist()) # Print to terminal if error occurs
             return None

        # 2. Ensure required value columns exist
        required_cols = ['Year', 'Men', 'Women']
        if not all(col in df_processed.columns for col in required_cols):
            missing = [col for col in required_cols if col not in df_processed.columns]
            st.error(f"Error creating plot: Missing required columns {missing}. Found: {df_processed.columns.tolist()}")
            return None

        # 3. Convert columns to numeric types
        for col in required_cols:
             df_processed[col] = pd.to_numeric(df_processed[col], errors='coerce')
        df_processed.dropna(subset=required_cols, inplace=True)
        df_processed['Year'] = df_processed['Year'].astype(int)

        # 4. Melt the dataframe
        df_melted = df_processed.melt(id_vars=['Year'],
                                      value_vars=['Men', 'Women'],
                                      var_name='Sex',
                                      value_name='Number of Deaths')

        # --- Plotting ---
        fig = px.line(
            df_melted,
            x='Year',
            y='Number of Deaths',
            color='Sex',
            title="Absolute Number of Deaths per Year",
            labels={
                'Year': 'Year',
                'Number of Deaths': 'Number of Deaths',
                'Sex': 'Sex'
            },
            markers=True
        )
        fig.update_layout(
            xaxis_title="Year",
            yaxis_title="Absolute Number of Deaths",
            legend_title_text='Sex'
        )

        return fig

    except Exception as e:
        st.error(f"An unexpected error occurred in create_absolute_deaths_plot:")
        st.exception(e) # Show full error in Streamlit app for easier debugging
        return None