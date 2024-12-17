from dash import Dash, html, dcc, Input, Output
from flask import request, send_file
import plotly.graph_objects as go
import pickle
import pandas as pd
from src.helper_fns import load_pickle, get_image_stats, get_image_id
import os

IMAGES_ROOT = '/data3/vaibhav.agrawal/SegmentAnyLine/SAL-Datasets/datasets'
RESULTS_ROOT = '/data3/vaibhav.agrawal/SegmentAnyLine/SAL-Datasets/results'
csv_path = 'outputs/flat_all_dataset_stats.csv'
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
bar_chart1.update_layout(barmode='group', title='Avg Height & Width', title_x=0.5)

# Create the second bar chart
bar_chart2 = go.Figure(data=[
    go.Bar(name='Avg ILG', x=datasets, y=avg_ilgs),
    go.Bar(name='N Line', x=datasets, y=n_lines)
])
bar_chart2.update_layout(barmode='group', title='Avg ILG & #Lines', title_x=0.5)

app = Dash(__name__, suppress_callback_exceptions=True) ### Supressing is not ideal
server = app.server  # Access the underlying Flask server


# App Layout
app.layout = html.Div([

    # Page Title
    html.H1(children='SAL Dataset Statistics'),
    # html.P(children='version: alpha'), 
    html.Hr(),

    # Global Dataset Stats
    html.H3(children='Stats Across All The Datasets'),
    html.Div([
        dcc.Graph(figure=bar_chart1, style={'flex': '1'}),
        dcc.Graph(figure=bar_chart2, style={'flex': '1'})
    ], style={'display': 'flex', 'flex-direction': 'row'}),

    html.Hr(), 

    # Individual Dataset Stats 
    html.H3(children='View Dataset Specific Stats'),
    html.Div([
        # Dropdown for Category
        html.Div([
            html.Label('Select Category:'),
            dcc.Dropdown(
                id='category-dropdown',
                options=[{'label': cat, 'value': cat} for cat in categories],
                value=None,
                placeholder='Select a category'
            )
        ], style={'flex': '1', 'margin-right': '10px'}),

        # Dropdown for Dataset
        html.Div([
            html.Label('Select Dataset:'),
            dcc.Dropdown(
                id='dataset-dropdown',
                options=[],
                value=None,
                placeholder='Select a dataset'
            )
        ], style={'flex': '1', 'margin-right': '10px'}),

        # Dropdown for Split
        html.Div([
            html.Label('Select Split:'),
            dcc.Dropdown(
                id='split-dropdown',
                options=[],
                value='all_splits',
                placeholder='Select a split'
            )
        ], style={'flex': '1'})
    ], style={'display': 'flex', 'flex-direction': 'row', 'align-items': 'center'}),

    # Div to display the statistics
    html.Div(id='stats-div', style={'margin-top': '20px', 'font-size': '16px'}),

    html.Hr(), 

    # Layout to include heading and input field initially hidden
    html.Div(id='input-section'), 

    # Placeholder div for the image section that will be updated dynamically
    html.Div(id='dataset-image-section')
])

# Callback to update the datasets based on selected category
@app.callback(
    Output('dataset-dropdown', 'options'),
    [Input('category-dropdown', 'value')]
)
def update_datasets(selected_category):
    if selected_category is None:
        return []
    filtered_datasets = df[df['category'] == selected_category]['dataset'].unique()
    return [{'label': ds, 'value': ds} for ds in filtered_datasets]

# Callback to update the splits based on selected category and dataset
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
    [Input('dataset-dropdown', 'value'),
     Input('split-dropdown', 'value')]
)
def display_statistics(selected_dataset, selected_split):
    if selected_dataset and selected_split:
        filtered_data = df[(df['dataset'] == selected_dataset) & (df['split'] == selected_split)]
        if not filtered_data.empty:
            stats = filtered_data.iloc[0]  # Get the first row (there should only be one row per dataset-split)
            return html.Div([
                html.P(f"Average Height: {stats['avg_height']}"),
                html.P(f"Average Width: {stats['avg_width']}"),
                html.P(f"Average ILG: {stats['avg_ilg']}"),
                html.P(f"Number of Lines: {stats['n_line']}")
            ])
    return "Please select a valid category, dataset and split to view statistics."


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

# Dynamically render image-id input box
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
        selected_image = f'{get_image_id(selected_image)}.jpg'
        image_dimension = f"{image_stats['height']} x {image_stats['width']}"
        image_avg_interline_gap = image_stats['avg_ilg']
        Image_n_lines = image_stats['n_line']
        
        return html.Div([
            # html.H3('Image Specific Stats'),
            # Display Statistics about the image
            html.Div([
                html.P(f"Filename: {selected_category}/{selected_dataset}/{selected_split}/{selected_image}"),
                html.P(f"Image Dimensions: {image_dimension}"),
                html.P(f"Average Interline Gap: {image_avg_interline_gap}"), 
                html.P(f"Average # Lines: {stats['n_line']}")
                html.P(f"No of Lines: {Image_n_lines}")
            ], style={'margin-top': '10px', 'font-weight': 'normal'}), 
            html.Img(
                id='dataset-image',
                src=f'/external_image?category={selected_category}&dataset={selected_dataset}&split={selected_split}&image={selected_image}',
                style={
                    'width': '100%',
                    'height': '600px',
                    'object-fit': 'contain',
                    'border': '1px solid #ccc'
                }
            )
        ])
    return ''  # Return nothing if dropdowns are not all selected





if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=2301)