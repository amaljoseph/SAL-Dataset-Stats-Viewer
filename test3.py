import dash
from dash import dcc, html
import pandas as pd
import plotly.express as px

# Sample data
df = pd.read_csv('outputs/flat_all_dataset_stats.csv')

# Create scatter plot
fig = px.scatter(
    df,
    x="avg_height",
    y="avg_width",
    color="category",
    hover_data=["dataset", "split", "avg_ilg", "n_line"],
    title="Scatter Plot of Average Height vs Average Width",
    labels={"avg_height": "Average Height", "avg_width": "Average Width"},
)

# Dash app layout
app = dash.Dash(__name__)
app.layout = html.Div(
    children=[
        html.H1("Dataset Statistics Dashboard"),
        dcc.Graph(figure=fig),
    ]
)

# Run the app
if __name__ == "__main__":
    app.run_server(debug=True, port=8051)
