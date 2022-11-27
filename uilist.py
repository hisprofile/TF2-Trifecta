import bpy
from bpy.props import *
from bpy.types import *
#from bpy.utils import *
from . import icons
paints = {"A Color Similar to Slate" : '47 79 79',
    "A Deep Commitment to Purple" : '125 64 113',
    "A Distinctive Lack of Hue" : '20 20 20',
    "A Mann's Mint" : '188 221 179',
    "After Eight" : '45 45 36',
    "Aged Moustache Grey" : '126 126 126',
    "An Air of Debonair Red" : '101 71 64',
    "An Air of Debonair Blu" : '40 57 77',
    "An Extraordinary Abundance of Tinge" : '230 230 230',
    "Australium Gold" : '231 181 59',
    "Balaclavas Are Forever Red" : '59 31 35',
    "Balaclavas Are Forever Blu" : '24 35 61',
    "Color No. 216-190-216" : '216 190 216',
    "Cream Spirit Red" : '195 108 45', 
    "Cream Spirit Blu" : '184 128 53',
    "Dark Salmon Injustice" : '233 150 122',
    "Drably Olive" : '128 128 0',
    "Indubitably Green" : '114 158 66',
    "Mann Co. Orange" : '207 115 54',
    "Muskelmannbraun" : '165 117 69',
    "Noble Hatter's Violet" : '81 56 74',
    "Operator's Overalls Red" : '72 56 56',
    "Operator's Overalls Blu" : '56 66 72',
    "Peculiarly Drab Tincture" : '197 175 145',
    "Pink as Hell" : '255 105 180',
    "Radigan Conagher Brown" : '105 77 58',
    "Team Spirit Red" : '184 56 59',
    "Team Spirit Blu" : '88 133 162',
    "The Bitter Taste of Defeat and Lime" : '50 205 50',
    "The Color of a Gentlemann's Business Pants" : '240 230 140',
    "The Value of Teamwork Red" : '128 48 32',
    "The Value of Teamwork Blu" : '37 109 141',
    "Waterlogged Lab Coat Red" : '168 154 140',
    "Waterlogged Lab Coat Blu" : '131 159 163',
    "Ye Olde Rustic Colour" : '124 108 87',
    "Zepheniah's Greed" : '66 79 59'}

paintnames = list(paints.keys())
class PaintList(bpy.types.PropertyGroup):
    name: StringProperty(
        name="Name",
        description='A name for this item',
        default='untitled')

    random_prop: StringProperty(
        name='some property',
        description='',
        default='')

class MaterialList(bpy.types.PropertyGroup):
    name: StringProperty(
        name="Name",
        description='A name for this item',
        default='untitled')

    random_prop: StringProperty(
        name='some property',
        description='',
        default='')

class HISANIM_UL_PAINTLIST(bpy.types.UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.label(text=item.name, icon_value= icons.id(item.name))

        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text='')

class HISANIM_UL_MATERIALLIST(bpy.types.UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.label(text=item.name, icon='MATERIAL')

        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text='')