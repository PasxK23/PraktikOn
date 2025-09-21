import sys
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtWidgets import*
import sqlite3
from sqlite3 import Error
from datetime import datetime
from PyQt6.QtCore import Qt
from datetime import date 



class Register_Agency_Dialog(QDialog):
    def __init__(self, cursor, regions):
        super().__init__()
        self.cursor = cursor
        self.regions = regions
        self.setWindowTitle("Εγγραφή Φορέα Υποδοχής")
        self.setMinimumSize(900,700)
        self.type_map={
            'Δ': "Δημόσιος",
            'Ι': "Ιδιωτικός",
            'Μ': "Μ.Κ.Ο" ,
            'Α': "Αλλο"
        }
        self.setStyleSheet("QDialog { background-color: darkblue; }")
        self.setup_ui() 
    def setup_ui(self):
 
        layout=QFormLayout()
        
        self.info1_label=QLabel("Στοιχεία Λογαριασμού Χρήστη")
        self.info1_label.setStyleSheet("font-size: 14px; text-decoration: underline;font-weight: bold")
        self.info2_label=QLabel("Στοιχεία Φορέα Υποδοχής Πρακτικής Άσκησης")
        self.info2_label.setStyleSheet("font-size: 14px; text-decoration: underline;font-weight: bold")
        self.info3_label=QLabel("Στοιχεία Υπευθύνου του Φορέα για το σύστημα Άτλας")
        self.info3_label.setStyleSheet("font-size: 14px; text-decoration: underline;font-weight: bold")
        self.username_input = QLineEdit()
        self.password_input = QLineEdit()
        self.AFM_input = QLineEdit()
        self.AFM_input.setMaxLength(9)
        self.phone_input = QLineEdit()
        self.phone_input.setMaxLength(10)
        self.email_input = QLineEdit()
        self.fname_input = QLineEdit()
        self.lname_input = QLineEdit()
        self.phoneR_input = QLineEdit()
        self.phoneR_input.setMaxLength(10)
        self.emailR_input = QLineEdit()
        self.Aname_input = QLineEdit()
        self.Location_input = QComboBox()
        
       
        self.Location_input.addItems(self.regions)
        self.empc_input=QSpinBox()
        self.password_length_label = QLabel("Μήκος Κωδικού>5")
        self.password_length_label.setStyleSheet("font-size: 11px; color: red;")
        self.empc_input.setMinimum(0)
        self.empc_input.setMaximum(10**7)
        self.type_input=QComboBox()
        
       
        self.type_input.addItems(list(self.type_map.values()))
        self.password_length_label.setVisible(False)
        layout.addRow(self.info1_label)
        layout.addRow(QLabel("Όνομα Χρήστη:"),self.username_input )
        layout.addRow(QLabel("Κωδικός Πρόσβασης:"),self.password_input )
        layout.addRow(self.password_length_label)
        self.password_length_label.setAlignment(Qt.AlignmentFlag.AlignCenter) 
        layout.addRow(self.info2_label)
        layout.addRow(QLabel("Α.Φ.Μ.:"),self.AFM_input )
        layout.addRow(QLabel("Επωνυμία :"),self.Aname_input )
        layout.addRow(QLabel("Τοποθεσία:"),self.Location_input)
        layout.addRow(QLabel("Tηλέφωνο(σταθερό):"),self.phone_input )
        layout.addRow(QLabel("Email:"),self.email_input )
        layout.addRow(QLabel("Είδος Φορέα"), self.type_input)
        layout.addRow(QLabel("Αριθμός Απασχολούμενων:"),self.empc_input)
        layout.addRow(self.info3_label)
        layout.addRow(QLabel("Όνομα Υπευθύνου:"),self.fname_input )
        layout.addRow(QLabel("Επώνυμο Υπευθύνου:"),self.lname_input )
        layout.addRow(QLabel("Tηλέφωνο Υπευθύνου:"),self.phoneR_input )
        layout.addRow(QLabel("Email Υπευθύνου:"),self.emailR_input )
        self.edit_button=QPushButton("Επεξεργασία Στοιχείων")
        layout.addRow( self.edit_button)
        self.edit_button.setVisible(False)
        self.password_input.textChanged.connect(self.update_password_length)
        self.buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.buttons.setCenterButtons(True)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        main_layout = QVBoxLayout()
        main_layout.addLayout(layout)  # Προσθήκη φόρμας
        main_layout.addWidget(self.buttons, alignment=Qt.AlignmentFlag.AlignBottom)  # Κουμπιά κάτω-κάτω
        self.setLayout(main_layout)

    def get_info(self):
        errors = []
        info_list=[self.AFM_input.text(),self.Aname_input.text(),self.Location_input.currentText(),self.username_input.text(),self.password_input.text(),self.email_input.text(),next((k for k, v in self.type_map.items() if v == self.type_input.currentText()), None),self.empc_input.text(),self.phone_input.text(),self.emailR_input.text(),self.phoneR_input.text(),self.fname_input.text(),self.lname_input.text()]
        if any(not info.strip() for info in info_list):
            errors.append( "Παρακαλώ συμπληρώστε όλα τα πεδία.")
        if len(self.password_input.text()) < 6:
            errors.append("Ο κωδικός πρέπει να έχει τουλάχιστον 6 χαρακτήρες.")
        if not self.email_input.text().count("@") or not self.emailR_input.text().count("@"):
            errors.append("Μη έγκυρη διεύθυνση email.")
        if not self.phone_input.text().isdigit() or len(self.phone_input.text())!= 10 or not self.phoneR_input.text().isdigit() or len(self.phoneR_input.text()) != 10:
            errors.append("Το τηλέφωνο πρέπει να περιέχει 10 ψηφία.")
        if not self.AFM_input.text().isdigit() or len(self.AFM_input.text())  !=9: 
            errors.append("Ο ΑΦΜ πρέπει να περιέχει 9 ψηφία.")
    
        if errors:
            QMessageBox.warning(None, "Σφάλμα Εισόδου", "\n".join(errors))
            return None
        return info_list    
    def update_password_length(self, text):
        length = len(text)
        
        if length < 6:
            self.password_length_label.setVisible(True) 
            self.password_length_label.setStyleSheet("font-size: 10px;color: red;")
        else:
            self.password_length_label.setVisible(False)