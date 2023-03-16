import os
import sys
import argparse
import os
import logging
import string
import random

logging.basicConfig(stream=sys.stdout, level=logging.INFO)




def generate_random_string(N=7):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=N))


class Node(object):
    IDENTIFIER = '__biku__'
    def __init__(self, value, is_dir = True):
        self.parent = None
        self.value = value
        self.children = []
        self.is_dir = is_dir

    def __repr__(self) -> str:
        return f'{self.value}'

    def deep_copy(self):
        result = Node(value = self.value, is_dir=self.is_dir)
        result.parent = self.parent
        for child in self.children:
            child_copy = child.deep_copy()
            child_copy.parent = result
            result.children.append( child_copy )
        return result
    
    def random_names(self, recursive=False):
        filename = os.path.basename(self.value)
        filefolder = os.path.dirname(self.value)
        # only change dir name, leave file name alone
        new_filename = generate_random_string(len(filename)) if self.is_dir else filename
        if self.parent:
            self.value = os.path.join(self.parent.value, new_filename)
        else:
            self.value = os.path.join(filefolder, new_filename)
        if recursive:
            for child in self.children:
                child.random_names(recursive)

    @staticmethod
    def get_folder_structure(root_path):
        result = Node(root_path)
        if not os.path.isdir(root_path):
            result.is_dir = False
            return result
        else:
            for sub_dir in os.listdir(root_path):
                sub_node = Node.get_folder_structure(os.path.join(root_path, sub_dir) )
                result.children.append(sub_node)
                sub_node.parent = result
        return result

    def safe_create_folder_structure(self, recursive=False, dry_run=False):
        total = 0
        changed = 0
        error = 0
        try:
            total += 1
            if self.is_dir:
                # is a dir
                if dry_run:
                    logging.info(f'to create {self.value}')
                    logging.info(f'to create {os.path.join(self.value, self.IDENTIFIER)}')
                else:
                    os.makedirs(self.value, exist_ok=True)
                    os.makedirs(os.path.join(self.value, self.IDENTIFIER), exist_ok=True)
                
            else:
                # is a file, use random file name as content, but with IDENDIFIER as file name
                file_content = os.path.basename(self.value)
                if dry_run:
                    logging.info(f'to create {self.value}')
                else:
                    with open(self.value, 'w') as f:
                        f.write(file_content)
                
            changed += 1
        except:
            error += 1
            logging.error(f'error create {self.value}, is_dir: {self.is_dir}')

        if recursive:
            for child in self.children:
                sub_total, sub_changed, sub_error = child.safe_create_folder_structure(recursive, dry_run)
                total += sub_total
                changed += sub_changed
                error += sub_error
        
        return total, changed, error

def main():
    parser = argparse.ArgumentParser('hello')
    parser.add_argument('-m', '--multiply', dest='multiply', type=int, default=1, help='multiply by number')
    parser.add_argument('-r', '--root', dest='root', type=str, help='root of the dir to flip')
    parser.add_argument('-d', '--dry-run', dest='dry_run', action='store_true', help=f'to dry run')
    args = parser.parse_args()
    multiply = args.multiply
    root_path = args.root
    dry_run = args.dry_run
    if not root_path:
        # use where the script is
        # would be interesting to see what happens when
        # it is an exe
        root_path = os.path.dirname(__file__)
    logging.info(f'multiply: {multiply}, root: {root_path}')
    total = 0
    changed = 0
    error = 0

    root_node = Node.get_folder_structure(root_path)
    recorded_smear_roots = []
    for i in range(multiply):
        copy_root_node = root_node.deep_copy()
        copy_root_node.random_names(recursive=True)
        sub_total, sub_changed, sub_error = copy_root_node.safe_create_folder_structure(recursive=True, dry_run=dry_run)
        total += sub_total
        changed += sub_changed
        error += sub_error
        recorded_smear_roots.append(copy_root_node.value)

    logging.info(f'operation smear complete, {changed} changed, {error} errors, {total} in total')
    logging.info(f'smear root dirs are: {recorded_smear_roots}')


if __name__ == '__main__':
    main()