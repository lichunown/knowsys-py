import json
import os.path
import pickle as pk

import numpy as np
import torch
import hashlib
from typing import Union


def md5(data: Union[str, bytes]):
    if isinstance(data, str):
        data = data.encode('utf-8')
    md5 = hashlib.md5()
    md5.update(data)
    return md5.hexdigest()


def write_txt(path, data):
    with open(path, 'w', encoding='utf8') as f:
        f.write(data)


def load_txt(path):
    with open(path, 'r', encoding='utf8') as f:
        return ''.join(f.readlines())


def load_json(path):
    with open(path, 'r', encoding='utf8') as f:
        return json.load(f)


def clean_data(data):
    if isinstance(data, dict):
        return {k: clean_data(v) for k, v in data.items()}
    if isinstance(data, list):
        return [clean_data(item) for item in data]
    if isinstance(data, tuple):
        return tuple([clean_data(item) for item in data])
    if isinstance(data, np.ndarray):
        return data.tolist()
    if isinstance(data, torch.Tensor):
        return data.detach().cpu().numpy().tolist()
    return data


def write_json(path, data, oneline=False):
    with open(path, 'w', encoding='utf8') as f:
        indent = 4 if not oneline else None
        json.dump(clean_data(data), f, ensure_ascii=False, indent=indent)


def write_pickle(path, data):
    dir_path = os.path.split(path)[0]
    os.makedirs(dir_path, exist_ok=True)
    with open(path, 'wb') as f:
        pk.dump(data, f)

def load_pickle(path):
    dir_path = os.path.split(path)[0]
    os.makedirs(dir_path, exist_ok=True)
    with open(path, 'rb') as f:
        return pk.load(f)
