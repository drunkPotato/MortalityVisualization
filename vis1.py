# Updated vis1.py

import pandas as pd
import plotly.express as px

def create_weekly_deaths_plot(dataframe):
    """
    Generates the weekly deaths line plot, summing deaths across age groups.
    Expects columns 'Year', 'Week', 'NoDeaths_EP'.
    """
    if dataframe is None or dataframe.empty:
        print("Warning in create_weekly_deaths_plot: Received empty or None data.")
        return None # Return None if data is bad

    try:
        # Ensure necessary columns exist
        required_cols = ['Year', 'Week', 'NoDeaths_EP']
        if not all(col in dataframe.columns for col in required_cols):
            missing = [col for col in required_cols if col not in dataframe.columns]
            print(f"Error creating plot: Missing columns {missing}")
            # In a real Streamlit app, you might use st.error here if called directly
            return None

        # --- Data Processing ---
        # 1. Ensure 'NoDeaths_EP' is numeric, coercing errors to NaN
        #    The '.' in your sample data needs handling.
        dataframe['NoDeaths_EP'] = pd.to_numeric(dataframe['NoDeaths_EP'], errors='coerce')
        # Optional: Drop rows where deaths couldn't be converted (or fill them e.g., with 0)
        dataframe.dropna(subset=['NoDeaths_EP'], inplace=True)
        dataframe['NoDeaths_EP'] = dataframe['NoDeaths_EP'].astype(int)


        # 2. Group by Year and Week, summing deaths across age groups
        weekly_totals = dataframe.groupby(['Year', 'Week'])['NoDeaths_EP'].sum().reset_index()

        # 3. Create a combined Year-Week column for plotting (better for sorting)
        #    Ensure week is zero-padded (e.g., W1 -> W01) for correct sorting
        weekly_totals['Year-Week'] = weekly_totals['Year'].astype(str) + '-W' + weekly_totals['Week'].astype(str).str.zfill(2)
        weekly_totals.sort_values('Year-Week', inplace=True) # Sort chronologically

        # --- Plotting ---
        fig = px.line(
            weekly_totals,
            x='Year-Week',
            y='NoDeaths_EP',
            title="Total Weekly Deaths (All Ages)",
            labels={ # More descriptive labels
                'Year-Week': 'Year and Week',
                'NoDeaths_EP': 'Number of Deaths'
            },
            markers=True # Optional: add markers to see individual points
        )

        # Customize the plot further if needed
        fig.update_layout(xaxis_title="Time (Year-Week)", yaxis_title="Total Deaths per Week")

        return fig # Return the Plotly figure object

    except Exception as e:
        # Log the error for debugging
        print(f"An unexpected error occurred in create_weekly_deaths_plot: {e}")
        # Optionally re-raise or return None depending on desired app behavior
        return None # Return None on error

# Keep this function if you plan to use it later, otherwise remove it
def create_another_plot(dataframe, some_parameter):
    # ... logic ...
    # fig = ...
    # return fig
    pass