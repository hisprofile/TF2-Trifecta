import bpy
import json
import os
import tomllib
import time
import traceback
from threading import Thread
from . import bpy_classes
from bpy.types import Panel
from bpy.utils import register_class, unregister_class
from .utils import download_file, time_to_calendar, textBox, play_sound, operator_report#, label_multiline
from .bpy_classes import master_classes
from .main_vars import (
	emb_path,
	emb_data_path,
	addon_path,
	addon_path_name,
	global_prefs_folder,
	global_prefs_path,
	messages_path,
	separate_chr
)
from bpy.props import PointerProperty

EMB_VERSION = (1, 0, 1) # i mean it's no different from using a .toml file

global_id = None
emb_id = None
emb_classes = set()

try:
	from .. import bl_info
except:
	print(f'bl_info for {os.path.basename(addon_path)} does not exist! ')
	bl_info = dict()


class AutoUpdateJson(dict):
	json_path = ''

	def auto_update(self):
		try:
			with open(self.json_path, 'w+') as file:
				file.write(json.dumps(self, indent=2))
				return None
		except:
			return None

	def write(self):
		self.auto_update()

	def __setitem__(self, key, value):
		super().__setitem__(key, value)
		self.auto_update()


class MsgsStructure(dict):
	file_path = ''
	block = False

	def __setitem__(self, key, value):
		super().__setitem__(key, value)
		if not self.block:
			self.write()

	def load(self, path):
		if not os.path.exists(path):
			raise OSError
		self.file_path = path
		file = open(path, 'r')
		string = file.read()
		file.close()
		self.string_to_dict(string)
		return self

	def string_to_dict(self, string: str):
		self.block = True
		string = string.lstrip('\n').rstrip('\n')
		lines = string.split('\n')
		while '' in lines:
			lines.remove('')
		lines = list(map(lambda a: a.split(separate_chr), lines))
		for item in lines:
			if len(item) != 5:
				continue
			id, title, text, icons, size = item
			self[int(id)] = {'title': title, 'text': text, 'icons': icons, 'size': size}
		self.block = False
		return self

	def write(self):
		file = open(self.file_path, 'w')
		for key, value in self.items():
			file.write(separate_chr.join([str(key), *list(value.values())]))
			file.write('\n')
		file.close()

	@property
	def first(self):
		return next(
			iter(sorted(list(self.items()), key=lambda a: a[0], reverse=True)), (0, 0)
		)


def get_addon_data() -> dict:
	# TOML manifest is prioritized over bl_info
	manifest_path = os.path.join(addon_path, 'blender_manifest.toml')
	if os.path.exists(os.path.join(addon_path, 'blender_manifest.toml')):
		with open(manifest_path, 'rb') as file:
			return tomllib.load(file)
	elif bl_info:
		return bl_info
	return dict()


def local_emb_settings() -> dict:
	with open(os.path.join(emb_path, 'settings.json'), 'r') as file:
		return json.loads(file.read())


def local_emb_data() -> AutoUpdateJson:
	init_data = AutoUpdateJson(
		{
			'last_message_time': int(time.time()),
			'new_messages': 0,
			'update_ignore_this_version': [0, 0, 0],
			'update_ignore_future_versions': False,
		}
	)
	if not os.path.exists(emb_data_path):
		init_data.json_path = emb_data_path
		init_data.write()
		return init_data
	else:
		try:
			with open(emb_data_path, 'r') as file:
				emb_data = AutoUpdateJson(json.loads(file.read()))
				emb_data.json_path = emb_data_path
				return emb_data
		except:
			init_data.json_path = emb_data_path
			init_data.write()
			return init_data

def global_prefs_path_exists() -> bool:
	return os.path.exists(global_prefs_path)


def global_prefs_json_write(data: dict) -> None:
	with open(global_prefs_path, 'x') as file:
		file.write(json.dumps(data, indent=2))
		return None


def global_prefs_json_read() -> dict:
	with open(global_prefs_path, 'r') as file:
		return json.loads(file.read())


def get_local_messages() -> dict:
	messages = MsgsStructure()
	if not os.path.exists(messages_path):
		messages.file_path = messages_path
		messages.write()
	else:
		try:
			messages.load(messages_path)
		except:
			messages.file_path = messages_path
			messages.write()
	return messages


addonData = get_addon_data()
emb_data = local_emb_data()
messages = get_local_messages()


def get_global_prefs() -> None:
	if global_prefs_path_exists():
		prefs = AutoUpdateJson(global_prefs_json_read())
		prefs.json_path = global_prefs_path
		return prefs
	else:  # first start
		notif_url = 'https://github.com/sourcesounds/tf/raw/refs/heads/master/sound/ui/message_update.wav'
		notif_name = notif_url.split('/')[-1]
		download_notif_thread = Thread(
			target=download_file, args=[notif_url, global_prefs_folder], daemon=True
		)
		download_notif_thread.start()
		init_data = AutoUpdateJson(
			{
				'interval': 600,  # How many seconds between each check
				'global_disable': False,  # Globally disable the checking
				'volume': 0.2,
				'notification_sound': os.path.join(global_prefs_folder, notif_name),
				'never_notify': False,
				'show_dev_message_generator': False,
			}
		)
		init_data.json_path = global_prefs_path
		init_data.write()
		return init_data


globalPrefs = get_global_prefs()
emb_settings = local_emb_settings()

def bpy_timer():
	if bpy.types.WindowManager.emb_vars['prefs']['global_disable']:
		return
	checker = Thread(target=emb_checking, daemon=True)
	checker.start()
	return bpy.types.WindowManager.emb_vars['prefs']['interval']


@bpy.app.handlers.persistent
def timer_ensure(a=None, b=None):
	if bpy.types.WindowManager.emb_vars['prefs']['global_disable']:
		return
	bpy.app.timers.register(bpy_timer)  # , first_interval=3)


def init_master() -> None:
	# Allocate globals within Blender's namespace. Is this allowed?
	bpy.types.WindowManager.emb_entries = dict()
	bpy.types.WindowManager.emb_classes = master_classes
	bpy.types.WindowManager.emb_vars = {
		'checker': emb_checking,
		'prefs': globalPrefs,
		'timer_ensure': timer_ensure,
		'bpy_timer': bpy_timer,
		'version': EMB_VERSION
	}

	[register_class(cls) for cls in master_classes]

	bpy.types.WindowManager.emb_props = PointerProperty(type=bpy_classes.emb_props)
	bpy.app.handlers.load_post.append(timer_ensure)
	bpy.app.timers.register(bpy_timer)  # , first_interval=3)


def uninit_master() -> None:
	emb_vars = bpy.types.WindowManager.emb_vars
	for cls in reversed(bpy.types.WindowManager.emb_classes):
		unregister_class(cls)
	bpy.app.handlers.load_post.remove(emb_vars['timer_ensure'])
	try:
		bpy.app.timers.unregister(emb_vars['bpy_timer'])
	except:
		pass
	del bpy.types.WindowManager.emb_entries
	del bpy.types.WindowManager.emb_classes
	del bpy.types.WindowManager.emb_vars
	del bpy.types.WindowManager.emb_props


def build_entry() -> dict:
	# addonData = get_addon_data()
	global global_id
	if not addonData:
		print(
			'Failure to retrieve addon data. Either non-existant bl_info or blender_manifest.toml!'
		)
		print(addon_path_name)
		entry = {'id': addon_path_name, 'failure': 'Missing sufficient add-on info'}
		return entry
	if (id := emb_settings.get('id')) in {None, ''}:
		id = addon_path_name

	# Check if at least one part of the EMB is configured to get any data from GitHub.
	if bool(emb_settings.get('message_board_path')):
		pass
	elif bool(emb_settings.get('update_board_path')):
		pass
	else:
		entry = {'id': id, 'failure': 'This EMB is not configured to get any data!'}
		return entry

	if (addonVersion := addonData.get('version')) in {None, ''}:  # If empty result
		addonVersion = 'N/A_VERSION'
	elif isinstance(addonVersion, str):  # if str
		addonVersion = tuple(map(int, addonVersion.split('.')))
	elif isinstance(addonVersion, tuple):  # if tuple (preferred)
		pass
	else:  # if anything else
		addonVersion = 'N/A_VERSION'

	global_id = id

	if (emb_data.get('latest_version', None) is None) and isinstance(addonVersion, tuple):
		emb_data['latest_version'] = addonVersion

	entry = {
		'id': id,
		'version': addonVersion,
		'name': addonData.get('name', id),
		'message_board_path': emb_settings.get('message_board_path'),
		'update_board_path': emb_settings.get('update_board_path'),
		'release_repository': emb_settings.get('release_repository'),
		'emb_path': emb_path,
		'data': emb_data,
		'messages': messages,
		'update_data': dict(),
		'ignore': False,  # Set this to True if an error occurs regarding its settings. It will be skipped by the checker, and only resets when Blender restarts.
		'local_classes': set(),
		'new_update': False,
	}

	return entry


def emb_checking() -> None:
	checking_vars = {
		'make_sound': False,
		'total_new_messages': 0,
		'total_new_updates': 0,
	}

	import requests

	emb_vars = bpy.types.WindowManager.emb_vars
	try:
		assert requests.get('https://www.google.com').status_code == 200
	except:
		return None

	entries: dict = bpy.types.WindowManager.emb_entries

	def process_update(entry, update_board_path):
		try:  # getting the url
			url = update_board_path
			get_messages = requests.get(url)
			assert get_messages.status_code == 200
		except:
			traceback.print_exc()
			if entry.get('last_error_upd', '') != 'UPD_BAD_URL':
				entry['last_error_upd'] = 'UPD_BAD_URL'
				operator_report(
					r_type='WARNING',
					r_message=f'{entry["id"]}: Failed to grab update data! Is the URL correct?',
				)
			return

		try:  # converting the data to a dict
			get_messages = json.loads(get_messages.content.decode())
		except:
			traceback.print_exc()
			if entry.get('last_error_upd', '') != 'UPD_BAD_ENCODE':
				entry['last_error_upd'] = 'UPD_BAD_ENCODE'
				operator_report(
					'INVOKE_DEFAULT',
					r_type='WARNING',
					r_message=f'{entry["id"]}: Failed to load update data as JSON! It was not formatted correctly!',
				)
			return

		try:
			assert bool(get_messages['version'])
			assert bool(get_messages['title'])
			assert bool(get_messages['text'])
			assert bool(get_messages['icons'])
			assert bool(get_messages['sizes'])
		except:
			bpy.ops.emb.quick_report(
				'INVOKE_DEFAULT',
				r_type='WARNING',
				r_message=f'{entry["id"]}: Update data was not formatted correctly!',
			)
			return

		get_messages['version'] = tuple(get_messages['version'])
		has_new_update = False
		no_notify = entry['data']['update_ignore_future_versions']

		if isinstance(entry['version'], tuple) and (
			get_messages['version'] > entry['version']
		):
			has_new_update = True and (not no_notify) and (not bool(entry['update_data']))
			
			entry['new_update'] = True
		if get_messages['version'] > tuple(entry['data'].get('latest_version', (0, 0, 0))):  # to prevent a ping from every time it checks and a user still hasn't updated
			checking_vars['make_sound'] = True and (not no_notify)
			has_new_update = True and (not no_notify)

		entry['data']['latest_version'] = get_messages['version']
		entry['update_data'] = get_messages
		checking_vars['total_new_updates'] += has_new_update#checking_vars['has_new_update']

	def process_messages(entry, message_board_path):
		global make_sound
		try:  # getting the url
			url = message_board_path
			get_messages = requests.get(url)
			assert get_messages.status_code == 200
		except:
			traceback.print_exc()
			if entry.get('last_error_msg', '') != 'MSG_BAD_URL':
				entry['last_error_msg'] = 'MSG_BAD_URL'
				operator_report(
					r_type='WARNING',
					r_message=f'{entry["id"]}: Failed to grab message data! Is the URL correct?',
				)
			return
		try:  # converting the data to a dict
			get_messages = MsgsStructure().string_to_dict(
				get_messages.content.decode()
			)
			assert bool(get_messages)
		except:
			traceback.print_exc()
			if entry.get('last_error_msg', '') != 'MSG_BAD_ENCODE':
				entry['last_error_msg'] = 'MSG_BAD_ENCODE'
				operator_report(
					r_type='WARNING',
					r_message=f'{entry["id"]}: Failed to read the message file! It was not written properly!',
				)
			return

		entry_msgs: MsgsStructure = entry['messages']
		entry_data: AutoUpdateJson = entry['data']
		msg_latest_time = entry_data['last_message_time']
		get_messages_latest_time = get_messages.first[0]

		if get_messages_latest_time > msg_latest_time:
			new_messages = sum(
				[bool(time > msg_latest_time) for time in get_messages.keys()]
			)
			checking_vars['total_new_messages'] += new_messages
			entry_data['new_messages'] = new_messages
			entry_data['last_message_time'] = get_messages_latest_time
			checking_vars['make_sound'] = True

		entry_msgs.clear()
		entry_msgs.update(get_messages)
		entry_msgs.write()

	for id, entry in list(entries.items()):
		if entry.get('failure'):
			continue
		if message_board_path := entry.get('message_board_path'):
			process_messages(entry, message_board_path)
		if (update_board_path := entry.get('update_board_path')) and isinstance(entry['version'], tuple):
			process_update(entry, update_board_path)

	if checking_vars['make_sound'] and (not emb_vars['prefs']['never_notify']):
		play_sound(emb_vars['prefs']['notification_sound'], emb_vars['prefs']['volume'])

	if emb_vars['prefs']['never_notify']:
		return

	def notify_user():
		if checking_vars['total_new_messages'] and checking_vars['total_new_updates']:
			message = 'messages' if checking_vars['total_new_messages'] > 1 else 'message'
			update = 'updates' if checking_vars['total_new_updates'] > 1 else 'update'
			bpy.ops.emb.quick_report(
				'INVOKE_DEFAULT',
				r_type='INFO',
				r_message=f'Tools > EMB: {checking_vars["total_new_messages"]} new {message}, {checking_vars["total_new_updates"]} new {update}!',
			)
		elif checking_vars['total_new_messages']:
			string = 'messages' if checking_vars['total_new_messages'] > 1 else 'message'
			bpy.ops.emb.quick_report(
				'INVOKE_DEFAULT',
				r_type='INFO',
				r_message=f'Tools > EMB: {checking_vars["total_new_messages"]} new {string}!',
			)
		elif checking_vars['total_new_updates']:
			string = 'updates' if checking_vars['total_new_updates'] > 1 else 'update'
			bpy.ops.emb.quick_report(
				'INVOKE_DEFAULT',
				r_type='INFO',
				r_message=f'Tools > EMB: {checking_vars["total_new_updates"]} new {string}!',
			)

	bpy.app.timers.register(notify_user)


def init_local() -> None:
	global emb_id
	entry = build_entry()
	emb_id = entry['id']

	class emb_panel: # we will use a generic class and then use layout.panel for drawing.
		bl_idname = f'EMB_PT_{emb_id}'
		label = addonData.get('name', addon_path_name)
		emb_id = entry['id']
		emb_entry = entry

		def draw_msg_body(self, context: bpy.types.Context, layout: bpy.types.UILayout):
			all_icons = bpy.types.UILayout.bl_rna.functions['label'].parameters['icon'].enum_items
			entry = self.emb_entry
			if not bool(entry.get('message_board_path')):
				layout.label(text='This EMB is not configured to check for messages.')
				return
			if not entry.get('messages', None):
				layout.label(text='No messages to display!')
				return

			if entry['data']['new_messages'] != 0:
				entry['data']['new_messages'] = 0

			for id, values in sorted(
				entry['messages'].items(), key=lambda a: a[0], reverse=True
			):
				title, text, icons, sizes = values.values()
				icons = icons.rstrip(',').lstrip(',')
				sizes = sizes.rstrip(',').lstrip(',')
				r = layout.row(align=True)
				s = r.split(factor=0.015)
				s.label(text='')
				col = s.column()
				header, body = col.panel(f'EMB_{self.emb_id}_{id}', default_closed=True)
				header.label(text=title)
				if not body:
					continue

				r = body.row(align=True)
				s = r.split(factor=0.015)
				s.label(text='')
				body = s.column(align=True)
				body.label(text='@ ' + time_to_calendar(id))
				body = body.column()
				text = text.replace('\\n', '\n')
				lines = text.split('\n')
				icons = icons.split(',')
				while len(lines) > len(icons):  # fill icons with default until length is same as text
					icons.append('BLANK1')
				sizes = list(map(int, sizes.split(',')))
				while len(lines) > len(sizes):  # fill sizes with default until length is same as text
					icons.append(56)
				for line, icon, size in zip(lines, icons, sizes):
					#box = body.box().column()
					#label_multiline(context, line, box, icon)
					if not icon in all_icons: icon = 'DOT'
					textBox(body, line, icon, size)

			pass

		def draw_upd_body(self, context: bpy.types.Context, layout: bpy.types.UILayout):
			all_icons = bpy.types.UILayout.bl_rna.functions['label'].parameters['icon'].enum_items
			entry = self.emb_entry
			update_data = entry.get('update_data')
			if entry['version'] == 'N/A_VERSION':
				layout.row().label(text='This EMB is not configured to check for new versions.')
				return None
			if bool(emb_settings.get('update_board_path')):
				pass
			else:
				layout.row().label(text='This EMB is not configured to check for new versions.')
				return None

			if not update_data:
				layout.row().label(text='Nothing to show yet...')
				return None
			
			r = layout.row(align=True)
			s = r.split(factor=0.015)
			s.label(text='')
			col = s.column(align=True)

			#col = layout.column(align=True)
			if update_data['version'] > entry['version']:
				col.row().label(text='A new update is available.')
				row = col.row()
				text = (
					'Ignore Future Versions'
					if not entry['data']['update_ignore_future_versions']
					else 'Notify for Future Versions'
				)
				row.operator('emb.ignore_future_versions', text=text).emb_id = self.emb_id
			elif update_data['version'] == entry['version']:
				col.row().label(text='You have the latest version.')
			elif update_data['version'] < entry['version']:
				col.row().label(text='You seem to be on a newer version')
			
			col.row().label(text='—')
			col.label(text=update_data['title'])
			col = col.column()

			lines = update_data['text'].split('\n')
			icons = update_data['icons'].split(',')
			sizes = map(int, update_data['sizes'].split(','))

			for line, icon, size in zip(lines, icons, sizes):
				if not icon in all_icons: icon = 'DOT'
				textBox(col, line, icon, size)

			if entry.get('release_repository'):
				layout.operator('wm.url_open', text='Releases Page').url = entry['release_repository']

		if entry.get('failure'):

			def draw_header(self, context, layout):
				text = self.label
				layout.label(text=text)

			failure_reason = entry['failure']

			def draw(self, context, layout):
				#layout = self.layout
				layout.label(
					text=f'The EMB for {self.label} ({self.emb_id}) failed to register.'
				)
				layout.label(text=self.failure_reason)
		else:

			def draw_header(self, context, layout):
				entry = self.emb_entry
				data = entry['data']
				text = self.label
				notifs = []

				if data['new_messages'] == 1:
					notifs.append('1 Message')
				elif data['new_messages'] > 1:
					notifs.append(f'{data["new_messages"]} Messages')
				if entry['new_update']:
					notifs.append('New Update')
				if notifs:
					notifs = ' (' + ', '.join(notifs) + ')'
					text += notifs
				layout.label(text=text)

			def draw(self, context, custom_layout=None):
				layout = custom_layout
				entry = self.emb_entry

				r = layout.row(align=True)
				s = r.split(factor=0.015)
				s.label(text='')
				col = s.column()
				msgs_header, msgs_body = col.panel(
					self.bl_idname + '_msgs', default_closed=True
				)
				header_text = 'Messages'
				if self.emb_entry['data']['new_messages']:
					header_text += ' (' + str(entry['data']['new_messages']) + ')'
				msgs_header.label(text=header_text)
				if msgs_body:
					self.draw_msg_body(context, msgs_body)
					layout.separator()

				r = layout.row(align=True)
				s = r.split(factor=0.015)
				s.label(text='')
				col = s.column()
				upd_header, upd_body = col.panel(
					self.bl_idname + '_update', default_closed=True
				)
				if isinstance(entry['version'], tuple) and (entry['new_update']):
					current_ver = '.'.join(map(str, entry['version']))
					new_ver = '.'.join(map(str, entry['update_data']['version']))
					up_string = f'Updates (New update! {current_ver} → {new_ver})'
				else:
					up_string = 'Updates'
				upd_header.row().label(text=up_string)
				if upd_body:
					self.draw_upd_body(context, upd_body)

	entries = bpy.types.WindowManager.emb_entries
	if existing := entries.get(emb_id):
		for cls in existing.get('local_classes', []):
			unregister_class(cls)
		del entries[emb_id]
	entries[emb_id] = entry
	#entry.setdefault('local_classes', set()).add(emb_panel)
	entry['panel_draw'] = emb_panel()
	#register_class(emb_panel)


def register():
	if bool(getattr(bpy.types.WindowManager, 'emb_vars', dict()).get('version', None)) and (EMB_VERSION > bpy.types.WindowManager.emb_vars['version']):
		print('uniniting!')
		uninit_master()
	if getattr(bpy.types.WindowManager, 'emb_entries', None) is None:
		init_master()
	init_local()
	pass


def unregister():
	entries = bpy.types.WindowManager.emb_entries
	if entries.get(global_id):
		for cls in entries[global_id]['local_classes']:
			unregister_class(cls)
		del entries[global_id]
	if len(entries) == 0:
		uninit_master()
	pass
