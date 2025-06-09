# Swiss Mortality & Population Trends Dashboard

## Project Overview

This project presents an interactive dashboard for visualizing weekly and yearly mortality data for Switzerland. Users can explore trends by age group, gender, and mortality rates, as well as view a seasonal heatmap of weekly deaths. The dashboard is built using Python with Streamlit for the web application, Pandas for data manipulation, and Plotly Express for generating interactive visualizations.

## Screenshot

![Dashboard Screenshot](<path_to_your_screenshot.png>)
*(Replace `<path_to_your_screenshot.png>` with the actual path to your screenshot file if you include it in the repository, or link to an image hosting service)*
*Self-note: I will use the provided screenshot URL when generating the final README if I have internet access. If not, I'll leave a placeholder.*
*(Update: Using the provided screenshot)*
![Dashboard Screenshot](https://i.stack.imgur.com/KzQ3L.png)

## Features

*   **Interactive Visualizations:** All charts are interactive, allowing users to hover for details.
*   **Dark Theme:** Custom CSS is applied for a modern dark theme and enhanced visual appeal.
*   **Weekly Deaths by Age Group:** Line chart showing weekly deaths for "0-64" and "65+" age groups.
*   **Absolute Yearly Deaths by Gender:** Line chart comparing the absolute number of deaths for men and women over the years.
*   **Yearly Mortality Rate by Gender:** Line chart showing the mortality rate per 100,000 inhabitants for men and women.
*   **Seasonal Heatmap of Weekly Deaths:** Heatmap visualizing the total number of deaths per calendar week for each year.
*   **Sidebar Controls:**
    *   Date range selectors for weekly data.
    *   Year range selectors for yearly data and the heatmap.
    *   Y-axis range selectors for line charts to allow focused analysis.
*   **Data Caching:** Streamlit's `@st.cache_data` is used to optimize data loading performance.
*   **Responsive Design:** The dashboard layout is set to "wide" for better use of screen real estate.
*   **Robust Data Loading:** Functions include error handling and data cleaning steps for various CSV formats (semicolon and comma-delimited, different decimal separators).

## Data Sources

The dashboard utilizes the following datasets (assumed to be located in a `data/` subdirectory):

1.  `data/Weekly_number_of_deaths.csv`: Contains weekly death counts, potentially broken down by age group. Used for Graph 1 and Graph 4.
2.  `data/Deaths_Absolute_number.csv`: Contains absolute yearly death counts, broken down by gender. Used for Graph 2.
3.  `data/Mortality_rate_per_100000_inhabitants.csv`: Contains yearly mortality rates per 100,000 inhabitants, broken down by gender. Used for Graph 3.

*Note: The actual data files are not included in this repository but are expected to be present in a `data/` folder for the application to run.*

## Technologies Used

*   **Python 3.x**
*   **Streamlit:** For building the interactive web application.
*   **Pandas:** For data manipulation and analysis.
*   **Plotly Express:** For creating interactive charts and visualizations.
*   **NumPy:** For numerical operations, especially in axis range calculations.
*   **OS & Datetime:** Standard Python libraries for file path management and date/time operations.

## Setup and Installation

1.  **Clone the repository (or download the files):**
    ```bash
    git clone <your_repository_url>
    cd <repository_name>
    ```

2.  **Create and activate a virtual environment (recommended):**
    ```bash
    python -m venv venv
    # On Windows
    venv\Scripts\activate
    # On macOS/Linux
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    Make sure you have a `requirements.txt` file. If not, you can create one from your environment:
    ```bash
    pip freeze > requirements.txt
    ```
    Then install:
    ```bash
    pip install -r requirements.txt
    ```
    Alternatively, if you don't have a `requirements.txt`, install the packages directly:
    ```bash
    pip install streamlit pandas plotly numpy
    ```

4.  **Data Files:**
    Ensure the required CSV data files (`Weekly_number_of_deaths.csv`, `Deaths_Absolute_number.csv`, `Mortality_rate_per_100000_inhabitants.csv`) are placed in a subdirectory named `data/` within the project's root folder.

## Running the Application

1.  Navigate to the project directory in your terminal.
2.  Run the Streamlit application using the following command (assuming your main script is named `app.py`):
    ```bash
    streamlit run app.py
    ```
3.  The application will open in your default web browser.

## Project Structure

├── app.py # Main Streamlit application script
├── data/
│ ├── Weekly_number_of_deaths.csv
│ ├── Deaths_Absolute_number.csv
│ └── Mortality_rate_per_100000_inhabitants.csv
├── requirements.txt # Python dependencies
├── README.md # This file
└── (Optional: your_screenshot.png) # Screenshot image




## Code Highlights

*   **Modular Data Loading:** Separate functions (`load_weekly_deaths_data`, `load_absolute_deaths_data`, etc.) are used for loading and preprocessing each dataset, promoting reusability and clarity. `@st.cache_data` is applied to these functions to prevent redundant data loading.
*   **Dynamic Axis Controls:** The `get_axis_ranges` helper function dynamically creates sidebar sliders for x and y axes based on the data type (datetime or numeric) and range of the provided columns.
*   **Custom CSS Injection:** `st.markdown(..., unsafe_allow_html=True)` is used to inject custom CSS for a dark theme, rounded corners on plots, and improved typography.
*   **Plotly Dark Template:** `px.defaults.template = "plotly_dark"` ensures all Plotly charts adhere to the dark theme by default.
*   **Data Transformation:** Pandas `melt` function is used effectively to transform data from wide to long format, suitable for plotting with Plotly Express when comparing categories (e.g., 'Men' vs. 'Women').
*   **Error Handling:** Basic error handling (e.g., `FileNotFoundError`, `Exception`) is included in data loading functions.

## Future Improvements

*   **More Granular Age Groups:** Allow selection of more specific age brackets for deeper analysis.
*   **Population Data Integration:** Incorporate population data to show relative changes or per capita figures where appropriate.
*   **Cause of Death Analysis:** If data is available, add visualizations for leading causes of death.
*   **Geographical Breakdown:** If data supports it, allow filtering or comparison by Swiss cantons.
*   **Advanced Statistical Insights:** Implement time series decomposition or anomaly detection.
*   **Export Functionality:** Allow users to download charts or filtered data.

---

This README provides a comprehensive overview of your project. Remember to replace placeholders like `<your_repository_url>` and ensure the screenshot path is correct. Good luck with your class!