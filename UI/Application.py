import os, shutil, sys
from typing import Optional
from PySide6.QtCore import Qt, QMimeData
from PySide6.QtWidgets import QMainWindow, QApplication
from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLayout, QSizePolicy, QGridLayout, QSpacerItem
from PySide6.QtWidgets import QFrame, QLabel, QPushButton, QFileDialog, QTableWidget
from PySide6.QtWidgets import QTableWidgetItem, QHeaderView
from PySide6.QtGui import QDragEnterEvent, QDropEvent, QIcon, QMouseEvent, QPixmap, QScreen, QDrag, QColor

from Resources.Addons import resource_path, get_language_pack

class MainWindow(QMainWindow):
	__version = '0.01.0000'
	def __init__(self) -> None:
		super().__init__()
		self.get_Label_data()
		self.init_UI()
		
	def get_Label_data(self):
		lang = 'KO-KR' # 언어정보
		self.lang = get_language_pack(lang)

	def get_label(self, name):
		element = self.lang.find(f".//LabelText[@name='{name}']")
		try:
			return element.text.replace('\\n','\n')
		except:
			return ''
	
	def init_UI(self):
		cwidget = self.cwidget_init()
		self.setCentralWidget(cwidget)

		self.setWindowTitle(f'{self.get_label("window_title")} V{self.__version}')
		# self.setWindowIcon(QIcon(resource_path('img')))
		self.setBaseSize(600,500)
		self.setAcceptDrops(True)

		self.setFocusPolicy(Qt.FocusPolicy.ClickFocus)

		

		# self.__center__()
		self.show()

	# 화면 중앙 배치
	def __center__(self):
		center = QScreen.availableGeometry(QApplication.primaryScreen()).center()
		geo = self.frameGeometry()
		geo.moveCenter(center)
		self.move(geo.topLeft())

	# 메인 위젯 생성
	def cwidget_init(self):
		cwidget = QWidget()

		mainGrid = QHBoxLayout()
		# 좌측 이미지 그리드
		imgGrid = QVBoxLayout()
		mainGrid.addLayout(imgGrid)
		imgBtnGroup = QHBoxLayout()
		imgGrid.addLayout(imgBtnGroup)

		self.imgAddBtn = QPushButton(self.get_label("select_image"))
		self.imgAddBtn.clicked.connect(self.select_img)
		imgBtnGroup.addWidget(self.imgAddBtn)

		self.imgRemoveBtn = QPushButton(self.get_label("remove_image"))
		self.imgRemoveBtn.clicked.connect(self.remove_img)
		imgBtnGroup.addWidget(self.imgRemoveBtn)

		self.imgFrame = ImageFrame(self)
		imgGrid.addWidget(self.imgFrame)

		# 우측 상세정보
		detailGrid = QVBoxLayout()
		mainGrid.addLayout(detailGrid)

		detailGrid.addWidget(QLabel(self.get_label("detail_title")))
		# 로고 지정 영역
		self.logoFrame = LogoFrame(self)
		self.logoLabel = QLabel(self.get_label("logo_title"))
		self.logoAddBtn = QPushButton(self.get_label("select_logo"))
		self.logoAddBtn.clicked.connect(self.select_logo)
		self.logoRemoveBtn = QPushButton(self.get_label("remove_logo"))
		self.logoRemoveBtn.clicked.connect(self.remove_logo)
		# 텍스트 지정 영역
		self.inputTextLabel = QLabel(self.get_label("table_title"))
		self.inputTextTable = QTableWidget(4, 2)
		# self.inputTextTable.setStyleSheet("QHeaderView{background-color: rgb(20, 20, 20)};")
		self.inputTextTable.setHorizontalHeaderLabels([self.get_label("col1"), self.get_label("col2")])
		self.inputTextTable.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
		self.inputTextTable.horizontalHeader().setSectionsClickable(False)
		self.inputTextTable.verticalHeader().hide()
		self.inputTextTable.setMaximumHeight(150)
		for i in range(8):
			text = self.get_label(f"tableitem{i+1}")
			if i < 4:
				self.inputTextTable.setItem(i, 0, QTableWidgetItem(text))
			else:
				self.inputTextTable.setItem(i-4, 1, QTableWidgetItem(text))
		# 미리보기
		self.watermarkTitle = QLabel(self.get_label('preview_title'))
		self.watermarkPreview = QLabel(self.get_label('preview_img'))
		self.watermarkPreview.setFixedSize(200, 100)
		self.watermarkPreview.setFrameShape(QFrame.Box)


		logoGrid = QGridLayout()
		# 좌측
		logoGrid.addWidget(self.logoFrame, 0, 0, 2, 1)
		logoGrid.addWidget(self.logoLabel, 0, 1, 1, 3)
		logoGrid.addWidget(self.logoAddBtn, 1, 1)
		logoGrid.addWidget(self.logoRemoveBtn, 1, 2)
		logoGrid.addWidget(HLine(), 2, 0, 1, 4)
		logoGrid.addWidget(self.inputTextLabel, 3, 0)
		logoGrid.addWidget(self.inputTextTable, 4, 0, 1, 4)
		logoGrid.addWidget(HLine(), 5, 0, 1, 4)
		logoGrid.addWidget(self.watermarkTitle, 6, 0)
		logoGrid.addWidget(self.watermarkPreview, 7, 0, 2, 2)
		# logoGrid.addWidget(VLine(), 0, 5, 10, 1)
		# 우측
		logoGrid.addItem(QSpacerItem(20,20,QSizePolicy.Policy.Preferred,QSizePolicy.Policy.Expanding), 9, 0)
		
		detailFrame = QFrame()
		detailFrame.setFrameShape(QFrame.Box)
		detailFrame.setLayout(logoGrid)
		detailGrid.addWidget(detailFrame)
		
		
		



		cwidget.setLayout(mainGrid)

		return cwidget
	
	# 이미지 추가 버튼
	def select_img(self):
		file_selector = QFileDialog(self, caption="이미지 선택", directory=os.getcwd())
		file_selector.setFileMode(QFileDialog.FileMode.ExistingFile)
		file_selector.setViewMode(QFileDialog.ViewMode.Detail)
		file_selector.setNameFilters({'Image File (*.png *.jpg)','Any files (*)'})
		file_selector.selectNameFilter('Image File (*.png *.jpg)')
		file_selector.exec()

		if len(file_selector.selectedFiles()):
			filename = file_selector.selectedFiles()[0]
			print(filename)
			self.imgFrame.set_image(filename)

	# 이미지 제거 버튼
	def remove_img(self):
		self.imgFrame.clear()
		self.imgFrame.setText(self.get_label('img_input_guide'))
		self.imgFrame.setToolTip('')

	# 로고 추가 버튼
	def select_logo(self):
		file_selector = QFileDialog(self, caption="이미지 선택", directory=os.getcwd())
		file_selector.setFileMode(QFileDialog.FileMode.ExistingFile)
		file_selector.setViewMode(QFileDialog.ViewMode.Detail)
		file_selector.setNameFilters({'Image File (*.png *.jpg)','Any files (*)'})
		file_selector.selectNameFilter('Image File (*.png *.jpg)')
		file_selector.exec()

		if len(file_selector.selectedFiles()):
			filename = file_selector.selectedFiles()[0]
			print(filename)
			self.logoFrame.set_image(filename)

	# 로고 제거 버튼
	def remove_logo(self):
		self.logoFrame.clear()
		self.logoFrame.setText(self.get_label('logo_input_guide'))
		self.logoFrame.setToolTip('')
			
	
# 이미지 표시
class ImageFrame(QLabel):
	def __init__(self, parent: QWidget=None) -> None:
		super().__init__(parent)
		self.setFixedSize(450,450)
		self.setAcceptDrops(True)
		self.setStyleSheet('QLabel{border: 4px dashed #aaa};')
		self.setText(self.parent().get_label('img_input_guide'))

		# 이미지 들어갈 라벨
		self.setAlignment(Qt.AlignmentFlag.AlignCenter)
		self.setAcceptDrops(True)
		self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)


	def dragEnterEvent(self, event: QDragEnterEvent) -> None:
		if event.mimeData().hasImage:
			event.accept()
		else:
			event.ignore()

	def dragMoveEvent(self, event: QDragEnterEvent) -> None:
		if event.mimeData().hasImage:
			event.accept()
		else:
			event.ignore()
	
	def dropEvent(self, event: QDropEvent) -> None:
		if event.mimeData().hasImage:
			self.set_image(event.mimeData().urls()[0].toLocalFile())
			event.accept()
		else:
			event.ignore()


	# 이미지 표시
	def set_image(self, imgpath):
		self.setToolTip(imgpath)
		self.img = QPixmap(imgpath)
		thumbnail = self.img.scaled(450, 450, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
		self.setPixmap(thumbnail)

# 이미지 표시
class LogoFrame(QLabel):
	def __init__(self, parent: QWidget=None) -> None:
		super().__init__(parent)
		self.setFixedSize(100,100)
		self.setAcceptDrops(True)
		self.setStyleSheet('QLabel{border: 4px dashed #aaa};')
		self.setText(self.parent().get_label('logo_input_guide'))

		# 이미지 들어갈 라벨
		self.setAlignment(Qt.AlignmentFlag.AlignCenter)
		self.setAcceptDrops(True)
		# self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)


	def dragEnterEvent(self, event: QDragEnterEvent) -> None:
		if event.mimeData().hasImage:
			event.accept()
		else:
			event.ignore()

	def dragMoveEvent(self, event: QDragEnterEvent) -> None:
		if event.mimeData().hasImage:
			event.accept()
		else:
			event.ignore()
	
	def dropEvent(self, event: QDropEvent) -> None:
		if event.mimeData().hasImage:
			self.set_image(event.mimeData().urls()[0].toLocalFile())
			event.accept()
		else:
			event.ignore()


	# 이미지 표시
	def set_image(self, imgpath):
		# self.setToolTip(imgpath)
		self.img = QPixmap(imgpath)
		thumbnail = self.img.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
		self.setPixmap(thumbnail)

class HLine(QFrame):
	def __init__(self, parent: QWidget=None) -> None:
		super().__init__(parent)
		self.setFrameShape(QFrame.Shape.HLine)
		
class VLine(QFrame):
	def __init__(self, parent: QWidget=None) -> None:
		super().__init__(parent)
		self.setFrameShape(QFrame.Shape.VLine)