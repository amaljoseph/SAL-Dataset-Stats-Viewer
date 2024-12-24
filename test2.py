import dash
from dash import dcc, html
import plotly.graph_objects as go
import pandas as pd

# Example data
datasets = ["Dataset A", "Dataset B", "Dataset C", "Dataset D"]
avg_heights = [50, 70, 60, 30]
avg_widths = [20, 5, 10, 30]

# Convert to DataFrame for easier sorting
df = pd.DataFrame({
    "Dataset": datasets,
    "Avg Height": avg_heights,
    "Avg Width": avg_widths
})

# Function to create the sorted figure
def create_sorted_figure(sort_by='Avg Height', ascending=True):
    sorted_df = df.sort_values(by=sort_by, ascending=ascending)
    fig = go.Figure(data=[
        go.Bar(name='Avg Height', x=sorted_df['Dataset'], y=sorted_df['Avg Height']),
        go.Bar(name='Avg Width', x=sorted_df['Dataset'], y=sorted_df['Avg Width'])
    ])
    fig.update_layout(
        barmode='group',
        title='Avg Height & Width',
        title_x=0.5,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=20, r=10, t=100, b=20),
        updatemenus=[
            dict(
                buttons=[
                    dict(label="Sort by Avg Height (Asc)",
                         method="update",
                         args=[{"x": [df.sort_values('Avg Height', ascending=True)['Dataset']] * 2,
                                "y": [df.sort_values('Avg Height', ascending=True)['Avg Height'],
                                      df.sort_values('Avg Height', ascending=True)['Avg Width']]}]),
                    dict(label="Sort by Avg Width (Asc)",
                         method="update",
                         args=[{"x": [df.sort_values('Avg Width', ascending=True)['Dataset']] * 2,
                                "y": [df.sort_values('Avg Width', ascending=True)['Avg Height'],
                                      df.sort_values('Avg Width', ascending=True)['Avg Width']]}]),
                ],
                direction="down",
                showactive=True,
                x=0,
                xanchor="left",
                y=1.2,
                yanchor="top"
            )
        ]
    )
    return fig

# Dash app setup
app = dash.Dash(__name__)

# Layout of the app
app.layout = html.Div([
    html.H1("Dynamic Sorting Graph with Dash", style={'textAlign': 'center'}),
    dcc.Graph(
        id='sorting-graph',
        figure=create_sorted_figure()
    )
])

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
