import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QTextEdit, QTableWidget, QTableWidgetItem, QDateTimeEdit, QFileDialog, QMessageBox
)
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import Qt, QDateTime
import sqlite3
from datetime import datetime

class VisitorTrackingSystem(QWidget):
    def __init__(self):
        super().__init__()

        self.db_connection = sqlite3.connect('visitors.db')
        self.create_table()

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Visitor Tracking System')
        self.setGeometry(100, 100, 1000, 600)
        self.setWindowIcon(QIcon('icon.png'))

        # Stylesheet for a modern and clean look
        self.setStyleSheet("""
            background-color: #f0f0f0;
            font-size: 18px;
        """)

        self.name_label = QLabel('Enter Visitor Name:', self)
        self.name_input = QLineEdit(self)

        self.mobile_label = QLabel('Enter Mobile Number:', self)
        self.mobile_input = QLineEdit(self)

        self.timestamp_label = QLabel('Timestamp:', self)
        self.timestamp_input = QDateTimeEdit(self)
        self.timestamp_input.setDateTime(QDateTime.currentDateTime())

        self.reason_label = QLabel('Reason for Visit:', self)
        self.reason_input = QLineEdit(self)

        self.mark_visit_button = QPushButton('Mark Visit', self)
        self.mark_visit_button.setStyleSheet("background-color: #4CAF50; color: white;")

        self.search_label = QLabel('Search Visitor Name:', self)
        self.search_input = QLineEdit(self)

        self.search_button = QPushButton('Search', self)
        self.search_button.setStyleSheet("background-color: #008CBA; color: white;")

        self.export_button = QPushButton('Export to CSV', self)
        self.export_button.setStyleSheet("background-color: #f44336; color: white;")

        self.view_details_button = QPushButton('View Details', self)
        self.view_details_button.setStyleSheet("background-color: #555555; color: white;")

        self.clear_records_button = QPushButton('Clear Records', self)
        self.clear_records_button.setStyleSheet("background-color: #FFA500; color: white;")

        self.log_display = QTextEdit(self)
        self.log_display.setReadOnly(True)

        self.visitors_table = QTableWidget(self)
        self.visitors_table.setColumnCount(5)
        self.visitors_table.setHorizontalHeaderLabels(['ID', 'Name', 'Mobile', 'Timestamp', 'Reason'])

        layout = QVBoxLayout(self)

        form_layout = QHBoxLayout()
        form_layout.addWidget(self.name_label)
        form_layout.addWidget(self.name_input)
        form_layout.addWidget(self.mobile_label)
        form_layout.addWidget(self.mobile_input)
        form_layout.addWidget(self.timestamp_label)
        form_layout.addWidget(self.timestamp_input)
        form_layout.addWidget(self.reason_label)
        form_layout.addWidget(self.reason_input)
        form_layout.addWidget(self.mark_visit_button)
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
        layout.addLayout(buttons_layout)

        layout.addWidget(self.log_display)
        layout.addWidget(self.visitors_table)

        self.mark_visit_button.clicked.connect(self.mark_visit)
        self.search_button.clicked.connect(self.search_visitors)
        self.export_button.clicked.connect(self.export_to_csv)
        self.view_details_button.clicked.connect(self.view_details)
        self.clear_records_button.clicked.connect(self.clear_records)

        self.update_visitors_table()
        self.show()

    def create_table(self):
        cursor = self.db_connection.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS visitors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                mobile TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                reason TEXT NOT NULL
            )
        ''')
        self.db_connection.commit()

    def mark_visit(self):
        name = self.name_input.text().strip()
        mobile = self.mobile_input.text().strip()
        timestamp = self.timestamp_input.dateTime().toString('yyyy-MM-dd HH:mm:ss')
        reason = self.reason_input.text().strip()

        if name and mobile and reason:
            cursor = self.db_connection.cursor()
            cursor.execute('INSERT INTO visitors (name, mobile, timestamp, reason) VALUES (?, ?, ?, ?)', (name, mobile, timestamp, reason))
            self.db_connection.commit()

            self.update_visitors_table()
            self.log_display.append(f'Marked visit for {name} at {timestamp} - Reason: {reason}')

    def search_visitors(self):
        search_name = self.search_input.text().strip()
        if search_name:
            cursor = self.db_connection.cursor()
            cursor.execute('SELECT * FROM visitors WHERE name LIKE ?', (f'%{search_name}%',))
            data = cursor.fetchall()

            self.visitors_table.setRowCount(len(data))
            for row_index, row_data in enumerate(data):
                for col_index, col_data in enumerate(row_data):
                    item = QTableWidgetItem(str(col_data))
                    item.setFlags(Qt.ItemIsEnabled)
                    self.visitors_table.setItem(row_index, col_index, item)

            self.log_display.append(f'Searched visits for {search_name}')

    def export_to_csv(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Visitors Data", "", "CSV Files (*.csv);;All Files (*)", options=options)

        if file_name:
            with open(file_name, 'w') as file:
                cursor = self.db_connection.cursor()
                cursor.execute('SELECT * FROM visitors')
                data = cursor.fetchall()

                headers = ['ID', 'Name', 'Mobile', 'Timestamp', 'Reason']
                file.write(','.join(headers) + '\n')

                for row_data in data:
                    file.write(','.join(map(str, row_data)) + '\n')

            self.log_display.append(f'Exported visitors data to {file_name}')

    def view_details(self):
        selected_row = self.visitors_table.currentRow()
        if selected_row >= 0:
            id_item = self.visitors_table.item(selected_row, 0)
            name_item = self.visitors_table.item(selected_row, 1)
            mobile_item = self.visitors_table.item(selected_row, 2)
            timestamp_item = self.visitors_table.item(selected_row, 3)
            reason_item = self.visitors_table.item(selected_row, 4)

            id_value = id_item.text()
            name_value = name_item.text()
            mobile_value = mobile_item.text()
            timestamp_value = timestamp_item.text()
            reason_value = reason_item.text()

            details = f'Details for ID {id_value}:\nName: {name_value}\nMobile: {mobile_value}\nTimestamp: {timestamp_value}\nReason: {reason_value}'
            self.log_display.append(details)

    def clear_records(self):
        confirmation = QMessageBox.question(self, 'Confirmation', 'Are you sure you want to clear all records? This action cannot be undone.', QMessageBox.Yes | QMessageBox.No)
        if confirmation == QMessageBox.Yes:
            cursor = self.db_connection.cursor()
            cursor.execute('DELETE FROM visitors')
            self.db_connection.commit()

            self.update_visitors_table()
            self.log_display.append('All records cleared.')

    def update_visitors_table(self):
        cursor = self.db_connection.cursor()
        cursor.execute('SELECT * FROM visitors')
        data = cursor.fetchall()

        self.visitors_table.setRowCount(len(data))
        for row_index, row_data in enumerate(data):
            for col_index, col_data in enumerate(row_data):
                item = QTableWidgetItem(str(col_data))
                item.setFlags(Qt.ItemIsEnabled)
                self.visitors_table.setItem(row_index, col_index, item)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = VisitorTrackingSystem()
    sys.exit(app.exec_())
