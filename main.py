import sys
import os
import random 
import time
from PySide6.QtWidgets import (
	QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton,
	QLabel, QHBoxLayout, QStackedWidget, QLineEdit, QMessageBox,
	QInputDialog, QDialog
)
from PySide6.QtCore import Qt, Signal as pyqtSignal

from data import AppData, DatabaseManager
from new_sale import NewSaleScreen, CartScreen, CustomerCartScreen
from view_sales import SalesScreen, WelcomeScreen
from edit_stock import EditStockScreen
from onhold_orders import OnHoldOrdersScreen

class PaymentDialog(QDialog):
	cash_selected = pyqtSignal()
	iban_selected = pyqtSignal()

	def __init__(self, parent=None):
		super().__init__(parent)
		self.setWindowTitle("Ödeme Yöntemi Seçin")
		self.setGeometry(0, 0, 400, 200)
		self.setStyleSheet("background-color: #333; color: white;")

		layout = QVBoxLayout()
		self.setLayout(layout)

		cash_button = QPushButton("Nakit")
		cash_button.setStyleSheet("""
			QPushButton {
				color: white;
				font-size: 48px;
				font-weight: bold;
				padding: 20px;
				border-radius: 10px;
				width: 275px;
				height: 60px;
				background-color: #5ab05b;
				border: 2px solid white;
			}
			QPushButton:hover {
				border: 5px solid #999;
			}
		""")
		cash_button.clicked.connect(self.accept_cash)
		layout.addWidget(cash_button)

		iban_button = QPushButton("IBAN")
		iban_button.setStyleSheet("""
			QPushButton {
				color: white;
				font-size: 48px;
				font-weight: bold;
				padding: 20px;
				border-radius: 10px;
				width: 250px;
				height: 60px;
				background-color: #5aacb0;
				border: 2px solid white;
			}
			QPushButton:hover {
				border: 5px solid #999;
			}
		""")
		iban_button.clicked.connect(self.accept_iban)
		layout.addWidget(iban_button)

		cancel_button = QPushButton("İptal")
		cancel_button.setStyleSheet("""
			QPushButton {
				color: white;
				font-size: 48px;
				font-weight: bold;
				padding: 20px;
				border-radius: 10px;
				width: 250px;
				height: 60px;
				background-color: #b0675a;
				border: 2px solid white;
			}
			QPushButton:hover {
				border: 5px solid #999;
			}
		""")
		cancel_button.clicked.connect(self.accept_cancel)
		layout.addWidget(cancel_button)
	
	def accept_cancel(self):
		self.accept()

	def accept_cash(self):
		self.cash_selected.emit()
		self.accept()

	def accept_iban(self):
		self.iban_selected.emit()
		self.accept()

class Window1(QMainWindow):
	def __init__(self, controller, second_window):
		super().__init__()
		self.setWindowTitle("BETA - Main Window")
		self.controller = controller
		self.second_window = second_window

		self.stacked_widget = QStackedWidget()
		self.setCentralWidget(self.stacked_widget)

		self.setStyleSheet("""
			QMainWindow {
				background-color: #111;
			}
			QWidget {
				background-color: #111;
			}
		""")

		self.main_menu_widget = self._create_main_menu()
		self.stacked_widget.addWidget(self.main_menu_widget)
		
		self.new_sale_screen = NewSaleScreen()
		self.stacked_widget.addWidget(self.new_sale_screen)
		
		self.sales_screen = SalesScreen(controller)
		self.stacked_widget.addWidget(self.sales_screen)
		
		self.cart_screen = CartScreen()
		self.stacked_widget.addWidget(self.cart_screen)

		self.edit_stock_screen = EditStockScreen(controller)
		self.stacked_widget.addWidget(self.edit_stock_screen)

		self.onhold_screen = OnHoldOrdersScreen(controller)
		self.stacked_widget.addWidget(self.onhold_screen)
		
		self.new_sale_button.clicked.connect(lambda: {
			self.stacked_widget.setCurrentIndex(1),
			self.new_sale_screen.name_input.setFocus()
		})
		self.sales_button.clicked.connect(lambda: [
			self.sales_screen.refresh_view_sales(),
			self.stacked_widget.setCurrentIndex(2)
		])
		self.stock_button.clicked.connect(lambda: {
			self.stacked_widget.setCurrentIndex(4),
			self.edit_stock_screen.refresh_stocks(),
			self.edit_stock_screen.id_input.setFocus()
		})
		self.onhold_button.clicked.connect(lambda: [
			self.onhold_screen.refresh_onhold_sales(),
			self.stacked_widget.setCurrentIndex(5)
		])
		self.quit_button.clicked.connect(QApplication.instance().quit)

		self.new_sale_screen.back_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
		self.new_sale_screen.next_button.clicked.connect(self.start_sale_and_show_cart)

		self.sales_screen.edit_sale_requested.connect(self.continue_sale)
		self.sales_screen.back_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))

		self.onhold_screen.back_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
		self.onhold_screen.continue_sale.connect(self.continue_sale)

		self.edit_stock_screen.back_to_menu.connect(lambda: self.stacked_widget.setCurrentIndex(0))

		self.cart_screen.back_button.clicked.connect(lambda: self.handle_put_on_onhold())
		self.cart_screen.cancel_button.clicked.connect(self.handle_cancel)
		self.cart_screen.item_added.connect(self.second_window.show_cart)
		self.cart_screen.payment_button.clicked.connect(self.handle_payment)

		self.showFullScreen()

	def	handle_put_on_onhold(self):
		if self.controller.curr_sale_id:
			self.controller.database_manager.update_sale_payment_info(self.controller.curr_sale_id, "WIP")
			self.controller.database_manager.update_sale_date(self.controller.curr_sale_id)
			self.stacked_widget.setCurrentIndex(0)
			self.second_window.show_welcome()

	def handle_cash_payment(self):
		if self.controller.curr_sale_id:
			self.controller.database_manager.update_sale_payment_info(self.controller.curr_sale_id, "Nakit")
			self.controller.database_manager.update_sale_date(self.controller.curr_sale_id)
			self.stacked_widget.setCurrentIndex(0)
			self.second_window.show_welcome()

	def handle_iban_payment(self):
		if self.controller.curr_sale_id:
			sender_name, ok = QInputDialog.getText(self, "IBAN Bilgisi", "Gönderici Adı:")
			if ok and sender_name:
				self.controller.database_manager.update_sale_payment_info(self.controller.curr_sale_id, "IBAN", sender_name)
				self.controller.database_manager.update_sale_date(self.controller.curr_sale_id)
				self.stacked_widget.setCurrentIndex(0)
				self.second_window.show_welcome()
			else:
				return

	def handle_payment(self):
		if not self.controller.curr_sale_id:
			return
		payment_dialog = PaymentDialog(self)

		parent_geometry = self.geometry()
		dialog_geometry = payment_dialog.geometry()

		center_x = parent_geometry.x() + (parent_geometry.width() - dialog_geometry.width())
		center_y = parent_geometry.y() + (parent_geometry.height() - (2 * dialog_geometry.height()))

		payment_dialog.move(center_x, center_y)

		payment_dialog.cash_selected.connect(self.handle_cash_payment)
		payment_dialog.iban_selected.connect(self.handle_iban_payment)
		payment_dialog.exec()

	def handle_cancel(self):
		self.controller.database_manager.remove_cart_of_sale(self.controller.curr_sale_id)
		self.stacked_widget.setCurrentIndex(0)
		self.second_window.show_welcome()

	def _create_main_menu(self):
		main_menu_widget = QWidget()
		main_menu_layout = QVBoxLayout()
		main_menu_layout.setAlignment(Qt.AlignCenter)

		self.new_sale_button = QPushButton("Yeni Satış")
		self.sales_button = QPushButton("Satışlar")
		self.stock_button = QPushButton("Stoklar")
		self.onhold_button = QPushButton("Askıdakiler")
		self.quit_button = QPushButton("Çıkış")

		base_style = """
			QPushButton {
				color: white;
				font-size: 48px;
				font-weight: bold;
				padding: 20px;
				border-radius: 10px;
				width: 500px;
				height: 80px;
			}
			QPushButton:hover {
				border: 5px solid #999;
			}
		"""

		self.new_sale_button.setStyleSheet(base_style + """
			QPushButton {
				background-color: #27ae60; 
				border: 2px solid #229954;
			}
		""")
		self.sales_button.setStyleSheet(base_style + """
			QPushButton {
				background-color: #f39c12; 
				border: 2px solid #e67e22;
			}
		""")
		self.stock_button.setStyleSheet(base_style + """
			QPushButton {
				background-color: #3498db; 
				border: 2px solid #2980b9;
			}
		""")
		self.onhold_button.setStyleSheet(base_style + """
			QPushButton {
				background-color: #C27D0E; 
				border: 2px solid #c0392b;
			}
		""")
		self.quit_button.setStyleSheet(base_style + """
			QPushButton {
				background-color: #e74c3c; 
				border: 2px solid #c0392b;
			}
		""")

		self.new_sale_button.setShortcut("n")
		self.sales_button.setShortcut("v")
		self.stock_button.setShortcut("s")
		self.onhold_button.setShortcut("o")
		self.quit_button.setShortcut("q")

		main_menu_layout.addStretch()
		main_menu_layout.addWidget(self.new_sale_button)
		main_menu_layout.addWidget(self.sales_button)
		main_menu_layout.addWidget(self.stock_button)
		main_menu_layout.addWidget(self.onhold_button)
		main_menu_layout.addWidget(self.quit_button)
		main_menu_layout.addStretch()

		main_menu_widget.setLayout(main_menu_layout)
		return main_menu_widget

	def start_sale_and_show_cart(self):
		customer_name = self.new_sale_screen.name_input.text().strip()
		if not customer_name:
			customer_name = "UNKNOWN"

		self.controller.curr_customer_name = customer_name
		self.controller.curr_sale_id = self.controller.database_manager.start_new_sale(customer_name)
		self.cart_screen.refresh_data(self.controller)
		self.stacked_widget.setCurrentIndex(3)
		self.second_window.show_cart()

	def continue_sale(self, selected_id):
		try:
			cursor = self.controller.database_manager.conn.cursor()
			cursor.execute("""
				SELECT customer_name FROM
				sales
				WHERE sale_id = ?
			""", (selected_id, ))
			cust_name = cursor.fetchone()
			if cust_name:
				self.controller.curr_customer_name = cust_name[0]
			else:
				print(f"ERROR   : continue_sale: Sale {selected_id} not found in sales table!")
				return
			self.controller.curr_customer_name = cust_name[0]
			self.controller.curr_sale_id = selected_id
			self.cart_screen.refresh_data(self.controller)
			self.stacked_widget.setCurrentIndex(3)
			self.second_window.show_cart()
		except Exception as e:
			print(f"ERROR   : continue_sale :{e}")

class Window2(QMainWindow):
	def __init__(self, controller):
		super().__init__()
		self.setWindowTitle("BETA - Customer Display")
		self.controller = controller
		
		self.stacked_widget = QStackedWidget()
		self.setCentralWidget(self.stacked_widget)
		self.setStyleSheet("background-color: #111;")
		
		self.welcome_screen = WelcomeScreen()
		self.stacked_widget.addWidget(self.welcome_screen)
		
		from new_sale import CustomerCartScreen
		self.customer_cart_screen = CustomerCartScreen(controller)
		self.stacked_widget.addWidget(self.customer_cart_screen)

		self.showFullScreen()
	
	def show_welcome(self):
		self.stacked_widget.setCurrentIndex(0)

	def show_cart(self):
		# This method is now called whenever the main cart is updated
		self.customer_cart_screen.refresh_data(self.controller)
		self.stacked_widget.setCurrentIndex(1)
		
if __name__ == "__main__":
	if not os.path.isfile("database.db"):
		print("ERROR   : Gerekli dosya bulunamadı: 'database.db'")
		print("Boş bir database oluşturmak için 'python generate_tables.py' deneyebilir,")
		print("ya da mevcut database'inizin ismini 'database.db' olarak güncelleyebilirsiniz.")
		sys.exit(1)

	app = QApplication(sys.argv)
	data = AppData()

	second_window = Window2(data)
	main_window = Window1(data, second_window)

	main_window.new_sale_button.clicked.connect(second_window.show_welcome)

	main_window.new_sale_screen.back_button.clicked.connect(second_window.show_welcome)
	main_window.sales_screen.back_button.clicked.connect(second_window.show_welcome)
	main_window.cart_screen.back_button.clicked.connect(second_window.show_welcome)
	main_window.edit_stock_screen.back_to_menu.connect(second_window.show_welcome)

	sys.exit(app.exec())

