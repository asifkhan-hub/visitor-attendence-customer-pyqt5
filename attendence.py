import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit, QTableWidget, QTableWidgetItem, QDateTimeEdit, QFileDialog, QMessageBox
from PyQt5.QtCore import Qt, QDateTime
import sqlite3
from datetime import datetime

class AttendanceSystem(QWidget):
    def __init__(self):
        super().__init__()

        self.db_connection = sqlite3.connect('attendance.db')
        self.create_table()

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Professional Attendance System')
        self.setGeometry(100, 100, 800, 400)

        self.name_label = QLabel('Enter Name:', self)
        self.name_input = QLineEdit(self)

        self.timestamp_label = QLabel('Timestamp:', self)
        self.timestamp_input = QDateTimeEdit(self)
        self.timestamp_input.setDateTime(QDateTime.currentDateTime())

        self.mark_attendance_button = QPushButton('Mark Attendance', self)
        self.search_label = QLabel('Search Name:', self)
        self.search_input = QLineEdit(self)
        self.search_button = QPushButton('Search', self)
        self.export_button = QPushButton('Export to CSV', self)
        self.view_details_button = QPushButton('View Details', self)
        self.clear_records_button = QPushButton('Clear Records', self)

        self.log_display = QTextEdit(self)
        self.log_display.setReadOnly(True)

        self.attendance_table = QTableWidget(self)
        self.attendance_table.setColumnCount(3)
        self.attendance_table.setHorizontalHeaderLabels(['ID', 'Name', 'Timestamp'])

        layout = QVBoxLayout(self)

        form_layout = QHBoxLayout()
        form_layout.addWidget(self.name_label)
        form_layout.addWidget(self.name_input)
        form_layout.addWidget(self.timestamp_label)
        form_layout.addWidget(self.timestamp_input)
        form_layout.addWidget(self.mark_attendance_button)
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
        layout.addWidget(self.attendance_table)

        self.mark_attendance_button.clicked.connect(self.mark_attendance)
        self.search_button.clicked.connect(self.search_attendance)
        self.export_button.clicked.connect(self.export_to_csv)
        self.view_details_button.clicked.connect(self.view_details)
        self.clear_records_button.clicked.connect(self.clear_records)

        self.update_attendance_table()
        self.show()

    def create_table(self):
        cursor = self.db_connection.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                timestamp TEXT NOT NULL
            )
        ''')
        self.db_connection.commit()

    def mark_attendance(self):
        name = self.name_input.text().strip()
        timestamp = self.timestamp_input.dateTime().toString('yyyy-MM-dd HH:mm:ss')

        if name:
            cursor = self.db_connection.cursor()
            cursor.execute('INSERT INTO attendance (name, timestamp) VALUES (?, ?)', (name, timestamp))
            self.db_connection.commit()

            self.update_attendance_table()
            self.log_display.append(f'Marked attendance for {name} at {timestamp}')

    def search_attendance(self):
        search_name = self.search_input.text().strip()
        if search_name:
            cursor = self.db_connection.cursor()
            cursor.execute('SELECT * FROM attendance WHERE name LIKE ?', (f'%{search_name}%',))
            data = cursor.fetchall()

            self.attendance_table.setRowCount(len(data))
            for row_index, row_data in enumerate(data):
                for col_index, col_data in enumerate(row_data):
                    item = QTableWidgetItem(str(col_data))
                    item.setFlags(Qt.ItemIsEnabled)
                    self.attendance_table.setItem(row_index, col_index, item)

            self.log_display.append(f'Searched attendance for {search_name}')

    def export_to_csv(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Attendance Data", "", "CSV Files (*.csv);;All Files (*)", options=options)

        if file_name:
            with open(file_name, 'w') as file:
                cursor = self.db_connection.cursor()
                cursor.execute('SELECT * FROM attendance')
                data = cursor.fetchall()

                headers = ['ID', 'Name', 'Timestamp']
                file.write(','.join(headers) + '\n')

                for row_data in data:
                    file.write(','.join(map(str, row_data)) + '\n')

            self.log_display.append(f'Exported attendance data to {file_name}')

    def view_details(self):
        selected_row = self.attendance_table.currentRow()
        if selected_row >= 0:
            id_item = self.attendance_table.item(selected_row, 0)
            name_item = self.attendance_table.item(selected_row, 1)
            timestamp_item = self.attendance_table.item(selected_row, 2)

            id_value = id_item.text()
            name_value = name_item.text()
            timestamp_value = timestamp_item.text()

            details = f'Details for ID {id_value}:\nName: {name_value}\nTimestamp: {timestamp_value}'
            self.log_display.append(details)

    def clear_records(self):
        confirmation = QMessageBox.question(self, 'Confirmation', 'Are you sure you want to clear all records? This action cannot be undone.', QMessageBox.Yes | QMessageBox.No)
        if confirmation == QMessageBox.Yes:
            cursor = self.db_connection.cursor()
            cursor.execute('DELETE FROM attendance')
            self.db_connection.commit()

            self.update_attendance_table()
            self.log_display.append('All records cleared.')

    def update_attendance_table(self):
        cursor = self.db_connection.cursor()
        cursor.execute('SELECT * FROM attendance')
        data = cursor.fetchall()

        self.attendance_table.setRowCount(len(data))
        for row_index, row_data in enumerate(data):
            for col_index, col_data in enumerate(row_data):
                item = QTableWidgetItem(str(col_data))
                item.setFlags(Qt.ItemIsEnabled)
                self.attendance_table.setItem(row_index, col_index, item)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = AttendanceSystem()
    sys.exit(app.exec_())
