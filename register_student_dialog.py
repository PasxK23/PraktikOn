import sys
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtWidgets import*
import sqlite3
from sqlite3 import Error
from datetime import datetime
from PyQt6.QtCore import Qt
from datetime import date

 


class Register_Student_Dialog(QDialog):
    def __init__(self, cursor, regions):
        super().__init__()
        self.cursor = cursor
        self.regions = regions
        self.setWindowTitle("Εγγραφή Φοιτητή")
        self.setFixedSize(800,600)
        self.setStyleSheet("QDialog { background-color: darkblue; }")
        self.setup_ui()
    def setup_ui(self):   
        layout=QFormLayout()
        self.info1_label=QLabel("Στοιχεία Λογαριασμού Χρήστη")
        self.info1_label.setStyleSheet("font-size: 14px; text-decoration: underline;font-weight: bold")
        self.info2_label=QLabel("Στοιχεία Φοιτητή")
        self.info2_label.setStyleSheet("font-size: 14px; text-decoration: underline;font-weight: bold")
        self.info3_label=QLabel("Στοιχεία Επικοινωνίας")
        self.info3_label.setStyleSheet("font-size: 14px; text-decoration: underline;font-weight: bold")
        self.username_input = QLineEdit()
        self.password_input = QLineEdit()
        self.address_input = QLineEdit()
        self.phone_input = QLineEdit()
        self.phone_input.setMaxLength(10)
        self.fname_input = QLineEdit()
        self.lname_input = QLineEdit()
        self.am_input = QLineEdit()
        self.email_input = QLineEdit()
        self.ama_input =QLineEdit()
        self.ama_input.setMaxLength(8)  
        self.uni_input=QComboBox()
        self.password_length_label = QLabel("Μήκος Κωδικού>5")
        self.password_length_label.setStyleSheet("font-size: 10px; color: red;")
        self.password_length_label.setVisible(False)
        self.uni_input.addItem("Κάνετε επιλογή")
        self.uni_input.model().item(0).setEnabled(False)
        self.cursor.execute("Select * from University")
        rows=self.cursor.fetchall()
        for row in rows:
            for value in row:
                self.uni_input.addItem(str(value))
        
                
        self.uni_input.currentIndexChanged.connect(self.load_departments)        
        self.dep_input=QComboBox()
        layout.addRow(self.info1_label)
        layout.addRow(QLabel("Όνομα Χρήστη:"),self.username_input )
        layout.addRow(QLabel("Κωδικός Πρόσβασης:"),self.password_input )
        layout.addRow(self.password_length_label)
        self.password_length_label.setAlignment(Qt.AlignmentFlag.AlignCenter) 
        layout.addRow(self.info2_label)
        layout.addRow(QLabel("Όνομα:"),self.fname_input )
        layout.addRow(QLabel("Επώνυμο :"),self.lname_input )
        layout.addRow(QLabel("Αριθμός Μητρώου:"),self.am_input )
        layout.addRow(QLabel("ΑΜΑ:"),self.ama_input )
        layout.addRow(QLabel("Πανεπιστήμιο:"),self.uni_input )
        layout.addRow(QLabel("Τμήμα:"),self.dep_input )
        layout.addRow(self.info3_label)
        layout.addRow(QLabel("Email:"),self.email_input )
        layout.addRow(QLabel("Tηλέφωνο:"),self.phone_input )
        self.edit_button=QPushButton("Επεξεργασία Στοιχείων")
        layout.addRow(self.edit_button)
        self.edit_button.setVisible(False)

        self.password_input.textChanged.connect(self.update_password_length)
        
        # Buttons
        self.buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.buttons.setCenterButtons(True)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        main_layout = QVBoxLayout()
        main_layout.addLayout(layout)  # Προσθήκη φόρμας
        main_layout.addWidget(self.buttons, alignment=Qt.AlignmentFlag.AlignBottom)  # Κουμπιά κάτω-κάτω
        self.setLayout(main_layout)
    def update_password_length(self, text):
        length = len(text)
        # Αλλαγή χρώματος κειμένου κωδικού ανάλογα με το μήκος
        if length < 6:
            self.password_length_label.setVisible(True) 
            self.password_length_label.setStyleSheet("font-size: 10px;color: red;")
        else:
            self.password_length_label.setVisible(False)   
    def load_departments(self):
        self.cursor.execute("SELECT title FROM department WHERE university_title= ?", (self.uni_input.currentText(),))
        departments = self.cursor.fetchall()
        # Προσθήκη τμημάτων στο ComboBox
        self.dep_input.clear()
        if departments:
            for (dep) in departments:
                for value in dep:
                    self.dep_input.addItem(value)
        else:
            self.dep_input.addItem("Δεν υπάρχουν τμήματα για το πανεπιστήμιο")     


    def get_info(self):
        errors = []
        if len(self.password_input.text()) < 6:
            errors.append("Ο κωδικός πρέπει να έχει τουλάχιστον 6 χαρακτήρες.")
        if not self.email_input.text().count("@"):
            errors.append("Μη έγκυρη διεύθυνση email.")
        if  not self.phone_input.text().isdigit() or len(self.phone_input.text()) != 10:
            errors.append("Το τηλέφωνο πρέπει να περιέχει 10 ψηφία.")
        if not self.ama_input.text().isdigit() or len(self.ama_input.text()) != 8:
            errors.append("Ο ΑΜΑ πρέπει να περιέχει 8 αριθμούς.")
        if not self.am_input.text().isdigit():
            errors.append("Μη έγκυρος Αριθμός Μητρώου")    

        if errors:
            QMessageBox.warning(None, "Σφάλμα Εισόδου", "\n".join(errors))
            return None  # Επιστροφή None αν υπάρχει πρόβλημα
        info_list=[self.fname_input.text(),self.lname_input.text(),self.phone_input.text(),self.am_input.text(),self.email_input.text(),self.username_input.text(),self.password_input.text(),self.ama_input.text(),self.dep_input.currentText(),self.uni_input.currentText()]
        return info_list