from dash import Dash, html, dcc, Input, Output
import plotly.graph_objects as go

# Initialize the Dash app
app = Dash(__name__)

# Graph 1: Example bar chart
fig1 = go.Figure(data=[
    go.Bar(name='#Lines', x=['Dataset1', 'Dataset2'], y=[10, 20], marker=dict(color='blue'))
])
fig1.update_layout(title='Graph 1: Avg No of Lines', title_x=0.5)

# Graph 2: Example scatter plot
fig2 = go.Figure(data=[
    go.Scatter(name='#Points', x=['Dataset1', 'Dataset2'], y=[30, 15], mode='markers', marker=dict(color='red', size=10))
])
fig2.update_layout(title='Graph 2: Point Distribution', title_x=0.5)

# Layout of the Dash app
app.layout = html.Div([
    dcc.Graph(id='graph-container'),  # Placeholder for graphs
    html.Button('Toggle Graph', id='toggle-button', n_clicks=0)  # Toggle button
])

# Callback to update the graph based on button clicks
@app.callback(
    Output('graph-container', 'figure'),
    Input('toggle-button', 'n_clicks')
)
def toggle_graph(n_clicks):
    # Show fig1 on even clicks and fig2 on odd clicks
    if n_clicks % 2 == 0:
        return fig1
    else:
        return fig2

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
