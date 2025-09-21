import sys
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtWidgets import*
import sqlite3
from sqlite3 import Error
from datetime import datetime
from PyQt6.QtCore import Qt
from datetime import date 


class Register_Office_Dialog(QDialog):
    def __init__(self, cursor, regions):
        super().__init__()
        self.cursor = cursor
        self.regions = regions
        self.setWindowTitle("Εγγραφή Γραφείου Πρακτικής")
        self.setFixedSize(800,600)
        self.setStyleSheet("QDialog { background-color: darkblue; }")
        self.setup_ui() 
    def setup_ui(self):
            layout=QFormLayout()
            self.info1_label=QLabel("Στοιχεία Λογαριασμού Χρήστη")
            self.info1_label.setStyleSheet("font-size: 14px; text-decoration: underline;font-weight: bold")
            self.info2_label=QLabel("Στοιχεία Γραφείου Πρακτικής Άσκησης")
            self.info2_label.setStyleSheet("font-size: 14px; text-decoration: underline;font-weight: bold")
            self.info3_label=QLabel("Στοιχεία Υπευθύνου για το Γραφείο Πρακτικής Άσκησης")
            self.info3_label.setStyleSheet("font-size: 14px; text-decoration: underline;font-weight: bold")
            self.info4_label=QLabel("Διαθέσιμα Τμήματα που εκπροσωπεί το Γραφείο")
            self.info4_label.setStyleSheet("font-size: 14px; text-decoration: underline;font-weight: bold")
            self.username_input = QLineEdit()
            self.password_input = QLineEdit()
            self.password_length_label = QLabel("Μήκος Κωδικού>5")
            self.password_length_label.setStyleSheet("font-size: 11px; color: red;")
            self.address_input = QLineEdit()
            self.phone_input = QLineEdit()
            self.phone_input.setMaxLength(10)
            self.email_input = QLineEdit()
            self.fname_input = QLineEdit()
            self.lname_input = QLineEdit()
            self.phoneR_input = QLineEdit()
            self.phoneR_input.setMaxLength(10)
            self.emailR_input = QLineEdit()
            self.dep_found=QLabel("Δεν υπάρχουν διαθέσιμα τμήματα για το πανεπιστήμιο")
            self.dep_found.setVisible(False)
            self.uni_input=QComboBox()
            self.uni_input.addItem("Κάνετε επιλογή")
            self.uni_input.model().item(0).setEnabled(False)
            self.password_length_label.setVisible(False)
            self.cursor.execute("Select * from University")
            rows=self.cursor.fetchall()
            for row in rows:
                for value in row:
                    self.uni_input.addItem(str(value))
            self.dep_input = QComboBox()
            self.dep_input.setEditable(True)
            self.dep_input.lineEdit().setReadOnly(True)
            self.uni_input.currentIndexChanged.connect(self.load_departments)
            # Δημιουργία QListWidget για το dropdown
            self.list_widget = QListWidget()
            self.checkbox_items = {}
            self.dep_input.setModel(self.list_widget.model())
            self.dep_input.setView(self.list_widget)
            self.off_code_label=QLabel()
            self.off_code_label.setVisible(False)
            layout.addRow(self.off_code_label)
            layout.addRow(self.info1_label)
            layout.addRow(QLabel("Όνομα Χρήστη:"),self.username_input )
            layout.addRow(QLabel("Κωδικός Πρόσβασης:"),self.password_input )
            layout.addRow(self.password_length_label)
            self.password_length_label.setAlignment(Qt.AlignmentFlag.AlignCenter) 
            layout.addRow(self.info2_label)
            layout.addRow(QLabel("Διεύθυνση Γραφείου:"),self.address_input )
            layout.addRow(QLabel("Τηλέφωνο Γραφείου(σταθερό) :"),self.phone_input )
            layout.addRow(QLabel("Email Γραφείου:"),self.email_input )
            
            layout.addRow(self.info3_label)
            layout.addRow(QLabel("Όνομα Υπευθύνου:"),self.fname_input )
            layout.addRow(QLabel("Επώνυμο Υπευθύνου:"),self.lname_input )
            layout.addRow(QLabel("Tηλέφωνο Υπευθύνου:"),self.phoneR_input )
            layout.addRow(QLabel("Email Υπευθύνου:"),self.emailR_input )
            layout.addRow(self.info4_label)
            layout.addRow(QLabel("Πανεπιστήμιο:"),self.uni_input )
            layout.addRow(QLabel("Τμήματα:"), self.dep_input) 
            layout.addRow(self.dep_found)
            self.dep_found.setStyleSheet("font-size: 10px;color: red;")
            self.dep_found.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.password_input.textChanged.connect(self.update_password_length)
            self.edit_button = QPushButton("Επεξεργασία Στοιχείων")
            layout.addRow(self.edit_button)
            self.edit_button.setVisible(False)
            
            # Buttons
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
        info_list=[self.phone_input.text(),self.email_input.text(),self.address_input.text(),self.username_input.text(),self.password_input.text(),self.fname_input.text(),self.lname_input.text(),self.emailR_input.text(),self.phoneR_input.text(),self.dep_input.currentText(),self.uni_input.currentText()]
        if any(not info.strip() for info in info_list):
            errors.append( "Παρακαλώ συμπληρώστε όλα τα πεδία.")
        if len(self.password_input.text()) < 6:
            errors.append("Ο κωδικός πρέπει να έχει τουλάχιστον 6 χαρακτήρες.")
        if not self.email_input.text().count("@") or not self.emailR_input.text().count("@"):
            errors.append("Μη έγκυρη διεύθυνση email.")
        if not self.phone_input.text().isdigit() or len(self.phone_input.text())!= 10 or not self.phoneR_input.text().isdigit() or len(self.phoneR_input.text()) != 10:
            errors.append("Το τηλέφωνο πρέπει να περιέχει 10 ψηφία.")
    
        if errors:
            QMessageBox.warning(None, "Σφάλμα Εισόδου", "\n".join(errors))
            return None
        return info_list    
    def update_password_length(self, text):
        length = len(text)
        # Αλλαγή χρώματος κειμένου κωδικού ανάλογα με το μήκος
        if length < 6:
            self.password_length_label.setVisible(True) 
            self.password_length_label.setStyleSheet("font-size: 10px;color: red;")
        else:
            self.password_length_label.setVisible(False) 
    def add_multi_select_item(self,text):
            list_item = QListWidgetItem(self.list_widget)
            checkbox = QCheckBox(text)
            self.list_widget.setItemWidget(list_item, checkbox)
            self.checkbox_items[text] = checkbox 
            checkbox.stateChanged.connect(self.update_multi_select_line_edit)

        # Μέθοδος για ενημέρωση του κειμένου στο QLineEdit
    def update_multi_select_line_edit(self):
            selected_items = [text for text, cb in self.checkbox_items.items() if cb.isChecked()]
            self.dep_input.lineEdit().setText(", ".join(selected_items))   
    def load_departments(self):
        self.cursor.execute("SELECT title FROM department WHERE university_title= ? and Office_Code is NULL", (self.uni_input.currentText(),))
        departments = self.cursor.fetchall()
        # Προσθήκη τμημάτων στο ComboBox
        self.dep_input.clear()
        self.checkbox_items.clear()
        if departments:
            self.dep_found.setVisible(False) 
            for (dep) in departments:
                for value in dep:
                    self.add_multi_select_item(value)
        else:
            self.dep_found.setVisible(True)