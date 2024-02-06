import os, sys, shutil
import xml.etree.ElementTree as ET
from random import randrange

# PATHS
APPDATA_PATH = os.getenv('APPDATA')
PRJ_NAME = 'auto_watermark'
MAIN_PATH = os.path.join(APPDATA_PATH, PRJ_NAME)
RESOURCE_PATH = os.path.join(MAIN_PATH, 'rsc')
TMP_PATH = os.path.join(MAIN_PATH, 'tmp')
# FILES
CONFIG_PATH = os.path.join(MAIN_PATH, 'setting.config')
LOGO_PATH = os.path.join(RESOURCE_PATH, 'logo.png')
WATERMARK_PATH = os.path.join(RESOURCE_PATH, 'watermark.png')
WATERMARK_SAMPLE_PATH = os.path.join(RESOURCE_PATH, 'watermark_sample.png')
PREVIEW_PATH = os.path.join(RESOURCE_PATH, 'preview.png')
MAIN_IMAGE_PATH = os.path.join(RESOURCE_PATH, 'image.png')

def prep_env():
	paths = [MAIN_PATH, RESOURCE_PATH, TMP_PATH]
	for path in paths:
		# print(f'make {path}')
		if not os.path.exists(path):
			os.makedirs(path, exist_ok=True)
		if path == MAIN_PATH:
			if not os.path.exists(CONFIG_PATH):
				shutil.copy(resource_path('setting.config'), CONFIG_PATH)
			else:
				base_data = read_xml(resource_path('setting.config'))
				config = read_xml(CONFIG_PATH)
				settingitems = [x.attrib['id'] for x in base_data.getroot().iter('SettingOption')]
				for element in config.iter('SettingOption'):
					if element.attrib['id'] in settingitems:
						target = base_data.find(f".//SettingOption[@id='{element.attrib['id']}']")
						target.attrib['value'] = config.find(f".//SettingOption[@id='{element.attrib['id']}']").attrib['value']
				save_xml(base_data, CONFIG_PATH)
				


def resource_path(*path):
	try:
		base_path = sys._MEIPASS
	except Exception:
		base_path = os.path.abspath(".")
	
	return os.path.join(base_path, *path)

def save_xml(data:ET.ElementTree, *path):
	data.write(resource_path(*path), encoding="utf-8", xml_declaration=True)
	# with open(resource_path(*path), 'w', encoding='utf-8') as f:
	# 	data.write(f)

def read_xml(*path):
	tree = ET.parse(resource_path(*path))
	# tree = ET.parse(resource_path('Resources','Translations','KO-KR.xml'))
	return tree

def get_language_pack(lang:str='en_US'):
	basepath = 'Resources/Translations/'
	langpath = basepath + lang + '.xml'
	if os.path.exists(langpath):
		return read_xml(langpath)
	else:
		return read_xml('Resources/Translations/en_US.xml')

def keygen(key_len=8):
	"""
	8자의 랜덤한 키를 생성합니다.

	Args:
		length: 키의 길이 (기본값: 8)

	Returns:
		8자의 랜덤한 키
	"""
	chars = "abcdefghijklmnopqrstuvwxyz0123456789"

	key = ''
	for _ in range(key_len):
		key = key + chars[randrange(len(chars))]
	return key

def gen_watermark_name(*path):
	fullpath = os.path.join(*path)
	dirpath = os.path.dirname(fullpath)
	filename = os.path.basename(fullpath)
	print(dirpath, filename)
	filename_alt = filename.replace('.','_watermark.')
	alt_path = os.path.join(dirpath, filename_alt)
	print(alt_path)
	return alt_path