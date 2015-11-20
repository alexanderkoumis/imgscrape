#!/usr/bin/env python

import json
import os
import sys
import timeit
from os import makedirs
from os.path import basename, dirname, getsize, isdir, isfile, join, realpath
from shutil import copy2
from StringIO import StringIO
from tld import get_tld
from tld.utils import update_tld_names

import cv2
cv2gpu_imported = True
try:
    import cv2gpu
except ImportError:
    print 'Install github.com/alexanderkoumis/opencv-gpu-py for faster pruning'
    cv2gpu_imported = False
    pass


scraped_dir = '/home/dev/Datasets/scrapy_collected/'
json_path_orig = join(scraped_dir, 'lol5.json')
processed_dir = join(scraped_dir, 'processed')
json_path_pruned = join(processed_dir, 'lol5_pruned.json')

cascade_dir = join(dirname(realpath(__file__)), 'haarcascades')
cascade_cpu_path = join(cascade_dir, 'haarcascade_frontalface_default.xml')
cascade_gpu_path = join(cascade_dir, 'haarcascade_frontalface_default_cuda.xml')

if isfile(json_path_pruned):
    os.remove(json_path_pruned)

def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)

def prune_paths(image_list):
    image_list_ret = []    
    for image_info in image_list:
        del image_info['image_urls']
        if len(image_info['images']) > 0:
            image_list_ret.extend(image_info['images'])
    return image_list_ret

def prune_nonexisting(image_list):
    image_obj = {}
    for image_info in image_list:
        image_path = join(scraped_dir, image_info['path'])
        if isfile(image_path):
            image_obj[image_path] = image_info['url']
    return image_obj

def sort_domains(image_obj):
    update_tld_names()
    image_obj_ret = {}
    for path in image_obj:
        url = image_obj[path]
        try:
            tld = get_tld(url)
            if tld not in image_obj_ret:
                image_obj_ret[tld] = {}
            image_obj_ret[tld][url] = path
        except:
            pass
    return image_obj_ret

def write_json(image_obj):
    with open(json_path_pruned, 'w') as outfile:
        outfile.write(json.dumps(image_obj, sort_keys=True, indent=4, ensure_ascii=False))

def count_images(image_obj):
    num_images = 0
    for tld in image_obj:
        images = image_obj[tld]
        for url in images:
            num_images += 1
    return num_images

def separate_images(image_obj):

    size_file_max = 200000

    def prune_func_gpu(image_path):
        if getsize(image_path) < size_file_max:
            faces = cv2gpu.find_faces(image_path)
            if faces:
                return len(faces) > 0
        return False

    def prune_func_cpu(image_path):
        if getsize(image_path) < size_file_max:
            image = cv2.imread(image_path, 0)
            faces = cascade.detectMultiScale(image)
            if faces:
                return len(faces) > 0
        return False

    if not isfile(cascade_gpu_path) or not isfile(cascade_cpu_path):
        print '{} or {} is not a file'.format(cascade_gpu_path, cascade_cpu_path)
        sys.exit(1)

    prune_func = None

    if cv2gpu_imported:
        prune_func = prune_func_gpu
        if cv2gpu.is_cuda_compatible():
            print 'Using GPU detector'
            cv2gpu.init_gpu_detector(cascade_gpu_path)
        else:
            print 'Using CPU detector'
            cv2gpu.init_cpu_detector(cascade_cpu_path)
    else:
        prune_func = prune_func_cpu
        cascade = cv2.CascadeClassifier(cascade_cpu_path)

    image_num_max = count_images(image_obj)
    image_num_curr = 0

    for tld in image_obj:
        out_dir = join(processed_dir, tld)
        if not isdir(out_dir):
            makedirs(out_dir)
        images = image_obj[tld]
        for url in images:
            path_orig = images[url]
            path_new = join(out_dir, basename(path_orig))
            print 'Image {} / {}, ({})'.format(image_num_curr, image_num_max, getsize(path_orig))
            image_num_curr += 1
            if not prune_func(path_orig):
                continue
            if not isfile(path_new):
                copy2(path_orig, path_new)
            images[url] = path_new
    return image_obj

def main():
    images_list = load_json(json_path_orig)
    images_list = prune_paths(images_list)    
    image_obj = prune_nonexisting(images_list)
    image_obj = sort_domains(image_obj)
    image_obj = separate_images(image_obj)
    write_json(image_obj)

if __name__ == '__main__':
    start_time = timeit.default_timer()
    main()
    elapsed = timeit.default_timer() - start_time
    print 'Process took this long: {}'.format(elapsed)
