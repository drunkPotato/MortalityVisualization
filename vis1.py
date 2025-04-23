import plotly.express as px

# Create a combined DataFrame suitable for plotly.express
df_combined = pd.concat([
    df_0_64[['Ending', 'NoDeaths_EP']].rename(columns={'NoDeaths_EP': 'Deaths'}).assign(Age='0–64'),
    df_65_plus[['Ending', 'NoDeaths_EP']].rename(columns={'NoDeaths_EP': 'Deaths'}).assign(Age='65+')
])

# Create the line chart using plotly.express
fig = px.line(
    df_combined,
    x='Ending',
    y='Deaths',
    color='Age',
    labels={'Ending': 'Week Ending Date', 'Deaths': 'Number of Deaths'},
    title='Weekly Number of Deaths by Age Group (0–64 vs. 65+)'
)

# Export as standalone HTML using CDN
export_path = "/mnt/data/weekly_deaths_plotly_express.html"
fig.write_html(export_path, include_plotlyjs="cdn")

export_path
