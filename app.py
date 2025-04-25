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


@st.cache_data
def load_data(file_path, is_excel=False, specific_delimiter=None, decimal_separator='.'): # ADD decimal_separator argument, default to '.'
    """Loads data from CSV or Excel, handling delimiters and decimal separators."""
    full_path = os.path.join(DATA_DIR, file_path)
    try:
        if is_excel or file_path.lower().endswith('.xlsx'):
            df = pd.read_excel(full_path)
            file_type = "Excel"
        elif file_path.lower().endswith('.csv'):
            file_type = "CSV"
            delimiter_to_use = specific_delimiter if specific_delimiter else ';' # Prioritize specific, else default to ';'
            try:
                # Use the specified or default delimiter AND the decimal separator
                df = pd.read_csv(full_path, delimiter=delimiter_to_use, decimal=decimal_separator)
            except (pd.errors.ParserError, ValueError) as e1:
                # If the first attempt fails, and we didn't specify a delimiter, try ','
                if not specific_delimiter and delimiter_to_use == ';':
                    st.warning(f"Parsing {file_path} with delimiter='{delimiter_to_use}' failed ({e1}), trying with ','...")
                    delimiter_to_use = ','
                    try:
                        # Try again with comma delimiter AND the specified decimal separator
                        df = pd.read_csv(full_path, delimiter=delimiter_to_use, decimal=decimal_separator)
                    except Exception as e2:
                       st.error(f"Failed to parse {file_path} with delimiter=',' ({e2}) after initial failure.")
                       return None
                else: # Failed even with specific delimiter, or failed the fallback comma attempt
                    st.error(f"Error parsing {file_path} with delimiter='{delimiter_to_use}' and decimal='{decimal_separator}': {e1}")
                    return None
            except Exception as csv_e: # Catch other CSV reading errors
                 st.error(f"Error reading CSV {file_path}: {csv_e}")
                 return None
        else:
            st.error(f"Unsupported file format: {file_path}")
            return None

        if df is None or df.empty:
             st.warning(f"Loaded empty or None dataframe from {file_path}")
             return None
        # st.success(f"Successfully loaded {file_type}: {file_path}") # Debug print
        return df
    except FileNotFoundError:
        st.error(f"Error: Data file not found at {full_path}")
        return None
    except Exception as e:
        st.error(f"An unexpected error occurred loading {file_path}: {e}")
        return None

# --- Load All Required Datasets ---
# Load data based on the identified files in the 'data' directory image
df_weekly_deaths = load_data('Weekly_number_of_deaths.csv')                     # For Vis 1
df_absolute_deaths = load_data('Deaths_Absolute_number.csv', specific_delimiter=',') # For Vis 2
df_rate_100k = load_data('Mortality_rate_per_100000_inhabitants.csv', specific_delimiter=',', decimal_separator=',')# For Vis 3
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
    st.header("Absolute Number of Deaths per Year") # Slightly more descriptive header
    if VIS2_IMPORTED and df_absolute_deaths is not None:
        # --- Call the function from vis2.py ---
        fig2 = create_absolute_deaths_plot(df_absolute_deaths.copy()) # Pass a copy
        if fig2:
            # Display the plot if successfully created
            st.plotly_chart(fig2, use_container_width=True)
        else:
            # Show a warning if plot creation failed inside the function
            st.warning("Could not generate the absolute deaths plot. Check data format or errors in vis2.py.")
        # --- End of updated logic for Vis 2 ---
    elif not VIS2_IMPORTED:
         st.error("Cannot display plot: vis2.py could not be imported or the function 'create_absolute_deaths_plot' is missing/has errors.")
    else: # df_absolute_deaths is None
        st.error("Cannot display plot: Data file 'Deaths_Absolute_number.csv' failed to load.")

# VIS 3 Display Logic
elif current_view == 'vis3':
    st.header("Mortality Rate per 100,000 Inhabitants")
    if VIS3_IMPORTED and df_rate_100k is not None:
        # --- Call the function from vis3.py ---
        fig3 = create_mortality_rate_plot(df_rate_100k.copy()) # Pass a copy
        if fig3:
            # Display the plot if successfully created
            st.plotly_chart(fig3, use_container_width=True)
        else:
            # Show a warning if plot creation failed inside the function
            st.warning("Could not generate the mortality rate plot. Check data format or errors in vis3.py.")
        # --- End of updated logic for Vis 3 ---
    elif not VIS3_IMPORTED:
         st.error("Cannot display plot: vis3.py could not be imported or the function 'create_mortality_rate_plot' is missing/has errors.")
    else: # df_rate_100k is None
        st.error("Cannot display plot: Data file 'Mortality_rate_per_100000_inhabitants.csv' failed to load. Check delimiter/decimal settings.")

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