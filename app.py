import PySide6, os, shutil, sys, ctypes, locale, traceback, shutil, time
import xml.etree.ElementTree, random, PIL.Image, PIL.ImageDraw, PIL.ImageFont
import PySide6.QtWidgets, PySide6.QtCore, PySide6.QtGui

from Resources.Application import MainWindow
from Resources.Addons import prep_env

class MainApplication(PySide6.QtWidgets.QApplication):...

if __name__ == "__main__":
  prep_env()
  app = MainApplication()
  ui = MainWindow()

  app.exec()
