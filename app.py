import PySide6, os, shutil, sys, ctypes, locale, traceback, shutil, time
import xml.etree.ElementTree, random, PIL.Image, PIL.ImageDraw, PIL.ImageFont
import PySide6.QtWidgets, PySide6.QtCore, PySide6.QtGui
from PySide6.QtWidgets import QApplication

from Resources.Application import MainWindow, Noti
from Resources.Addons import prep_env, resource_path, PRJ_NAME

class MainApplication(QApplication):
	def __init__(self, *argv):
		super().__init__(*argv)
		self.icon = PySide6.QtGui.QIcon(resource_path('Resources','Img','icon.ico'))
		self.setQuitOnLastWindowClosed(False)
		self.init_main()
		self.init_tray()

	def init_main(self):
		self.main = MainWindow()
		self.main.app_quit.connect(self.quit_action)
		self.main.notification.connect(self.show_notification)

	def init_tray(self):
		tray = PySide6.QtWidgets.QSystemTrayIcon(self.icon)
		tray.setVisible(True)
		tray.setToolTip(PRJ_NAME)
		tray.activated.connect(self.onActivated)
		self.tray = tray

	def onActivated(self, reason):
		if reason == PySide6.QtWidgets.QSystemTrayIcon.ActivationReason.DoubleClick:
			self.open_action()

	def open_action(self):
		self.main.show()
		self.main.setWindowState(PySide6.QtCore.Qt.WindowState.WindowActive)
		self.main.activateWindow()

	def quit_action(self, signal=None):
		self.main.close()
		self.quit()

	@PySide6.QtCore.Slot()
	def show_notification(self, object:Noti):
		type = object.type 
		title = object.title or PRJ_NAME
		desc = object.desc
		if type == 0:
			icon = PySide6.QtWidgets.QSystemTrayIcon.MessageIcon.Information
		elif type == -1:
			icon = PySide6.QtWidgets.QSystemTrayIcon.MessageIcon.Warning
		duration = 3 * 1000 #3 seconds

		self.tray.showMessage(title, desc, icon, duration)

	def show_message(self, text, info=None, detail=None):
		msg = PySide6.QtWidgets.QMessageBox()
		msg.setIcon(self.icon)
		msg.setWindowIcon(self.icon)

		msg.setWindowTitle('JAS')
		msg.setText(text)
		if info:
			msg.setInformativeText(info)
		if detail:
			msg.setDetailedText(detail)
		msg.setDefaultButton()
		msg.exec()


if __name__ == "__main__":
	prep_env()
	app = MainApplication()

	app.exec()
