import os
import numpy as np
import pickle
from dash import html


def load_pickle(path):
    with open(path, 'rb') as f:
        data = pickle.load(f)
    return data

def save_pickle(data, path):
    with open(path, 'wb') as f:
        pickle.dump(data, f)

def get_image_id(image_id):
    image_id = str(image_id)
    if len(image_id) == 6 and image_id.isdigit():
        return image_id
    return f"{int(image_id):06}"

def make_path(ROOT, category, dataset, split, image_id, file=''):
    image_id = get_image_id(image_id)
    image_path = os.path.join(*[ROOT, f'{category}/{dataset}/{split}/{image_id}', file])
    return image_path
    
def extract_image_stats(data):
    return {
        'height': data['dims'][0], 
        'width': data['dims'][1], 
        'avg_ilg': data['avg_interline_gap'], 
        'n_line': len(data['all_gaps'])
    }

def get_image_stats(ROOT, category, dataset, split, image_id):
    file = 'result.pkl'
    path = make_path(ROOT, category, dataset, split, image_id, file)
    data = load_pickle(path)
    image_stats = extract_image_stats(data)
    return image_stats

def get_dataset_image_counts(ROOT, category, dataset):
    dataset_path = os.path.join(*[ROOT, category, dataset])
    image_counts_dict = {}
    for split in os.listdir(dataset_path):
        n_images = len([file for file in os.listdir(os.path.join(dataset_path, split)) if file.endswith('.jpg')])
        image_counts_dict[split] = n_images
    image_counts_dict['total'] = sum([count for count in image_counts_dict.values()])
    return image_counts_dict

def render_image_counts(ROOT, category, dataset):
    image_counts_dict = get_dataset_image_counts(ROOT, category, dataset)
    image_count_spans = []
    image_count_spans.append(html.Span([
        "No of Images in ", 
        html.B(dataset),  # Bold the dataset name
        " collection:"
    ], style={'margin-right': '20px'}))
    for key in image_counts_dict.keys():
        image_count_spans.append(
            html.Span(f'{key.capitalize()}: {image_counts_dict[key]}', style={'margin-right': '20px'})
        )

    return html.P(image_count_spans) 
