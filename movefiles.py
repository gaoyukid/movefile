import os
import sys
import argparse
import shutil
import os
import glob
import logging

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

default_suffix_types_str = ','.join(['mp4', 'avi', 'mkv', 'wmv','rm','rmvb'])



reverse_type_func_dict = {
    'type1': lambda st: f'{st[-1]}{st[0:-1]}',
    'type2': lambda st: f'{st[1:]}{st[0]}',
    'type3': lambda st: f'{st[::-1]}',
}



def generate_suffix_mapping_func(action, suffix_types, reverse_type_funcs):
    if action == 'open':
        # generate two mapping
        # 4mp -> mp4
        # 4pm -> mp4
        # kvm -> mkv
        # via -> avi
        # TODO: what if reverse type has conflict? i.e. .aba will result in .aba for type1, type2 and type3
        reverse_suffix_dict = {}
        for st in suffix_types:
            for reverse_type_func in reverse_type_funcs:
                reverse_suffix_dict[reverse_type_func(st)] = st
        #reverse_suffix_dict = { reverse_type_func(st):st for st in suffix_types for reverse_type_func in reverse_type_funcs}
        # quick assert no conflict
        
        for item in reverse_suffix_dict:
            assert item not in reverse_suffix_dict.values()
        def suffix_mapping_reverse(curr_suffix):
            new_suffix = reverse_suffix_dict.get(curr_suffix)
            if new_suffix is not None:
                return new_suffix
            return None
        return suffix_mapping_reverse
    else:
        def suffix_mapping_open(curr_suffix):
            if curr_suffix in suffix_types:
                # for close, will always use type3
                new_suffix = reverse_type_func_dict['type3'](curr_suffix)
                return new_suffix
        return suffix_mapping_open
        


def change_file_name(filepath: str, suffix_mapping_func)->str:
    '''
    should change filename by its suffix, i.e. mp4 -> 4pm
    '''
    filedir = os.path.dirname(filepath)
    filename_tokens = os.path.basename(filepath).split('.')
    curr_suffix = filename_tokens[-1]
    new_suffix = suffix_mapping_func(curr_suffix)
    if new_suffix is not None:
        new_filename = '.'.join(filename_tokens[:-1] + [new_suffix])
        return os.path.join(filedir, new_filename)
    return None

def get_file_iterators(root_path: str):
    target_path = os.path.join(root_path, '**')
    return glob.iglob(target_path, recursive=True)


def main():
    parser = argparse.ArgumentParser('hello')
    parser.add_argument('-a', '--action', dest='action', type=str, help='action, open or close')
    parser.add_argument('-r', '--root', dest='root', type=str, help='root of the dir to flip')
    parser.add_argument('--suffix', dest='suffix_types', type=str, default=default_suffix_types_str, 
                        help=f'comma-separated suffix types to include, default to {default_suffix_types_str}')
    parser.add_argument('-t', '--reverse-type', dest='reverse_type', type=str, default='all', 
                        help=f'type1: file.abc -> file.cba; type2: file.abc -> file.cab; type3: file.abc -> file.bca; all: all above')
    args = parser.parse_args()
    action = args.action
    root_path = args.root
    suffix_types = args.suffix_types.split(',')
    reverse_type = args.reverse_type
    if not root_path:
        # use where the script is
        # would be interesting to see what happens when
        # it is an exe
        root_path = os.path.dirname(__file__)
    logging.info(f'action: {action}, root: {root_path}')
    total = 0
    changed = 0
    error = 0
    reverse_type_funcs = list(reverse_type_func_dict.values()) if reverse_type == 'all' else [reverse_type_func_dict[reverse_type]]
    suffix_mapping_func = generate_suffix_mapping_func(action, suffix_types, reverse_type_funcs)
    for fp in get_file_iterators(root_path):
        total += 1
        new_fp = change_file_name(fp, suffix_mapping_func)
        if new_fp is not None:
            try:
                shutil.move(fp, new_fp)
                logging.debug(f'changed {fp} -> {new_fp}')
                changed += 1
            except Exception as ex:
                error += 1
                logging.error(f'error change {fp} -> {new_fp}')

    logging.info(f'operation {action} complete, {changed} changed, {error} errors, {total} in total')


if __name__ == '__main__':
    main()