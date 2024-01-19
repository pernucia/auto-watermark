import PySide6
import PySide6.QtWidgets, PySide6.QtCore, PySide6.QtGui

from UI.Application import MainWindow

class MainApplication(PySide6.QtWidgets.QApplication):...

if __name__ == "__main__":
  app = MainApplication()
  ui = MainWindow()

  app.exec()
