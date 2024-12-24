import dash
from dash import dcc, html
import plotly.graph_objects as go
import pandas as pd

# Example data
datasets = ["dataset A", "dataset B", "dataset C", "dataset D"]
avg_heights = [50, 70, 60, 30]
avg_widths = [20, 5, 10, 30]

# Convert to DataFrame for easier sorting
# df = pd.DataFrame({
#     "dataset": datasets,
#     "avg_height": avg_heights,
#     "avg_width": avg_widths
# })
df = pd.read_csv('outputs/flat_all_dataset_stats.csv')
df_all_splits = df[df.split == 'all_splits']
# Function to create the sorted figure
def create_sorted_figure(sort_by='avg_height', ascending=True):
    sorted_df = df_all_splits.sort_values(by=sort_by, ascending=ascending)
    fig = go.Figure(data=[
        go.Bar(name='avg_height', x=sorted_df['dataset'], y=sorted_df['avg_height']),
        go.Bar(name='avg_width', x=sorted_df['dataset'], y=sorted_df['avg_width'])
    ])
    fig.update_layout(
        barmode='group',
        title='avg_height & Width',
        title_x=0.5,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=20, r=10, t=100, b=20),
        updatemenus=[
            dict(
                buttons=[
                    dict(label="Sort by avg_height (Asc)",
                         method="update",
                         args=[{"x": [df_all_splits.sort_values('avg_height', ascending=True)['dataset']] * 2,
                                "y": [df_all_splits.sort_values('avg_height', ascending=True)['avg_height'],
                                      df_all_splits.sort_values('avg_height', ascending=True)['avg_width']]}]),
                    dict(label="Sort by avg_width (Asc)",
                         method="update",
                         args=[{"x": [df_all_splits.sort_values('avg_width', ascending=True)['dataset']] * 2,
                                "y": [df_all_splits.sort_values('avg_width', ascending=True)['avg_height'],
                                      df_all_splits.sort_values('avg_width', ascending=True)['avg_width']]}]),
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
