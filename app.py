from dash import Dash, html, dcc, Input, Output
from flask import request, send_file
import plotly.graph_objects as go
import pickle
import pandas as pd
import dash_bootstrap_components as dbc  # Import Bootstrap Components
from src.helper_fns import load_pickle, get_image_stats, get_image_id, get_dataset_image_counts
import os

# Define paths for datasets and results
IMAGES_ROOT = '/data3/vaibhav.agrawal/SegmentAnyLine/SAL-Datasets/datasets'
RESULTS_ROOT = '/data3/vaibhav.agrawal/SegmentAnyLine/SAL-Datasets/results'
csv_path = 'outputs/flat_all_dataset_stats.csv'

# Load CSV data
df = pd.read_csv(csv_path)
df_all_splits = df[df['split'] == 'all_splits']

# Extract data for the charts
categories = df['category'].unique()
datasets = df_all_splits['dataset']
avg_heights = df_all_splits['avg_height']
avg_widths = df_all_splits['avg_width']
avg_ilgs = df_all_splits['avg_ilg']
n_lines = df_all_splits['n_line']

# Create the first bar chart
bar_chart1 = go.Figure(data=[
    go.Bar(name='Avg Height', x=datasets, y=avg_heights),
    go.Bar(name='Avg Width', x=datasets, y=avg_widths)
])
bar_chart1.update_layout(
    barmode='group', title='Avg Height & Width', title_x=0.5, 
    legend=dict(orientation="h",yanchor="bottom",y=1.02,xanchor="right",x=1), 
    margin=dict(l=20, r=10, t=100, b=20), 
)

# Create the second bar chart
bar_chart2 = go.Figure(data=[
    go.Bar(name='Avg ILG', x=datasets, y=avg_ilgs, marker=dict(color='rgba(239, 169, 33, 0.8)'))
])
bar_chart2.update_layout(
    barmode='group', title='Avg Interline Gap', title_x=0.5, 
    legend=dict(orientation="h",yanchor="bottom",y=1.02,xanchor="right",x=1), 
    margin=dict(l=10, r=10, t=100, b=20), 
)

# Create the second bar chart
bar_chart3 = go.Figure(data=[
    go.Bar(name='#Lines', x=datasets, y=n_lines, marker=dict(color='rgba(97, 239, 33, 0.8)'))
])
bar_chart3.update_layout(
    barmode='group', title='Avg No of Lines', title_x=0.5, 
    legend=dict(orientation="h",yanchor="bottom",y=1.02,xanchor="right",x=1), 
    margin=dict(l=10, r=10, t=100, b=20), template='plotly'
)

# Initialize the Dash app with Bootstrap theme
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)
app.title = 'SAL Dataset Stats Viewer'
server = app.server  # Access the underlying Flask server

# App Layout
app.layout = html.Div([
    dbc.Container([
        # Page Title
        dbc.Row([
            dbc.Col(html.H1('SAL Dataset Statistics', className='text-center mb-4'), width=12)
        ]),

        html.Hr(),

        # Global Dataset Stats
        html.H3('Stats Across All The Datasets'),
        dbc.Row([
            dbc.Col(dcc.Graph(figure=bar_chart1), width=12, style={'height': '500px'}),
        ]),
        dbc.Row([
            dbc.Col(dcc.Graph(figure=bar_chart2), width=6, style={'height': '500px'}),
            dbc.Col(dcc.Graph(figure=bar_chart3), width=6, style={'height': '500px'}),
        ]),

        html.Hr(),

        # Individual Dataset Stats 
        html.H3('View Dataset Specific Stats'),
        dbc.Row([
            dbc.Col([
                html.Label('Select Category:'),
                dcc.Dropdown(
                    id='category-dropdown',
                    options=[{'label': cat, 'value': cat} for cat in categories],
                    value=None,
                    placeholder='Select a category'
                )
            ], width=4),

            dbc.Col([
                html.Label('Select Dataset:'),
                dcc.Dropdown(
                    id='dataset-dropdown',
                    options=[],
                    value=None,
                    placeholder='Select a dataset'
                )
            ], width=4),

            dbc.Col([
                html.Label('Select Split:'),
                dcc.Dropdown(
                    id='split-dropdown',
                    options=[],
                    value='all_splits',
                    placeholder='Select a split'
                )
            ], width=4)
        ]),

        # Div to display the statistics
        dbc.Row([
            dbc.Col(html.Div(id='stats-div', style={'margin-top': '20px', 'font-size': '16px'}), width=12)
        ]),

        html.Hr(),

        # Dynamically render the input section
        dbc.Row([
            dbc.Col(html.Div(id='input-section'), width=12)
        ]),

        html.Hr(),

        # Placeholder div for the image section
        dbc.Row([
            dbc.Col(html.Div(id='dataset-image-section'), width=12)
        ])
    ])
])


# Callback to update datasets based on selected category
@app.callback(
    Output('dataset-dropdown', 'options'),
    [Input('category-dropdown', 'value')]
)
def update_datasets(selected_category):
    if selected_category is None:
        return []
    filtered_datasets = df[df['category'] == selected_category]['dataset'].unique()
    return [{'label': ds, 'value': ds} for ds in filtered_datasets]

# Callback to update splits based on selected category and dataset
@app.callback(
    Output('split-dropdown', 'options'),
    [Input('category-dropdown', 'value'),
     Input('dataset-dropdown', 'value')]
)
def update_splits(selected_category, selected_dataset):
    if selected_category is None or selected_dataset is None:
        return []
    filtered_splits = df[(df['category'] == selected_category) & (df['dataset'] == selected_dataset)]['split'].unique()
    return [{'label': split, 'value': split} for split in filtered_splits]

# Callback to display the statistics based on dataset and split
@app.callback(
    Output('stats-div', 'children'),
    [Input('category-dropdown', 'value'), 
    Input('dataset-dropdown', 'value'),
    Input('split-dropdown', 'value')]
)
def display_statistics(selected_category, selected_dataset, selected_split):
    print('inside show stats', selected_dataset, selected_split)
    if selected_dataset and selected_split:
        filtered_data = df[(df['dataset'] == selected_dataset) & (df['split'] == selected_split)]
        if not filtered_data.empty:
            image_counts = get_dataset_image_counts(IMAGES_ROOT, selected_category, selected_dataset)
            stats = filtered_data.iloc[0]
            return html.Div([
                image_counts, 
                html.P(f"Average Height: emsp;{stats['avg_height']}"),
                html.P(f"Average Width: {stats['avg_width']}"),
                html.P(f"Average ILG: {stats['avg_ilg']}"),
                html.P(f"Average # Lines: {stats['n_line']}")
            ])
    return "Please select a valid category, dataset, and split to view statistics."

# Flask route to serve the image from an external disk
@server.route('/external_image')
def serve_external_image():
    selected_category = request.args.get('category')
    selected_dataset = request.args.get('dataset')
    selected_split = request.args.get('split')
    selected_image = request.args.get('image')

    img_path = f'{IMAGES_ROOT}/{selected_category}/{selected_dataset}/{selected_split}/{selected_image}'
    if os.path.exists(img_path):
        return send_file(img_path)
    return "Image Not Found", 404

# Dynamically render input-section
@app.callback(
    Output('input-section', 'children'),
    [Input('category-dropdown', 'value'),
     Input('dataset-dropdown', 'value'),
     Input('split-dropdown', 'value')]
)
def toggle_input_section(selected_category, selected_dataset, selected_split):
    if selected_category and selected_dataset and selected_split:
        return html.Div([
            html.H3('Image Specific Stats'),
            html.P('Enter an Image ID: '), 
            dcc.Input(
                id='image-id-input',
                type='text',
                placeholder='Default Image ID: 0',
                style={'margin-bottom': '20px', 'width': '300px', 'display-inline': 'block'}
            )
        ])
    return ''



# Callback to dynamically render the image section
@app.callback(
    Output('dataset-image-section', 'children'),
    [Input('category-dropdown', 'value'),
     Input('dataset-dropdown', 'value'),
     Input('split-dropdown', 'value'),
     Input('image-id-input', 'value')],
    prevent_initial_call=True
)
def render_image_section(selected_category, selected_dataset, selected_split, selected_image):
    if selected_category and selected_dataset and selected_split:
        if selected_split == 'all_splits':
            selected_split = 'train'

        if not selected_image:
            selected_image = 0

        image_stats = get_image_stats(RESULTS_ROOT, selected_category, selected_dataset, selected_split, selected_image)
        selected_image_path = f'{get_image_id(selected_image)}.jpg'

        return html.Div([
            html.P(f"Filename: {selected_category}/{selected_dataset}/{selected_split}/{selected_image_path}"),
            html.P(f"Dimensions: {image_stats['height']} x {image_stats['width']}"),
            html.P(f"Average Interline Gap: {image_stats['avg_ilg']}"),
            html.P(f"Number of Lines: {image_stats['n_line']}"),
            html.Img(
                src=f'/external_image?category={selected_category}&dataset={selected_dataset}&split={selected_split}&image={selected_image_path}',
                style={'width': '100%', 'height': '600px', 'object-fit': 'contain', 'border': '1px solid #ccc'}
            )
        ])
    return ''

if __name__ == '__main__':
    # for debug use port 2301, else 2300
    debug = True
    if debug:
        app.run(debug=debug, host='0.0.0.0', port=2301)
    else:
        app.run(debug=debug, host='0.0.0.0', port=2300)
