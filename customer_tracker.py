import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QTextEdit, QTableWidget, QTableWidgetItem, QFileDialog, QMessageBox
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
import sqlite3
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class CustomerManagementSystem(QWidget):
    def __init__(self):
        super().__init__()

        self.db_connection = sqlite3.connect('customers.db')
        self.create_table()

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Customer Management System')
        self.setGeometry(100, 100, 1200, 800)
        self.setWindowIcon(QIcon('icon.png'))

        # Stylesheet for a modern and clean look
        self.setStyleSheet("""
            background-color: #f0f0f0;
            font-size: 18px;
        """)

        self.name_label = QLabel('Enter Customer Name:', self)
        self.name_input = QLineEdit(self)

        self.contact_label = QLabel('Enter Contact Number:', self)
        self.contact_input = QLineEdit(self)

        self.item_label = QLabel('Enter Purchased Item:', self)
        self.item_input = QLineEdit(self)

        self.amount_label = QLabel('Enter Purchase Amount:', self)
        self.amount_input = QLineEdit(self)

        self.add_customer_button = QPushButton('Add Customer', self)
        self.add_customer_button.setStyleSheet("background-color: #4CAF50; color: white;")

        self.edit_customer_button = QPushButton('Edit Customer', self)
        self.edit_customer_button.setStyleSheet("background-color: #3498db; color: white;")

        self.search_label = QLabel('Search Customer Name:', self)
        self.search_input = QLineEdit(self)

        self.search_button = QPushButton('Search', self)
        self.search_button.setStyleSheet("background-color: #008CBA; color: white;")

        self.export_button = QPushButton('Export to CSV', self)
        self.export_button.setStyleSheet("background-color: #f44336; color: white;")

        self.view_details_button = QPushButton('View Details', self)
        self.view_details_button.setStyleSheet("background-color: #555555; color: white;")

        self.clear_records_button = QPushButton('Clear Records', self)
        self.clear_records_button.setStyleSheet("background-color: #FFA500; color: white;")

        self.calculate_total_button = QPushButton('Calculate Total Amount', self)
        self.calculate_total_button.setStyleSheet("background-color: #e74c3c; color: white;")

        self.view_chart_button = QPushButton('View Purchase Chart', self)
        self.view_chart_button.setStyleSheet("background-color: #9b59b6; color: white;")

        self.log_display = QTextEdit(self)
        self.log_display.setReadOnly(True)

        self.customers_table = QTableWidget(self)
        self.customers_table.setColumnCount(5)
        self.customers_table.setHorizontalHeaderLabels(['ID', 'Name', 'Contact', 'Item', 'Amount'])

        layout = QVBoxLayout(self)

        form_layout = QHBoxLayout()
        form_layout.addWidget(self.name_label)
        form_layout.addWidget(self.name_input)
        form_layout.addWidget(self.contact_label)
        form_layout.addWidget(self.contact_input)
        form_layout.addWidget(self.item_label)
        form_layout.addWidget(self.item_input)
        form_layout.addWidget(self.amount_label)
        form_layout.addWidget(self.amount_input)
        form_layout.addWidget(self.add_customer_button)
        form_layout.addWidget(self.edit_customer_button)
        layout.addLayout(form_layout)

        search_layout = QHBoxLayout()
        search_layout.addWidget(self.search_label)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_button)
        layout.addLayout(search_layout)

        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.export_button)
        buttons_layout.addWidget(self.view_details_button)
        buttons_layout.addWidget(self.clear_records_button)
        buttons_layout.addWidget(self.calculate_total_button)
        buttons_layout.addWidget(self.view_chart_button)
        layout.addLayout(buttons_layout)

        layout.addWidget(self.log_display)
        layout.addWidget(self.customers_table)

        self.add_customer_button.clicked.connect(self.add_customer)
        self.edit_customer_button.clicked.connect(self.edit_customer)
        self.search_button.clicked.connect(self.search_customers)
        self.export_button.clicked.connect(self.export_to_csv)
        self.view_details_button.clicked.connect(self.view_details)
        self.clear_records_button.clicked.connect(self.clear_records)
        self.calculate_total_button.clicked.connect(self.calculate_total_amount)
        self.view_chart_button.clicked.connect(self.view_purchase_chart)

        self.update_customers_table()
        self.show()

    def create_table(self):
        cursor = self.db_connection.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                contact TEXT NOT NULL,
                item TEXT NOT NULL,
                amount TEXT NOT NULL
            )
        ''')
        self.db_connection.commit()

    def add_customer(self):
        name = self.name_input.text().strip()
        contact = self.contact_input.text().strip()
        item = self.item_input.text().strip()
        amount = self.amount_input.text().strip()

        if name and contact and item and amount:
            cursor = self.db_connection.cursor()
            cursor.execute('INSERT INTO customers (name, contact, item, amount) VALUES (?, ?, ?, ?)', (name, contact, item, amount))
            self.db_connection.commit()

            self.update_customers_table()
            self.log_display.append(f'Added customer: {name} - Contact: {contact} - Item: {item} - Amount: {amount}')

    def edit_customer(self):
        selected_row = self.customers_table.currentRow()
        if selected_row >= 0:
            id_item = self.customers_table.item(selected_row, 0)
            name_item = self.customers_table.item(selected_row, 1)
            contact_item = self.customers_table.item(selected_row, 2)
            item_item = self.customers_table.item(selected_row, 3)
            amount_item = self.customers_table.item(selected_row, 4)

            id_value = id_item.text()
            name_value = name_item.text()
            contact_value = contact_item.text()
            item_value = item_item.text()
            amount_value = amount_item.text()

            # Assuming a new amount is entered for editing
            new_amount, ok_pressed = QInputDialog.getDouble(self, "Edit Amount", f"Edit amount for {name_value}:", float(amount_value), 0, 100000, 2)

            if ok_pressed:
                cursor = self.db_connection.cursor()
                cursor.execute('UPDATE customers SET amount = ? WHERE id = ?', (new_amount, id_value))
                self.db_connection.commit()

                self.update_customers_table()
                self.log_display.append(f'Edited amount for {name_value}. New amount: {new_amount}')

    def search_customers(self):
        search_name = self.search_input.text().strip()
        if search_name:
            cursor = self.db_connection.cursor()
            cursor.execute('SELECT * FROM customers WHERE name LIKE ?', (f'%{search_name}%',))
            data = cursor.fetchall()

            self.customers_table.setRowCount(len(data))
            for row_index, row_data in enumerate(data):
                for col_index, col_data in enumerate(row_data):
                    item = QTableWidgetItem(str(col_data))
                    item.setFlags(Qt.ItemIsEnabled)
                    self.customers_table.setItem(row_index, col_index, item)

            self.log_display.append(f'Searched customers for {search_name}')

    def export_to_csv(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Customers Data", "", "CSV Files (*.csv);;All Files (*)", options=options)

        if file_name:
            with open(file_name, 'w') as file:
                cursor = self.db_connection.cursor()
                cursor.execute('SELECT * FROM customers')
                data = cursor.fetchall()

                headers = ['ID', 'Name', 'Contact', 'Item', 'Amount']
                file.write(','.join(headers) + '\n')

                for row_data in data:
                    file.write(','.join(map(str, row_data)) + '\n')

            self.log_display.append(f'Exported customers data to {file_name}')

    def view_details(self):
        selected_row = self.customers_table.currentRow()
        if selected_row >= 0:
            id_item = self.customers_table.item(selected_row, 0)
            name_item = self.customers_table.item(selected_row, 1)
            contact_item = self.customers_table.item(selected_row, 2)
            item_item = self.customers_table.item(selected_row, 3)
            amount_item = self.customers_table.item(selected_row, 4)

            id_value = id_item.text()
            name_value = name_item.text()
            contact_value = contact_item.text()
            item_value = item_item.text()
            amount_value = amount_item.text()

            details = f'Details for ID {id_value}:\nName: {name_value}\nContact: {contact_value}\nItem: {item_value}\nAmount: {amount_value}'
            self.log_display.append(details)

    def clear_records(self):
        confirmation = QMessageBox.question(self, 'Confirmation', 'Are you sure you want to clear all records? This action cannot be undone.', QMessageBox.Yes | QMessageBox.No)
        if confirmation == QMessageBox.Yes:
            cursor = self.db_connection.cursor()
            cursor.execute('DELETE FROM customers')
            self.db_connection.commit()

            self.update_customers_table()
            self.log_display.append('All records cleared.')

    def calculate_total_amount(self):
        cursor = self.db_connection.cursor()
        cursor.execute('SELECT SUM(amount) FROM customers')
        total_amount = cursor.fetchone()[0]

        self.log_display.append(f'Total purchase amount from all customers: {total_amount}')

    def view_purchase_chart(self):
        cursor = self.db_connection.cursor()
        cursor.execute('SELECT name, amount FROM customers')
        data = cursor.fetchall()

        names = [row[0] for row in data]
        amounts = [float(row[1]) for row in data]

        fig, ax = plt.subplots()
        ax.bar(names, amounts)
        ax.set_ylabel('Purchase Amount')
        ax.set_xlabel('Customer Names')
        ax.set_title('Purchase Amounts by Customer')

        plt.show()

    def update_customers_table(self):
        cursor = self.db_connection.cursor()
        cursor.execute('SELECT * FROM customers')
        data = cursor.fetchall()

        self.customers_table.setRowCount(len(data))
        for row_index, row_data in enumerate(data):
            for col_index, col_data in enumerate(row_data):
                item = QTableWidgetItem(str(col_data))
                item.setFlags(Qt.ItemIsEnabled)
                self.customers_table.setItem(row_index, col_index, item)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = CustomerManagementSystem()
    sys.exit(app.exec_())
