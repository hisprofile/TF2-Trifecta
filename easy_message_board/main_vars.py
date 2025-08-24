import bpy
import os
from pathlib import Path

emb_path = os.path.dirname(__file__)
emb_data_path = os.path.join(emb_path, 'data.json')
path_split = emb_path.split(os.path.sep)
addon_path = os.path.sep.join(path_split[:-1])
addon_path_name = os.path.basename(addon_path)
blender_resource_path = str(Path(bpy.utils.resource_path('USER')).parents[0])
global_prefs_folder = os.path.join(blender_resource_path, 'emb_data')
if not os.path.exists(global_prefs_folder):
	os.makedirs(global_prefs_folder)
global_prefs_path = os.path.join(global_prefs_folder, 'emb_prefs.json')
messages_path = os.path.join(emb_path, 'messages.data')
separate_chr = '¸'