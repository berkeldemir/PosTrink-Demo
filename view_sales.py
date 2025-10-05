from PySide6.QtWidgets import (
	QWidget, QVBoxLayout, QPushButton, QLabel,
	QScrollArea, QDialog, QTableWidget, QTableWidgetItem, QHeaderView,
	QHBoxLayout, QSpacerItem, QSizePolicy, QLineEdit
)
from PySide6.QtCore import Qt, Signal
from data import AppData

class SaleDetailsDialog(QDialog):
	def __init__(self, sale_id, db, parent=None):
		super().__init__(parent)
		self.setWindowTitle(f"Satış {sale_id} Detayları")
		self.setStyleSheet("""
			background-color: #2c3e50;
			color: white;
		""")
		layout = QVBoxLayout()
		self.setLayout(layout)

		try:
			cursor = db.conn.cursor()
			cursor.execute("""
				SELECT ci.item_count, i.item_name, ci.item_total, s.payment_method, s.payment_info, s.customer_name
				FROM items AS i
				JOIN cart_items AS ci ON i.item_id = ci.item_id
				JOIN sales AS s ON ci.sale_id = s.sale_id
				WHERE ci.sale_id = ?
			""", (sale_id,))
			rows = cursor.fetchall()
			rows = [dict(r) for r in rows] if rows else []
		except Exception as e:
			print(f"ERROR   : SaleDetailsDialog: {e}")
			rows = []

		if not rows:
			label = QLabel("Satışta ürün bulunamadı.")
			label.setAlignment(Qt.AlignCenter)
			layout.addWidget(label)
			return

		table = QTableWidget(len(rows) + 1, 3)
		table.setHorizontalHeaderLabels(["Adet", "Ürün Adı", "Tutar"])
		table.setStyleSheet("""
			QTableWidget {
				background-color: #34495e;
				color: white;
				font-size: 28px;
			}
			QHeaderView::section {
				background-color: #1abc9c;
				color: white;
				font-weight: bold;
				font-size: 28px;
			}
		""")
		table.verticalHeader().setVisible(False)

		total_sum = 0
		for i, r in enumerate(rows):
			item_count = QTableWidgetItem(str(r['item_count']))
			item_count.setTextAlignment(Qt.AlignCenter)
			table.setItem(i, 0, item_count)

			table.setItem(i, 1, QTableWidgetItem(r['item_name']))

			item_total = QTableWidgetItem(f"{r['item_total']:.2f}₺")
			item_total.setTextAlignment(Qt.AlignCenter)
			table.setItem(i, 2, item_total)

			total_sum += r['item_total']

		table.setItem(len(rows), 0, QTableWidgetItem(""))
		total_label = QTableWidgetItem("TOTAL")
		total_label.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
		table.setItem(len(rows), 1, total_label)
		total_amount_item = QTableWidgetItem(f"{total_sum:.2f}₺")
		total_amount_item.setTextAlignment(Qt.AlignCenter)
		table.setItem(len(rows), 2, total_amount_item)

		table.resizeColumnsToContents()
		table.resizeRowsToContents()
		table.setEditTriggers(QTableWidget.NoEditTriggers)
		table.setSelectionMode(QTableWidget.NoSelection)

		table.horizontalHeader().setStretchLastSection(True)
		table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
		table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
		table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)

		table.verticalHeader().setDefaultSectionSize(42)
		layout.addWidget(table)

		payment_detail = r["payment_info"]
		if (not payment_detail):
			payment_detail = "-"
		payment_infos = f"MÜŞTERİ ADI:\t\t{r["customer_name"]}\nÖDEME YÖNTEMİ:\t{r["payment_method"]}\nÖDEME DETAYI:\t\t{payment_detail}\n"
		payment_infos_label = QLabel(payment_infos)
		payment_infos_label.setStyleSheet("""
			font-size: 24px;
			font-weight: medium;
			color: white;
		""")
		layout.addWidget(payment_infos_label)

		self.resize(800, 600)
		self.setMinimumSize(800, 600)

class SalesScreen(QWidget):
	back_to_menu = Signal()
	edit_sale_requested = Signal(str)

	def __init__(self, appdata, parent=None):
		super().__init__(parent)
		self.app_data = appdata

		main_layout = QVBoxLayout()

		self.title_text = "SATIŞLAR"
		self.title_style = """
			font-size: 56px;
			font-weight: bold;
			color: white;
		"""
		self.title = QLabel(self.title_text)
		self.title.setStyleSheet(self.title_style)
		self.title.setAlignment(Qt.AlignCenter)
		main_layout.addWidget(self.title)

		self.inputstyle = """
			QLineEdit {
				font-size: 28px;
				padding: 15px;
				background-color: #34495e;
				color: white;
				border: 2px solid white;
				border-radius: 10px;
			}
		"""

		search_boxes_layout = QHBoxLayout()
		search_boxes_layout.setAlignment(Qt.AlignTop)

		self.date_input = QLineEdit()
		self.date_input.setPlaceholderText("YYYY-AA-GGTSS:DD:SS")
		self.date_input.setStyleSheet(self.inputstyle)
		self.date_input.setMaxLength(32)

		self.name_input = QLineEdit()
		self.name_input.setPlaceholderText("Müşteri Adı")
		self.name_input.setStyleSheet(self.inputstyle)
		self.name_input.setMaxLength(32)

		self.remove_filters_button = QPushButton("X")
		self.remove_filters_button.setStyleSheet("""
			QPushButton {
				background-color: #2c3e50;
				color: white;
				font-size: 28px;
				font-weight: bold;
				padding: 15px;
				border-radius: 10px;
				border: 2px solid white;
			}
			QPushButton:hover {
				background-color: #34495e;
			}
		""")

		search_boxes_layout.addWidget(self.date_input, 2)
		search_boxes_layout.addWidget(self.name_input, 5)
		search_boxes_layout.addWidget(self.remove_filters_button, 1)

		main_layout.addLayout(search_boxes_layout)

		self.date_input.textChanged.connect(self.refresh_view_sales)
		self.name_input.textChanged.connect(self.refresh_view_sales)

		self.sales_buttons_layout = QVBoxLayout()
		self.sales_buttons_layout.setAlignment(Qt.AlignTop)

		scroll_content = QWidget()
		scroll_content.setLayout(self.sales_buttons_layout)

		scroll = QScrollArea()
		scroll.setWidgetResizable(True)
		scroll.setWidget(scroll_content)
		main_layout.addWidget(scroll, stretch=1)

		self.back_button = QPushButton("Geri")
		self.back_button.setStyleSheet("""
			QPushButton {
				background-color: #2c3e50;
				color: white;
				font-size: 48px;
				font-weight: bold;
				padding: 20px;
				border-radius: 10px;
				width: 450px;
				height: 80px;
				border: 2px solid white;
			}
			QPushButton:hover {
				background-color: #34495e;
			}
		""")
		main_layout.addWidget(self.back_button, alignment=Qt.AlignCenter)

		self.setLayout(main_layout)
		self.refresh_view_sales()
		self.back_button.clicked.connect(self.back_to_menu.emit)

	def format_datetime(self, dt_string):
		date_part, time_part = dt_string.split('T')
		year, month, day = date_part.split('-')
		hours, minutes, seconds_with_microseconds = time_part.split(':')
		seconds = seconds_with_microseconds.split('.')[0]
		return f"{day}/{month}/{year} | {hours}:{minutes}:{seconds}"
	
	def load_sales(self):
		while self.sales_buttons_layout.count():
			child = self.sales_buttons_layout.takeAt(0)
			if child.widget():
				child.widget().deleteLater()
		sales = self.app_data.database_manager.get_filtered_sales(
			self.date_input.text().strip(),
			self.name_input.text().strip()
		)
		if not sales:
			no_sales = QLabel("Satış Bulunamadı!")
			no_sales.setStyleSheet("""
				font-size: 28px;
				color: #ccc;
			""")
			no_sales.setAlignment(Qt.AlignCenter)
			self.sales_buttons_layout.addWidget(no_sales)
			return
		for sale in sales:
			self.add_sale_row(sale, self.sales_buttons_layout)

	def add_sale_row(self, sale, layout):
		sale_id = sale.get("sale_id")
		sale_date = self.format_datetime(sale.get("sale_date"))
		customer_name = sale.get("customer_name", "Müşteri")
		total_amount = sale.get("total_amount", 0)
		payment_method = sale.get("payment_method")

		row_widget = QWidget()
		row_widget.setStyleSheet("""
			QWidget {
				background-color: #34495e;
				border-radius: 10px;
				padding: 15px;
				margin: 5px;
			}
		""")
		row_layout = QHBoxLayout(row_widget)

		date_label = QLabel(sale_date)
		date_label.setStyleSheet("""
			color: white;
			font-size: 28px;
			font-weight: 600;
		""")
		date_label.setAlignment(Qt.AlignLeft)

		customer_label = QLabel(customer_name)
		customer_label.setStyleSheet("""
			color: white;
			font-size: 28px;
			font-weight: 600;
			margin-right: 20px;
		""")
		customer_label.setAlignment(Qt.AlignLeft)

		total_label = QLabel(f"{total_amount:.2f} ₺")
		total_label.setStyleSheet("""
			color: white;
			font-size: 28px;
			font-weight: 600;
		""")
		total_label.setAlignment(Qt.AlignRight)

		onhold_label = QLabel("İŞLEM ASKIDA")
		onhold_label.setStyleSheet("""
			color: #bc9c1a;
			font-size: 28px;
			font-weight: 800;
		""")

		view_btn = QPushButton("Detay")
		view_btn.setStyleSheet("""
			QPushButton {
				background-color: #1abc9c;
				color: white;
				font-size: 24px;
				font-weight: 800;
				padding: 8px 12px;
				border-radius: 12px;
			}
			QPushButton:hover {
				background-color: #16a085;
			}
		""")
		view_btn.clicked.connect(lambda checked, sid=sale_id: self.show_sale_details(sid))

		edit_btn = QPushButton("Düzenle")
		edit_btn.setStyleSheet("""
			QPushButton {
				background-color: #27ae60;
				color: white;
				font-size: 24px;
				font-weight: 800;
				padding: 8px 12px;
				border-radius: 12px;
			}
			QPushButton:hover {
				background-color: #2ecc71;
			}
		""")
		edit_btn.clicked.connect(lambda checked, sid=sale_id: self.edit_sale_requested.emit(sid))

		row_layout.addWidget(date_label, 3)
		row_layout.addWidget(customer_label, 5)

		row_layout.addStretch()

		row_layout.addWidget(total_label, 3)

		if (payment_method == 'WIP'):
			row_layout.addWidget(onhold_label, 2)
		else:
			row_layout.addWidget(view_btn, 1)
			row_layout.addWidget(edit_btn, 1)

		layout.addWidget(row_widget)

	def show_sale_details(self, sale_id):
		dlg = SaleDetailsDialog(sale_id, self.app_data.database_manager, self)
		dlg.exec()

	def refresh_view_sales(self):
		self._clear_layout(self.sales_buttons_layout)
		self.load_sales()
		self.sales_buttons_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

	def _clear_layout(self, layout):
		while layout.count():
			item = layout.takeAt(0)
			if item.widget():
				item.widget().deleteLater()
			elif item.layout():
				self._clear_layout(item.layout())

class WelcomeScreen(QWidget):
	def __init__(self):
		super().__init__()
		layout = QVBoxLayout()
		label = QLabel("Hoş geldiniz!")
		label.setAlignment(Qt.AlignCenter)
		label.setStyleSheet("""
			font-size: 72px;
			font-weight: bold;
			color: #999;
		""")
		layout.addWidget(label)
		self.setLayout(layout)
