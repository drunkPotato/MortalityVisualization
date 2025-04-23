import pandas as pd
import plotly.express as px

# Step 1: Load the CSV file
df = pd.read_csv("data/Deaths_Absolute_number.csv")

# Step 2: Rename columns for clarity
df.columns = ['Year', 'Men', 'Women']

# Step 3: Convert data types
df['Year'] = df['Year'].astype(int)
df['Men'] = df['Men'].astype(int)
df['Women'] = df['Women'].astype(int)

# Step 4: Reshape for Plotly Express
df_melted = df.melt(id_vars='Year', value_vars=['Men', 'Women'],
                    var_name='Gender', value_name='Number of Deaths')

# Step 5: Create line chart
fig = px.line(
    df_melted,
    x='Year',
    y='Number of Deaths',
    color='Gender',
    labels={'Year': 'Year', 'Number of Deaths': 'Absolute Number of Deaths'},
    title='Absolute Number of Deaths by Gender (1970 Onward)'
)

# Step 6: Export to HTML with CDN
fig.write_html("absolute_deaths_by_gender.html", include_plotlyjs="cdn")
