import bpy, os, colorsys
import bpy.utils.previews
paints = {'A Distinctive Lack of Hue': '20 20 20',
        'Aged Moustache Grey': '126 126 126',
        'An Extraordinary Abundance of Tinge': '230 230 230',
        "Operator's Overalls Red": '72 56 56',
        'The Value of Teamwork Red': '128 48 32',
        'An Air of Debonair Red': '101 71 64',
        'Dark Salmon Injustice': '233 150 122',
        'Mann Co. Orange': '207 115 54',
        'Radigan Conagher Brown': '105 77 58',
        'Cream Spirit Red': '195 108 45',
        'Waterlogged Lab Coat Red': '168 154 140',
        'Muskelmannbraun': '165 117 69',
        'Ye Olde Rustic Colour': '124 108 87',
        'Cream Spirit Blu': '184 128 53',
        'Peculiarly Drab Tincture': '197 175 145',
        'Australium Gold': '231 181 59',
        "The Color of a Gentlemann's Business Pants": '240 230 140',
        'After Eight': '45 45 36',
        'Drably Olive': '128 128 0',
        'Indubitably Green': '114 158 66',
        "Zepheniah's Greed": '66 79 59',
        "A Mann's Mint": '188 221 179',
        'The Bitter Taste of Defeat and Lime': '50 205 50',
        'A Color Similar to Slate': '47 79 79',
        'Waterlogged Lab Coat Blu': '131 159 163',
        'The Value of Teamwork Blu': '37 109 141',
        "Operator's Overalls Blu": '56 66 72',
        'Team Spirit Blu': '88 133 162',
        'An Air of Debonair Blu': '40 57 77',
        'Balaclavas Are Forever Blu': '24 35 61',
        'Color No. 216-190-216': '216 190 216',
        'A Deep Commitment to Purple': '125 64 113',
        "Noble Hatter's Violet": '81 56 74',
        'Pink as Hell': '255 105 180',
        'Balaclavas Are Forever Red': '59 31 35',
        'Team Spirit Red': '184 56 59'}

#paints = {key: list(map(lambda a: int(a)/255, val.split(' '))) for key, val in paints.items()}
#print(paints)
#paints = {key: value for key, value in sorted(paints.items(), key=lambda a: colorsys.rgb_to_hsv(int(a[1].split(' ')[0])/255, int(a[1].split(' ')[1])/255, int(a[1].split(' ')[2])/255)[0])}
#print(str(paints).replace("',", "',\n"))
def get_items(self, context):
    items = []
    directory = os.path.join(os.path.dirname(__file__), 'icons')
    #images = [img for img in os.listdir(directory) if img.endswith('.png')]

    pcoll = preview_collections['main']

    for i, name in enumerate(paints.keys()):
        filepath = os.path.join(directory, name.casefold().replace(' ', '') + '.png')
        icon = pcoll.get(name)
        if not icon:
            img = pcoll.load(name, filepath, 'IMAGE')
        else:
            img = pcoll[name]
        items.append((name, name, '', img.icon_id, i))
    return items

preview_collections = {}

# i don't even know how this stuff works lol

def register():
    bpy.types.WindowManager.hisanim_paints = bpy.props.EnumProperty(items=get_items)
    pcoll = bpy.utils.previews.new()

    preview_collections["main"] = pcoll
def unregister():
    del bpy.types.WindowManager.hisanim_paints

    for pcoll in preview_collections.values():
        bpy.utils.previews.remove(pcoll)
    preview_collections.clear()
