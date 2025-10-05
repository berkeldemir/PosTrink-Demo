from PySide6.QtWidgets import (
	QWidget, QVBoxLayout, QPushButton,
	QLabel, QScrollArea, QFrame, QSpacerItem, QSizePolicy,
	QHBoxLayout
)
from PySide6.QtCore import Qt, Signal
from data import AppData

class OnHoldOrdersScreen(QWidget):
	back_to_menu = Signal()
	continue_sale = Signal(str)

	def __init__(self, app_data, parent=None):
		super().__init__(parent)
		self.app_data = app_data

		main_layout = QVBoxLayout()
		main_layout.setAlignment(Qt.AlignCenter)

		title = QLabel("ASKIDA BEKLEYEN İŞLEMLER")
		title.setStyleSheet("""
			font-size: 56px;
			font-weight: bold;
			color: white;
		""")
		title.setAlignment(Qt.AlignCenter)
		main_layout.addWidget(title)

		self.scroll_area = QScrollArea()
		self.scroll_area.setWidgetResizable(True)
		self.scroll_area.setStyleSheet("border: none;")
		main_layout.addWidget(self.scroll_area, 1)

		self.sales_buttons_container = QVBoxLayout()
		self.sales_buttons_container.setAlignment(Qt.AlignTop)
		container_widget = QWidget()
		container_widget.setLayout(self.sales_buttons_container)
		self.scroll_area.setWidget(container_widget)

		back_button = QPushButton("Geri")
		back_button.setStyleSheet("""
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
		back_button.clicked.connect(self.back_to_menu.emit)
		main_layout.addWidget(back_button, alignment=Qt.AlignCenter)
		self.back_button = back_button

		self.setLayout(main_layout)
		self.refresh_onhold_sales()

	def format_datetime(self, dt_string):
		date_part, time_part = dt_string.split('T')
		year, month, day = date_part.split('-')
		hours, minutes, seconds_with_microseconds = time_part.split(':')
		seconds = seconds_with_microseconds.split('.')[0]
		return f"{day}/{month}/{year} | {hours}:{minutes}:{seconds}"

	def refresh_onhold_sales(self):
		self._clear_layout(self.sales_buttons_container)
		onhold_sales = self.app_data.database_manager.get_onhold_sales()
		onhold_sales.sort(key=lambda x: x["sale_date"], reverse=True)
		for row in onhold_sales:
			self.add_sale_row(row, self.sales_buttons_container)
		self.sales_buttons_container.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

	def add_sale_row(self, row, layout):
		sale_id = row["sale_id"]
		sale_date = self.format_datetime(row["sale_date"])
		customer_name = row["customer_name"]
		total_amount = row["total_amount"]
		
		row_widget = QWidget()
		row_widget.setStyleSheet("""
			QWidget {
				background-color: #34495e;
				border-radius: 10px;
				padding: 15px;
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
		""")
		customer_label.setAlignment(Qt.AlignLeft)

		total_label = QLabel(f"{total_amount:.2f} ₺")
		total_label.setStyleSheet("""
			color: white;
			font-size: 28px;
			font-weight: 600;
		""")
		total_label.setAlignment(Qt.AlignRight)

		btn = QPushButton("Askıdan Çağır")
		btn.setStyleSheet("""
			QPushButton {
				background-color: #27ae60;
				color: white;
				font-size: 24px;
				font-weight: bold;
				padding: 8px 12px;
				border-radius: 8px;
				margin-left: 10px;
			}
			QPushButton:hover {
				background-color: #2ecc71;
			}
		""")
		btn.setFixedSize(250, 50)
		btn.clicked.connect(lambda checked, s=sale_id: self.load_sale(s))

		row_layout.addWidget(date_label, 1)
		row_layout.addWidget(customer_label, 2)
		row_layout.addWidget(total_label, 1)

		row_layout.addStretch()
		row_layout.addWidget(btn)
		
		layout.addWidget(row_widget)
		
	def _clear_layout(self, layout):
		while layout.count():
			item = layout.takeAt(0)
			if item.widget():
				item.widget().deleteLater()
			elif item.layout():
				self._clear_layout(item.layout())

	def load_sale(self, sale_id):
		self.app_data.curr_sale_id = sale_id

		cur = self.app_data.database_manager.conn.cursor()
		cur.execute("SELECT customer_name FROM sales WHERE sale_id = ?", (sale_id,))
		row = cur.fetchone()
		if row:
			self.app_data.curr_customer_name = row["customer_name"]

		print(f"OLD SALE: {sale_id} for {self.app_data.curr_customer_name}")
		self.continue_sale.emit(sale_id)
