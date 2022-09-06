'''
Author: zhuyf
Date: 2022-02-23 16:25:28
LastEditors: error: git config user.name && git config user.email & please set dead value or install git
LastEditTime: 2022-06-09 08:39:49
Description: file content
FilePath: /jp6_test/sub/sub_interface_json.py
'''

import json


def read_data():
    inp = {}
    fp = open('inp.dat', 'r')
    for line in fp:
        if line.strip() != '':
            inp[line.split()[0]] = line.split()[1]
    return inp


def read_data_with_label(filename):
    inp = {}
    fp = open(filename, 'r')
    for line in fp:
        if line.strip() != '':
            if "=" in line.strip():
                string_read = line.strip().split('=', 1)
                string_zero = string_read[0].replace(' ', '')
                strong_one = string_read[1].replace(' ', '')
                inp[string_zero] = strong_one
    return inp


def load_json(filename):
    """
    load an object in json format.
    """
    json.encoder.FLOAT_REPR = lambda f: format("%.18g" % f)
    fp = open(filename, mode='r')
    obj = json.load(fp)
    return obj



def dump_json(filename, obj):
    """
    dump an object in json format.
    """
    json.encoder.FLOAT_REPR = lambda f: format("%.18g" % f)
    fp = open(filename, mode='w')
    my_str = json.dumps(obj, indent=2)
    fp.write(my_str)
    fp.close()
    return


def input_to_json_file (input_file, json_file) :
    xxx = read_data_with_label (input_file)
    dump_json(json_file, xxx)
    
def read_from_json (json_file) :
    para_all = load_json(json_file)
    return para_all

def input_and_read(input_file, json_file):
    input_to_json_file (input_file, json_file)
    para_all = read_from_json(json_file)
    return para_all 