import pandas as pd
import plotly.express as px

# Step 1: Load the CSV file (adjust path if necessary)
file_path = "Weekly_number_of_deaths.csv"
df = pd.read_csv(file_path, delimiter=';', engine='python')

# Step 2: Clean the 'Age' column (remove whitespace)
df['Age'] = df['Age'].str.strip()

# Step 3: Filter for age groups 0–64 and 65+
df_0_64 = df[df['Age'] == '0-64'].copy()
df_65_plus = df[df['Age'] == '65+'].copy()

# Step 4: Convert columns to proper formats
df_0_64['Ending'] = pd.to_datetime(df_0_64['Ending'], format='%d.%m.%Y')
df_65_plus['Ending'] = pd.to_datetime(df_65_plus['Ending'], format='%d.%m.%Y')

df_0_64['NoDeaths_EP'] = pd.to_numeric(df_0_64['NoDeaths_EP'], errors='coerce')
df_65_plus['NoDeaths_EP'] = pd.to_numeric(df_65_plus['NoDeaths_EP'], errors='coerce')

# Step 5: Combine data for Plotly Express
df_combined = pd.concat([
    df_0_64[['Ending', 'NoDeaths_EP']].rename(columns={'NoDeaths_EP': 'Deaths'}).assign(Age='0–64'),
    df_65_plus[['Ending', 'NoDeaths_EP']].rename(columns={'NoDeaths_EP': 'Deaths'}).assign(Age='65+')
])

# Step 6: Create the Plotly Express line chart
fig = px.line(
    df_combined,
    x='Ending',
    y='Deaths',
    color='Age',
    labels={'Ending': 'Week Ending Date', 'Deaths': 'Number of Deaths'},
    title='Weekly Number of Deaths by Age Group (0–64 vs. 65+)'
)

# Step 7: Export the chart as HTML (uses CDN for plotly.js)
fig.write_html("weekly_deaths_plotly_express.html", include_plotlyjs="cdn")

print("Chart exported to: weekly_deaths_plotly_express.html")
