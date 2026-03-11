import json

from artillery_struct import Artillery


def save_artillery(artillery, filename):
    with open(filename, 'w') as f:
        f.write(artillery.to_json())


def load_artillery(filename):
    with open(filename, 'r') as f:
        json_data = f.read()
        return Artillery.from_json(json_data)


def save_artillery_list(artillery_list, filename):
    with open(filename, 'w') as f:
        json_list = [art.to_json() for art in artillery_list]
        json.dump([json.loads(j) for j in json_list], f, indent=4)


def load_artillery_list(filename):
    with open(filename, 'r') as f:
        data_list = json.load(f)
        return [Artillery.from_json(json.dumps(data)) for data in data_list]
