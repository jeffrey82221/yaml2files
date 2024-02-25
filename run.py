import os
import yaml
import jinja2
import copy


def get_config(config_file):
    with open(config_file, 'r') as f:
        result = yaml.safe_load(f)
    return result['template']


def create_folder(folder_name):
    if not os.path.exists(folder_name):
        os.mkdir(folder_name)
        print('folder:', folder_name, 'created')


def create_file(file_name, content):
    _content = copy.copy(content)
    with open(file_name, 'w') as f:
        f.write(_content)
    print('file:', file_name, 'created')


def render(template, vars):
    _template = copy.copy(template)
    return jinja2.Template(_template).render(**vars)


def get_permute(top_list):
    results = []

    def permute(top_list, data=[]):
        _top_list = copy.copy(top_list)
        if len(_top_list) == 0:
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
        results.append(dict([(var, matrix[var][indices[i]])
                       for i, var in enumerate(vars)]))
    return results


def expand_var_instance(var_instance, matrix):
    var_instance_list = []
    for var_instance in permute_matrix(matrix):
        _var_instance = copy.copy(var_instance)
        _var_instance.update(var_instance)
        var_instance_list.append(_var_instance)
    return var_instance_list


def generate_files(folders, directory='.', var_instance=dict()):
    for _, folder_content in folders.items():
        if 'matrix' in folder_content:
            var_instance_list = expand_var_instance(
                var_instance, folder_content['matrix'])
        else:
            var_instance_list = [var_instance]
        for var_i in var_instance_list:
            folder_name = render(folder_content['name'], var_i)
            create_folder(directory + '/' + folder_name)
            if 'files' in folder_content:
                for _, file_content in folder_content['files'].items():
                    if 'matrix' in file_content:
                        var_instance_list_inner = expand_var_instance(
                            var_instance, file_content['matrix'])
                    else:
                        var_instance_list_inner = [var_instance]
                    for var_j in var_instance_list_inner:
                        file_name = render(file_content['name'], var_j)
                        content_text = render(file_content['content'], var_j)
                        create_file(
                            directory +
                            '/' +
                            folder_name +
                            '/' +
                            file_name,
                            content_text)
            elif 'folders' in folder_content:
                generate_files(folder_content['folders'],
                               directory=directory + '/' + folder_name, var_instance=var_i)


def generate_all_files(folders, matrix):
    instances = permute_matrix(matrix)
    print(instances)
    for var_instance in instances:
        generate_files(folders, var_instance=var_instance)


if __name__ == '__main__':
    config = get_config('template.yml')
    generate_all_files(config['folders'], config['matrix'])
