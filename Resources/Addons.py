import os, sys, shutil
import xml.etree.ElementTree as ET
from random import randrange

APPDATA_PATH = os.getenv('APPDATA')
MAIN_PATH = os.path.join(APPDATA_PATH, 'auto_watermark')
CONFIG_PATH = os.path.join(MAIN_PATH, 'setting.config')
RESOURCE_PATH = os.path.join(MAIN_PATH, 'rsc')
LOGO_PATH = os.path.join(RESOURCE_PATH, 'logo.png')
PREVIEW_PATH = os.path.join(RESOURCE_PATH, 'preview.png')
PREVIEW_SAMPLE_PATH = os.path.join(RESOURCE_PATH, 'preview_sample.png')
TMP_PATH = os.path.join(MAIN_PATH, 'tmp')

def prep_env():
	paths = [MAIN_PATH, RESOURCE_PATH, TMP_PATH]
	for path in paths:
		# print(f'make {path}')
		if not os.path.exists(path):
			os.makedirs(path, exist_ok=True)
		if path == MAIN_PATH:
			shutil.copy(resource_path('setting.config'), CONFIG_PATH)


def resource_path(*path):
	try:
		base_path = sys._MEIPASS
	except Exception:
		base_path = os.path.abspath(".")
	
	return os.path.join(base_path, *path)

def save_xml(data:ET.ElementTree, *path):
	with open(resource_path(*path), 'w', encoding='utf-8') as f:
		data.write(f)

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