import sys
import importlib
if  args := sys.argv[1:]:
    key = args[0]
else:
    key = 'pet'
key_map = {
    'pet': importlib.import_module('pet.pet'),
    'music_player': importlib.import_module('pet.music.music_player'),
    'translater': importlib.import_module('pet.translate.translater')
}

key_map[key].run()
