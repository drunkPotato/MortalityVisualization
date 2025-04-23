import pandas as pd
import plotly.express as px

# Step 1: Load the CSV
df = pd.read_csv("Mortality_rate_per_100000_inhabitants.csv")

# Step 2: Rename columns for convenience
df.columns = ['Year', 'Men', 'Women']

# Step 3: Convert year to integer, replace comma with dot, and convert to float
df['Year'] = df['Year'].astype(int)
df['Men'] = df['Men'].str.replace(',', '.').astype(float)
df['Women'] = df['Women'].str.replace(',', '.').astype(float)

# Step 4: Reshape for Plotly Express
df_melted = df.melt(id_vars='Year', value_vars=['Men', 'Women'],
                    var_name='Gender', value_name='Mortality Rate')

# Step 5: Create line chart with Plotly Express
fig = px.line(
    df_melted,
    x='Year',
    y='Mortality Rate',
    color='Gender',
    labels={'Year': 'Year', 'Mortality Rate': 'Rate per 100,000'},
    title='Mortality Rate per 100,000 Inhabitants by Gender'
)

# Step 6: Export to HTML with CDN
fig.write_html("mortality_rate_by_gender.html", include_plotlyjs="cdn")
