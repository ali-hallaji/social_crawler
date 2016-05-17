# Python Import
import codecs
import json

# Core import
from config.settings import BASE_DIR


def added_component(name):
    json_path = BASE_DIR + '/config/installed_component.json'
    read_component = open(json_path, 'r').read()

    installed_component = json.loads(read_component)
    installed_component.append(name)
    data = json.dumps(installed_component, sort_keys=True, ensure_ascii=False)

    with codecs.open(json_path, 'w', 'utf8') as write_json:
        write_json.write(data)

