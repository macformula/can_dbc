import cantools
import math
import os
import json
import shutil
from pathlib import Path
from argparse import ArgumentParser
from sys import stderr, exit
from os import mkdir
from os.path import normpath, basename
from mako.template import Template

class Node:
    def __init__(self, name):
        self.name = name.upper()

def load_configs(filename):
    with open(filename, "r") as file:
        configs = json.load(file)
    return configs

def parse_dbc_files(dbc_path, skip_files, verbose=False):
    can_db = cantools.database.Database()
    dbc_files = []

    if verbose:
        print("Adding dbc files:")
    for filename in os.listdir(dbc_path):
        f = os.path.join(dbc_path,filename).replace("\\","/")

        if os.path.isfile(f) and str(f).endswith(".dbc") and (filename not in skip_files):
            if verbose:
                print("\t", filename)
            dbc_files.append(f)

    if len(dbc_files) == 0:
        print(f'ERROR: no dbc files found in path: "{dbc_path}"')
        sys.exit()

    for f in dbc_files:
        with open(f, 'r') as fin:
            can_db.add_dbc(fin)
    
    return can_db

def get_signal_types(can_db):
    sig_types = {}

    for message in can_db.messages:
        for signal in message.signals:
            num_bits = signal.length
            sign = ""

            if signal.scale > 1: 
                num_bits = signal.length + math.ceil(math.log2(signal.scale))

            if not signal.is_signed:
                sign = "u"
            
            if isinstance(signal.scale, float) or signal.is_float:
                if num_bits < 32:
                    sig_types[message.name+signal.name] = "float"
                    continue
                else:
                    sig_types[message.name+signal.name] = "double"
                    continue
            if num_bits == 1:
                sig_types[message.name+signal.name] = "_Bool"
            elif num_bits <= 8:
                sig_types[message.name+signal.name] = sign + "int8_t"
                continue
            elif num_bits <= 16:
                sig_types[message.name+signal.name] = sign + "int16_t"
                continue
            elif num_bits <= 32:
                sig_types[message.name+signal.name] = sign + "int32_t"
                continue
            else:
                sig_types[message.name+signal.name] = sign + "int64_t"
                continue
                
    return sig_types

def template_render(tmpl_dir, out_dir, tmpl_files, can_db, node, sig_types_dict):
    try:
        for template in tmpl_files:
            template_file_path = (
                tmpl_dir + "/" + basename(normpath(template)))
            print(f"Rendering {template_file_path}")
            output_file_path = (
                out_dir + "/" + basename(normpath(template))).replace(".tmpl", "")
            print(f"Generating {output_file_path}")
            # Create output directory if it doesn't exist
            try:
                mkdir(out_dir)
            except FileExistsError as e:
                # Directory already exists
                pass
            try:
                with open(Path(template_file_path).resolve(), 'rb') as tf:
                    template = Template(tf.read())
                    try:
                        with open(Path(output_file_path), 'wb') as of:
                            template_output = template.render(
                                can_db=can_db, node=node, sig_types=sig_types_dict)
                            of.write(template_output.encode('utf8'))
                    except FileNotFoundError as e:  # pylint: disable=possibly-unused-variable
                        print(
                            f"Could not find : {Path(output_file_path).resolve()}")
            except FileNotFoundError as e:  # pylint: disable=possibly-unused-variable
                print(f"Could not find : {Path(template_file_path).resolve()}")
    except FileNotFoundError as e:  # pylint: disable=possibly-unused-variable
        print(f"{e} : {Path(args.can_tmpl_fp).resolve()}")
        print(can_descriptor.ecu_name)

def move_files(move_to_dest_path, base_src_path_c, base_src_path_h, base_dst_path_c, base_dst_path_h):
    if move_to_dest_path:
        # Make full path to allow overwritting
        full_src_path_c = fr"{base_src_path_c}\canal_messages.c"
        full_dst_path_c = fr"{base_dst_path_c}\canal_messages.c"
        full_src_path_h = fr"{base_src_path_h}\canal_messages.h"
        full_dst_path_h = fr"{base_dst_path_h}\canal_messages.h"

    try:
        # Extract the destination directory path from the destination file
        dest_dir = os.path.dirname(full_dst_path_c)

        # Create the destination directory if it doesn't exist
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)

        # Copy the file to the destination
        shutil.copy(full_src_path_c, full_dst_path_c)
        shutil.copy(full_src_path_h, full_dst_path_h)
        print(fr"Copied {full_src_path_c} --> {full_dst_path_c}")
        print(fr"Copied {full_src_path_h} --> {full_dst_path_h}")
    except Exception as e:
        print(f"Error: {e}")

def main():
    json_file = "configs/tms.json"

    # Load the constants from the JSON file
    configs = load_configs(json_file)
    node = Node(configs["NODE"])

    dbc_path = configs["DBC_PATH"]
    skip_files = configs["IGNORED_DBCS"]

    can_db = parse_dbc_files(dbc_path, skip_files, verbose=True)
    sig_types = get_signal_types(can_db)
    
    tmpl_dir = configs["TEMPLATE_LOCATION"]
    out_dir = configs["OUTPUT_LOCATION"]
    tmpl_files = ["canal_messages.c.tmpl", "canal_messages.h.tmpl"]
    template_render(tmpl_dir, out_dir, tmpl_files, can_db, node, sig_types)

    move_to_dest_path = configs["MIGRATE_FILES"]
    # Where the files are taken from
    base_src_path_c = configs["OUTPUT_LOCATION"]
    base_src_path_h = configs["OUTPUT_LOCATION"]
    # Where the files are going
    base_dst_path_c = configs["MOVE_TO_LOCATION"]
    base_dst_path_h = configs["MOVE_TO_LOCATION"]
    move_files(move_to_dest_path, base_src_path_c, base_src_path_h, base_dst_path_c, base_dst_path_h)

if __name__ == "__main__":
    main()