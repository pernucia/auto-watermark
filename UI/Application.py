import os, shutil, sys
from typing import Optional
from PySide6.QtCore import Qt, QMimeData
from PySide6.QtWidgets import QMainWindow, QApplication
from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLayout, QSizePolicy, QGridLayout, QSpacerItem
from PySide6.QtWidgets import QFrame, QLabel, QPushButton, QFileDialog, QTableWidget, QRadioButton, QCheckBox, QLineEdit, QComboBox, QSpinBox, QSlider
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
		self.setFixedSize(895, 500)
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
		self.inputTextTable.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
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

		self.gen_previewBtn = QPushButton(self.get_label('generate_preview'))
		self.gen_previewBtn.clicked.connect(self.generate_preview)

		self.saveBtn = QPushButton(self.get_label('save'))
		self.saveBtn.clicked.connect(self.save_img)

		
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
		self.textAlignOneCol.toggled.connect(self.show_logo_preview)
		
		self.textAlignTwoCol = QRadioButton(self.get_label('align_two_column'))
		self.textAlignTwoCol.setToolTip(self.get_label('align_two_column'))
		self.textAlignTwoCol.toggled.connect(self.show_logo_preview)
		
		self.textAlignThreeCol = QRadioButton(self.get_label('align_three_column'))
		self.textAlignThreeCol.setToolTip(self.get_label('align_three_column'))
		self.textAlignThreeCol.toggled.connect(self.show_logo_preview)

		alignLayout.addWidget(self.textAlignOneCol, 0, 0)
		alignLayout.addWidget(self.textAlignTwoCol, 0, 1)
		alignLayout.addWidget(self.textAlignThreeCol, 0, 2)
		# 워터마크 위치
		self.textPosLabel = QLabel(self.get_label('position_title'))
		self.textPosWidget = QWidget()
		textposLayout = QGridLayout()
		textposLayout.setContentsMargins(1,1,1,10)
		textposLayout.setSpacing(5)
		textposLayout.setColumnMinimumWidth(0, 120)
		textposLayout.setColumnMinimumWidth(1, 120)
		textposLayout.setColumnMinimumWidth(2, 120)
		self.textPosWidget.setLayout(textposLayout)

		self.textPos_Center = QRadioButton(self.get_label('pos_center'))
		self.textPos_Center.setChecked(True)
		# self.textPos_Center.toggled.connect(self.show_logo_preview)
		self.textPos_Custom = QRadioButton(self.get_label('pos_custom'))
		# self.textPos_Custom.toggled.connect(self.show_logo_preview)
		self.textPosCustomX = QSpinBox()
		self.textPosCustomX.setRange(0, 100)
		self.textPosCustomX.setToolTip(self.get_label('pos_x'))
		self.textPosCustomX.setEnabled(False)
		# self.textPosCustomX.valueChanged.connect(self.show_logo_preview)

		self.textPosCustomY = QSpinBox()
		self.textPosCustomY.setRange(0, 100)
		self.textPosCustomY.setToolTip(self.get_label('pos_y'))
		self.textPosCustomY.setEnabled(False)
		# self.textPosCustomY.valueChanged.connect(self.show_logo_preview)

		self.textPosCustomType = QComboBox()
		self.textPosCustomType.addItems(['Pixel','%'])
		self.textPosCustomType.setEnabled(False)
		# self.textPosCustomType.currentTextChanged.connect(self.show_logo_preview)

		self.textPos_Top = QRadioButton(self.get_label('pos_top'))
		# self.textPos_Top.toggled.connect(self.show_logo_preview)
		self.textPos_Bottom = QRadioButton(self.get_label('pos_bottom'))
		# self.textPos_Bottom.toggled.connect(self.show_logo_preview)
		self.textPos_Left = QRadioButton(self.get_label('pos_left'))
		# self.textPos_Left.toggled.connect(self.show_logo_preview)
		self.textPos_Right = QRadioButton(self.get_label('pos_right'))
		# self.textPos_Right.toggled.connect(self.show_logo_preview)

		self.textPos_TopLeft = QRadioButton(self.get_label('pos_topleft'))
		# self.textPos_TopLeft.toggled.connect(self.show_logo_preview)
		self.textPos_TopRight = QRadioButton(self.get_label('pos_topright'))
		# self.textPos_TopRight.toggled.connect(self.show_logo_preview)
		self.textPos_BottomLeft = QRadioButton(self.get_label('pos_bottomleft'))
		# self.textPos_BottomLeft.toggled.connect(self.show_logo_preview)
		self.textPos_BottomRight = QRadioButton(self.get_label('pos_bottomright'))
		# self.textPos_BottomRight.toggled.connect(self.show_logo_preview)
		
		textposLayout.addWidget(self.textPos_TopLeft, 0, 0)
		textposLayout.addWidget(self.textPos_Top, 0, 1)
		textposLayout.addWidget(self.textPos_TopRight, 0, 2)
		textposLayout.addWidget(self.textPos_Left, 1, 0)
		textposLayout.addWidget(self.textPos_Center, 1, 1)
		textposLayout.addWidget(self.textPos_Right, 1, 2)
		textposLayout.addWidget(self.textPos_BottomLeft, 2, 0)
		textposLayout.addWidget(self.textPos_Bottom, 2, 1)
		textposLayout.addWidget(self.textPos_BottomRight, 2, 2)
		textposLayout.addWidget(self.textPos_Custom, 3, 0, 1, 3)
		textposLayout.addWidget(self.textPosCustomX, 4, 0)
		textposLayout.addWidget(self.textPosCustomY, 4, 1)
		textposLayout.addWidget(self.textPosCustomType, 4, 2)

		self.textPos_Custom.toggled.connect(self.toggle_textpos)

		# 회전
		self.textOrientTitle = QLabel(self.get_label('orient_title'))
		self.textOrientLine = QLineEdit()
		self.textOrientLine.setFixedWidth(50)
		self.textOrientLine.setText('0')
		self.textOrientLine.textChanged.connect(self.input_orient_value)
		# self.textOrientLine.textChanged.connect(self.show_logo_preview)
		self.textOrientSlider = QSlider()
		self.textOrientSlider.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
		self.textOrientSlider.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
		self.textOrientSlider.setTickPosition(QSlider.TickPosition.TicksAbove)
		self.textOrientSlider.setRange(0,360)
		self.textOrientSlider.setTickInterval(45)
		self.textOrientSlider.setSingleStep(15)
		self.textOrientSlider.setPageStep(90)
		self.textOrientSlider.setOrientation(Qt.Orientation.Horizontal)
		self.textOrientSlider.valueChanged.connect(self.set_orient_value)
		# self.textOrientSlider.valueChanged.connect(self.show_logo_preview)


		# 방식(단일, 바둑판)
		self.textTypeTitle = QLabel(self.get_label('type_title'))
		self.textTypeWidget = QWidget()
		typeLayout = QHBoxLayout()
		typeLayout.setContentsMargins(0,1,0,10)
		self.textTypeWidget.setLayout(typeLayout)

		self.textType_Single = QRadioButton(self.get_label('type_single'))
		self.textType_Single.setChecked(True)
		self.textType_Expand = QRadioButton(self.get_label('type_expand'))
		self.textType_Checkbox = QRadioButton(self.get_label('type_checkbox'))

		typeLayout.addWidget(self.textType_Single)
		typeLayout.addWidget(self.textType_Expand)
		typeLayout.addWidget(self.textType_Checkbox)


		# 좌측
		# 1~4
		logoGrid = QGridLayout()
		logoGrid.setContentsMargins(0,0,0,0)
		logoGrid.setSpacing(5)
		logoGrid.addWidget(self.logoFrame, 0, 0, 2, 1)
		logoGrid.addWidget(self.logoLabel, 0, 1, 1, 3)
		logoGrid.addWidget(self.logoAddBtn, 1, 1)
		logoGrid.addWidget(self.logoRemoveBtn, 1, 2)
		logoGrid.addWidget(HLine(), 2, 0, 1, 4)
		logoGrid.addWidget(self.inputTextLabel, 3, 0)
		logoGrid.addWidget(self.inputTextTable, 4, 0, 1, 4)
		logoGrid.addWidget(HLine(), 5, 0, 1, 4)
		logoGrid.addWidget(self.watermarkTitle, 6, 0, 1, 3)
		logoGrid.addWidget(self.toggleDetailBtn, 6, 3)
		logoGrid.addWidget(self.watermarkPreview, 7, 0, 2, 2)
		logoGrid.addWidget(self.gen_previewBtn, 7, 3)
		logoGrid.addWidget(self.saveBtn, 8, 3)
		logoGrid.addItem(QSpacerItem(20,20,QSizePolicy.Policy.Preferred,QSizePolicy.Policy.Expanding), 9, 0)

		# detailGrid.addWidget(self.midLine, 0, 5, 10, 1)
		# 우측
		# 6~
		detailGrid = QGridLayout()
		detailGrid.setContentsMargins(0,0,0,0)
		detailGrid.setSpacing(5)
		detailGrid.addWidget(self.textLocalLabel, 0, 0)
		detailGrid.addWidget(self.textLocalWidget, 0, 1, 1, 3)
		detailGrid.addWidget(HLine(), 1, 0, 1, 4)
		detailGrid.addWidget(self.textAlignLabel, 2, 0)
		detailGrid.addWidget(self.textAlignWidget, 3, 0, 1, 4)
		detailGrid.addWidget(HLine(), 4, 0, 1, 4)
		detailGrid.addWidget(self.textPosLabel, 5, 0)
		detailGrid.addWidget(self.textPosWidget, 6, 0, 2, 4)
		detailGrid.addWidget(HLine(), 7, 0, 1, 4)
		detailGrid.addWidget(self.textOrientTitle, 8, 0)
		detailGrid.addWidget(self.textOrientSlider, 9, 0, 1, 3)
		detailGrid.addWidget(self.textOrientLine, 9, 3)
		detailGrid.addWidget(HLine(), 10, 0, 1, 4)
		detailGrid.addWidget(self.textTypeTitle, 11, 0)
		detailGrid.addWidget(self.textTypeWidget, 12, 0, 1, 4)
		# detailGrid.addItem(QSpacerItem(20,20,QSizePolicy.Policy.Preferred,QSizePolicy.Policy.Expanding), 20, 0)
		

		self.leftWidget = QWidget()
		self.leftWidget.setFixedWidth(400)
		self.leftWidget.setLayout(logoGrid)
		self.rightWidget = QWidget()
		self.rightWidget.setFixedWidth(390)
		self.rightWidget.setLayout(detailGrid)
		
		self.rightWidget.hide()
		self.midLine.hide()

		mainLayout = QHBoxLayout()
		mainLayout.setAlignment(Qt.AlignmentFlag.AlignLeft)
		mainLayout.addWidget(self.leftWidget)
		mainLayout.addWidget(self.midLine)
		mainLayout.addWidget(self.rightWidget)

		detailFrame = QFrame()
		detailFrame.setFrameShape(QFrame.Box)
		detailFrame.setLayout(mainLayout)
		detailLayout.addWidget(detailFrame)
		
		self.show_logo_preview()
		



		cwidget.setLayout(mainGrid)

		return cwidget
	
	############################################################
	######              Element Actions                   ######
	############################################################

	# 워터마크 위치 직접입력
	def toggle_textpos(self):
		if self.textPos_Custom.isChecked():
			self.textPosCustomX.setEnabled(True)
			self.textPosCustomY.setEnabled(True)
			self.textPosCustomType.setEnabled(True)
		else:
			self.textPosCustomX.setEnabled(False)
			self.textPosCustomY.setEnabled(False)
			self.textPosCustomType.setEnabled(False)

	# 회전 슬라이더 값
	def set_orient_value(self):
		self.textOrientLine.setText(str(self.textOrientSlider.value()))
	def input_orient_value(self):
		self.textOrientSlider.setValue(int(self.textOrientLine.text()))

	
	############################################################
	######              Button Actions                    ######
	############################################################
		
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

	# 상세설정 표시 버튼
	def toggle_detail(self):
		if self.toggleDetailBtn.text() == self.get_label('detail_open'):
			self.midLine.show()
			self.rightWidget.show()
			self.setFixedSize(1300, 500)
			self.toggleDetailBtn.setText(self.get_label('detail_close'))
			self.toggleDetailBtn.setToolTip(self.get_label('detail_close_tooltip'))
		else:
			self.midLine.hide()
			self.rightWidget.hide()
			self.setFixedSize(895, 500)
			self.toggleDetailBtn.setText(self.get_label('detail_open'))
			self.toggleDetailBtn.setToolTip(self.get_label('detail_open_tooltip'))


	# 로고 미리보기 갱신
	def show_logo_preview(self):
		# self.
		pass

	def generate_preview(self):...


	def save_img(self):...



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
		self.setStyleSheet('QLabel{border: 2px dashed #aaa};')
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