import os
import numpy as np
import pickle

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