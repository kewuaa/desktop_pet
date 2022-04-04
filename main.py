import sys
import importlib


if args := sys.argv[1:]:
    key = args[0]
else:
    key = 'pet'
key_map = {
    'pet': 'pet.pet',
    'music_player': 'pet.music.music_player',
    'translater': 'pet.translate.translater',
}
assert key in key_map, 'params error'

importlib.import_module(key_map[key]).run()
