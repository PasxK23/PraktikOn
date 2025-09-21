import sys
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtWidgets import*
import sqlite3
from sqlite3 import Error
from datetime import datetime
from PyQt6.QtCore import Qt
from datetime import date


class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Σύνδεση Χρήστη")
        self.setFixedSize(500,400)
        self.setup_ui()
    def setup_ui(self):
        layout = QVBoxLayout()
        layout1=QHBoxLayout()
        layout2=QHBoxLayout()
        # Username Field
        self.username_label = QLabel("Όνομα Χρήστη:")
        self.username_label.setStyleSheet("font-family: Arial; font-size: 18px; font-weight: bold;")
        layout1.addWidget(self.username_label,alignment=Qt.AlignmentFlag.AlignBottom)
        self.username_input = QLineEdit()
        self.username_input.setStyleSheet("font-family: Arial; font-size: 18px;")
        layout1.addWidget(self.username_input,alignment=Qt.AlignmentFlag.AlignBottom)
        # Password Field
        self.password_label = QLabel("Κωδικός Πρόσβασης:")
        self.password_label.setStyleSheet("font-family: Arial; font-size: 18px; font-weight: bold;")
        layout2.addWidget(self.password_label)
        self.password_input = QLineEdit()
        self.password_input.setStyleSheet("font-family: Arial; font-size: 16px;")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout2.addWidget(self.password_input)
        layout.addLayout(layout1)
        layout.addLayout(layout2)

        # Buttons
        self.buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons,alignment=Qt.AlignmentFlag.AlignCenter|Qt.AlignmentFlag.AlignBottom)      
        self.setLayout(layout)

    def get_credentials(self):
        return self.username_input.text(), self.password_input.text()