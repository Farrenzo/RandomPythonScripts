#Add, or delete entries to a JSON file.

import os, json
from json import JSONEncoder

with open('/animals - Copy.json', 'r') as data_file:
    animals = json.load(data_file)
    print(animals)

program = 0
while program < 1:
    name = input('Enter animal to be deleted: ')
    try:
        old_cat = [animal for animal in animals if animal['name'] == name]
        animals.remove(old_cat[0])
        
        os.unlink('/animals - Copy.json')
        new_file = open('/new_animals.json', 'w')
        new_file.write(str(JSONEncoder(indent=4).encode(animals)))

        program = 1
    except IndexError:
        result = 'That animal is not in the database.'
