import os, shutil, sys, ctypes, locale
from PySide6.QtCore import Qt, QMimeData, Signal, QRunnable, QObject, QTimer, QThreadPool
from PySide6.QtCore import QTimerEvent
from PySide6.QtWidgets import QMainWindow, QApplication
from PySide6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QLayout, QSizePolicy, QGridLayout, QSpacerItem,
															 QScrollArea)
from PySide6.QtWidgets import (QFrame, QLabel, QPushButton, QFileDialog, QTableWidget, QRadioButton, QCheckBox, 
															 QLineEdit, QComboBox, QSpinBox, QSlider, QProgressBar, QColorDialog)
from PySide6.QtWidgets import QTableWidgetItem, QHeaderView

from PySide6.QtGui import (QDragEnterEvent, QDropEvent, QIcon, QMouseEvent, QPixmap, QScreen, QDrag, 
													 QColor, QPalette)
from time import sleep

from Resources.Runners import Timer, LogoPreview, SaveImage, ShowImage
from Resources.Addons import read_xml, save_xml, resource_path, get_language_pack, LOGO_PATH, WATERMARK_PATH, WATERMARK_SAMPLE_PATH, CONFIG_PATH, FONTS_PATH
from Resources.Image import *

class Noti:
	def __init__(self, *, type:int=0, title:str='', desc:str='') -> None:
		self.type:int=type
		self.title:str=title
		self.desc:str=desc
		
palette_red = QPalette()
palette_red.setColor(QPalette.ColorRole.Highlight, QColor(Qt.GlobalColor.red))

language = ['ko_KR', 'en_US']

class MainWindow(QMainWindow):
	__version = '0.02.0205'
	app_quit = Signal()
	notification = Signal(object)
	config = None
	
	def __init__(self) -> None:
		super().__init__()
		self.get_config()
		self.get_Label_data()
		self.init_UI()
		self.setup_worker()
		
	def get_config(self):
		self.config = read_xml(CONFIG_PATH)

	def save_config(self):
		save_xml(self.config, CONFIG_PATH)

	def get_config_data(self, id):
		result = self.config.find(f".//SettingOption[@id='{id}']")
		try:
			type = result.attrib["type"]
			if result.attrib["value"]:
				if type == 'str':
					value = result.attrib["value"]
				elif type == 'int':
					value = int(result.attrib["value"])
				elif type =='bool':
					value = True if result.attrib["value"]=='True' else False
				return value
			else:
				return 
		except Exception as e:
			print(e)
			return
	
	def get_Label_data(self):
		if not self.config:
			lang = locale.windows_locale[ctypes.windll.kernel32.GetUserDefaultUILanguage()]
		else:
			lang = self.get_config_data('language')
		self.lang = get_language_pack(lang)
	
	def init_UI(self):
		cwidget = self.cwidget_init()
		self.setCentralWidget(cwidget)

		self.setWindowTitle(f'{self.get_label("window_title")} V{self.__version}')
		self.setWindowIcon(QIcon(resource_path('Resources', 'Img','icon.ico')))
		self.setFixedSize(950, 650)
		self.setAcceptDrops(True)

		self.setFocusPolicy(Qt.FocusPolicy.ClickFocus)

		self.show()


	def setup_worker(self):
		self.pool = QThreadPool()

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

		self.imgFrame = ImageFrame(self.get_label('img_input_guide'), self)
		imgGrid.addWidget(self.imgFrame)

		# 우측 상세정보
		detailLayout = QVBoxLayout()
		mainGrid.addLayout(detailLayout)

		# 상세정보 상단 타이틀 바
		detailTitleLayout = QHBoxLayout()
		detailTitleLayout.setContentsMargins(0,0,0,0)
		self.detailSettingTitle = QLabel(self.get_label("detail_title"))
		self.detailSettingTitle.setMinimumWidth(310)
		detailTitleLayout.addWidget(self.detailSettingTitle)
		self.selectLangCombo = QComboBox()
		self.selectLangCombo.setMinimumWidth(100)
		self.selectLangCombo.addItems(['한국어 Kor','영어 Eng'])
		self.selectLangCombo.currentIndexChanged.connect(self.change_language)
		if self.get_config_data('language'):
			index = language.index(self.get_config_data('language'))
			self.selectLangCombo.setCurrentIndex(index)
		
		self.titleSpacer = QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
		self.titleSpacer.changeSize(0, 0, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

		detailTitleLayout.addWidget(self.selectLangCombo)
		detailTitleLayout.addItem(self.titleSpacer)
		detailLayout.addLayout(detailTitleLayout)

		# 로고 지정 영역
		self.logoFrame = LogoFrame(self.get_label('logo_input_guide'), self)
		self.logoFrame.changed.connect(self.show_logo_preview)
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
			text = self.get_config_data(f"tableitem{i+1}")
			if self.get_config_data("first_run"): text = self.get_label(f"tableitem{i+1}")
			if i < 4:
				self.inputTextTable.setItem(i, 0, QTableWidgetItem(text))
			else:
				self.inputTextTable.setItem(i-4, 1, QTableWidgetItem(text))
		self.inputTextTable.cellChanged.connect(self.show_logo_preview)
		# 미리보기
		self.watermarkTitle = QLabel(self.get_label('preview_title'))
		self.watermarkPreview = LogoPreviewFrame(self.get_label('preview_img'))
		self.buttonsWidget = QWidget()
		buttonsLayout = QVBoxLayout()
		buttonsLayout.setContentsMargins(0,0,0,0)
		buttonsLayout.setSpacing(5)
		self.buttonsWidget.setLayout(buttonsLayout)

		self.toggleDetailBtn = QPushButton(self.get_label('detail_open'))
		self.toggleDetailBtn.setToolTip(self.get_label('detail_open_tooltip'))
		self.toggleDetailBtn.setMaximumHeight(300)
		self.toggleDetailBtn.clicked.connect(self.toggle_detail)
		buttonsLayout.addWidget(self.toggleDetailBtn)

		self.gen_logoBtn = QPushButton(self.get_label('generate_logo'))
		self.gen_logoBtn.setMaximumHeight(300)
		self.gen_logoBtn.clicked.connect(self.generate_logo_preview)
		buttonsLayout.addWidget(self.gen_logoBtn)

		self.gen_previewBtn = QPushButton(self.get_label('generate_preview'))
		self.gen_previewBtn.setMaximumHeight(300)
		self.gen_previewBtn.setEnabled(False)
		self.gen_previewBtn.clicked.connect(self.generate_preview)
		buttonsLayout.addWidget(self.gen_previewBtn)

		self.saveBtn = QPushButton(self.get_label('save'))
		self.saveBtn.setMaximumHeight(300)
		self.saveBtn.clicked.connect(self.save_img)
		buttonsLayout.addWidget(self.saveBtn)

		self.resultLabel = QLabel()
		self.resultLabel.setAlignment(Qt.AlignmentFlag.AlignTop)
		self.resultLabel.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
		self.resultLabel.setWordWrap(True)
		self.resultLabel.setMaximumWidth(190)

		self.progressBar = QProgressBar()
		self.progressBar.setTextVisible(False)
		self.progressBar.setFixedHeight(20)
		self.progressBar.setRange(0, 1)
		self.progressBar.setEnabled(False)

		
		# 우측 상세설정
		self.midLine = VLine()
		# 기타 설정
		self.settingsLabel = QLabel(self.get_label('setting_title'))
		self.settingsWidget = QWidget()
		settingLayout = QGridLayout()
		self.settingsWidget.setLayout(settingLayout)
		self.realtimeCheck = QCheckBox(self.get_label('realtime_update'))
		if self.get_config_data('realtime_update'):
			self.realtimeCheck.setChecked(self.get_config_data('realtime_update'))
		else:
			self.realtimeCheck.setChecked(False)
		settingLayout.addWidget(self.realtimeCheck)
		
		# 폰트 설정
		self.fontSettingLabel = QLabel(self.get_label('font_title'))
		self.fontSettingwidget = QWidget()
		fontLayout = QGridLayout()
		self.fontSettingwidget.setLayout(fontLayout)
		
		self.fontSelectCombo = QComboBox()
		self.fontSelectCombo.addItems(self.get_fonts())
		self.fontColorLabel = QLabel()
		self.fontColorLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
		color = self.get_config_data('font_color')
		self.fontColorLabel.setText(color)
		self.fontColorLabel.setStyleSheet('QLabel {color: ' + color + '; font: bold 12px ;}')
		self.fontColorBtn = QPushButton(text = self.get_label('font_color'))
		self.fontColorBtn.clicked.connect(self.select_font_color)

		self.fontBorderCheck = QCheckBox()
		self.fontBorderCheck.setText(self.get_label('font_border'))
		if self.get_config_data('font_border'):
			self.fontBorderCheck.setChecked(True)
		fontBorderLayout = QHBoxLayout()
		self.fontBorderColorLabel = QLabel()
		self.fontBorderColorLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
		color = self.get_config_data('font_border_color')
		self.fontBorderColorLabel.setText(color)
		self.fontBorderColorLabel.setStyleSheet('QLabel {color: ' + color + '; font: bold 12px ;}')
		self.fontBorderWidth = QSpinBox()
		self.fontBorderWidth.setValue(self.get_config_data('font_border_width'))
		self.fontBorderColorBtn = QPushButton(self.get_label('font_border_color'))
		self.fontBorderColorBtn.clicked.connect(self.select_font_border_color)
		fontBorderLayout.addWidget(self.fontBorderWidth)
		fontBorderLayout.addWidget(self.fontBorderColorLabel)
		fontBorderLayout.addWidget(self.fontBorderColorBtn)

		
		
		fontLayout.addWidget(self.fontSelectCombo, 0, 0, 1, 3)
		fontLayout.addWidget(self.fontColorLabel, 0, 3)
		fontLayout.addWidget(self.fontColorBtn, 0, 4)
		fontLayout.addWidget(self.fontBorderCheck, 1, 0, 1, 2)
		fontLayout.addLayout(fontBorderLayout, 1, 2, 1, 3)

		# 텍스트 위치
		self.textLocalLabel = QLabel(self.get_label('local_title'))
		self.textLocalWidget = QWidget()
		localLayout = QHBoxLayout(self.textLocalWidget)
		localLayout.setContentsMargins(0,5,0,5)
		self.textLocalDown = QRadioButton(self.get_label('text_local_down'))
		self.textLocalLeft = QRadioButton(self.get_label('text_local_left'))
		self.textLocalRight = QRadioButton(self.get_label('text_local_right'))
		self.textLocalNone = QRadioButton(self.get_label('text_local_none'))

		if self.get_config_data('text_location'):
			[self.textLocalNone, self.textLocalDown, self.textLocalLeft, self.textLocalRight][self.get_config_data('text_location')].setChecked(True)
		else:
			self.textLocalDown.setChecked(True)

		self.textLocalDown.clicked.connect(self.show_logo_preview)
		self.textLocalLeft.clicked.connect(self.show_logo_preview)
		self.textLocalRight.clicked.connect(self.show_logo_preview)
		self.textLocalNone.clicked.connect(self.show_logo_preview)
		localLayout.addWidget(self.textLocalDown)
		# localLayout.addWidget(self.textLocalLeft)
		localLayout.addWidget(self.textLocalRight)
		localLayout.addWidget(self.textLocalNone)
		# 배열 방식
		self.textAlignLabel =  QLabel(self.get_label('align_title'))
		self.textAlignWidget = QWidget()
		alignLayout = QGridLayout(self.textAlignWidget)
		alignLayout.setContentsMargins(1,1,1,2)
		self.textAlignOneCol = QRadioButton(self.get_label('align_one_column'))
		self.textAlignOneCol.setToolTip(self.get_label('align_one_column'))
		# self.textAlignOneCol.setChecked(True)
		
		self.textAlignTwoCol = QRadioButton(self.get_label('align_two_column'))
		self.textAlignTwoCol.setToolTip(self.get_label('align_two_column'))
		
		self.textAlignThreeCol = QRadioButton(self.get_label('align_three_column'))
		self.textAlignThreeCol.setToolTip(self.get_label('align_three_column'))
		
		if self.get_config_data('text_location'):
			[self.textAlignOneCol, self.textAlignTwoCol, self.textAlignThreeCol][self.get_config_data('align')].setChecked(True)
		else:
			self.textAlignOneCol.setChecked(True)

		self.textAlignOneCol.toggled.connect(self.show_logo_preview)
		self.textAlignTwoCol.toggled.connect(self.show_logo_preview)
		self.textAlignThreeCol.toggled.connect(self.show_logo_preview)

		alignLayout.addWidget(self.textAlignOneCol, 0, 0)
		alignLayout.addWidget(self.textAlignTwoCol, 0, 1)
		alignLayout.addWidget(self.textAlignThreeCol, 0, 2)
		# 워터마크 위치
		self.markLocLabel = QLabel(self.get_label('position_title'))
		self.markLocWidget = QWidget()
		markLocLayout = QGridLayout()
		markLocLayout.setContentsMargins(1,1,1,10)
		markLocLayout.setSpacing(5)
		markLocLayout.setColumnMinimumWidth(0, 120)
		markLocLayout.setColumnMinimumWidth(1, 120)
		markLocLayout.setColumnMinimumWidth(2, 120)
		self.markLocWidget.setLayout(markLocLayout)

		self.markLoc_Center = QRadioButton(self.get_label('pos_center'))
		# self.textPos_Center.toggled.connect(self.show_logo_preview)
		self.markLoc_Custom = QRadioButton(self.get_label('pos_custom'))
		self.markLoc_Custom.toggled.connect(self.toggle_textpos)
		# self.textPos_Custom.toggled.connect(self.show_logo_preview)
		self.markLocCustomX = QSpinBox()
		self.markLocCustomX.setRange(0, 100)
		self.markLocCustomX.setToolTip(self.get_label('pos_x'))
		self.markLocCustomX.setEnabled(False)
		# self.textPosCustomX.valueChanged.connect(self.show_logo_preview)

		self.markLocCustomY = QSpinBox()
		self.markLocCustomY.setRange(0, 100)
		self.markLocCustomY.setToolTip(self.get_label('pos_y'))
		self.markLocCustomY.setEnabled(False)
		# self.textPosCustomY.valueChanged.connect(self.show_logo_preview)

		self.markLocCustomType = QComboBox()
		self.markLocCustomType.addItems(['Pixel','%'])
		self.markLocCustomType.currentIndexChanged.connect(self.select_custom_markloc_type)
		self.markLocCustomType.setEnabled(False)
		# self.textPosCustomType.currentTextChanged.connect(self.show_logo_preview)

		self.markLoc_Top = QRadioButton(self.get_label('pos_top'))
		# self.textPos_Top.toggled.connect(self.show_logo_preview)
		self.markLoc_Bottom = QRadioButton(self.get_label('pos_bottom'))
		# self.textPos_Bottom.toggled.connect(self.show_logo_preview)
		self.markLoc_Left = QRadioButton(self.get_label('pos_left'))
		# self.textPos_Left.toggled.connect(self.show_logo_preview)
		self.markLoc_Right = QRadioButton(self.get_label('pos_right'))
		# self.textPos_Right.toggled.connect(self.show_logo_preview)

		self.markLoc_TopLeft = QRadioButton(self.get_label('pos_topleft'))
		# self.textPos_TopLeft.toggled.connect(self.show_logo_preview)
		self.markLoc_TopRight = QRadioButton(self.get_label('pos_topright'))
		# self.textPos_TopRight.toggled.connect(self.show_logo_preview)
		self.markLoc_BottomLeft = QRadioButton(self.get_label('pos_bottomleft'))
		# self.textPos_BottomLeft.toggled.connect(self.show_logo_preview)
		self.markLoc_BottomRight = QRadioButton(self.get_label('pos_bottomright'))
		# self.textPos_BottomRight.toggled.connect(self.show_logo_preview)
		
		if self.get_config_data('mark_location'):
			[self.markLoc_Center, self.markLoc_TopLeft, self.markLoc_Top, self.markLoc_TopRight, self.markLoc_Left, self.markLoc_Right, self.markLoc_BottomLeft, self.markLoc_Bottom, self.markLoc_BottomRight, self.markLoc_Custom][self.get_config_data('mark_location')].setChecked(True)
		else:
			self.markLoc_Center.setChecked(True)

		if self.get_config_data('mark_location') == 9:
			self.markLocCustomX.setValue(self.get_config_data('mark_custom_x'))
			self.markLocCustomY.setValue(self.get_config_data('mark_custom_y'))
			self.markLocCustomType.setCurrentIndex(self.get_config_data('mark_custom_type'))
			
		markLocLayout.addWidget(self.markLoc_TopLeft, 0, 0)
		markLocLayout.addWidget(self.markLoc_Top, 0, 1)
		markLocLayout.addWidget(self.markLoc_TopRight, 0, 2)
		markLocLayout.addWidget(self.markLoc_Left, 1, 0)
		markLocLayout.addWidget(self.markLoc_Center, 1, 1)
		markLocLayout.addWidget(self.markLoc_Right, 1, 2)
		markLocLayout.addWidget(self.markLoc_BottomLeft, 2, 0)
		markLocLayout.addWidget(self.markLoc_Bottom, 2, 1)
		markLocLayout.addWidget(self.markLoc_BottomRight, 2, 2)
		markLocLayout.addWidget(self.markLoc_Custom, 3, 0, 1, 3)
		markLocLayout.addWidget(self.markLocCustomX, 4, 0)
		markLocLayout.addWidget(self.markLocCustomY, 4, 1)
		markLocLayout.addWidget(self.markLocCustomType, 4, 2)

		# 크기
		self.markSizeTitle = QLabel(self.get_label('size_title'))

		self.markSizeWidth = QSpinBox()
		self.markSizeWidth.setRange(0, 100)
		if self.get_config_data('mark_size'):
			self.markSizeWidth.setValue(self.get_config_data('mark_size'))

		self.markSizeType = QComboBox()
		self.markSizeType.addItems(['Pixel','%'])
		if self.get_config_data('mark_size_type'):
			self.markSizeType.setCurrentIndex(self.get_config_data('mark_size_type'))
		self.markSizeType.currentIndexChanged.connect(self.select_custom_marksize_type)

		self.markSizeDescriptionLabel = QLabel(self.get_label('size_desc'))


		# 회전
		self.textOrientTitle = QLabel(self.get_label('orient_title'))
		self.textOrientLine = QSpinBox()
		self.textOrientLine.setFixedWidth(60)
		self.textOrientLine.setValue(0)
		self.textOrientLine.setRange(-180, 180)
		self.textOrientLine.textChanged.connect(self.input_orient_value)
		self.textOrientSlider = QSlider()
		self.textOrientSlider.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
		self.textOrientSlider.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
		self.textOrientSlider.setTickPosition(QSlider.TickPosition.TicksAbove)
		self.textOrientSlider.setRange(-180, 180)
		self.textOrientSlider.setValue(0)
		self.textOrientSlider.setTickInterval(45)
		self.textOrientSlider.setSingleStep(15)
		self.textOrientSlider.setPageStep(90)
		self.textOrientSlider.setOrientation(Qt.Orientation.Horizontal)
		self.textOrientSlider.valueChanged.connect(self.set_orient_value)

		if self.get_config_data('orientation'):
			self.textOrientSlider.setValue(self.get_config_data('orientation'))
			
		# 투명도
		self.markAlphaTitle = QLabel(self.get_label('alpha_title'))
		self.markAlphaLine = QSpinBox()
		self.markAlphaLine.setFixedWidth(60)
		self.markAlphaLine.setRange(0, 100)
		self.markAlphaLine.setValue(100)
		self.markAlphaLine.textChanged.connect(self.input_alpha_value)
		self.markAlphaSlider = QSlider()
		self.markAlphaSlider.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
		self.markAlphaSlider.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
		self.markAlphaSlider.setTickPosition(QSlider.TickPosition.TicksAbove)
		self.markAlphaSlider.setRange(0, 100)
		self.markAlphaSlider.setValue(100)
		self.markAlphaSlider.setTickInterval(10)
		self.markAlphaSlider.setSingleStep(10)
		self.markAlphaSlider.setPageStep(25)
		self.markAlphaSlider.setOrientation(Qt.Orientation.Horizontal)
		self.markAlphaSlider.valueChanged.connect(self.set_alpha_value)

		if self.get_config_data('alpha'):
			self.markAlphaSlider.setValue(self.get_config_data('alpha'))


		# 방식(단일, 바둑판)
		self.textTypeTitle = QLabel(self.get_label('type_title'))
		self.textTypeWidget = QWidget()
		typeLayout = QHBoxLayout()
		typeLayout.setContentsMargins(0,1,0,10)
		self.textTypeWidget.setLayout(typeLayout)

		self.markType_Single = QRadioButton(self.get_label('type_single'))
		self.markType_Single.toggled.connect(self.select_marktype)
		self.markType_Fit = QRadioButton(self.get_label('type_fit'))
		self.markType_Fit.toggled.connect(self.select_marktype)
		self.markType_Expand = QRadioButton(self.get_label('type_expand'))
		self.markType_Expand.toggled.connect(self.select_marktype)
		self.markType_Checkboard = QRadioButton(self.get_label('type_checkboard'))
		self.markType_Checkboard.toggled.connect(self.select_marktype)

		if self.get_config_data('type'):
			[self.markType_Single, self.markType_Fit, self.markType_Expand, self.markType_Checkboard][self.get_config_data('type')].setChecked(True)
		else:
			self.markType_Single.setChecked(True)

		typeLayout.addWidget(self.markType_Single)
		typeLayout.addWidget(self.markType_Fit)
		typeLayout.addWidget(self.markType_Expand)
		typeLayout.addWidget(self.markType_Checkboard)


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
		logoGrid.addWidget(self.textLocalLabel, 6, 0)
		logoGrid.addWidget(self.textLocalWidget, 6, 1, 1, 3)
		logoGrid.addWidget(HLine(), 7, 0, 1, 4)
		logoGrid.addWidget(self.watermarkTitle, 8, 0, 1, 4)
		logoGrid.addWidget(self.watermarkPreview, 9, 0, 1, 3)
		logoGrid.addWidget(self.buttonsWidget, 9, 3)
		# logoGrid.addWidget(self.gen_previewBtn, 10, 0)
		# logoGrid.addWidget(self.saveBtn, 10, 1)
		# logoGrid.addWidget(self.toggleDetailBtn, 10, 3)
		logoGrid.addWidget(self.progressBar, 11, 0, 1, 4)
		logoGrid.addWidget(self.resultLabel, 12, 0, 1, 4)
		# logoGrid.addItem(QSpacerItem(20,20,QSizePolicy.Policy.Preferred,QSizePolicy.Policy.Expanding), 20, 0)

		# detailGrid.addWidget(self.midLine, 0, 5, 10, 1)
		# 우측
		# 6~
		detailGrid = QGridLayout()
		detailGrid.setContentsMargins(0,0,0,0)
		detailGrid.setSpacing(5)
		detailGrid.addWidget(self.settingsLabel, 0, 0)
		detailGrid.addWidget(self.settingsWidget, 1, 0, 1, 4)
		detailGrid.addWidget(HLine(), 2, 0, 1, 4)
		detailGrid.addWidget(self.fontSettingLabel, 3, 0)
		detailGrid.addWidget(self.fontSettingwidget, 4, 0, 1, 4)
		detailGrid.addWidget(HLine(), 5, 0, 1, 4)
		detailGrid.addWidget(self.textTypeTitle, 6, 0)
		detailGrid.addWidget(self.textTypeWidget, 7, 0, 1, 4)
		detailGrid.addWidget(HLine(), 8, 0, 1, 4)
		detailGrid.addWidget(self.markLocLabel, 9, 0)
		detailGrid.addWidget(self.markLocWidget, 10, 0, 2, 4)
		detailGrid.addWidget(HLine(), 11, 0, 1, 4)
		detailGrid.addWidget(self.markSizeTitle, 12, 0)
		detailGrid.addWidget(self.markSizeWidth, 13, 0)
		detailGrid.addWidget(self.markSizeType, 13, 1)
		detailGrid.addWidget(self.markSizeDescriptionLabel, 14, 0, 1, 4)
		detailGrid.addWidget(HLine(), 15, 0, 1, 4)
		detailGrid.addWidget(self.textOrientTitle, 16, 0)
		detailGrid.addWidget(self.textOrientSlider, 17, 0, 1, 3)
		detailGrid.addWidget(self.textOrientLine, 17, 3)
		detailGrid.addWidget(HLine(), 18, 0, 1, 4)
		detailGrid.addWidget(self.markAlphaTitle, 19, 0)
		detailGrid.addWidget(self.markAlphaSlider, 20, 0, 1, 3)
		detailGrid.addWidget(self.markAlphaLine, 20, 3)
		# detailGrid.addItem(QSpacerItem(20,20,QSizePolicy.Policy.Preferred,QSizePolicy.Policy.Expanding), 21, 0)
		

		self.leftWidget = QWidget()
		self.leftWidget.setFixedWidth(400)
		self.leftWidget.setLayout(logoGrid)
		self.rightWidget = QWidget()
		self.rightWidget.setFixedWidth(390)
		self.rightWidget.setLayout(detailGrid)
		self.rightWidget.setContentsMargins(5,5,5,5)
		
		self.rightScroll = QScrollArea()
		self.rightScroll.setWidget(self.rightWidget)
		self.rightScroll.setWidgetResizable(True)

		self.rightScroll.hide()
		self.midLine.hide()

		mainLayout = QHBoxLayout()
		mainLayout.setAlignment(Qt.AlignmentFlag.AlignLeft)
		mainLayout.addWidget(self.leftWidget)
		mainLayout.addWidget(self.midLine)
		mainLayout.addWidget(self.rightScroll)

		detailFrame = QFrame()
		detailFrame.setFrameShape(QFrame.Box)
		detailFrame.setLayout(mainLayout)
		
		detailLayout.addWidget(detailFrame)
		
		self.show_logo_preview()
		self.select_marktype()

		cwidget.setLayout(mainGrid)

		return cwidget
	
	############################################################
	######              Element Actions                   ######
	############################################################

	def change_language(self):
		index = self.selectLangCombo.currentIndex()
		self.update_xml('language', language[index])
		save_xml(self.config, CONFIG_PATH)

		self.get_Label_data()
		self.update_language()

	def update_language(self):
		self.centralWidget().deleteLater()
		self.setCentralWidget(self.cwidget_init())

	def show_result_msg(self, msg):
		self.resultLabel.setText(msg)
		worker = Timer(5, 'RM_0')
		worker.timer_end.connect(self.timer_cleanup)
		self.pool.start(worker)

	# 로딩바
	def setup_progress_bar(self, min, max):
		self.progressBar.setRange(min, max)
		self.progressBar.setEnabled(True)

	def update_progress_bar(self, progress):
		print('progress', progress)
		if isinstance(progress, str):
			self.resultLabel.setText(progress)
			self.progressBar.setStyleSheet('QProgressBar::chunk{background-color:red;};')
			self.progressBar.setValue(self.progressBar.maximum())
			worker = Timer(5, 'PG_0')
			worker.timer_end.connect(self.timer_cleanup)
			self.pool.start(worker)
			return 
		self.progressBar.setValue(progress)
		if self.progressBar.maximum() == self.progressBar.value():
			self.progressBar.setEnabled(False)
			self.progressBar.setRange(0, 100)
			self.progressBar.setValue(0)

	def change_font_color(self, color:QColor):
		changedColor = color.name(QColor.NameFormat.HexRgb)
		self.fontColorLabel.setText(changedColor)
		self.fontColorLabel.setStyleSheet('QLabel {color: ' + changedColor + '; font: bold 12px ;}')

	def change_font_border_color(self, color:QColor):
		changedColor = color.name(QColor.NameFormat.HexRgb)
		self.fontBorderColorLabel.setText(changedColor)
		self.fontBorderColorLabel.setStyleSheet('QLabel {color: ' + changedColor + '; font: bold 12px ;}')


	# 워터마크 위치 직접입력
	def toggle_textpos(self):
		if self.markLoc_Custom.isChecked():
			self.markLocCustomX.setEnabled(True)
			self.markLocCustomY.setEnabled(True)
			self.markLocCustomType.setEnabled(True)
		else:
			self.markLocCustomX.setEnabled(False)
			self.markLocCustomY.setEnabled(False)
			self.markLocCustomType.setEnabled(False)
	
	def select_custom_markloc_type(self):
		img_width = self.imgFrame.img_width
		img_height = self.imgFrame.img_height
		if self.markLocCustomType.currentIndex() == 0:
			self.markLocCustomX.setMaximum(img_width)
			self.markLocCustomY.setMaximum(img_height)
			x_value = self.markLocCustomX.value()
			if x_value != 0:
				x_value_alt, ext = divmod(img_width*x_value, 100)
				x_value_alt = x_value_alt + round(ext/100)
				self.markLocCustomX.setValue(x_value_alt)
			y_value = self.markLocCustomY.value()
			if y_value != 0:
				y_value_alt, ext = divmod(img_width*y_value, 100)
				y_value_alt = y_value_alt + round(ext/100)
				self.markLocCustomY.setValue(y_value_alt)
		elif self.markLocCustomType.currentIndex() == 1:
			self.markLocCustomX.setMaximum(100)
			self.markLocCustomY.setMaximum(100)
			x_value = self.markLocCustomX.value()
			if x_value != 0:
				x_value_alt, ext = divmod(img_width*100, x_value)
				x_value_alt = x_value_alt + round(ext/x_value)
				self.markLocCustomX.setValue(x_value_alt)
			y_value = self.markLocCustomY.value()
			if y_value != 0:
				y_value_alt, ext = divmod(img_width*100, y_value)
				y_value_alt = y_value_alt + round(ext/y_value)
				self.markLocCustomY.setValue(y_value_alt)

	# 워터마크 크기 타입 선택
	def select_custom_marksize_type(self):
		img_width = self.imgFrame.img_width
		if self.markSizeType.currentIndex() == 0:
			width = self.markSizeWidth.value()
			width_alt, ext = divmod(img_width*width, 100)
			width_alt = width_alt + round(ext/100)
			self.markSizeWidth.setMaximum(img_width)
			self.markSizeWidth.setValue(width_alt)
		elif self.markSizeType.currentIndex() == 1:
			width = self.markSizeWidth.value()
			width_alt, ext = divmod(width*100, img_width)
			width_alt = width_alt + round(ext/img_width)
			self.markSizeWidth.setMaximum(100)
			self.markSizeWidth.setValue(width_alt)

	# 워터마크 유형 선택
	def select_marktype(self):
		if self.markType_Single.isChecked() or self.markType_Checkboard.isChecked():
			self.markLocWidget.setEnabled(True)
			self.markSizeWidth.setEnabled(True)
			self.markSizeType.setEnabled(True)
		else:
			self.markLocWidget.setEnabled(False)
			self.markSizeWidth.setEnabled(False)
			self.markSizeType.setEnabled(False)


	# 회전 슬라이더 값
	def set_orient_value(self):
		self.textOrientLine.setValue(self.textOrientSlider.value())
	def input_orient_value(self):
		self.textOrientSlider.setValue(self.textOrientLine.value())

	# 투명도 슬라이더 값
	def set_alpha_value(self):
		self.markAlphaLine.setValue(self.markAlphaSlider.value())
	def input_alpha_value(self):
		self.markAlphaSlider.setValue(self.markAlphaLine.value())

	
	############################################################
	######              Button Actions                    ######
	############################################################
		
	# 이미지 추가 버튼
	def select_img(self):
		directory = self.get_config_data('folderpath') or os.getcwd()
		file_selector = QFileDialog(self, caption="이미지 선택", directory=directory)
		file_selector.setFileMode(QFileDialog.FileMode.ExistingFile)
		file_selector.setViewMode(QFileDialog.ViewMode.Detail)
		file_selector.setNameFilters({'Image File (*.png *.jpg)','Any files (*)'})
		file_selector.selectNameFilter('Image File (*.png *.jpg)')
		file_selector.exec()

		if len(file_selector.selectedFiles()):
			filename = file_selector.selectedFiles()[0]
			filepath = os.path.basename(filename)
			self.update_xml('folderpath', filepath)
			print(filename)
			self.imgFrame.set_image(filename)
			img_width = self.imgFrame.img_width
			img_height = self.imgFrame.img_height
			if self.markLocCustomType.currentIndex() == 0:
				self.markLocCustomX.setMaximum(img_width)
				self.markLocCustomY.setMaximum(img_height)
			if self.markSizeType.currentIndex() == 0:
				self.markSizeWidth.setMaximum(img_width)
			shutil.copy(filename, MAIN_IMAGE_PATH)
			


	# 이미지 제거 버튼
	def remove_img(self):
		self.imgFrame.clear()
		self.imgFrame.setText(self.get_label('img_input_guide'))
		self.imgFrame.setToolTip('')

	# 로고 추가 버튼
	def select_logo(self):
		directory = self.get_config_data('folderpath') or os.getcwd()
		file_selector = QFileDialog(self, caption="이미지 선택", directory=directory)
		file_selector.setFileMode(QFileDialog.FileMode.ExistingFile)
		file_selector.setViewMode(QFileDialog.ViewMode.Detail)
		file_selector.setNameFilters({'Image File (*.png *.jpg)','Any files (*)'})
		file_selector.selectNameFilter('Image File (*.png *.jpg)')
		file_selector.exec()

		if len(file_selector.selectedFiles()):
			filename = file_selector.selectedFiles()[0]
			filepath = os.path.basename(filename)
			self.update_xml('folderpath', filepath)
			print(filename)
			self.logoFrame.set_image(filename)
			shutil.copyfile(filename, LOGO_PATH, follow_symlinks=False)
		
		self.show_logo_preview()

	# 로고 제거 버튼
	def remove_logo(self):
		self.logoFrame.clear()
		self.logoFrame.setText(self.get_label('logo_input_guide'))
		self.logoFrame.setToolTip('')
		self.watermarkPreview.clear()
		

	# 상세설정 표시 버튼
	def toggle_detail(self):
		if self.toggleDetailBtn.text() == self.get_label('detail_open'):
			self.midLine.show()
			self.rightScroll.show()
			self.setFixedWidth(1400)
			self.toggleDetailBtn.setText(self.get_label('detail_close'))
			self.toggleDetailBtn.setToolTip(self.get_label('detail_close_tooltip'))
			self.titleSpacer.changeSize(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
		else:
			self.midLine.hide()
			self.rightScroll.hide()
			self.setFixedWidth(950)
			self.toggleDetailBtn.setText(self.get_label('detail_open'))
			self.toggleDetailBtn.setToolTip(self.get_label('detail_open_tooltip'))
			self.titleSpacer.changeSize(0, 0, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

	def get_setting_data(self):
		texts = []
		for row in range(4):
			row_temp = []
			for col in range(2):
				row_temp.append(self.inputTextTable.item(row, col).text())
			texts.append(' '.join(row_temp))
			row_temp = []
		
		settings = {}
		settings["text_location"] = self.get_text_location_setting()
		settings["align"] = self.get_text_align_setting()
		settings["mark_size"] = self.get_mark_size_setting()
		settings["mark_location"] = self.get_mark_location_setting()
		settings['mark_custom_location'] = [*self.get_mark_custom_location()]
		settings["orientation"] = self.textOrientSlider.value()
		settings["type"] = self.get_mark_type_setting()
		settings["font"] = self.fontSelectCombo.currentText()
		settings["font_color"] = self.fontColorLabel.text()
		settings["font_border"] = self.fontBorderCheck.isChecked()
		settings["font_border_width"] = self.fontBorderWidth.value()
		settings["font_border_color"] = self.fontBorderColorLabel.text()
		settings["alpha"] = self.markAlphaSlider.value()
		return texts, settings


	# 로고 미리보기 갱신
	def show_logo_preview(self, *, force=False):
		if not self.realtimeCheck.isChecked() and not force:
			return
		if self.logoFrame.pixmap():
			texts, settings = self.get_setting_data()

			self.setup_progress_bar(0, 10)
			worker = LogoPreview(texts, settings)
			# worker.setup_bar.connect(self.setup_progress_bar)
			worker.progress.connect(self.update_progress_bar)
			worker.finish.connect(self.finish_logo_preview)
			self.pool.start(worker)
		else:
			self.show_result_msg(self.get_label('no_logo'))

	def finish_logo_preview(self):
		preview = QPixmap(WATERMARK_SAMPLE_PATH)
		self.watermarkPreview.setPixmap(preview)
		self.show_result_msg(self.get_label('finish_logo_gen'))

	def generate_logo_preview(self):
		self.show_logo_preview(force=True)
		self.update_config()

	def generate_preview(self):
		self.update_config()
		texts, settings = self.get_setting_data()
		worker = Timer(3, 'test')
		worker.finish.connect(self.finish_save_image)
		self.pool.start(worker)

	def save_img(self):
		if self.imgFrame.pixmap():
			self.update_config()
			texts, settings = self.get_setting_data()
			path = self.imgFrame.toolTip()
			# filename = os.path.basename(path)
			
			self.setup_progress_bar(0, 10)
			worker = SaveImage(settings, path)
			worker.progress.connect(self.update_progress_bar)
			worker.finish.connect(self.finish_save_image)
			self.pool.start(worker)
		else:
			self.show_result_msg(self.get_label('no_main_image'))

	def finish_save_image(self):
		sleep(1)
		if 'red' not in self.progressBar.styleSheet():
			self.show_result_msg(self.get_label('finish_save'))

		worker = ShowImage(self.imgFrame.toolTip())
		self.pool.start(worker)

	def select_font_color(self):
		color = self.fontColorLabel.text().replace('#', '')
		colorObj = QColor().fromRgb(*[int(color[2*x:2*x+2], 16) for x in range(3)])
		picker = QColorDialog(colorObj, self)
		picker.colorSelected.connect(self.change_font_color)
		
		picker.exec()

	def select_font_border_color(self):
		color = self.fontColorLabel.text().replace('#', '')
		colorObj = QColor().fromRgb(*[int(color[2*x:2*x+2], 16) for x in range(3)])
		picker = QColorDialog(colorObj, self)
		picker.colorSelected.connect(self.change_font_border_color)
		
		picker.exec()

	############################################################
	######                  Sub Method                    ######
	############################################################

	def timer_cleanup(self, code):
		if code == 'PG_0':
			self.progressBar.setStyleSheet('')
			self.progressBar.setValue(0)
			self.resultLabel.setText('')
		elif code == 'RM_0':
			self.resultLabel.setText('')

	def get_label(self, name):
		element = self.lang.getroot().find(f".//LabelText[@name='{name}']")
		try:
			return element.text
		except:
			return ''
		
	def update_xml(self, id, value):
		element = self.config.getroot().find(f".//SettingOption[@id='{id}']")
		element.attrib["value"] = str(value)
		# try:
		# 	element.attrib["value"] = str(value)
		# except AttributeError as e:
		# 	import xml.etree.ElementTree as ET
		# 	if isinstance(value, str):
		# 		element = ET.Element('SettingOption', {'id':id, 'type':'str', 'value':str(value)})
		# 	elif isinstance(value, bool):
		# 		element = ET.Element('SettingOption', {'id':id, 'type':'bool', 'value':str(value)})
		# 	elif isinstance(value, int):
		# 		element = ET.Element('SettingOption', {'id':id, 'type':'int', 'value':str(value)})
		# 	self.config.getroot().append(element)

	def update_config(self):
		texts, settings = self.get_setting_data()
		for col in range(2):
			for row in range(4):
				value = self.inputTextTable.item(row, col).text()
				self.update_xml(f'tableitem{col*4+row+1}', value)
		self.update_xml('first_run', False)
		self.update_xml('realtime_update', self.realtimeCheck.isChecked())
		self.update_xml('text_location', settings['text_location'])
		self.update_xml('align', settings['align'])
		self.update_xml('mark_size', settings['mark_size'][0])
		self.update_xml('mark_size_type', settings['mark_size'][1])
		self.update_xml('mark_location', settings['mark_location'])
		self.update_xml('mark_custom_x', settings['mark_custom_location'][0])
		self.update_xml('mark_custom_y', settings['mark_custom_location'][1])
		self.update_xml('mark_custom_type', settings['mark_custom_location'][2])
		self.update_xml('orientation', settings['orientation'])
		self.update_xml('type', settings['type'])
		self.update_xml('font', settings['font'])
		self.update_xml('font_color', settings['font_color'])
		self.update_xml('font_border', settings['font_border'])
		self.update_xml('font_border_width', settings['font_border_width'])
		self.update_xml('font_border_color', settings['font_border_color'])
		self.update_xml('alpha', settings['alpha'])

		save_xml(self.config, CONFIG_PATH)

	def get_text_location_setting(self):
		if self.textLocalNone.isChecked():
			return 0
		elif self.textLocalDown.isChecked():
			return 1
		elif self.textLocalLeft.isChecked():
			return 2
		elif self.textLocalRight.isChecked():
			return 3

	def get_text_align_setting(self):
		if self.textAlignOneCol.isChecked():
			return 0
		elif self.textAlignTwoCol.isChecked():
			return 1
		elif self.textAlignThreeCol.isChecked():
			return 2

	def get_mark_size_setting(self):
		return [self.markSizeWidth.value(), self.markSizeType.currentIndex()]

	def get_mark_location_setting(self):
		if self.markLoc_Center.isChecked():
			return 0
		elif self.markLoc_TopLeft.isChecked():
			return 1
		elif self.markLoc_Top.isChecked():
			return 2
		elif self.markLoc_TopRight.isChecked():
			return 3
		elif self.markLoc_Left.isChecked():
			return 4
		elif self.markLoc_Right.isChecked():
			return 5
		elif self.markLoc_BottomLeft.isChecked():
			return 6
		elif self.markLoc_Bottom.isChecked():
			return 7
		elif self.markLoc_BottomRight.isChecked():
			return 8
		elif self.markLoc_Custom.isChecked():
			return 9
	
	def get_mark_custom_location(self):
		return self.markLocCustomX.value(), self.markLocCustomY.value(), self.markLocCustomType.currentIndex()

	def get_mark_type_setting(self):
		if self.markType_Single.isChecked():
			return 0
		elif self.markType_Fit.isChecked():
			return 1
		elif self.markType_Expand.isChecked():
			return 2
		elif self.markType_Checkboard.isChecked():
			return 3
		
	def get_fonts(self):
		import glob
		fonts = ['.'.join(os.path.basename(x).split('.')[:-1]) for x in glob.glob(FONTS_PATH+'/*')]
		return fonts



	############################################################
	######                 Slot Method                    ######
	############################################################
		
	def hideEvent(self, event):
		self.hide()
		self.setWindowState(Qt.WindowState.WindowMinimized)
	
	def closeEvent(self, event):
		self.update_config()
		if self.pool.activeThreadCount():
			self.app_quit.emit()
			event.accept()


############################################################
######                 Sub Classes                    ######
############################################################

# 이미지 표시
class ImageFrame(QLabel):
	def __init__(self, label, parent: QWidget=None) -> None:
		super().__init__(parent)
		self.setFixedWidth(505)
		self.setAcceptDrops(True)
		self.setStyleSheet('QLabel{border: 4px dashed #aaa};')
		self.setText(label)
		# self.setText(self.parent().get_label('img_input_guide'))

		# 이미지 들어갈 라벨
		self.setAlignment(Qt.AlignmentFlag.AlignCenter)
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
			path = event.mimeData().urls()[0].toLocalFile()
			self.set_image(path)
			shutil.copy(path, MAIN_IMAGE_PATH)
			event.accept()
		else:
			event.ignore()


	# 이미지 표시
	def set_image(self, imgpath):
		self.setToolTip(imgpath)
		self.get_img_size(imgpath)
		self.img = QPixmap(imgpath)
		thumbnail = self.img.scaled(self.width(), self.height(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
		self.setPixmap(thumbnail)

	def get_img_size(self, path):
		img = Image.open(path)
		self.img_width = img.width
		self.img_height = img.height

# 이미지 표시
class LogoFrame(QLabel):
	changed = Signal()
	def __init__(self, label, parent: QWidget=None) -> None:
		super().__init__(parent)
		self.setFixedSize(100,100)
		self.setAcceptDrops(True)
		self.setStyleSheet('QLabel{border: 2px dashed #aaa};')
		self.setText(label)
		# self.setText(self.parent().get_label('logo_input_guide'))

		# 이미지 들어갈 라벨
		self.setAlignment(Qt.AlignmentFlag.AlignCenter)

		if os.path.exists(LOGO_PATH):
			img = QPixmap(LOGO_PATH)
			logo = img.scaledToWidth(self.width(), Qt.TransformationMode.SmoothTransformation)
			self.setPixmap(logo)
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
			path = event.mimeData().urls()[0].toLocalFile()
			self.set_image(path)
			shutil.copyfile(path, LOGO_PATH)
			self.changed.emit()
			event.accept()
		else:
			event.ignore()


	# 이미지 표시
	def set_image(self, imgpath):
		# self.setToolTip(imgpath)
		self.img = QPixmap(imgpath)
		thumbnail = self.img.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
		self.setPixmap(thumbnail)

class LogoPreviewFrame(QLabel):
	def __init__(self, parent: QWidget=None) -> None:
		super().__init__(parent)
		self.setFixedSize(300, 160)
		self.setContentsMargins(0, 0, 0, 0)
		self.setFrameShape(QFrame.Box)

		# 이미지 들어갈 라벨
		self.setAlignment(Qt.AlignmentFlag.AlignCenter)

		if os.path.exists(WATERMARK_PATH):
			img = QPixmap(WATERMARK_PATH)
			logo = img.scaled(self.width()-10, self.height()-10, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
			self.setPixmap(logo)


	# 이미지 표시
	def set_image(self, imgpath):
		self.img = QPixmap(imgpath)
		thumbnail = self.img.scaled(self.width()-10, self.height()-10, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
		self.setPixmap(thumbnail)



class HLine(QFrame):
	def __init__(self, parent: QWidget=None) -> None:
		super().__init__(parent)
		self.setFrameShape(QFrame.Shape.HLine)
		
class VLine(QFrame):
	def __init__(self, parent: QWidget=None) -> None:
		super().__init__(parent)
		self.setFrameShape(QFrame.Shape.VLine)