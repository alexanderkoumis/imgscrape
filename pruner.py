#!/usr/bin/env python

import json
import sys
from os import makedirs
from os.path import basename, isdir, isfile, join
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
json_path = join(scraped_dir, 'lol4.json')
cascade_cpu_path = join(scraped_dir, 'haarcascade_frontalface_default.xml')
cascade_gpu_path = join(scraped_dir, 'haarcascade_frontalface_default_cuda.xml')


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
    pruned_path = '{}_pruned.json'.format(json_path.split('.')[0])
    with open(pruned_path, 'w') as outfile:
        outfile.write(json.dumps(image_obj, sort_keys=True, indent=4, ensure_ascii=False))

def separate_images(image_obj):

    def prune_func_gpu(image_path):
        if isfile(image_path):
            print image_path
            faces = cv2gpu.find_faces(image_path)
            if len(faces) > 0:
                return True
        return False

    def prune_func_cpu(image_path):
        if isfile(image_path):
            image = cv2.imread(image_path, 0)
            faces = cascade.detectMultiScale(image, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30), flags=cv2.cv.CV_HAAR_SCALE_IMAGE)
            if len(faces) > 0:
                return True
        return False

    if not isfile(cascade_gpu_path) or not isfile(cascade_cpu_path):
        print '{} or {} is not a file'.format(cascade_gpu_path, cascade_cpu_path)
        sys.exit(1)

    prune_func = None

    if cv2gpu_imported:
        prune_func = prune_func_gpu
        if cv2gpu.is_cuda_compatible():
            cv2gpu.init_gpu_detector(cascade_gpu_path)
        else:
            cv2gpu.init_cpu_detector(cascade_cpu_path)
    else:
        prune_func = prune_func_cpu
        cascade = cv2.CascadeClassifier(cascade_cpu_path)

    for tld in image_obj:
        out_dir = join(scraped_dir, 'processed', tld)
        images = image_obj[tld]
        for url in images:
            path_orig = images[url]
            base = basename(path_orig)
            path_new = join(out_dir, base)
            if prune_func(path_orig):
                if not isdir(out_dir):
                    makedirs(out_dir)
                copy2(path_orig, path_new)
                images[url] = path_new
    return image_obj

def main():
    images_list = load_json(json_path)
    images_list = prune_paths(images_list)    
    image_obj = prune_nonexisting(images_list)
    image_obj = sort_domains(image_obj)
    image_obj = separate_images(image_obj)
    write_json(image_obj)

if __name__ == '__main__':
    main()
