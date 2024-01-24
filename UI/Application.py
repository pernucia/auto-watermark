import os, shutil, sys
from typing import Optional
from PySide6.QtCore import Qt, QMimeData
from PySide6.QtWidgets import QMainWindow, QApplication
from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLayout, QSizePolicy, QGridLayout, QSpacerItem
from PySide6.QtWidgets import QFrame, QLabel, QPushButton, QFileDialog, QTableWidget, QRadioButton, QCheckBox
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
			return element.text
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
		detailLayout = QVBoxLayout()
		mainGrid.addLayout(detailLayout)

		detailLayout.addWidget(QLabel(self.get_label("detail_title")))
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
		self.inputTextTable.cellChanged.connect(self.show_logo_preview)
		# 미리보기
		self.watermarkTitle = QLabel(self.get_label('preview_title'))
		self.watermarkPreview = QLabel(self.get_label('preview_img'))
		self.watermarkPreview.setFixedSize(200, 100)
		self.watermarkPreview.setFrameShape(QFrame.Box)
		self.toggleDetailBtn = QPushButton(self.get_label('detail_open'))
		self.toggleDetailBtn.setToolTip(self.get_label('detail_open_tooltip'))
		self.toggleDetailBtn.clicked.connect(self.toggle_detail)
		
		# 우측 상세설정
		self.midLine = VLine()
		# 텍스트 위치
		self.textLocalLabel = QLabel(self.get_label('local_title'))
		self.textLocalWidget = QWidget()
		localLayout = QHBoxLayout(self.textLocalWidget)
		self.textLocalDown = QRadioButton(self.get_label('text_local_down'))
		self.textLocalDown.setChecked(True)
		self.textLocalDown.clicked.connect(self.show_logo_preview)
		self.textLocalLeft = QRadioButton(self.get_label('text_local_left'))
		self.textLocalLeft.clicked.connect(self.show_logo_preview)
		self.textLocalRight = QRadioButton(self.get_label('text_local_right'))
		self.textLocalRight.clicked.connect(self.show_logo_preview)
		self.textLocalNone = QRadioButton(self.get_label('text_local_none'))
		self.textLocalNone.clicked.connect(self.show_logo_preview)
		localLayout.addWidget(self.textLocalDown)
		localLayout.addWidget(self.textLocalLeft)
		localLayout.addWidget(self.textLocalRight)
		localLayout.addWidget(self.textLocalNone)
		# 배열 방식
		self.textAlignLabel =  QLabel(self.get_label('align_title'))
		self.textAlignWidget = QWidget()
		alignLayout = QGridLayout(self.textAlignWidget)
		alignLayout.setContentsMargins(1,1,1,2)
		self.textAlignOneCol = QRadioButton(self.get_label('align_one_column'))
		self.textAlignOneCol.setToolTip(self.get_label('align_one_column'))
		self.textAlignOneCol.setChecked(True)
		
		self.textAlignTwoCol = QRadioButton(self.get_label('align_two_column'))
		self.textAlignTwoCol.setToolTip(self.get_label('align_two_column'))
		
		self.textAlignThreeCol = QRadioButton(self.get_label('align_three_column'))
		self.textAlignThreeCol.setToolTip(self.get_label('align_three_column'))

		alignLayout.addWidget(self.textAlignOneCol, 0, 0)
		alignLayout.addWidget(self.textAlignTwoCol, 0, 1)
		alignLayout.addWidget(self.textAlignThreeCol, 0, 2)
		# 배치(위치, 방식)
		self.textPosLabel = QLabel(self.get_label('align_title'))


		# 회전


		# 좌측
		# 1~4
		logoGrid = QGridLayout()
		logoGrid.addWidget(self.logoFrame, 0, 0, 2, 1)
		logoGrid.addWidget(self.logoLabel, 0, 1, 1, 3)
		logoGrid.addWidget(self.logoAddBtn, 1, 1)
		logoGrid.addWidget(self.logoRemoveBtn, 1, 2)
		logoGrid.addWidget(HLine(), 2, 0, 1, 4)
		logoGrid.addWidget(self.inputTextLabel, 3, 0)
		logoGrid.addWidget(self.inputTextTable, 4, 0, 1, 4)
		logoGrid.addWidget(HLine(), 5, 0, 1, 4)
		logoGrid.addWidget(self.watermarkTitle, 6, 0, 1, 3)
		logoGrid.addWidget(self.toggleDetailBtn, 6, 4)
		logoGrid.addWidget(self.watermarkPreview, 7, 0, 2, 2)
		logoGrid.addItem(QSpacerItem(20,20,QSizePolicy.Policy.Preferred,QSizePolicy.Policy.Expanding), 9, 0)

		# detailGrid.addWidget(self.midLine, 0, 5, 10, 1)
		# 우측
		# 6~
		detailGrid = QGridLayout()
		detailGrid.addWidget(self.textLocalLabel, 0, 0)
		detailGrid.addWidget(self.textLocalWidget, 0, 1)
		detailGrid.addWidget(HLine(), 1, 0, 1, 2)
		detailGrid.addWidget(self.textAlignLabel, 2, 0)
		detailGrid.addWidget(self.textAlignWidget, 3, 0, 1, 2)
		detailGrid.addWidget(HLine(), 4, 0, 1, 2)
		detailGrid.addItem(QSpacerItem(20,20,QSizePolicy.Policy.Preferred,QSizePolicy.Policy.Expanding), 9, 0)
		
		mainLayout = QHBoxLayout()
		mainLayout.addLayout(logoGrid)
		mainLayout.addWidget(self.midLine)
		mainLayout.addLayout(detailGrid)

		detailFrame = QFrame()
		detailFrame.setFrameShape(QFrame.Box)
		detailFrame.setLayout(mainLayout)
		detailLayout.addWidget(detailFrame)
		
		self.show_logo_preview()
		



		cwidget.setLayout(mainGrid)

		return cwidget
	

	# 로고 미리보기 갱신
	def show_logo_preview(self):...
	
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
		
		self.show_logo_preview()

	# 로고 제거 버튼
	def remove_logo(self):
		self.logoFrame.clear()
		self.logoFrame.setText(self.get_label('logo_input_guide'))
		self.logoFrame.setToolTip('')
		
		self.show_logo_preview()

	def toggle_detail(self):
		if self.toggleDetailBtn.text() == self.get_label('detail_open'):
			self.midLine.show()
			self.textLocalLabel.show()
			self.textLocalWidget.show()
			self.toggleDetailBtn.setText(self.get_label('detail_close'))
			self.toggleDetailBtn.setToolTip(self.get_label('detail_close_tooltip'))
		else:
			self.midLine.hide()
			self.textLocalLabel.hide()
			self.textLocalWidget.hide()
			self.toggleDetailBtn.setText(self.get_label('detail_open'))
			self.toggleDetailBtn.setToolTip(self.get_label('detail_open_tooltip'))

	
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