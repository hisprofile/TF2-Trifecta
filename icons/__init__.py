import bpy
import bpy.utils.previews
import os


pcoll = None

mercs = ['scout', 'soldier', 'pyro', 'demo',
            'heavy', 'engineer', 'medic', 'sniper', 'spy']

def id(identifier):
    global pcoll

    if pcoll.get(identifier) != None:
        return pcoll[identifier].icon_id
    else:
        return 0

    #except:
        #return pcoll['missing'].icon_id


def register():
    global pcoll
    pcoll = bpy.utils.previews.new()
    directory = os.path.dirname(__file__)
    names = []

    for filename in os.listdir(directory):
        path = os.path.join(directory, filename)
        if not os.path.isfile(path):
            continue
        if not path.endswith('.png'): continue
        name = filename[:filename.rindex('.')]
        names.append(name)
        pcoll.load(name, path, 'IMAGE')
        #pcoll[name].icon_size = pcoll[name].image_size
        #pcoll[name].icon_pixels = pcoll[name].image_pixels

    #for name in names:
    for merc in mercs:
        if (p := pcoll.get(merc)) != None:
            p.icon_size = p.image_size
            p.icon_pixels = p.image_pixels

def unregister():
    global pcoll
    bpy.utils.previews.remove(pcoll)
