# app.py - Updated for specified data files and navigation

import streamlit as st
import pandas as pd
import os

# --- Page Configuration ---
st.set_page_config(
    page_title="Mortality Visualization Dashboard",
    page_icon="📊",
    layout="wide"
)

# --- Data Loading Function (Keep as before, handles CSV/XLSX) ---
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')

@st.cache_data # Cache the data loading
def load_data(file_path, is_excel=False):
    """Loads data from CSV or Excel, handling potential errors."""
    full_path = os.path.join(DATA_DIR, file_path)
    # st.write(f"Attempting to load: {full_path}") # Uncomment for debugging load paths
    try:
        if is_excel or file_path.lower().endswith('.xlsx'):
            # Make sure openpyxl is installed: pip install openpyxl
            df = pd.read_excel(full_path)
            file_type = "Excel"
        elif file_path.lower().endswith('.csv'):
            # --- Assume semicolon delimiter for CSVs unless specified otherwise ---
            # You might need error handling here to try comma if semicolon fails
            try:
                df = pd.read_csv(full_path, delimiter=';')
            except pd.errors.ParserError:
                 st.warning(f"Parsing {file_path} with ';' failed, trying with ','...")
                 df = pd.read_csv(full_path, delimiter=',') # Fallback to comma
            except Exception as csv_e: # Catch other CSV reading errors
                 st.error(f"Error reading CSV {file_path}: {csv_e}")
                 return None
            file_type = "CSV"
        else:
            st.error(f"Unsupported file format: {file_path}")
            return None

        if df is None or df.empty:
             st.warning(f"Loaded empty or None dataframe from {file_path}")
             return None
        # st.success(f"Successfully loaded {file_type}: {file_path}") # Uncomment for debugging load success
        return df
    except FileNotFoundError:
        st.error(f"Error: Data file not found at {full_path}")
        return None
    except pd.errors.ParserError as e:
         # This might catch issues even with the fallback, e.g., inconsistent delimiters
         st.error(f"Final parsing error for {file_path}: {e}. Check file structure/delimiters.")
         return None
    except Exception as e:
        # Catch other potential errors (e.g., permissions, corrupted Excel file)
        st.error(f"An unexpected error occurred loading {file_path}: {e}")
        return None

# --- Load All Required Datasets ---
# Load data based on the identified files in the 'data' directory image
df_weekly_deaths = load_data('Weekly_number_of_deaths.csv')                     # For Vis 1
df_absolute_deaths = load_data('Deaths_Absolute_number.csv')                   # For Vis 2
df_rate_100k = load_data('Mortality_rate_per_100000_inhabitants.csv')           # For Vis 3
df_by_canton = load_data('Deaths_per_week_by_5-year_age_group_sex_and_canton.csv') # For Vis 4
df_by_region = load_data('Deaths_per_week_by_5-year_age_group_sex_and_major_region.csv')# For Vis 5
df_causes_men = load_data('Sterbefälle_und_Sterbeziffern_wichtiger_Todesursachen_Männer_seit_1970.xlsx', is_excel=True) # For Vis 6

# Optional: Load data for women's causes of death if needed later
# df_causes_women = load_data('Sterbefälle_und_Sterbeziffern_wichtiger_Todesursachen_Frauen_seit_1970.xlsx', is_excel=True)

# --- Import Visualization Functions ---
# Use descriptive function names you intend to create in visX.py files

# VIS1: Weekly Deaths
try:
    from vis1 import create_weekly_deaths_plot
    VIS1_IMPORTED = True
except ImportError:
    VIS1_IMPORTED = False

# VIS2: Absolute Deaths
try:
    from vis2 import create_absolute_deaths_plot # Implement this in vis2.py
    VIS2_IMPORTED = True
except ImportError:
    VIS2_IMPORTED = False

# VIS3: Mortality Rate
try:
    from vis3 import create_mortality_rate_plot # Implement this in vis3.py
    VIS3_IMPORTED = True
except ImportError:
    VIS3_IMPORTED = False

# VIS4: Deaths by Canton
try:
    from vis4 import create_canton_plot # Implement this in vis4.py
    VIS4_IMPORTED = True
except ImportError:
    VIS4_IMPORTED = False

# VIS5: Deaths by Major Region
try:
    from vis5 import create_region_plot # Implement this in vis5.py
    VIS5_IMPORTED = True
except ImportError:
    VIS5_IMPORTED = False

# VIS6: Causes of Death (Men)
try:
    from vis6 import create_causes_men_plot # Implement this in vis6.py
    VIS6_IMPORTED = True
except ImportError:
    VIS6_IMPORTED = False


# --- Initialize Session State for Navigation ---
if 'current_view' not in st.session_state:
    st.session_state.current_view = 'vis1' # Default view

# --- Sidebar Navigation ---
st.sidebar.title("Navigation")
st.sidebar.write("Select a visualization:")

# Use more descriptive button labels based on the data
if st.sidebar.button("Weekly Deaths"):
    st.session_state.current_view = 'vis1'
if st.sidebar.button("Absolute Deaths"):
    st.session_state.current_view = 'vis2'
if st.sidebar.button("Mortality Rate / 100k"):
    st.session_state.current_view = 'vis3'
if st.sidebar.button("Deaths by Canton"):
    st.session_state.current_view = 'vis4'
if st.sidebar.button("Deaths by Major Region"):
    st.session_state.current_view = 'vis5'
if st.sidebar.button("Causes of Death (Men)"):
    st.session_state.current_view = 'vis6'

# --- Main Content Area ---
st.title("Swiss Mortality Data Visualization")

# Display content based on the selected view
current_view = st.session_state.current_view

# VIS 1 Display Logic
if current_view == 'vis1':
    st.header("Weekly Deaths Overview")
    if VIS1_IMPORTED and df_weekly_deaths is not None:
        fig1 = create_weekly_deaths_plot(df_weekly_deaths.copy()) # Pass a copy to avoid modifying cached data
        if fig1:
            st.plotly_chart(fig1, use_container_width=True)
        else:
            st.warning("Could not generate the weekly deaths plot.")
    elif not VIS1_IMPORTED:
         st.error("Cannot display plot: Error in vis1.py.")
    else: # df_weekly_deaths is None
        st.error("Cannot display plot: Data ('Weekly_number_of_deaths.csv') failed to load.")

# VIS 2 Display Logic
elif current_view == 'vis2':
    st.header("Absolute Number of Deaths")
    if VIS2_IMPORTED and df_absolute_deaths is not None:
        # --- Replace placeholder with actual plot call when vis2.py is ready ---
        # fig2 = create_absolute_deaths_plot(df_absolute_deaths.copy())
        # if fig2:
        #     st.plotly_chart(fig2, use_container_width=True)
        # else:
        #     st.warning("Could not generate plot from vis2.py")
        st.info("Placeholder: Vis 2 Function needs to be implemented in vis2.py")
        st.dataframe(df_absolute_deaths.head()) # Show head as placeholder
    elif not VIS2_IMPORTED:
         st.error("Cannot display plot: Error in vis2.py or function missing.")
    else: # df_absolute_deaths is None
        st.error("Cannot display plot: Data ('Deaths_Absolute_number.csv') failed to load.")

# VIS 3 Display Logic
elif current_view == 'vis3':
    st.header("Mortality Rate per 100,000 Inhabitants")
    if VIS3_IMPORTED and df_rate_100k is not None:
        # --- Replace placeholder with actual plot call when vis3.py is ready ---
        # fig3 = create_mortality_rate_plot(df_rate_100k.copy())
        # if fig3:
        #     st.plotly_chart(fig3, use_container_width=True)
        # else:
        #      st.warning("Could not generate plot from vis3.py")
        st.info("Placeholder: Vis 3 Function needs to be implemented in vis3.py")
        st.dataframe(df_rate_100k.head()) # Show head as placeholder
    elif not VIS3_IMPORTED:
         st.error("Cannot display plot: Error in vis3.py or function missing.")
    else: # df_rate_100k is None
        st.error("Cannot display plot: Data ('Mortality_rate_per_100000_inhabitants.csv') failed to load.")

# VIS 4 Display Logic
elif current_view == 'vis4':
    st.header("Deaths per Week by Canton, Age Group, and Sex")
    if VIS4_IMPORTED and df_by_canton is not None:
        # --- Replace placeholder with actual plot call when vis4.py is ready ---
        # fig4 = create_canton_plot(df_by_canton.copy()) # Might need filters too
        # if fig4:
        #     st.plotly_chart(fig4, use_container_width=True)
        # else:
        #      st.warning("Could not generate plot from vis4.py")
        st.info("Placeholder: Vis 4 Function needs to be implemented in vis4.py (likely needs filters)")
        st.dataframe(df_by_canton.head()) # Show head as placeholder
    elif not VIS4_IMPORTED:
         st.error("Cannot display plot: Error in vis4.py or function missing.")
    else: # df_by_canton is None
        st.error("Cannot display plot: Data ('Deaths_per_week_by_5-year_age_group_sex_and_canton.csv') failed to load.")

# VIS 5 Display Logic
elif current_view == 'vis5':
    st.header("Deaths per Week by Major Region, Age Group, and Sex")
    if VIS5_IMPORTED and df_by_region is not None:
        # --- Replace placeholder with actual plot call when vis5.py is ready ---
        # fig5 = create_region_plot(df_by_region.copy()) # Might need filters too
        # if fig5:
        #     st.plotly_chart(fig5, use_container_width=True)
        # else:
        #      st.warning("Could not generate plot from vis5.py")
        st.info("Placeholder: Vis 5 Function needs to be implemented in vis5.py (likely needs filters)")
        st.dataframe(df_by_region.head()) # Show head as placeholder
    elif not VIS5_IMPORTED:
         st.error("Cannot display plot: Error in vis5.py or function missing.")
    else: # df_by_region is None
        st.error("Cannot display plot: Data ('Deaths_per_week_by_5-year_age_group_sex_and_major_region.csv') failed to load.")

# VIS 6 Display Logic
elif current_view == 'vis6':
    st.header("Causes of Death Since 1970 (Men)")
    if VIS6_IMPORTED and df_causes_men is not None:
        # --- Replace placeholder with actual plot call when vis6.py is ready ---
        # fig6 = create_causes_men_plot(df_causes_men.copy()) # Might need filters too
        # if fig6:
        #     st.plotly_chart(fig6, use_container_width=True)
        # else:
        #      st.warning("Could not generate plot from vis6.py")
        st.info("Placeholder: Vis 6 Function needs to be implemented in vis6.py")
        st.dataframe(df_causes_men.head()) # Show head as placeholder
    elif not VIS6_IMPORTED:
         st.error("Cannot display plot: Error in vis6.py or function missing.")
    else: # df_causes_men is None
        st.error("Cannot display plot: Data ('Sterbefälle_und_Sterbeziffern_wichtiger_Todesursachen_Männer_seit_1970.xlsx') failed to load.")

# Fallback for unknown view state
else:
    st.error("Something went wrong with the view selection.")

# --- Optional: Add a footer ---
st.markdown("---")
# st.markdown("Data source: [Provide source link if applicable]")