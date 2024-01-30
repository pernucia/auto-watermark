import PySide6
import PySide6.QtWidgets, PySide6.QtCore, PySide6.QtGui

from UI.Application import MainWindow
from Resources.Addons import prep_env

class MainApplication(PySide6.QtWidgets.QApplication):...

if __name__ == "__main__":
  prep_env()
  app = MainApplication()
  ui = MainWindow()

  app.exec()
