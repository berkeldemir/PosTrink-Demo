from PySide6.QtWidgets import (
	QWidget, QVBoxLayout, QPushButton, QLabel,
	QScrollArea, QDialog, QTableWidget, QTableWidgetItem, QHeaderView,
	QHBoxLayout, QSpacerItem, QSizePolicy, QLineEdit, QCheckBox, QFrame
)
from PySide6.QtGui import QPixmap, QIcon, QPainter, QColor
from PySide6.QtCore import Qt, Signal, QTimer, QSize
from data import AppData

class InfoBoxWidget(QWidget):
	def __init__(self, message: str, icon_type: str = 'warning', parent=None):
		super().__init__(parent)

		self.setObjectName("InfoBox")

		self.layout = QHBoxLayout(self)
		self.layout.setContentsMargins(8, 6, 8, 6)
		self.layout.setSpacing(10)
		self.layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

		self.icon_label = QLabel()
		self.icon_label.setFixedSize(56, 56)
		self.layout.addWidget(self.icon_label)
		
		self.message_label = QLabel(message)
		self.message_label.setWordWrap(True)
		self.message_label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft) 
		self.message_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
		self.layout.addWidget(self.message_label)
		self.current_style_config = self.get_style_config(icon_type)
		self.set_icon(icon_type)
		self.apply_style()
		self.setAttribute(Qt.WidgetAttribute.WA_NoMousePropagation, True)

	def paintEvent(self, event):
		painter = QPainter(self)
		painter.setRenderHint(QPainter.RenderHint.Antialiasing)

		bg_color = self.current_style_config['bg_color']
		border_color = self.current_style_config['border_color']
		border_radius = self.current_style_config['border_radius']

		painter.setBrush(QColor(bg_color))
		painter.setPen(Qt.PenStyle.NoPen)
		painter.drawRoundedRect(self.rect(), border_radius, border_radius)
		painter.setPen(QColor(border_color))
		painter.setBrush(Qt.BrushStyle.NoBrush)
		painter.drawRoundedRect(self.rect(), border_radius, border_radius)
		
		super().paintEvent(event)

	def get_style_config(self, icon_type: str):
		if icon_type == 'warning':
			return {
				'bg_color': "#FFF3CD",
				'border_color': "#FFE0A8",
				'text_color': "#664D03",
				'border_radius': 8
			}
		elif icon_type == 'information':
			return {
				'bg_color': "#CCE5FF",
				'border_color': "#A9D5FA",
				'text_color': "#004085",
				'border_radius': 8
			}
		else:
			return {
				'bg_color': "#E9E9E9",
				'border_color': "#C0C0C0",
				'text_color': "#000000",
				'border_radius': 8
			}

	def set_icon(self, icon_type: str):
		if icon_type == 'warning':
			icon = self.style().standardIcon(self.style().StandardPixmap.SP_MessageBoxWarning)
		elif icon_type == 'information':
			icon = self.style().standardIcon(self.style().StandardPixmap.SP_MessageBoxInformation)
		else:
			self.icon_label.clear()
			return
		pixmap = icon.pixmap(QSize(56, 56)) 
		self.icon_label.setPixmap(pixmap)

	def apply_style(self):
		text_color = self.current_style_config['text_color']
		
		style_sheet = f"""
			QLabel {{
				color: {text_color};
				font-size: 20px;
				font-weight: 700;
				background-color: transparent;
			}}
		"""
		self.setStyleSheet(style_sheet)

class ItemEditDialog(QDialog):
	def __init__(self, item_id, db, parent=None):
		super().__init__(parent)
		self.setWindowTitle(f"Ürün {item_id} düzenleniyor:")
		self.setStyleSheet("background-color: #111; color: #e9eaf2;")

		details = db.get_item_details(item_id)

		layout = QVBoxLayout()
		self.setLayout(layout)

		self.labelstyle = """
			font-size: 20px;
			font-weight: bold;
			color: #e9eaf2;
		"""

		self.inputstyle = """
			QLineEdit {
				font-size: 20px;
				padding: 6px;
				background-color: #011f26;
				color: #e9eaf2;
				border: 2px solid #e9eaf2;
				border-radius: 12px;
			}
		"""

		input_boxes_layout = QVBoxLayout()
		input_boxes_layout.setAlignment(Qt.AlignTop)

		name_label = QLabel("Ürün Adı:")
		name_label.setStyleSheet(self.labelstyle)
		self.name_edit = QLineEdit()
		self.name_edit.setPlaceholderText("Ürün Adı")
		self.name_edit.setText(details["item_name"])
		self.name_edit.setStyleSheet(self.inputstyle)
		self.name_edit.setMaxLength(32)

		price_label = QLabel("Ürün Fiyatı:")
		price_label.setStyleSheet(self.labelstyle)
		self.price_edit = QLineEdit()
		self.name_edit.setPlaceholderText("Ürün Fiyatı")
		self.price_edit.setText(str(details["item_price"]))
		self.price_edit.setStyleSheet(self.inputstyle)
		self.price_edit.setMaxLength(32)
	
		stock_label = QLabel("Ürün Stoğu:")
		stock_label.setStyleSheet(self.labelstyle)
		self.stock_edit = QLineEdit()
		self.name_edit.setPlaceholderText("Ürün Stoğu")
		self.stock_edit.setText(str(details["item_stock"]))
		self.stock_edit.setStyleSheet(self.inputstyle)
		self.stock_edit.setMaxLength(32)

		warning_box = InfoBoxWidget("Varolan ürünün kodu doğrudan değiştirilemez.", icon_type="information")
		warning_box.setSizePolicy(
			QSizePolicy.Policy.MinimumExpanding,
			QSizePolicy.Policy.Fixed
		)

		buttons_layout = QHBoxLayout()
		buttons_layout.setAlignment(Qt.AlignRight)

		trash_icon = self.style().standardIcon(
			self.style().StandardPixmap.SP_TrashIcon
		)
		icon_size = QSize(28, 28) 

		self.remove_button = QPushButton("")
		self.remove_button.setStyleSheet("""
			QPushButton {
				background-color: #024059;
				color: #e9eaf2;
				font-size: 20px;
				font-weight: bold;
				padding: 6px;
				border-radius: 12px;
				border: 2px solid #e9eaf2;
			}
			QPushButton:hover {
				background-color: #03658c;
			}
		""")
		self.remove_button.setIcon(trash_icon)
		self.remove_button.setIconSize(icon_size)
		self.remove_button.clicked.connect(lambda:{
			db.remove_item(item_id),
			self.accept()
		})
		buttons_layout.addWidget(self.remove_button)

		self.cancel_button = QPushButton("Vazgeç")
		self.cancel_button.setStyleSheet("""
			QPushButton {
				background-color: #024059;
				color: #e9eaf2;
				font-size: 20px;
				font-weight: bold;
				padding: 6px;
				border-radius: 12px;
				border: 2px solid #e9eaf2;
			}
			QPushButton:hover {
				background-color: #03658c;
			}
		""")
		self.cancel_button.clicked.connect(lambda:{
			self.accept()
		})
		buttons_layout.addWidget(self.cancel_button)

		self.complete_button = QPushButton("Tamamla")
		self.complete_button.setStyleSheet("""
			QPushButton {
				background-color: #024059;
				color: #e9eaf2;
				font-size: 20px;
				font-weight: bold;
				padding: 6px;
				border-radius: 12px;
				border: 2px solid #e9eaf2;
			}
			QPushButton:hover {
				background-color: #03658c;
			}
		""")
		self.complete_button.clicked.connect(lambda: (
			(success := db.update_item(
				item_id, 
				self.name_edit.text().strip(),
				self.price_edit.text().strip(),
				self.stock_edit.text().strip()
			)),
			self.accept() if success
			else print("ItemEditDialog: non-float input detected.")
		))
		buttons_layout.addWidget(self.complete_button, stretch=1)

		input_boxes_layout.addWidget(name_label)
		input_boxes_layout.addWidget(self.name_edit)
		input_boxes_layout.addWidget(price_label)
		input_boxes_layout.addWidget(self.price_edit)
		input_boxes_layout.addWidget(stock_label)
		input_boxes_layout.addWidget(self.stock_edit)

		layout.addWidget(warning_box)
		layout.addLayout(input_boxes_layout)
		layout.addLayout(buttons_layout)

		self.name_edit.returnPressed.connect(self.complete_button.click)
		self.price_edit.returnPressed.connect(self.complete_button.click)
		self.stock_edit.returnPressed.connect(self.complete_button.click)

		self.resize(600, 600)
		self.setMinimumSize(600, 600)

		self.setLayout(layout)

class EditStockScreen(QWidget):
	back_to_menu = Signal()

	def __init__(self, appdata, parent=None):
		super().__init__(parent)
		self.app_data = appdata

		main_layout = QVBoxLayout()
		main_layout.setAlignment(Qt.AlignCenter)

		self.title_text = "STOKLAR"
		self.title_style = """
			font-size: 36px;
			font-weight: bold;
			color: #e9eaf2;
		"""
		self.title = QLabel(self.title_text)
		self.title.setStyleSheet(self.title_style)
		self.title.setAlignment(Qt.AlignCenter)
		main_layout.addWidget(self.title)

		self.inputstyle = """
			QLineEdit {
				font-size: 20px;
				padding: 6px;
				background-color: #011f26;
				color: #e9eaf2;
				border: 2px solid #e9eaf2;
				border-radius: 12px;
			}
		"""

		search_boxes_layout = QHBoxLayout()
		search_boxes_layout.setAlignment(Qt.AlignTop)

		self.id_input = QLineEdit()
		self.id_input.setPlaceholderText("Ürün Kodu")
		self.id_input.setStyleSheet(self.inputstyle)
		self.id_input.setMaxLength(32)

		self.name_input = QLineEdit()
		self.name_input.setPlaceholderText("Ürün Adı")
		self.name_input.setStyleSheet(self.inputstyle)
		self.name_input.setMaxLength(32)

		self.price_input = QLineEdit()
		self.price_input.setPlaceholderText("Fiyat")
		self.price_input.setStyleSheet(self.inputstyle)
		self.price_input.setMaxLength(32)
	
		self.stock_input = QLineEdit()
		self.stock_input.setPlaceholderText("Stok")
		self.stock_input.setStyleSheet(self.inputstyle)
		self.stock_input.setMaxLength(32)

		self.add_item_button = QPushButton("Ürün Ekle")
		self.add_item_button.setStyleSheet("""
			QPushButton {
				background-color: #024059;
				color: #e9eaf2;
				font-size: 20px;
				font-weight: bold;
				padding: 6px;
				border-radius: 12px;
				border: 2px solid #e9eaf2;
			}
			QPushButton:hover {
				background-color: #03658c;
			}
		""")

		self.remove_filters_button = QPushButton("X")
		self.remove_filters_button.setStyleSheet("""
			QPushButton {
				background-color: #024059;
				color: #e9eaf2;
				font-size: 20px;
				font-weight: bold;
				padding: 6px;
				border-radius: 12px;
				border: 2px solid #e9eaf2;
			}
			QPushButton:hover {
				background-color: #03658c;
			}
		""")

		search_boxes_layout.addWidget(self.id_input, 3)
		search_boxes_layout.addWidget(self.name_input, 5)
		search_boxes_layout.addWidget(self.price_input, 2)
		search_boxes_layout.addWidget(self.stock_input, 2)
		search_boxes_layout.addWidget(self.add_item_button, 2)
		search_boxes_layout.addWidget(self.remove_filters_button, 1)

		main_layout.addLayout(search_boxes_layout)

		self.id_input.textChanged.connect(self.handle_input_changed)
		self.id_input.returnPressed.connect(self.add_item_button.click)
		self.name_input.textChanged.connect(self.handle_input_changed)
		self.name_input.returnPressed.connect(self.add_item_button.click)
		self.price_input.textChanged.connect(self.handle_input_changed)
		self.price_input.returnPressed.connect(self.add_item_button.click)
		self.stock_input.textChanged.connect(self.handle_input_changed)
		self.stock_input.returnPressed.connect(self.add_item_button.click)

		self.add_item_button.clicked.connect(self.add_item)

		self.remove_filters_button.clicked.connect(lambda:{
			self.id_input.clear(),
			self.name_input.clear(),
			self.price_input.clear(),
			self.stock_input.clear()
		})

		self.scroll_area = QScrollArea()
		self.scroll_area.setWidgetResizable(True)
		self.scroll_area.setStyleSheet("border: none;")
		main_layout.addWidget(self.scroll_area)

		self.items_buttons_container = QVBoxLayout()
		self.items_buttons_container.setAlignment(Qt.AlignTop)
		container_widget = QWidget()
		container_widget.setLayout(self.items_buttons_container)
		self.scroll_area.setWidget(container_widget)

		back_button = QPushButton("Geri")
		back_button.setStyleSheet("""
			QPushButton {
				background-color: #024059;
				color: #e9eaf2;
				font-size: 20px;
				font-weight: bold;
				padding: 8px;
				border-radius: 12px;
				width: 300px;
				height: 40px;
				border: 2px solid #e9eaf2;
			}
			QPushButton:hover {
				background-color: #03658c;
			}
		""")
		back_button.clicked.connect(self.back_to_menu.emit)
		back_button.clicked.connect(lambda:{
			self.id_input.clear(),
			self.name_input.clear(),
			self.price_input.clear(),
			self.stock_input.clear()
		})
		main_layout.addWidget(back_button, alignment=Qt.AlignCenter)
		self.back_button = back_button

		self.setLayout(main_layout)
		self.refresh_stocks()

	def handle_input_changed(self):
		self.refresh_stocks()

	def refresh_stocks(self):
		self._clear_layout(self.items_buttons_container)
		items = self.app_data.database_manager.get_filtered_items(
			self.id_input.text().strip(),
			self.name_input.text().strip(),
			self.price_input.text().strip(),
			self.stock_input.text().strip()
		)
		items.sort(key=lambda x: x["item_id"], reverse=False)
		for row in items:
			self.add_item_row(row, self.items_buttons_container)
		self.items_buttons_container.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

	def	isfloat(self, string):
		try:
			float(string)
			return (True)
		except:
			return (False)

	def	add_item(self):
		if (not self.id_input.text().strip()
			or not self.name_input.text().strip()
			or not self.price_input.text().strip()
			or not self.stock_input.text().strip()):
			self.error_message("ÜRÜN EKLEMEK İÇİN BÜTÜN KUTULARI DOLDURUN!")
		elif (not self.id_input.text().strip().isdigit()
			or not self.isfloat(self.price_input.text().strip())
			or not self.isfloat(self.stock_input.text().strip())):
			self.error_message("ÜRÜN KODU, FİYATI VE STOĞU BİRER POZİTİF SAYI OLMALIDIR!")
		else:
			ret = self.app_data.database_manager.add_new_item(
				self.id_input.text().strip(),
				self.name_input.text().strip(),
				self.price_input.text().strip(),
				self.stock_input.text().strip()
			)
			if ret == True:
				print(f"NEW ITEM: {self.id_input.text().strip()} added. See details:")
				print(f"    name: {self.name_input.text().strip()}")
				print(f"   price: {self.price_input.text().strip()}")
				print(f"   stock: {self.stock_input.text().strip()}")
				#self.id_input.clear()
				#self.name_input.clear()
				#self.price_input.clear()
				#self.stock_input.clear()
				self.refresh_stocks()
				self.id_input.setFocus()
			else:
				self.error_message("ÜRÜN KODLARI BENZERSİZ, SAYILAR POZİTİF OLMALIDIR!")
	def add_item_row(self, row, layout):
		row_widget = QWidget()
		row_widget.setStyleSheet("""
			QWidget {
				background-color: #011f26;
				border-radius: 12px;
				padding: 6px;
			}
		""")	
		row_layout = QHBoxLayout(row_widget)

		item_id = QLabel(str(row["item_id"]))
		item_id.setStyleSheet("""
			color: #e9eaf2;
			font-size: 20px;
			font-weight: 600;
		""")

		item_name = QLabel(row["item_name"])
		item_name.setStyleSheet("""
			color: #e9eaf2;
			font-size: 20px;
			font-weight: 600;
		""")

		item_price = QLabel(str(f"{row["item_price"]:.2f}₺"))
		item_price.setStyleSheet("""
			color: #e9eaf2;
			font-size: 20px;
			font-weight: 600;
		""")

		item_stock = QLabel(str(row["item_stock"]) + " ad.")
		item_stock.setStyleSheet("""
			color: #e9eaf2;
			font-size: 20px;
			font-weight: 600;
		""")

		edit_btn = QPushButton("Düzenle")
		edit_btn.setStyleSheet("""
			QPushButton {
				background-color: #024059;
				color: #e9eaf2;
				font-size: 16px;
				font-weight: bold;
				padding: 6px;
				border-radius: 12px;
				margin-left: 10px;
			}
			QPushButton:hover {
				background-color: #03658c;
			}
		""")

		edit_btn.clicked.connect(lambda: self.edit_item_details(row["item_id"]))

		row_layout.addWidget(item_id, 3)
		row_layout.addWidget(item_name, 5)
		row_layout.addWidget(item_price, 2)
		row_layout.addWidget(item_stock, 2)

		row_layout.addStretch()
		row_layout.addWidget(edit_btn, 3)
		layout.addWidget(row_widget)

	def	edit_item_details(self, id):
		dlg = ItemEditDialog(id, self.app_data.database_manager, self)
		dlg.exec()
		self.refresh_stocks()

	def	error_message(self, msg):
		self.title.setText(msg)
		self.title.setStyleSheet("""
			font-size: 36px;
			font-weight: bold;
			color: #aa5555;
		""")
		QTimer.singleShot(3000, lambda: {
			self.title.setText(self.title_text),
			self.title.setStyleSheet(self.title_style)
		})

	def _clear_layout(self, layout):
		while layout.count():
			item = layout.takeAt(0)
			if item.widget():
				item.widget().deleteLater()
			elif item.layout():
				self._clear_layout(item.layout())