import bpy

from bpy.props import (
	StringProperty,
	IntProperty,
	FloatProperty,
	CollectionProperty,
	BoolProperty,
	EnumProperty,
)
from bpy.types import Operator, Panel, PropertyGroup
from .utils import textBox, play_sound
from .main_vars import separate_chr


class EMB_PT_main_panel(Panel):
	bl_label = 'Easy Message Board'
	bl_category = 'Tool'
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'UI'

	def draw(self, context):
		layout = self.layout
		#return
		emb_entries: dict = context.window_manager.emb_entries
		items = emb_entries.items()
		items = sorted(items, key=lambda a: a[1]['name'])
		for id, entry in items:
			original_panel = entry['panel_draw']
			panel, body = layout.panel(original_panel.bl_idname, default_closed=True)
			original_panel.draw_header(context, panel)
			if body:
				original_panel.draw(context, body)

		layout.operator('emb.adjust_preferences')


class EMB_PT_gen_panel(Panel):
	bl_label = 'Generate Message'
	bl_category = 'Tool'
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'UI'
	bl_parent_id = 'EMB_PT_main_panel'
	bl_options = {'DEFAULT_CLOSED'}
	bl_order = 999999

	@classmethod
	def poll(cls, context):
		emb_vars = bpy.types.WindowManager.emb_vars
		return emb_vars['prefs']['show_dev_message_generator']

	def draw(self, context):
		props = context.window_manager.emb_props
		icons = bpy.types.UILayout.bl_rna.functions['label'].parameters['icon']
		layout = self.layout
		# layout.label(text='This is a tool for Developers who use EMB in their add-ons.')
		layout.operator('emb.clear_gen')
		layout.separator()
		layout.prop(props, 'message_type', expand=True)
		layout.prop(props, 'title', text='Message Title')
		if props.message_type == 'UPDATE':
			r = layout.row()
			r.alignment = 'LEFT'
			r.label(text='Version')
			r.prop(props, 'v_major', text='')
			r.prop(props, 'v_minor', text='')
			r.prop(props, 'v_patch', text='')

		# col = layout.column()
		r = layout.row()
		r1 = r.row()
		r1.alignment = 'LEFT'
		c1 = r1.column()
		c1.alignment = 'LEFT'
		c1.label(text='Icon / URL')
		r2 = r.row()
		r2.alignment = 'EXPAND'
		c2 = r2.column()
		c2.alignment = 'EXPAND'
		c2.label(text='Text / URL Name')
		r3 = r.row()
		r3.alignment = 'LEFT'
		c3 = r3.column()
		c3.alignment = 'LEFT'
		c3.label(text='Size')
		r4 = r.row()
		r4.alignment = 'RIGHT'
		c4 = r4.column()
		c4.alignment = 'RIGHT'
		c4.label(text='')
		# col.label(text='')
		for n, box in enumerate(props.text_boxes):
			if not box.is_url:
				c1.prop_search(
					box,
					'icon',
					icons,
					'enum_items',
					text='',
					icon='NONE' if not box.icon else box.icon,
				)
				c2.prop(box, 'text', text='')
				c3.prop(box, 'size', text='')
			else:
				c1.prop(box, 'link', text='')
				c2.prop(box, 'name', text='')
				c3.label(text='')
			r = c4.row(align=True)
			op = r.operator('emb.move_box', text='', icon='TRIA_UP')
			op.pos = n
			op.move = n - 1
			op = r.operator('emb.move_box', text='', icon='TRIA_DOWN')
			op.pos = n
			op.move = n + 1
			op = r.operator('emb.rem_box', icon='CANCEL', text='')
			op.pos = n
			r.prop(box, 'is_url', text='', icon='URL', toggle=True)

		layout.operator('emb.add_box')

		col = layout.column(align=True)
		col.separator()
		col.label(text='Preview —')
		layout.label(text=props.title)
		for box in props.text_boxes:
			if not box.is_url:
				textBox(layout, box.text, box.icon, box.size)
			else:
				textBox(layout, f'LINK:{box.link}|NAME:{box.name if box.name else box.link}')
		layout.label(text='—')
		layout.operator('emb.boxes_clipboard')


class EMB_OT_quick_report(Operator):
	bl_label = 'EMB Quick Report'
	bl_idname = 'emb.quick_report'

	r_type: StringProperty()
	r_message: StringProperty()

	def modal(self, context, event):
		if event.type == 'TIMER':
			self.report({self.r_type}, self.r_message)
			return {'FINISHED'}
		return {'RUNNING_MODAL'}

	def execute(self, context):
		wm = context.window_manager
		self._timer = wm.event_timer_add(0.1, window=context.window)
		wm.modal_handler_add(self)
		return {'RUNNING_MODAL'}


class EMB_OT_boxes_clipboard(Operator):
	bl_idname = 'emb.boxes_clipboard'
	bl_label = 'Copy Text Boxes to clipboard'

	def execute(self, context):
		props = context.window_manager.emb_props
		icons = bpy.types.UILayout.bl_rna.functions['label'].parameters['icon']

		if props.message_type == 'MESSAGE':
			from time import time

			texts = '\\n'.join(
				[
					box.text if not box.is_url else f'LINK:{box.link}|NAME:{box.name if box.name else box.link}'
					for box in props.text_boxes
				]
			)
			icons = ','.join([box.icon for box in props.text_boxes])
			sizes = ','.join([str(box.size) for box in props.text_boxes])
			final = separate_chr.join(
				[str(int(time())), props.title, texts, icons, sizes]
			)
			context.window_manager.clipboard = final
			self.report(
				{'INFO'},
				'Paste the contents into a new line of the message board. Do not leave empty lines before or after other messages.',
			)
			return {'FINISHED'}
		else:
			import json

			data = {
				'version': (props.v_major, props.v_minor, props.v_patch),
				'title': props.title,
				'text': '\n'.join(
					[
						box.text if not box.is_url else f'LINK:{box.link}|NAME:{box.name if box.name else box.link}'
						for box in props.text_boxes
					]
				),
				'icons': ','.join([box.icon for box in props.text_boxes]),
				'sizes': ','.join([str(box.size) for box in props.text_boxes]),
			}
			context.window_manager.clipboard = json.dumps(data, indent=2)
			self.report(
				{'INFO'},
				'Replace the entirety of the update board with the contents of the clipboard. Do not leave a trace of old messages.',
			)
			return {'FINISHED'}


class EMB_OT_move_box(Operator):
	bl_idname = 'emb.move_box'
	bl_label = 'EMB Move Box'

	pos: IntProperty()
	move: IntProperty()

	def execute(self, context):
		props = context.window_manager.emb_props
		props.text_boxes.move(self.pos, self.move)
		return {'FINISHED'}


class EMB_OT_rem_box(Operator):
	bl_idname = 'emb.rem_box'
	bl_label = 'Remove Box'

	pos: IntProperty()

	def invoke(self, context, event):
		return context.window_manager.invoke_confirm(
			self, event, title='Delete the text box?'
		)

	def execute(self, context):
		props = context.window_manager.emb_props
		props.text_boxes.remove(self.pos)
		return {'FINISHED'}


class EMB_OT_add_box(Operator):
	bl_idname = 'emb.add_box'
	bl_label = 'Add Box'

	def execute(self, context):
		props = context.window_manager.emb_props
		props.text_boxes.add()
		return {'FINISHED'}


class EMB_OT_clear_gen(Operator):
	bl_idname = 'emb.clear_gen'
	bl_label = 'Clear Message Generation'

	def invoke(self, context, event):
		return context.window_manager.invoke_confirm(
			self, event, title='Clear the message setup?'
		)

	def execute(self, context):
		props = context.window_manager.emb_props
		props.text_boxes.clear()
		props.title = 'Message Title'
		props.v_major = 1
		props.v_minor = 0
		props.v_patch = 0
		return {'FINISHED'}


class EMB_OT_ignore_version(Operator):
	bl_idname = 'emb.ignore_version'
	bl_label = 'Ignore Version'

	emb_id: StringProperty()
	v_major: IntProperty()
	v_minor: IntProperty()
	v_patch: IntProperty()

	def invoke(self, context, event):
		return context.window_manager.invoke_confirm(
			self, event, message='Irreversible!'
		)

	def execute(self, context):
		emb_entries = bpy.types.WindowManager.emb_entries
		entry = emb_entries[self.emb_id]
		ignoring = entry['data']['update_ignore_this_version']
		ignoring[0] = self.v_major
		ignoring[1] = self.v_minor
		ignoring[2] = self.v_major
		entry['data'].write()
		self.report({'INFO'}, 'You will be notified when the next version releases.')
		return {'FINISHED'}


class EMB_OT_ignore_future_versions(Operator):
	bl_idname = 'emb.ignore_future_versions'
	bl_label = 'Ignore Future Versions'

	emb_id: StringProperty()

	def execute(self, context):
		emb_entries = bpy.types.WindowManager.emb_entries
		entry = emb_entries[self.emb_id]
		data = entry['data']
		data['update_ignore_future_versions'] = bool(
			1 - data['update_ignore_future_versions']
		)
		string = (
			'You will no longer be notified for future updates.'
			if data['update_ignore_future_versions']
			else 'You will be notified for future updates.'
		)
		self.report({'INFO'}, string)
		return {'FINISHED'}


class EMB_OT_play_sound(Operator):
	bl_idname = 'emb.play_sound'
	bl_label = 'Play Sound'

	path: StringProperty()
	volume: FloatProperty()

	def execute(self, context):
		play_sound(self.path, self.volume)
		return {'FINISHED'}


class EMB_OT_adjust_preferences(Operator):
	bl_idname = 'emb.adjust_preferences'
	bl_label = 'Adjust Preferences'

	props = [
		'interval',
		'global_disable',
		'volume',
		'notification_sound',
		'never_notify',
		'show_dev_message_generator',
	]

	labels = [
		'EMB Check Interval (seconds)',
		'Globally disable EMB',
		'Notification Volume',
		'Notification Sound',
		'Never Notify (No report, no sound)',
		'Show Developer Message Generator',
	]

	interval: IntProperty(min=3)
	global_disable: BoolProperty()
	volume: FloatProperty(min=0.0, max=1.0)
	notification_sound: StringProperty(subtype='FILE_PATH')
	never_notify: BoolProperty()
	show_dev_message_generator: BoolProperty()

	def draw(self, context):
		layout = self.layout
		for prop, label in zip(self.props, self.labels):
			layout.prop(self, prop, text=label)
		op = layout.operator('emb.play_sound')
		op.path = self.notification_sound
		op.volume = self.volume

		layout.separator()
		layout.operator('wm.url_open', text='EMB Documentation', icon='URL').url = 'https://github.com/hisprofile/emb_template/blob/main/README.md'

	def invoke(self, context, event):
		emb_v = context.window_manager.emb_vars
		prefs = emb_v['prefs']

		for prop in self.props:
			setattr(self, prop, prefs[prop])

		return context.window_manager.invoke_props_dialog(
			self, width=400, title='Properties'
		)

	def execute(self, context):
		emb_v = context.window_manager.emb_vars
		prefs = emb_v['prefs']

		data = dict()
		for prop in self.props:
			data[prop] = getattr(self, prop)

		prefs.update(data)
		prefs.write()
		return {'FINISHED'}


class textbox_props(PropertyGroup):
	text: StringProperty(
		default='Sample Text', options={'TEXTEDIT_UPDATE'}, name='Text'
	)
	icon: StringProperty(default='DOT', name='Icon')
	size: IntProperty(default=56, min=0, name='Size')
	is_url: BoolProperty(default=False, name='Make Box URL')
	link: StringProperty(options={'TEXTEDIT_UPDATE'}, name='URL')
	name: StringProperty(options={'TEXTEDIT_UPDATE'}, name='URL Name')


class emb_props(PropertyGroup):
	text_boxes: CollectionProperty(type=textbox_props)
	title: StringProperty(
		name='Title',
		description='The title for this latest update/message',
		default='Message Title',
		options={'TEXTEDIT_UPDATE'},
	)
	message_type: EnumProperty(
		items=(
			('MESSAGE', 'Is Message', 'Make the generation type for messages'),
			('UPDATE', 'Is Update', 'Make the generation type for updates'),
		),
		name='Message Type',
		default='MESSAGE',
	)

	v_major: IntProperty(min=0, default=1)
	v_minor: IntProperty(min=0)
	v_patch: IntProperty(min=0)


master_classes = [
	EMB_PT_main_panel,
	EMB_PT_gen_panel,
	EMB_OT_move_box,
	EMB_OT_rem_box,
	EMB_OT_add_box,
	EMB_OT_clear_gen,
	EMB_OT_quick_report,
	EMB_OT_boxes_clipboard,
	EMB_OT_adjust_preferences,
	EMB_OT_play_sound,
	# EMB_OT_ignore_version,
	EMB_OT_ignore_future_versions,
	textbox_props,
	emb_props,
]
