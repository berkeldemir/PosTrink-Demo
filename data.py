import random
import time
import sqlite3
from datetime import datetime

class DatabaseManager:
	def __init__(self):
		self.conn = None
		self.db_name = 'database.db'
		self.connect()

	def connect(self):
		try:
			self.conn = sqlite3.connect(self.db_name)
			self.conn.row_factory = sqlite3.Row
			print("DATABASE: Successfully connected.")
		except sqlite3.Error as e:
			print(f"DATABASE: Connection failed: {e}")

	def close(self):
		if self.conn:
			self.conn.close()
			print("DATABASE: Connection closed.")

	def start_new_sale(self, customer_name):
		sale_id = f"{int(time.time())}-{random.randint(100, 999)}"
		sale_date = datetime.now().isoformat()
		try:
			cursor = self.conn.cursor()
			cursor.execute("""
				INSERT INTO sales (sale_id, sale_date, customer_name, total_discount_perc, total_discount_num, total_amount, payment_method, payment_info)
				VALUES (?, ?, ?, ?, ?, ?, ?, ?)
			""", (sale_id, sale_date, customer_name, 0, 0.0, 0.0, "WIP", ""))
			self.conn.commit()
			print(f"NEW SALE: {sale_id} | {customer_name}")
			return sale_id
		except sqlite3.Error as e:
			print(f"ERROR   : start_new_sale: {e}")
			return None

	def update_sale_payment_info(self, sale_id, payment_method, payment_info=None):
		try:
			cursor = self.conn.cursor()
			cursor.execute("""
				UPDATE sales
				SET payment_method = ?,
					payment_info = ?
				WHERE sale_id = ?
			""", (payment_method, payment_info, sale_id))
			self.conn.commit()
			print(f"UPDATE  : {sale_id} payment_method updated to '{payment_method}'")
			if payment_info:
				print(f"UPDATE  : {sale_id} payment_info updated to '{payment_info}'")
			return True
		except sqlite3.Error as e:
			print(f"ERROR    : update_sale_payment_info: {e}")
			return False

	def update_sale_date(self, sale_id):
		try:
			sale_date = datetime.now().isoformat()
			cursor = self.conn.cursor()
			cursor.execute("""
				UPDATE sales
				SET sale_date = ?
				WHERE sale_id = ?
			""", (sale_date, sale_id))
			print(f"UPDATE  : {sale_id} sale_date updated to '{sale_date}'")
			self.conn.commit()
		except sqlite3.Error as e:
			print(f"ERROR    : update_sale_date: {e}")

	def get_available_products(self):
		try:
			cursor = self.conn.cursor()
			cursor.execute("""
				SELECT *
				FROM items
				WHERE item_stock > 0
			""")
			return cursor.fetchall()
		except sqlite3.Error as e:
			print(f"ERROR   : get_all_products: {e}")
			return []

	def get_sale_products(self, sale_id):
		try:
			cursor = self.conn.cursor()
			cursor.execute("""
				SELECT *
				FROM cart_items
				WHERE sale_id = ?
			""", (sale_id, ))
		except sqlite3.Error as e:
			print(f"ERROR   : get_sale_products: {e}")

	def total_amount_calculator(self, sale_id):
		try:
			cursor_total = self.conn.cursor()
			cursor_total.execute("""
				SELECT item_total
				FROM cart_items
				WHERE sale_id = ?
			""", (sale_id, ))
			item_total_tuple = cursor_total.fetchall()
			if not item_total_tuple:
				return 0
			total = 0
			for i in item_total_tuple:
				total = total + i[0]
			return total
		except Exception as e:
			print(f"ERROR   : total_amount_calculator: {e}")
			self.conn.rollback()
			return 0

	def total_discount_num(self, sale_id):
		try:
			cursor = self.conn.cursor()
			cursor.execute("""
				SELECT total_discount_num
				FROM sales
				WHERE sale_id = ?
			""", (sale_id,))
			row = cursor.fetchone()
			return row[0] if row else 0
		except Exception as e:
			print(f"ERROR   : total_discount_num: {e}")
			self.conn.rollback()
			return 0

	def add_item_to_cart(self, sale_id, item_id, item_count, item_discount_perc, item_discount_num):
		try:
			if (not self.check_item_available(item_id)):
				return False
			self.decrease_item_stock(item_id)
			cur = self.conn.cursor()
			cur.execute("""
				SELECT ci.item_count, ci.item_total, i.item_price
				FROM cart_items ci
				JOIN items i ON ci.item_id = i.item_id
				WHERE ci.sale_id = ? AND ci.item_id = ?
			""", (sale_id, item_id))
			row = cur.fetchone()
			if row:
				new_count = row[0] + item_count
				new_total = row[1] + (item_count * row[2])
				cur.execute("""
					UPDATE cart_items
					SET item_count = ?,
						item_total = ?
					WHERE sale_id = ? AND item_id = ?
				""", (new_count, new_total, sale_id, item_id))
				self.conn.commit()
				return True
			cur.execute("""
				SELECT item_price
				FROM items
				WHERE item_id = ?
			""", (item_id,))
			price_row = cur.fetchone()
			if not price_row:
				print(f"ERROR:   Item ID not found: {item_id}")
				return False
			base_price = price_row[0]
			line_total = base_price
			if item_discount_perc:
				line_total = line_total * (100 - item_discount_perc) / 100.0
			if item_discount_num:
				line_total = line_total - item_discount_num
			cur.execute("""
				INSERT INTO cart_items (sale_id, item_id, item_count, item_discount_perc, item_discount_num, item_total)
				VALUES (?, ?, ?, ?, ?, ?)
			""", (sale_id, item_id, item_count, item_discount_perc, item_discount_num, line_total * item_count))
			self.conn.commit()
			return True
		except Exception as e:
			print(f"ERROR   : add_item_to_cart: {e}")
			self.conn.rollback()
			return False

	def apply_discounts(self, sale_id):
		try:
			cur = self.conn.cursor()
			cur.execute("""
				SELECT ci.item_id, ci.item_count, i.item_price
				FROM cart_items ci
				JOIN items i ON i.item_id = ci.item_id
				WHERE ci.sale_id = ?
			""", (sale_id,))
			rows = cur.fetchall()
			for item_id, item_count, item_price in rows:
				base_total = (item_price or 0) * (item_count or 0)
				cur.execute("""
					SELECT disc_type, disc_val, min_quan
					FROM campaigns
					WHERE item_id = ?
					AND min_quan <= ?
					ORDER BY min_quan DESC
					LIMIT 1
				""", (item_id, item_count))
				camp = cur.fetchone()
				discount_num = 0.0
				discount_perc = 0.0
				if camp and item_count >= camp["min_quan"]:
					if camp["disc_type"] == "percent":
						discount_num = base_total * (camp["disc_val"] / 100.0)
						discount_perc = camp["disc_val"]
					elif camp["disc_type"] == "fixed":
						discount_num = min(base_total, camp["disc_val"])  # don’t go negative
						discount_perc = (discount_num / base_total * 100.0) if base_total > 0 else 0.0
				new_total = base_total - discount_num
				cur.execute("""
					UPDATE cart_items
					SET item_discount_perc = ?,
						item_discount_num  = ?,
						item_total         = ?
					WHERE sale_id = ? AND item_id = ?
				""", (discount_perc, discount_num, new_total, sale_id, item_id))
			cur.execute("""
				SELECT COALESCE(SUM(item_discount_num), 0.0),
					COALESCE(SUM(item_total), 0.0)
				FROM cart_items
				WHERE sale_id = ?
			""", (sale_id,))
			disc_sum, total_sum = cur.fetchone() or (0.0, 0.0)
			cur.execute("""
				UPDATE sales
				SET total_discount_num = ?,
					total_amount       = ?
				WHERE sale_id = ?
			""", (disc_sum, total_sum, sale_id))
			self.conn.commit()
		except Exception as e:
			print(f"ERROR   : apply_discounts: {e}")
			self.conn.rollback()

	def get_cart_items(self, sale_id):
		try:
			self.apply_discounts(sale_id)
			cursor = self.conn.cursor()
			cursor.execute("""
				SELECT
					ci.item_count,
					i.item_name,
					ci.item_discount_perc,
					ci.item_discount_num,
					ci.item_total
				FROM cart_items AS ci
				JOIN items  AS i  ON ci.item_id = i.item_id
				WHERE ci.sale_id = ?
			""", (sale_id,))
			return cursor.fetchall()
		except Exception as e:
			print(f"ERROR   : get_cart_items: {e}")
			return []

	def remove_item_from_cart(self, sale_id, i):
		try:
			cart_items = get_cart_items(sale_id)
			cursor = self.conn.cursor()
			cursor.execute("""
				DELETE FROM cart_items
				WHERE cart_items_id = ?
			""", (cart_items[i][0], ))
			self.conn.commit()
			return True
		except Exception as e:
				print(f"ERROR   : remove_item_from_cart: {e}")
				return False
	
	def remove_cart_of_sale(self, sale_id):
		try:
			cursor = self.conn.cursor()
			cursor.execute("""
				UPDATE items
				SET item_stock = item_stock + (
					SELECT item_count
					FROM cart_items
					WHERE cart_items.item_id = items.item_id
					AND cart_items.sale_id = ?
				)
				WHERE EXISTS (
					SELECT 1
					FROM cart_items
					WHERE cart_items.item_id = items.item_id
					AND cart_items.sale_id = ?
				);
			""", (sale_id, sale_id))
			self.conn.commit()
			cursor = self.conn.cursor()
			cursor.execute("""
				DELETE FROM cart_items
				WHERE sale_id = ?
			""", (sale_id, ))
			self.conn.commit()
			cursor = self.conn.cursor()
			cursor.execute("""
				DELETE FROM sales
				WHERE sale_id = ?
			""", (sale_id, ))
			self.conn.commit()
			print(f"UPDATE  : {sale_id} sale removed.")
		except Exception as e:
			print(f"ERROR   : remove_cart_of_sale: {e}")

	def	onhold_orders(self):
		try:
			cursor = self.conn.cursor()
			cursor.execute("""
				SELECT *
				FROM sales
				WHERE payment_method = "WIP"
			""")
			return (cursor.fetchall())
		except Exception as e:
			print(f"ERROR   : onhold_orders: {e}")

	def calculate_cart_discount(self, sale_id):
		try:
			cursor = self.conn.cursor()
			cursor.execute("""
				SELECT item_id, item_count
				FROM cart_items
				WHERE sale_id = ?
			""", (sale_id,))
			cart_items = cursor.fetchall()
			total_discount = 0
			for item_id, count in cart_items:
				discount = self.get_applicable_discount(item_id, count)
				total_discount += discount
			return total_discount
		except Exception as e:
			print(f"ERROR   : calculate_cart_discount: {e}")
			return 0

	def available_campaigns(self):
		try:
			cursor = self.conn.cursor()
			cursor.execute("""
				SELECT
					i.item_name,
					c.min_quan,
					c.disc_val
				FROM campaigns AS c
				JOIN items AS i
					ON c.item_id = i.id;
			""")
		except Exception as e:
			print("ERROR   : available_campaigns: {e}")

	def get_onhold_sales(self):
		try:
			cursor = self.conn.cursor()
			cursor.execute("""
				SELECT
					sale_id,
					sale_date,
					customer_name,
					total_amount
				FROM sales
				WHERE payment_method = "WIP";
			""")
			return cursor.fetchall()
		except Exception as e:
			print(f"ERROR   : get_onhold_sales: {e}")

	def get_sales(self):
		try:
			cursor = self.conn.cursor()
			cursor.execute("""
				SELECT sale_id, sale_date, customer_name, total_amount, payment_method
				FROM sales
				ORDER BY sale_date DESC
			""")
			rows = cursor.fetchall()
			return [dict(r) for r in rows]
		except Exception as e:
			print(f"ERROR   : get_sales: {e}")
			return []

	def get_filtered_items(self, id_input, name_input, price_input, stock_input):
		try:
			cursor = self.conn.cursor()
			cursor.execute("""
				SELECT *
				FROM items
				WHERE item_id LIKE '%' || ? || '%'
				AND item_name LIKE '%' || ? || '%'
				AND item_price LIKE '%' || ? || '%'
				AND item_stock LIKE '%' || ? || '%';
			""", (id_input, name_input, price_input, stock_input))
			return cursor.fetchall()
		except sqlite3.Error as e:
			print(f"ERROR   : get_filtered_items: {e}")
			return []

	def get_filtered_sales(self, date_input, name_input):
		try:
			cursor = self.conn.cursor()
			cursor.execute("""
				SELECT *
				FROM sales
				WHERE sale_date LIKE '%' || ? || '%'
				AND customer_name LIKE '%' || ? || '%'
				ORDER BY sale_date DESC;
			""", (date_input, name_input))
			rows = cursor.fetchall()
			return [dict(r) for r in rows]
		except Exception as e:
			print(f"ERROR   : get_sales: {e}")
			return []

	def	add_new_item(self, id, name, price, stock):
		try:
			cursor = self.conn.cursor()
			cursor.execute("""
				INSERT INTO items
				(item_id, item_name, item_price, item_stock)
				VALUES
				(? , ? , ? , ?)
			""", (id, name, price, stock))
			return True
		except sqlite3.Error as e:
			print(f"ERROR   : add_new_item: {e}")
			return False

	def get_item_details(self, id):
		try:
			cursor = self.conn.cursor()
			cursor.execute("""
				SELECT *
				FROM items
				WHERE item_id = ?
			""", (id, ))
			row = cursor.fetchone()
			return dict(row)
		except sqlite3.Error as e:
			print(f"ERROR   : get_item_detail: {e}")
			return []

	def update_item(self, item_id, name, price, stock):
		try:
			float(item_id)
			float(price)
			float(stock)
		except (TypeError, ValueError):
			print(f"ERRORMSG: update_item: non-float input detected.")
			return False
		try:
			cursor = self.conn.cursor()
			cursor.execute("""
				UPDATE items
				SET
				item_name = ?,
				item_price = ?,
				item_stock = ?
				WHERE item_id = ?;
			""", (name, price, stock, item_id))
			self.conn.commit()
			print(f"UPDATE  : {item_id} item updated, details:")
			print(f"  name  : {name}")
			print(f" price  : {price}")
			print(f" stock  : {stock}")
			return True
		except sqlite3.Error as e:
			print(f"ERROR   : update_item: {e}")

	def remove_item(self, id):
		try:
			cursor = self.conn.cursor()
			cursor.execute("""
				DELETE FROM items
				WHERE item_id = ?
			""", (id, ))
			self.conn.commit()
			print(f"UPDATE  : {id} item deleted.")
		except sqlite3.Error as e:
			print(f"ERROR   : remove_item: {e}")
		
	def check_item_available(self, id):
		try:
			cursor = self.conn.cursor()
			cursor.execute("""
				SELECT item_stock
				FROM items
				WHERE item_id = ?
			""", (id, ))
			count = cursor.fetchone()
			if (count[0] > 0):
				return True
			else:
				return False
		except sqlite3.Error as e:
			print(f"ERROR   : check_item_available: {e}")
			return False

	def decrease_item_stock(self, id):
		try:
			cursor = self.conn.cursor()
			cursor.execute("""
				UPDATE items
				SET item_stock = item_stock - 1.0
				WHERE item_id = ?
			""", (id, ))
			self.conn.commit()
		except sqlite3.Error as e:
			print(f"ERROR   : decrease_item_stock: {e}")

class AppData:
	def __init__(self):
		self.database_manager = DatabaseManager()
		self.curr_sale_id = None
		self.curr_customer_name = ""
