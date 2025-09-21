import sys
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
import sqlite3
from sqlite3 import Error
from datetime import datetime
from PyQt6.QtCore import Qt
from datetime import date
from register_agency_dialog import Register_Agency_Dialog
from register_office_dialog import Register_Office_Dialog
from register_student_dialog import Register_Student_Dialog
from student_menu import StudentMenu
from agency_menu import AgencyMenu
from office_menu import OfficeMenu

from login_dialog import LoginDialog


class StartApp(QMainWindow):

    def __init__(self, conn, cursor, regions):

        conn.commit()
        super().__init__()

        self.conn = conn
        self.cursor = cursor
        self.regions = regions

        self.setWindowTitle("Είσοδος Χρηστών")
        self.setFixedSize(900, 600)
        self.setWindowIcon(QIcon(r"myicon1.png"))

        self.setStyleSheet(
            f"""
            QMainWindow {{
                background-image: url("myicon1.png");
                background-repeat: no-repeat;
                background-position: center;
            }}
        """
        )
        self.setGeometry(self.rect())
        self.setup_ui()

    def setup_ui(self):

        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        self.layout = QVBoxLayout()
        self.layout1 = QHBoxLayout()
        self.role_label = QLabel("Επιλέξτε τον τύπο χρήστη:")
        self.role_label.setStyleSheet(
            """
        font-family: Arial;
        font-size: 20px;
        font-weight: bold;
        color: black;
        background-color: rgba(255, 255, 255, 0.7);
        border-radius: 5px;
    """
        )
        self.role_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout1.addWidget(self.role_label)
        self.role_combo = QComboBox()
        self.role_combo.setStyleSheet(
            """
                QComboBox {
                    font-family: Arial;
                    font-size: 20px;
                    font-weight: bold;
                    background-color: rgba(255, 255, 255, 0.7);
                    border-radius: 5px;
                    padding: 10px;
                    color: black;
                }
                QComboBox QAbstractItemView {
                    background-color: white;
                    border-radius: 10px;
                    color: black;
    }
            """
        )

        self.role_combo.addItems(["Φοιτητής", "Γραφείο Πρακτικής", "Φορέας"])
        self.layout1.addWidget(self.role_combo)
        self.button_layout = QHBoxLayout()
        self.login_button = QPushButton("Σύνδεση")
        self.login_button.setFixedSize(400, 80)
        self.login_button.setStyleSheet(
            "font-family: Arial; font-size: 14px; font-weight: bold;"
        )
        self.login_button.clicked.connect(self.login_user)
        self.button_layout.addWidget(self.login_button)
        self.register_button = QPushButton("Εγγραφή")
        self.register_button.clicked.connect(self.register_user)
        self.register_button.setFixedSize(400, 80)
        self.register_button.setStyleSheet(
            "font-family: Arial; font-size: 14px; font-weight: bold;"
        )
        self.button_layout.addWidget(self.register_button)
        self.layout.addLayout(self.layout1)
        self.layout.addLayout(self.button_layout)
        self.main_widget.setLayout(self.layout)

    def login_user(self):
        dialog = LoginDialog()
        if dialog.exec() == QDialog.DialogCode.Accepted:
            username, password = dialog.get_credentials()
            self.authenticate_user(username, password)

    def authenticate_user(self, username, password):
        user_type = self.role_combo.currentText()
        user_map = {
            "Φοιτητής": ["STUDENT", "id", StudentMenu],
            "Γραφείο Πρακτικής": ["INTERNSHIP_OFFICE", "Office_code", OfficeMenu],
            "Φορέας": ["AGENCY", "AFM", AgencyMenu],
        }

        self.cursor.execute(
            f"SELECT {user_map[user_type][1]} FROM {user_map[user_type][0]} WHERE username = ? AND password = ?",
            (username, password),
        )
        user = self.cursor.fetchone()

        if user:

            user_id = user[0]  # Αναλόγως του τύπου χρήστη, παίρνουμε το σωστό ID
            # Άνοιγμα του κατάλληλου μενού ανάλογα με τον τύπο χρήστη
            if user_type == "Φοιτητής":
                self.open_student_menu(user_id)
            elif user_type == "Φορέας":
                self.open_agency_menu(user_id)
            elif user_type == "Γραφείο Πρακτικής":
                self.open_office_menu(user_id)
        else:
            QMessageBox.warning(None, "Αποτυχία", "Λάθος όνομα χρήστη ή κωδικός.")

    def open_student_menu(self, student_id):
        self.student_menu = StudentMenu(
            student_id, self.conn, self.cursor, self.regions, self
        )
        self.hide()
        self.student_menu.show()

    def open_agency_menu(self, agency_afm):
        self.agency_menu = AgencyMenu(
            agency_afm, self.conn, self.cursor, self.regions, self
        )
        self.hide()
        self.agency_menu.show()

    def open_office_menu(self, office_code):
        self.office_menu = OfficeMenu(
            office_code, self.conn, self.cursor, self.regions, self
        )
        self.hide()
        self.office_menu.show()

    def register_user(self):
        user_type = self.role_combo.currentText()
        user_map = {
            "Φοιτητής": ["STUDENT", "id", Register_Student_Dialog],
            "Γραφείο Πρακτικής": [
                "INTERNSHIP_OFFICE",
                "Office_code",
                Register_Office_Dialog,
            ],
            "Φορέας": ["AGENCY", "AFM", Register_Agency_Dialog],
        }
        dialog = user_map[user_type][2](self.cursor, self.regions)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            if user_type == "Φοιτητής":
                student_info = dialog.get_info()
                if student_info != None:
                    try:
                        self.cursor.execute(
                            "INSERT into STUDENT VALUES(NULL,?,?,?,?,?,?,?,?,?,?)",
                            student_info,
                        )
                        QMessageBox.information(
                            None, "Επιτυχία", " Η εγγραφή σας ολοκληρώθηκε!"
                        )
                        id = self.cursor.lastrowid
                        self.open_student_menu(id)
                    except sqlite3.IntegrityError as e:
                        error_message = str(e)
                        if "Username" in error_message:
                            QMessageBox.warning(
                                None,
                                "Σφάλμα",
                                " Το όνομα χρήστη υπάρχει ήδη, Παρακαλώ επιλέξτε άλλο",
                            )
                        elif "AMA" in error_message:
                            QMessageBox.warning(
                                None, "Σφάλμα", " Ο ΑΜΑ υπάρχει ήδη καταχωρημένος!"
                            )
                        elif "PASS" in error_message:
                            QMessageBox.warning(
                                None,
                                "Σφάλμα",
                                "Το μήκος του κωδικού πρέπει να είναι μεγαλύτερο του 5!",
                            )
                        else:
                            QMessageBox.warning(
                                None, "Σφάλμα", f"Άλλο σφάλμα: {error_message}"
                            )
            elif user_type == "Γραφείο Πρακτικής":
                office_info = dialog.get_info()
                if office_info != None:
                    try:
                        self.cursor.execute(
                            "INSERT into INTERNSHIP_OFFICE VALUES(NULL,?,?,?,?,?,?,?,?,?)",
                            office_info[:-2],
                        )
                        office_code = self.cursor.lastrowid
                        splited = [
                            title.strip()
                            for title in office_info[-2].split(",")
                            if title.strip()
                        ]
                        titles = ",".join(["?" for _ in splited])
                        self.cursor.execute(
                            f"UPDATE Department set office_code=? where title in ({titles}) and university_title=?",
                            [office_code] + splited + [office_info[-1]],
                        )
                        QMessageBox.information(
                            None, "Επιτυχία", " Η εγγραφή σας ολοκληρώθηκε!"
                        )
                        self.open_office_menu(office_code)
                    except sqlite3.IntegrityError as e:
                        error_message = str(e)
                        if "Username" in error_message:
                            QMessageBox.warning(
                                None,
                                "Σφάλμα",
                                " Το όνομα χρήστη υπάρχει ήδη, Παρακαλώ επιλέξτε άλλο",
                            )
                        elif "PASS" in error_message:
                            QMessageBox.warning(
                                None,
                                "Σφάλμα",
                                "Το μήκος του κωδικού πρέπει να είναι μεγαλύτερο του 5!",
                            )
                        else:
                            QMessageBox.warning(
                                None, "Σφάλμα", f"Άλλο σφάλμα: {error_message}"
                            )
            elif user_type == "Φορέας":
                agency_info = dialog.get_info()
                if agency_info != None:
                    try:
                        self.cursor.execute(
                            "INSERT into AGENCY VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)",
                            agency_info,
                        )
                        QMessageBox.information(
                            None, "Επιτυχία", " Η εγγραφή σας ολοκληρώθηκε!"
                        )
                        self.open_agency_menu(agency_info[0])
                    except sqlite3.IntegrityError as e:
                        error_message = str(e)
                        if "Username" in error_message:
                            QMessageBox.warning(
                                None,
                                "Σφάλμα",
                                " Το όνομα χρήστη υπάρχει ήδη, Παρακαλώ επιλέξτε άλλο",
                            )
                        elif "PASS" in error_message:
                            QMessageBox.warning(
                                None,
                                "Σφάλμα",
                                "Το μήκος του κωδικού πρέπει να είναι μεγαλύτερο του 5!",
                            )
                        elif "AFM" in error_message:
                            QMessageBox.warning(
                                None, "Σφάλμα", " Ο ΑΦΜ υπάρχει ήδη καταχωρημένος!"
                            )
                        else:
                            QMessageBox.warning(
                                None, "Σφάλμα", f"Άλλο σφάλμα: {error_message}"
                            )
        else:
            QMessageBox.information(None, "Ακύρωση", "Η εγγραφή ακυρώθηκε.")
