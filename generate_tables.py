import sqlite3

def create_tables(db_name='database.db'):
	conn = None
	try:
		conn = sqlite3.connect(db_name)
		cursor = conn.cursor()

		create_items_table = """
		CREATE TABLE IF NOT EXISTS items (
			item_id INTEGER PRIMARY KEY,
			item_name TEXT NOT NULL CHECK(LENGTH(item_name) <= 32),
			item_price REAL NOT NULL,
			item_stock INTEGER NOT NULL CHECK(item_stock >= 0)
		);
		"""

		create_sales_table = """
		CREATE TABLE IF NOT EXISTS sales (
			sale_id TEXT PRIMARY KEY NOT NULL CHECK(LENGTH(sale_id) <= 15),
			sale_date TEXT NOT NULL,
			customer_name TEXT NOT NULL CHECK(LENGTH(customer_name) <= 32),
			total_discount_perc INTEGER NOT NULL CHECK(total_discount_perc >= 0 AND total_discount_perc <= 100),
			total_discount_num REAL NOT NULL,
			total_amount REAL NOT NULL,
			payment_method TEXT NOT NULL,
			payment_info TEXT
		);
		"""

		create_cart_items_table = """
		CREATE TABLE IF NOT EXISTS cart_items (
			cart_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
			sale_id TEXT NOT NULL,
			item_id INTEGER NOT NULL,
			item_count INTEGER NOT NULL CHECK(item_count > 0),
			item_discount_perc INTEGER NOT NULL CHECK(item_discount_perc >= 0 AND item_discount_perc <= 100),
			item_discount_num REAL NOT NULL,
			item_total REAL NOT NULL,
			
			FOREIGN KEY (sale_id) REFERENCES sales(sale_id) ON DELETE CASCADE,
			FOREIGN KEY (item_id) REFERENCES items(item_id) ON DELETE CASCADE
		);
		"""

		create_campaigns_table = """
		CREATE TABLE campaigns (
			camp_id INTEGER PRIMARY KEY AUTOINCREMENT,
			item_id INTEGER NOT NULL,
			min_quan INTEGER NOT NULL,
			disc_type TEXT NOT NULL, -- "fixed" or "percent"
			disc_val REAL NOT NULL
		);
		"""

		cursor.execute(create_items_table)
		cursor.execute(create_sales_table)
		cursor.execute(create_cart_items_table)
		cursor.execute(create_campaigns_table)

		conn.commit()
		print(f"All three tables created successfully in {db_name}.")

	except sqlite3.Error as e:
		print(f"An error occurred: {e}")
	finally:
		if conn:
			conn.close()
			print("Database connection closed.")

if __name__ == "__main__":
	create_tables()
