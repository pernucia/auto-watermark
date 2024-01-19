import os, sys
import xml.etree.ElementTree as ET

def resource_path(*path):
	try:
		base_path = sys._MEIPASS
	except Exception:
		base_path = os.path.abspath(".")
	
	return os.path.join(base_path, *path)

def read_xml(*path):
	tree = ET.parse(resource_path(*path))
	# tree = ET.parse(resource_path('Resources','Translations','KO-KR.xml'))
	return tree.getroot()

def get_language_pack(lang):
	basepath = 'Resources/Translations/'
	langpath = basepath + lang + '.xml'
	return read_xml(langpath)
