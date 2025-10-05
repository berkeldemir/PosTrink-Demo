from PySide6.QtWidgets import (
	QWidget, QVBoxLayout, QPushButton, QLabel, QHBoxLayout,
	QLineEdit, QMessageBox, QScrollArea, QGridLayout, QSizePolicy
)
from PySide6.QtCore import Qt, Signal, QDateTime, QTimer
from data import AppData

class NewSaleScreen(QWidget):
	continue_sale = Signal()
	back_to_menu = Signal()

	def __init__(self, parent=None):
		super().__init__(parent)
		
		layout = QVBoxLayout()
		layout.setAlignment(Qt.AlignCenter)

		title = QLabel("MÜŞTERİ ADI")
		title.setStyleSheet("""
			font-size: 56px;
			font-weight: bold;
			color: white;
		""")
		title.setAlignment(Qt.AlignCenter)

		self.name_input = QLineEdit()
		self.name_input.setPlaceholderText("")
		self.name_input.setStyleSheet("""
			QLineEdit {
				font-size: 36px;
				padding: 15px;
				background-color: #34495e;
				color: white;
				border: 2px solid white;
				border-radius: 10px;
			}
		""")
		self.name_input.setMaxLength(32)
		self.name_input.setFixedSize(750, 80)

		self.next_button = QPushButton("Devam")
		self.next_button.setStyleSheet("""
			QPushButton {
				background-color: #55cc55;
				color: white;
				font-size: 36px;
				font-weight: bold;
				padding: 20px;
				margin-top: 5px;
				border-radius: 10px;
				height: 60px;
				border: 2px solid white;
			}
		""")

		self.name_input.returnPressed.connect(self.next_button.click)

		self.back_button = QPushButton("Geri")
		self.back_button.setStyleSheet("""
			QPushButton {
				background-color: #2c3e50;
				color: white;
				font-size: 36px;
				font-weight: bold;
				padding: 20px;
				border-radius: 10px;
				height: 60px;
				border: 2px solid white;
			}
			QPushButton:hover {
				background-color: #34495e;
			}
		""")

		layout.addWidget(title)
		layout.addWidget(self.name_input)
		layout.addWidget(self.next_button)
		layout.addWidget(self.back_button)
		
		self.setLayout(layout)
		self.name_input.setFocus()

		self.next_button.clicked.connect(self.continue_sale.emit)
		self.back_button.clicked.connect(self.back_to_menu.emit)
		self.name_input.textChanged.connect(self._to_uppercase)

	def _to_uppercase(self, text):
		cursor_pos = self.name_input.cursorPosition()
		self.name_input.blockSignals(True)
		self.name_input.setText(text.upper())
		self.name_input.blockSignals(False)
		self.name_input.setCursorPosition(cursor_pos)

class CartScreen(QWidget):
	back_to_menu = Signal()
	item_added = Signal()

	def __init__(self, parent=None):
		super().__init__(parent)

		main_layout = QVBoxLayout()

		info_layout = QHBoxLayout()
		info_layout.setAlignment(Qt.AlignTop)

		label_style = """
			font-size: 28px;
			color: white;
			padding: 10px;
			font-weight: bold;
		"""
		self.customer_label = QLabel("Müşteri: -")
		self.customer_label.setStyleSheet(label_style)
		info_layout.addWidget(self.customer_label, 1, Qt.AlignLeft)

		info_layout.addStretch(1)

		self.date_time_label = QLabel("-")
		self.date_time_label.setStyleSheet(label_style)
		info_layout.addWidget(self.date_time_label, 1, Qt.AlignRight)

		self.timer = QTimer(self)
		self.timer.timeout.connect(self.update_date_time)
		self.timer.start(1000)

		content_layout = QHBoxLayout()
	
		products_layout_container = QVBoxLayout()
		self.products_container = QWidget()
		self.products_grid_layout = QGridLayout(self.products_container)
		self.products_scroll_area = QScrollArea()
		self.products_scroll_area.setWidgetResizable(True)
		self.products_scroll_area.setWidget(self.products_container)
		self.products_scroll_area.setStyleSheet("""
			QScrollArea {
				border: 2px solid #111;
				border-radius: 10px;
				text-align: left;
				background-color: #333;
			}
		""")
		products_layout_container.addWidget(self.products_scroll_area)

		cart_layout_container = QVBoxLayout()
		
		self.cart_items_layout = QVBoxLayout()
		self.cart_items_layout.setAlignment(Qt.AlignTop)
		self.cart_scroll_area = QScrollArea()
		self.cart_scroll_area.setWidgetResizable(True)
		cart_items_widget = QWidget()
		cart_items_widget.setLayout(self.cart_items_layout)
		self.cart_scroll_area.setWidget(cart_items_widget)
		self.cart_scroll_area.setStyleSheet("""
			QScrollArea {
				border: 2px solid #111;
				border-radius: 10px;
				background-color: #333;
			}
		""")
		cart_layout_container.addWidget(self.cart_scroll_area)

		buttons_layout = QVBoxLayout()

		base_style = """
			QPushButton {
				color: white;
				font-size: 36px;
				font-weight: bold;
				padding: 20px;
				border-radius: 10px;
				width: 275px;
				height: 60px;
			}
			QPushButton:hover {
				border: 5px solid #999;
			}
		"""

		self.back_button = QPushButton("Askıya Al")
		self.back_button.setStyleSheet(base_style + """
			QPushButton {
				background-color: #b0ac5a;
				border: 2px solid white;
			}
		""")

		self.cancel_button = QPushButton("İptal")
		self.cancel_button.setStyleSheet(base_style + """
			QPushButton {
				background-color: #b0675a;
				border: 2px solid white;
			}
		""")

		self.payment_button = QPushButton("Ödeme")
		self.payment_button.setStyleSheet(base_style + """
			QPushButton {
				background-color: #cccccc;
				border: 2px solid white;
			}
		""")

		self.back_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
		buttons_layout.addWidget(self.back_button, alignment=Qt.AlignCenter)
		self.cancel_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
		buttons_layout.addWidget(self.cancel_button, alignment=Qt.AlignCenter)
		self.payment_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
		buttons_layout.addWidget(self.payment_button, alignment=Qt.AlignCenter)

		buttons_layout.addStretch(1)

		content_layout.addLayout(products_layout_container, 4)
		content_layout.addLayout(cart_layout_container, 4)
		content_layout.addLayout(buttons_layout, 2)

		main_layout.addLayout(info_layout)
		main_layout.addLayout(content_layout, 1)
		self.setLayout(main_layout)

	def update_date_time(self):
		current_datetime = QDateTime.currentDateTime()
		formatted_datetime = current_datetime.toString("dd.mm.yyyy | hh:mm:ss")
		self.date_time_label.setText(f"{formatted_datetime}")

	def refresh_data(self, app_data: AppData):
		self.customer_label.setText(f"Müşteri: {app_data.curr_customer_name}")
		self.update_date_time()
		self.load_products(app_data)
		self.refresh_cart_items(app_data)

	def wrap_text(self, text, max_chars=15):
		words = text.split(' ')
		lines = []
		current_line = ''
		for word in words:
			if len(current_line + ' ' + word) > max_chars:
				lines.append(current_line)
				current_line = word
			else:
				if current_line:
					current_line += ' ' + word
				else:
					current_line = word
		lines.append(current_line)
		return '\n'.join(lines)
		
	def load_products(self, app_data: AppData):
		for i in reversed(range(self.products_grid_layout.count())):
			widget_to_remove = self.products_grid_layout.itemAt(i).widget()
			if widget_to_remove is not None:
				widget_to_remove.setParent(None)

		products = app_data.database_manager.get_available_products()
		row = 0
		col = 0
		for product in products:
			product_dict = dict(product)
			item_name = product_dict.get('item_name', 'Bilinmeyen Ürün')

			wrapped_name = self.wrap_text(item_name, 15)
			item_button = QPushButton(wrapped_name)
			item_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
			item_button.setStyleSheet("""
				QPushButton {
					background-color: #2c3e50;
					color: white;
					font-size: 32px;
					font-weight: bold;
					border: 2px solid #555;
					border-radius: 10px;
				}
				QPushButton:hover {
					background-color: #34495e;
				}
			""")
			item_button.clicked.connect(lambda _, id=product['item_id'], ad=app_data: self.handle_product_click(id, ad))
			self.products_grid_layout.addWidget(item_button, row, col)
			col += 1
			if col > 1:
				col = 0
				row += 1

	def handle_product_click(self, item_id, app_data:AppData):
		if app_data.database_manager.add_item_to_cart(app_data.curr_sale_id, item_id, 1, 0, 0):
			self.refresh_cart_items(app_data)
			self.item_added.emit()
		else:
			print("ERROR   : Item is out of stocks.")

	def refresh_cart_items(self, app_data: AppData):
		while self.cart_items_layout.count():
			child = self.cart_items_layout.takeAt(0)
			if child.widget():
				child.widget().deleteLater()
		cart_items = app_data.database_manager.get_cart_items(app_data.curr_sale_id)
		
		row_container_style = """
			QWidget {
				background-color: #2c3e50;
				margin: 0px 0px 0px 0px;
				color: white;
				border: .3px solid white;
				border-radius: 5px;
				margin-bottom: 5px;
			}
		"""
		row_label_style = """
			font-size: 28px;
			font-weight: bold;
		"""
		for i, item in enumerate(cart_items):
			if (item['item_discount_num'] == 0):
				self.price_label = f"{item['item_total']:.2f} TL"
				special_color = ""
			else:
				self.price_label = f"{self.strikethrough(f"{item['item_total'] + item['item_discount_num']:.2f} TL")}\n {item['item_total']:.2f} TL"
				special_color = "QWidget{background-color: #2c503e;}"
			
			item_price_lbl = QLabel(self.price_label)
			item_row_widget = QWidget()
			item_row_widget.setStyleSheet(row_container_style + special_color)
			item_row_layout = QHBoxLayout(item_row_widget)
			item_row_layout.setContentsMargins(5, 5, 5, 5)

			item_number_lbl = QLabel(f"{item['item_count']}")
			item_number_lbl.setStyleSheet(row_label_style + "min-width: 16 px;")
			item_number_lbl.setAlignment(Qt.AlignLeft)

			item_name_lbl = QLabel(f"{item['item_name']}")
			item_name_lbl.setStyleSheet(row_label_style + "min-width: 64px;")
			item_name_lbl.setAlignment(Qt.AlignLeft)

			item_price_lbl.setStyleSheet(row_label_style + "min-width: 36px;")
			item_price_lbl.setAlignment(Qt.AlignRight)

			item_row_layout.addWidget(item_number_lbl)
			item_row_layout.addSpacing(2)
			item_row_layout.addWidget(item_name_lbl, 1)
			item_row_layout.addWidget(item_price_lbl)

			self.cart_items_layout.addWidget(item_row_widget)

		total_discount = app_data.database_manager.total_discount_num(app_data.curr_sale_id)
		total_amount = app_data.database_manager.total_amount_calculator(app_data.curr_sale_id)

		subtotal_row = QWidget()
		subtotal_row.setStyleSheet(row_container_style + "QWidget{background-color: #50503e;}")
		subtotal_layout = QHBoxLayout(subtotal_row)
		subtotal_layout.setContentsMargins(5, 5, 5, 5)

		subtotal_label = QLabel("ARA TOPLAM:")
		subtotal_label.setStyleSheet(row_label_style)
		subtotal_layout.addWidget(subtotal_label, 1)

		subtotal_price = QLabel(f"{total_amount + total_discount:.2f} TL")
		subtotal_price.setStyleSheet(row_label_style)
		subtotal_layout.addWidget(subtotal_price)

		self.cart_items_layout.addWidget(subtotal_row)

		disc_row = QWidget()
		disc_row.setStyleSheet(row_container_style + "QWidget{background-color: #50503e;}")
		disc_layout = QHBoxLayout(disc_row)
		disc_layout.setContentsMargins(5, 5, 5, 5)

		disc_label = QLabel("TOPLAM İNDİRİM:")
		disc_label.setStyleSheet(row_label_style)
		disc_layout.addWidget(disc_label, 1)

		disc_price = QLabel(f"{total_discount:.2f} TL")
		disc_price.setStyleSheet(row_label_style)
		disc_layout.addWidget(disc_price)

		self.cart_items_layout.addWidget(disc_row)

		total_row = QWidget()
		total_row.setStyleSheet(row_container_style + "QWidget{background-color: #50503e;}")
		total_layout = QHBoxLayout(total_row)
		total_layout.setContentsMargins(5, 5, 5, 5)

		total_label = QLabel("TOTAL:")
		total_label.setStyleSheet(row_label_style)
		total_layout.addWidget(total_label, 1)

		total_price = QLabel(f"{total_amount:.2f} TL")
		total_price.setStyleSheet(row_label_style)
		total_layout.addWidget(total_price)

		self.cart_items_layout.addWidget(total_row)
	
	def strikethrough(self, text):
		return "".join(c + '\u0336' for c in text)

class CustomerCartScreen(QWidget):
	def __init__(self, app_data: AppData):
		super().__init__()

		self.app_data = app_data

		layout = QVBoxLayout()

		info_layout = QHBoxLayout()
		info_layout.setAlignment(Qt.AlignTop)

		self.customer_label = QLabel("Hoş geldiniz, ")
		self.date_time_label = QLabel("-")

		label_style = """
			font-size: 28px;
			color: white;
			padding: 10px;
			font-weight: bold;
		"""
		self.customer_label.setStyleSheet(label_style)
		self.date_time_label.setStyleSheet(label_style)

		info_layout.addWidget(self.customer_label, 1, Qt.AlignLeft)
		info_layout.addStretch(1)
		info_layout.addWidget(self.date_time_label, 1, Qt.AlignRight)

		layout.addLayout(info_layout)

		cart_layout_container = QVBoxLayout()

		self.cart_items_layout = QVBoxLayout()
		self.cart_items_layout.setAlignment(Qt.AlignTop)
		self.cart_scroll_area = QScrollArea()
		self.cart_scroll_area.setWidgetResizable(True)
		cart_items_widget = QWidget()
		cart_items_widget.setLayout(self.cart_items_layout)
		self.cart_scroll_area.setWidget(cart_items_widget)
		self.cart_scroll_area.setStyleSheet("""
			QScrollArea {
				border: 2px solid #111;
				border-radius: 10px;
				background-color: #333;
			}
		""")
		cart_layout_container.addWidget(self.cart_scroll_area)

		layout.addWidget(self.cart_scroll_area)

		self.setLayout(layout)

		self.timer = QTimer(self)
		self.timer.timeout.connect(self.update_date_time)
		self.timer.start(1000)

		self.refresh_data(app_data)

	def update_date_time(self):
		current_datetime = QDateTime.currentDateTime()
		formatted_datetime = current_datetime.toString("dd.mm.yyyy | hh:mm:ss")
		self.date_time_label.setText(formatted_datetime)

	def strikethrough(self, text):
		return "".join(c + '\u0336' for c in text)

	def refresh_data(self, app_data: AppData):
		self.customer_label.setText(f"Hoş geldiniz, {app_data.curr_customer_name}")
		self.update_date_time()
		self.refresh_cart_items(app_data)

	def refresh_cart_items(self, app_data: AppData):
		while self.cart_items_layout.count():
			child = self.cart_items_layout.takeAt(0)
			if child.widget():
				child.widget().deleteLater()
		cart_items = app_data.database_manager.get_cart_items(app_data.curr_sale_id)
		
		row_container_style = """
			QWidget {
				background-color: #2c3e50;
				margin: 0px 0px 0px 0px;
				color: white;
				border: .3px solid white;
				border-radius: 5px;
				margin-bottom: 5px;
			}
		"""
		row_label_style = """
			font-size: 36px;
			font-weight: bold;
		"""
		for i, item in enumerate(cart_items):
			if (item['item_discount_num'] == 0):
				self.price_label = f"{item['item_total']:.2f} TL"
				special_color = ""
			else:
				self.price_label = f"{self.strikethrough(f"{item['item_total'] + item['item_discount_num']:.2f} TL")}\n {item['item_total']:.2f} TL"
				special_color = "QWidget{background-color: #2c503e;}"
			
			item_price_lbl = QLabel(self.price_label)
			item_row_widget = QWidget()
			item_row_widget.setStyleSheet(row_container_style + special_color)
			item_row_layout = QHBoxLayout(item_row_widget)
			item_row_layout.setContentsMargins(5, 5, 5, 5)

			item_number_lbl = QLabel(f"{item['item_count']}")
			item_number_lbl.setStyleSheet(row_label_style + "min-width: 16 px;")
			item_number_lbl.setAlignment(Qt.AlignLeft)

			item_name_lbl = QLabel(f"{item['item_name']}")
			item_name_lbl.setStyleSheet(row_label_style + "min-width: 64px;")
			item_name_lbl.setAlignment(Qt.AlignLeft)

			item_price_lbl.setStyleSheet(row_label_style + "min-width: 36px;")
			item_price_lbl.setAlignment(Qt.AlignRight)

			item_row_layout.addWidget(item_number_lbl)
			item_row_layout.addSpacing(2)
			item_row_layout.addWidget(item_name_lbl, 1)
			item_row_layout.addWidget(item_price_lbl)

			self.cart_items_layout.addWidget(item_row_widget)

		total_discount = app_data.database_manager.total_discount_num(app_data.curr_sale_id)
		total_amount = app_data.database_manager.total_amount_calculator(app_data.curr_sale_id)

		subtotal_row = QWidget()
		subtotal_row.setStyleSheet(row_container_style + "QWidget{background-color: #50503e;}")
		subtotal_layout = QHBoxLayout(subtotal_row)
		subtotal_layout.setContentsMargins(5, 5, 5, 5)

		subtotal_label = QLabel("ARA TOPLAM:")
		subtotal_label.setStyleSheet(row_label_style)
		subtotal_layout.addWidget(subtotal_label, 1)

		subtotal_price = QLabel(f"{total_amount + total_discount:.2f} TL")
		subtotal_price.setStyleSheet(row_label_style)
		subtotal_layout.addWidget(subtotal_price)

		self.cart_items_layout.addWidget(subtotal_row)

		disc_row = QWidget()
		disc_row.setStyleSheet(row_container_style + "QWidget{background-color: #50503e;}")
		disc_layout = QHBoxLayout(disc_row)
		disc_layout.setContentsMargins(5, 5, 5, 5)

		disc_label = QLabel("TOPLAM İNDİRİM:")
		disc_label.setStyleSheet(row_label_style)
		disc_layout.addWidget(disc_label, 1)

		disc_price = QLabel(f"{total_discount:.2f} TL")
		disc_price.setStyleSheet(row_label_style)
		disc_layout.addWidget(disc_price)

		self.cart_items_layout.addWidget(disc_row)

		total_row = QWidget()
		total_row.setStyleSheet(row_container_style + "QWidget{background-color: #50503e;}")
		total_layout = QHBoxLayout(total_row)
		total_layout.setContentsMargins(5, 5, 5, 5)

		total_label = QLabel("TOTAL:")
		total_label.setStyleSheet(row_label_style)
		total_layout.addWidget(total_label, 1)

		total_price = QLabel(f"{total_amount:.2f} TL")
		total_price.setStyleSheet(row_label_style)
		total_layout.addWidget(total_price)

		self.cart_items_layout.addWidget(total_row)