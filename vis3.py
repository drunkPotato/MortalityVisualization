# vis3.py
import pandas as pd
import plotly.express as px
import streamlit as st # Optional, for potential error messages

def create_mortality_rate_plot(dataframe):
    """
    Generates a line plot showing the mortality rate per 100k for men and women over the years.
    Expects columns 'X.1' (Year), 'Men', 'Women', where values are numeric rates.
    """
    if dataframe is None or dataframe.empty:
        print("Warning in create_mortality_rate_plot: Received empty or None data.")
        return None

    try:
        # --- Data Preparation ---
        df_processed = dataframe.copy()

        # 1. Rename the 'X.1' column to 'Year'
        if 'X.1' in df_processed.columns:
             df_processed = df_processed.rename(columns={'X.1': 'Year'})
        elif 'Year' not in df_processed.columns:
             st.error("Error creating plot: Column 'X.1' or 'Year' not found.")
             print("Columns found:", df_processed.columns.tolist())
             return None

        # 2. Ensure required value columns exist
        required_cols = ['Year', 'Men', 'Women']
        if not all(col in df_processed.columns for col in required_cols):
            missing = [col for col in required_cols if col not in df_processed.columns]
            st.error(f"Error creating plot: Missing required columns {missing}. Found: {df_processed.columns.tolist()}")
            return None

        # 3. Convert columns to numeric (should already be float due to load_data, but good practice to ensure)
        #    No need for errors='coerce' if load_data worked correctly with decimal=','
        try:
            df_processed['Year'] = pd.to_numeric(df_processed['Year']) # Year should be convertible
            df_processed['Men'] = pd.to_numeric(df_processed['Men'])
            df_processed['Women'] = pd.to_numeric(df_processed['Women'])
        except Exception as convert_e:
             st.error(f"Error converting columns to numeric: {convert_e}. Check data types after loading.")
             print("Data types before error:\n", df_processed.dtypes)
             return None

        # Optional: Check for NaNs introduced during conversion if errors='coerce' was used
        # df_processed.dropna(subset=required_cols, inplace=True)

        # Ensure Year is integer type for plotting axis
        df_processed['Year'] = df_processed['Year'].astype(int)

        # 4. Melt the dataframe to long format
        df_melted = df_processed.melt(id_vars=['Year'],
                                      value_vars=['Men', 'Women'],
                                      var_name='Sex',
                                      value_name='Mortality Rate per 100k') # More specific value name

        # --- Plotting ---
        fig = px.line(
            df_melted,
            x='Year',
            y='Mortality Rate per 100k',
            color='Sex',
            title="Mortality Rate per 100,000 Inhabitants per Year",
            labels={ # Customize labels
                'Year': 'Year',
                'Mortality Rate per 100k': 'Mortality Rate (per 100k)',
                'Sex': 'Sex'
            },
            markers=True
        )

        # Customize layout
        fig.update_layout(
            xaxis_title="Year",
            yaxis_title="Mortality Rate (per 100,000)",
            legend_title_text='Sex'
        )

        return fig # Return the Plotly figure object

    except Exception as e:
        st.error(f"An unexpected error occurred in create_mortality_rate_plot:")
        st.exception(e) # Show full error details in the Streamlit app
        return None