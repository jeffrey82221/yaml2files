import os
import yaml
import jinja2
import copy
import shutil

def get_config(config_file):
    with open(config_file, 'r') as f:
        result = yaml.safe_load(f)
    return result['template']

def create_folder(folder_name):
    if not os.path.exists(folder_name):
        os.mkdir(folder_name)
        print('folder:', folder_name, 'created')


def create_file(file_name, content):
    with open(file_name, 'w') as f:
        f.write(content)
    print('file:', file_name, 'created')

def render(template, vars):
    return jinja2.Template(template).render(**vars)

def generate_files(folders, directory = '.', var_instance=dict()):
    for _, folder_content in folders.items():
        folder_name = render(folder_content['name'], var_instance)
        create_folder(directory + '/' + folder_name)
        if 'files' in folder_content:
            for _, file_content in folder_content['files'].items():
                file_name = render(file_content['name'], var_instance)
                file_content = render(file_content['content'], var_instance)
                create_file(directory + '/' + folder_name + '/' + file_name, file_content)
        elif 'folders' in folder_content:
            generate_files(folder_content['folders'], 
                            directory=directory + '/' +folder_name, var_instance=var_instance)

def get_permute(top_list):
    results = []
    def permute(top_list, data=[]):
        _top_list = copy.copy(top_list)
        if len(_top_list)==0:
            results.append(data)
        else:
            num = _top_list.pop()
            for i in range(num):
                permute(_top_list, data=copy.copy(data + [i]))
    permute(top_list)
    return results

def permute_matrix(matrix):
    vars = list(matrix.keys())
    top_num_list = [len(matrix[var]) for var in vars][::-1]
    indices_list = get_permute(top_num_list)
    results = []
    for indices in indices_list:
        results.append(dict([(var, matrix[var][indices[i]]) for i, var in enumerate(vars)]))
    return results

def generate_all_files(folders, matrix):
    instances = permute_matrix(matrix)
    print(instances)
    for var_instance in instances:
        generate_files(folders, var_instance=var_instance)

if __name__ == '__main__':
    config = get_config('template.yml')
    generate_all_files(config['folders'], config['matrix'])