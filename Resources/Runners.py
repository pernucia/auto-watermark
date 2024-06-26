import PySide6.QtCore 
from PySide6.QtCore import Signal, QObject, QTimer, QRunnable
# from PySide6.QtWidgets import 
from time import sleep

from Resources.Image import *
from Resources.Addons import gen_watermark_name

class CommSignals(QObject):
	finish = Signal()

	setup_bar = Signal(int, int)
	progress = Signal(object)
	timer_end = Signal(str)

	logo_preview = Signal(object, object)
	save = Signal(object, str)
	
class RunnerBase(QRunnable):
	def __init__(self) -> None:
		super().__init__()
		self.signals = CommSignals()
	
	@property
	def finish(self):
		return self.signals.finish
	@property
	def progress(self):
		return self.signals.progress
	@property
	def timer_end(self):
		return self.signals.timer_end
	@property
	def logo_preview(self):
		return self.signals.logo_preview
	@property
	def save(self):
		return self.signals.save
		
	
class Timer(RunnerBase):
	def __init__(self, time, code) -> None:
		super().__init__()
		self.time:int = time
		self.code:str = code

	def run(self):
		sleep(self.time)
		self.timer_end.emit(self.code)


class LogoPreview(RunnerBase):
	def __init__(self, texts, settings):
		super().__init__()
		self.texts = texts
		self.settings = settings

	def run(self):
		print('start gen logo')
		generate_logo_preview(self.texts, self.settings, self.progress)
		self.finish.emit()


class SaveImage(RunnerBase):
	def __init__(self, settings, path):
		super().__init__()
		self.path = path
		self.settings = settings

	def run(self):
		print('start save')
		generate_image(self.settings, self.path, self.progress)
		self.finish.emit()
		

class ShowImage(RunnerBase):
	def __init__(self, path):
		super().__init__()
		self.path = gen_watermark_name(path)

	def run(self):
		img = Image.open(self.path)
		img.show()
		self.finish.emit()