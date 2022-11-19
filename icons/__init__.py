import bpy
import bpy.utils.previews
import os


pcoll = None


def id(identifier):
    global pcoll

    #try:
    return pcoll[identifier.replace(' ','').casefold().replace('png','').replace('svg','')].icon_id

    #except:
        #return pcoll['missing'].icon_id


def register():
    global pcoll
    pcoll = bpy.utils.previews.new()
    directory = os.path.dirname(__file__)

    for filename in os.listdir(directory):
        if filename.lower().endswith('.png') or filename.lower().endswith('.svg'):
            name = filename.lower().replace('.png','').replace('.svg','')
            path = os.path.join(directory, filename)
            pcoll.load(name, path, 'IMAGE')


def unregister():
    global pcoll
    bpy.utils.previews.remove(pcoll)
