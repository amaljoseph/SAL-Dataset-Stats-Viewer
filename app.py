from dash import Dash, html, dcc, Input, Output
from flask import request, send_file
import plotly.graph_objects as go
import plotly.express as px
import pickle
import pandas as pd
import dash_bootstrap_components as dbc  # Import Bootstrap Components
from src.helper_fns import load_pickle, get_image_stats, get_image_id, get_dataset_image_counts, render_image_counts
import os
import argparse


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


fig = px.scatter(
    df[df['split'] == 'all_splits'],
    x="avg_height",
    y="avg_width",
    color="category",
    hover_data=["dataset", "split", "avg_ilg", "n_line"],
    title="Avg Height vs Avg Width",
    labels={"avg_height": "Average Height", "avg_width": "Average Width"},
)


# Graph for script distribution
def script_chart1_data():
    ############################## OPTIMIZATION - STORE AND USE in scriptchart() scriptstats, dataset stats
    data = []
    for category in categories:
        dataset_list = list(df[df['category'] == category]['dataset'].unique())
        category_count = 0
        for dataset in dataset_list:
            image_counts_dict = get_dataset_image_counts(IMAGES_ROOT, category, dataset)
            category_count = category_count + image_counts_dict['total']
        

        data.append([category, category_count])
    return data

script_chart1_data = script_chart1_data()
script_chart1 = go.Figure(data=[
    go.Bar(
        name='Script Count Distribution', 
        x=[row[0] for row in script_chart1_data], 
        y=[row[1] for row in script_chart1_data],
        text=[row[1] for row in script_chart1_data], 
        textposition='outside'
    )
])
script_chart1.update_layout(
    barmode='group', title='Total Image Count per Script', title_x=0.5, 
    legend=dict(orientation="h",yanchor="bottom",y=1.02,xanchor="right",x=1), 
    margin=dict(l=10, r=10, t=100, b=0), template='plotly'
)

def create_sorted_figure(sort_by='aspect_ratio', ascending=True):
    # Filter the DataFrame for 'all_splits'
    df_all_splits = df[df.split == 'all_splits']
    
    # Calculate the aspect ratio
    df_all_splits['aspect_ratio'] = df_all_splits['avg_height'] / df_all_splits['avg_width']
    
    # Sort the DataFrame based on the selected column (aspect_ratio, avg_height, or avg_width)
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
                    dict(label="Sort by Aspect Ratio (Asc)",
                         method="update",
                         args=[{"x": [df_all_splits.sort_values('aspect_ratio', ascending=True)['dataset']] * 2,
                                "y": [df_all_splits.sort_values('aspect_ratio', ascending=True)['avg_height'],
                                      df_all_splits.sort_values('aspect_ratio', ascending=True)['avg_width']]}]),
                    dict(label="Sort by Aspect Ratio (Dsc)",
                         method="update",
                         args=[{"x": [df_all_splits.sort_values('aspect_ratio', ascending=False)['dataset']] * 2,
                                "y": [df_all_splits.sort_values('aspect_ratio', ascending=False)['avg_height'],
                                      df_all_splits.sort_values('aspect_ratio', ascending=False)['avg_width']]}]),
                    dict(label="Sort by Avg Height (Asc)",
                         method="update",
                         args=[{"x": [df_all_splits.sort_values('avg_height', ascending=True)['dataset']] * 2,
                                "y": [df_all_splits.sort_values('avg_height', ascending=True)['avg_height'],
                                      df_all_splits.sort_values('avg_height', ascending=True)['avg_width']]}]),
                    dict(label="Sort by Avg Height (Dsc)",
                         method="update",
                         args=[{"x": [df_all_splits.sort_values('avg_height', ascending=False)['dataset']] * 2,
                                "y": [df_all_splits.sort_values('avg_height', ascending=False)['avg_height'],
                                      df_all_splits.sort_values('avg_height', ascending=False)['avg_width']]}]),
                    dict(label="Sort by Avg Width (Asc)",
                         method="update",
                         args=[{"x": [df_all_splits.sort_values('avg_width', ascending=True)['dataset']] * 2,
                                "y": [df_all_splits.sort_values('avg_width', ascending=True)['avg_height'],
                                      df_all_splits.sort_values('avg_width', ascending=True)['avg_width']]}]),
                    dict(label="Sort by Avg Width (Dsc)",
                         method="update",
                         args=[{"x": [df_all_splits.sort_values('avg_width', ascending=False)['dataset']] * 2,
                                "y": [df_all_splits.sort_values('avg_width', ascending=False)['avg_height'],
                                      df_all_splits.sort_values('avg_width', ascending=False)['avg_width']]}]),
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

        # html.Div([
        #     html.P('')
        # ]),
        # html.Hr(),

        # Global Dataset Stats
        html.H3('Stats Across All The Datasets'),
        dbc.Row([
            dbc.Col(dcc.Graph(id='sorting-graph', figure=create_sorted_figure()), width=12, style={'height': '500px'})
        ]), 
        # dbc.Row([
        #     dbc.Col(dcc.Graph(figure=bar_chart1), width=12, style={'height': '500px'}),
        # ]),
        dbc.Row([
            dbc.Col(dcc.Graph(figure=bar_chart2), width=6, style={'height': '500px'}),
            dbc.Col(dcc.Graph(figure=bar_chart3), width=6, style={'height': '500px'}),
        ]),

        dbc.Row([
            dbc.Col(dcc.Graph(figure=fig), width=12)
            
        ]),

        html.Hr(),

        # Script/Category Level Stats
        html.H3('Script / Category wise Stats'),
        dbc.Row([
            dbc.Col(dcc.Graph(figure=script_chart1), width=12, style={'height': '475px'})
        ]),
        html.P('Select Script/Category'), 
        dcc.Dropdown(
            id='script-dropdown', 
            options=[{'label': cat, 'value': cat} for cat in categories],
            value=None,
            placeholder='Select a script/category',
            style={'width': '350px'}
        ),
        html.Div(id='script-div'), 
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
        ]),

        html.Br(),
        html.Br(), 
    ])
])

# Callback to display Script-level stats
@app.callback(
    Output('script-div', 'children'), 
    [Input('script-dropdown', 'value')]
)
def display_script_statistics(selected_script):
    if selected_script:
        filtered_data = df[df['category'] == selected_script]
        n_datasets = filtered_data['dataset'].nunique()
        selected_datasets = list(filtered_data.dataset.unique())
        image_counts_list = [[dataset, get_dataset_image_counts(IMAGES_ROOT, selected_script, dataset)['total']] for dataset in selected_datasets]
        return html.Div([
            html.P(f"{n_datasets} datasets available. Total {sum([row[1] for row in image_counts_list])} images."),
            html.Ul([html.Li(f'{row[0]} - {row[1]} images') for row in image_counts_list]),
        ])
    return "Please select a valid script/ category."


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
            image_counts = render_image_counts(IMAGES_ROOT, selected_category, selected_dataset)
            stats = filtered_data.iloc[0]
            return html.Div([
                image_counts, 
                html.P(f"Average Height: {stats['avg_height']}"),
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
            ),
            # http://10.4.16.102:2308/arabic/moc/train/0
            html.Div(
                dbc.Button(
                    "Open Image in SAL Viewer", color="secondary", className="me-md-2",
                    href=f"http://10.4.16.102:2308/{selected_category}/{selected_dataset}/{selected_split}/{int(get_image_id(selected_image))}", 
                    target="_blank", 
                style={'margin-top': '20px'}
                ),
            ),
            
        ])
    return ''

def parse_args():
    parser = argparse.ArgumentParser(description="Run the Flask app")
    parser.add_argument('--debug', action='store_true', help="Run the app in debug mode")
    return parser.parse_args()

if __name__ == '__main__':
    # for debug use port 2301, else 2300
    args = parse_args()
    print(args.debug)
    if args.debug:
        app.run(debug=args.debug, host='0.0.0.0', port=2301)
    else:
        app.run(debug=args.debug, host='0.0.0.0', port=2300)
