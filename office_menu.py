import sys
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
import sqlite3
from sqlite3 import Error
from datetime import datetime
from PyQt6.QtCore import Qt
from datetime import date

from register_office_dialog import Register_Office_Dialog


class OfficeMenu(QMainWindow):
    def __init__(self, office_code, conn, cursor, regions, startapp):

        super().__init__()
        self.conn = conn
        self.cursor = cursor
        self.regions = regions
        self.office_code = office_code
        self.Startapp = startapp
        self.initUI()
        self.type_map = {"Δ": "Δημόσιος", "Ι": "Ιδιωτικός", "Μ": "Μ.Κ.Ο", "Α": "Αλλο"}

    def initUI(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.status_colors = {
            "Ε": "lightblue",
            "Π": "white",
            "Α": "darkviolet",
            "Υ": "yellow",
            "Ο": "green",
            "Χ": "red",
        }

        # Δημιουργία layout
        layout = QVBoxLayout()

        # Προσθήκη ετικέτας
        self.label = QLabel("Επιλέξτε μία από τις παρακάτω επιλογές:")
        layout.addWidget(self.label)

        # Προσθήκη κουμπιών
        self.button1 = QPushButton("Στοιχεία Γραφείου")
        self.button1.clicked.connect(self.view_office_details)
        layout.addWidget(self.button1)

        self.button2 = QPushButton("Προβολή Επιλεγμένων Θεσεών")
        self.button2.clicked.connect(self.view_selected_positions)
        layout.addWidget(self.button2)

        self.button3 = QPushButton("Προβολή Φοιτητών")
        self.button3.clicked.connect(lambda: self.view_students(pos_code=None))
        layout.addWidget(self.button3)

        self.button4 = QPushButton("Προβολή όλων των Θεσεών")
        self.button4.clicked.connect(self.view_all_positions)
        layout.addWidget(self.button4)

        self.button5 = QPushButton("Αξιολόγηση Φορέα Υποδοχής")
        self.button5.clicked.connect(self.evaluation_agency)
        layout.addWidget(self.button5)

        self.button6 = QPushButton("Έξοδος")
        self.button6.clicked.connect(self.exit)
        layout.addWidget(self.button6)

        # Σύνδεση του layout με το central_widget
        central_widget.setLayout(layout)

        # Τίτλος παραθύρου
        self.setFixedSize(750, 300)
        self.setWindowTitle("Γραφείο Μενού")

    def exit(self):
        for widget in QApplication.topLevelWidgets():
            if widget is self.Startapp and isinstance(widget, QMainWindow):
                widget.show()  # Εμφανίζει το StartApp
        self.close()

    def view_office_details(self):
        self.cursor.execute(
            "SELECT * FROM INTERNSHIP_OFFICE as O join Department as D on O.office_code=D.office_code WHERE O.Office_Code=?",
            (self.office_code,),
        )
        rows = self.cursor.fetchall()
        office_with_dep = True
        if not rows:
            self.cursor.execute(
                "SELECT * FROM INTERNSHIP_OFFICE as O  WHERE O.Office_Code=?",
                (self.office_code,),
            )
            office_with_dep = False
            rows = self.cursor.fetchall()

        self.dialog = Register_Office_Dialog(self.cursor, self.regions)
        self.dialog.dep_found.setVisible(False)
        self.dialog.off_code_label.setText(f"Κωδικός Γραφείου:{self.office_code}")
        self.dialog.off_code_label.setStyleSheet("font-size: 14px;font-weight: bold")
        self.dialog.off_code_label.setVisible(True)
        self.dialog.setWindowTitle("Στοιχεία Γραφείου Πρακτικής")
        self.dialog.username_input.setText(f"{rows[0][4]}")
        self.dialog.password_input.setText(f"{rows[0][5]}")
        self.dialog.address_input.setText(f"{rows[0][3]}")
        self.dialog.phone_input.setText(f"{rows[0][1]}")
        self.dialog.email_input.setText(f"{rows[0][2]}")
        self.dialog.fname_input.setText(f"{rows[0][6]}")
        self.dialog.lname_input.setText(f"{rows[0][7]}")
        self.dialog.phoneR_input.setText(f"{rows[0][9]}")
        self.dialog.emailR_input.setText(f"{rows[0][8]}")
        dep_list = []
        if office_with_dep:
            self.dialog.uni_input.setCurrentText(f"{rows[0][12]}")
            for row in rows:
                dep_list.append(row[10])
                self.dialog.add_multi_select_item(row[10])
            self.dialog.dep_input.setCurrentText(", ".join(dep_list))
        self.dialog.username_input.setReadOnly(True)
        self.dialog.password_input.setReadOnly(True)
        self.dialog.address_input.setReadOnly(True)
        self.dialog.phone_input.setReadOnly(True)
        self.dialog.email_input.setReadOnly(True)
        self.dialog.fname_input.setReadOnly(True)
        self.dialog.lname_input.setReadOnly(True)
        self.dialog.phoneR_input.setReadOnly(True)
        self.dialog.emailR_input.setReadOnly(True)
        self.dialog.uni_input.setEnabled(not True)
        self.dialog.dep_input.setEnabled(not True)
        self.dialog.edit_button.setVisible(True)
        self.dialog.dep_found.setVisible(False)
        self.dialog.edit_button.clicked.connect(self.set_details_editable)
        self.edit_pressed = False
        if (
            self.dialog.exec() == QDialog.DialogCode.Accepted
            and self.edit_pressed == True
        ):
            office_info = self.dialog.get_info()
            if office_info != None:
                try:
                    self.cursor.execute(
                        "UPDATE  INTERNSHIP_OFFICE SET  Phone=?, Email=?, Address=?, Username=?, Password=?, Responsible_First_Name=?, Responsible_Last_Name=?, Responsible_Email=?, Responsible_Phone=? WHERE office_code=?",
                        office_info[:-2] + [self.office_code],
                    )
                    splited = [
                        title.strip()
                        for title in office_info[-2].split(",")
                        if title.strip()
                    ]
                    titles = ",".join(["?" for _ in splited])

                    if office_with_dep:
                        placehold = ", ".join(["?" for _ in dep_list])
                        self.cursor.execute(
                            f"UPDATE Department set office_code=? where title in ({placehold}) and university_title=?",
                            [None] + dep_list + [rows[0][12]],
                        )
                    self.cursor.execute(
                        f"UPDATE Department set office_code=? where title in ({titles}) and university_title=?",
                        [self.office_code] + splited + [office_info[-1]],
                    )
                    QMessageBox.information(
                        None, "Επιτυχία", "Τα στοιχεία ενημερώθηκαν"
                    )
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

    def set_details_editable(self):
        self.dialog.edit_button.setEnabled(False)
        self.dialog.username_input.setReadOnly(False)
        self.dialog.password_input.setReadOnly(False)
        self.dialog.address_input.setReadOnly(False)
        self.dialog.phone_input.setReadOnly(False)
        self.dialog.email_input.setReadOnly(False)
        self.dialog.fname_input.setReadOnly(False)
        self.dialog.lname_input.setReadOnly(False)
        self.dialog.phoneR_input.setReadOnly(False)
        self.dialog.emailR_input.setReadOnly(False)
        self.dialog.uni_input.setEnabled(not False)
        self.dialog.dep_input.setEnabled(not False)
        self.edit_pressed = True

    def show_selected_position(self, row):
        if row:
            # Δημιουργία παραθύρου λεπτομερειών
            self.details_window = QWidget()
            self.details_window.setWindowTitle(
                f"Λεπτομέρειες Θέσης #{row['Position_number']}"
            )

            details_layout = QVBoxLayout()

            region_label = QLabel(f"Περιοχή: {row['Region']}")
            description_label = QLabel(f"Περιγραφή: ")
            description = QLabel(f"{row['Description']}")
            description.setStyleSheet("color: white")
            description.setWordWrap(True)
            scroll_area2 = QScrollArea()
            scroll_area2.setWidgetResizable(True)
            description_widget = QWidget()
            description_layout = QVBoxLayout()
            description_layout.addWidget(description)
            description_widget.setLayout(description_layout)
            scroll_area2.setWidget(description_widget)

            duration_label = QLabel(f"Διάρκεια(σε μήνες): {row['Duration']}")

            type_label = QLabel(f"Είδος Θέσης: {row['Type']}")
            insertion_date_label = QLabel(
                f"Ημερομηνία Εισαγωγής: {row['Insertion_date']}"
            )
            supervisor_fname_lname_label = QLabel(
                f"Όνοματεπώνυμο Επόπτη : {row[5]} {row[6]}"
            )
            supervisor_phone_label = QLabel(f"Τηλέφωνο Επόπτη : {row[7]}")
            supervisor_email_label = QLabel(f"Email Επόπτη : {row[8]}")
            specialty_name_label = QLabel("Αντικείμενα:")
            specialty_list = QLabel(f"{row[9]}")
            specialty_list.setStyleSheet("color: white")
            specialty_list.setWordWrap(True)
            scroll_area1 = QScrollArea()
            scroll_area1.setWidgetResizable(True)
            specialties_widget = QWidget()
            specialties_layout = QVBoxLayout()
            specialties_layout.addWidget(specialty_list)
            specialties_widget.setLayout(specialties_layout)
            scroll_area1.setWidget(specialties_widget)

            # Προσθήκη των λεπτομερειών στη διάταξη
            details_layout.addWidget(QLabel(f"Τίτλος: {row['Title']}"))
            details_layout.addWidget(description_label)
            details_layout.addWidget(scroll_area2)

            details_layout.addWidget(duration_label)
            details_layout.addWidget(type_label)
            details_layout.addWidget(region_label)
            details_layout.addWidget(insertion_date_label)
            details_layout.addWidget(supervisor_fname_lname_label)
            details_layout.addWidget(supervisor_phone_label)
            details_layout.addWidget(supervisor_email_label)
            self.details_window.setFixedSize(500, 400)
            edit_button = QPushButton("Στοιχεία Φορέα")
            edit_button.clicked.connect(
                lambda _, r=row["Agency_Afm"]: self.show_agency_details(r)
            )

            if row["Status"] != "Π":
                self.cursor.execute(
                    "SELECT * FROM STUDENT WHERE ID = ?", (row["Student_Id"],)
                )
                self.stud_info = self.cursor.fetchone()
                student_key_ID_label = QLabel(f"Κωδικός Φοιτητή: {row['Student_Id']}")
                student__ID_label = QLabel(
                    f"Αρ. Μητρώου Φοιτητή: {self.stud_info['Student_Id']}"
                )
                student_name_label = QLabel(
                    f"Ονοματεπώνυμο Φοιτητή: {self.stud_info['Name']} {self.stud_info['Surname']}"
                )
                student_phone_label = QLabel(
                    f"Τηλέφωνο Φοιτητή: {self.stud_info['Phone']}"
                )
                student_email_label = QLabel(
                    f"Email Φοιτητή: {self.stud_info['Email']}"
                )
                student_uni_label = QLabel(
                    f"Πανεπιστήμιο: {self.stud_info['University_title']}"
                )
                student_dep_label = QLabel(
                    f"Τμήμα: {self.stud_info['Department_title']}"
                )
                if row["Status"] != "Ο":
                    date1_label = QLabel(
                        f"Προβλεπόμενη Ημερομηνία Εναρξης: {row['Predicted_Start_Date']}"
                    )
                    date2_label = QLabel(
                        f"Προβλεπόμενη Ημερομηνία Λήξης: {row['Predicted_End_Date']}"
                    )
                else:
                    date1_label = QLabel(
                        f"Ημερομηνία Εναρξης: {row['Internship_Start_Date']}"
                    )
                    date2_label = QLabel(
                        f"Ημερομηνία Λήξης: {row['Internship_End_Date']}"
                    )
                self.details_window.setFixedSize(500, 700)

                info1_label = QLabel("Στοιχεία Φοιτητή")
                info1_label.setStyleSheet(
                    "font-size: 14px; text-decoration: underline;font-weight: bold"
                )
                info2_label = QLabel("Στοιχεία Τμήματος")
                info2_label.setStyleSheet(
                    "font-size: 14px; text-decoration: underline;font-weight: bold"
                )

                # Προσθήκη των λεπτομερειών στη διάταξη
                details_layout.addWidget(date1_label)
                details_layout.addWidget(date2_label)
                details_layout.addWidget(info1_label)
                details_layout.addWidget(student_key_ID_label)
                details_layout.addWidget(student__ID_label)
                details_layout.addWidget(student_name_label)
                details_layout.addWidget(student_phone_label)
                details_layout.addWidget(student_email_label)
                details_layout.addWidget(info2_label)
                details_layout.addWidget(student_uni_label)
                details_layout.addWidget(student_dep_label)

            details_layout.addWidget(specialty_name_label)
            details_layout.addWidget(scroll_area1)
            details_layout.addWidget(edit_button)
            self.details_window.setLayout(details_layout)
            self.details_window.setWindowModality(Qt.WindowModality.ApplicationModal)

            self.details_window.show()

    def view_selected_positions(self):
        self.cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_matching_student_id ON Matching (Student_ID,Position_Number);"
        )
        self.cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_matching_position_number ON Matching (Position_Number);"
        )
        self.cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_specialty_position_number ON Specialty_Position (Position_Number);"
        )
        self.cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_position_position_number ON Position (Position_Number);"
        )
        self.cursor.execute("DROP VIEW IF EXISTS SELECTED_POSITIONS")
        self.cursor.execute(
            """CREATE VIEW IF NOT EXISTS SELECTED_POSITIONS AS
SELECT
    P.Position_Number,
    P.Title,
    P.region,
    P.Insertion_Date,
    P.status,
    P.Supervisor_First_Name,
    P.Supervisor_Last_Name,
    P.Supervisor_Phone,
    P.Supervisor_Email,
    GROUP_CONCAT(S.Object_Name, ', ') AS Specialties,
    P.Description,
    P.Duration,
    P.type,
    P.Agency_AFM,
    P.office_code,
    M.Student_id,
    M.predicted_start_date,
    M.predicted_end_date,
    P.Internship_start_date,
    P.Internship_end_date
FROM
    Position AS P
LEFT JOIN
    Matching AS M ON P.Position_Number = M.Position_Number
JOIN
    Specialty_Position AS S ON S.Position_Number = P.Position_Number
GROUP BY
    P.Position_Number;
"""
        )

        self.cursor.execute(
            "SELECT * from Selected_positions where office_code=?", (self.office_code,)
        )
        rows = self.cursor.fetchall()

        self.position_window = QWidget()
        self.position_window.setWindowTitle("Επιλεγμένες Θέσεις")
        scroll_area = QScrollArea(self.position_window)
        scroll_area.setWidgetResizable(True)

        central_widget = QWidget()
        central_layout = QVBoxLayout(central_widget)
        if rows:
            for row in rows:

                if row:
                    details_group = QGroupBox(f"Θέση #{row[0]}")
                    details_group.setStyleSheet(
                        f"""
                QGroupBox {{
            background-color: {self.status_colors.get(row['Status'])};
        }}
        QGroupBox::title {{
            color: black;
            font-weight: bold;
                }}
                """
                    )

                    details_layout = QVBoxLayout()

                    title_button = QPushButton(f"{row[1]}")
                    title_button.clicked.connect(
                        lambda _, r=row: self.show_selected_position(r)
                    )
                    title_button.setStyleSheet("font-size:14px;color:white")
                    central_widget.setStyleSheet("QLabel { color: black; }")

                    top_layout = QHBoxLayout()
                    top_layout.addWidget(title_button)

                    region_label = QLabel(f"Περιοχή: {row[2]}")
                    insertion_date_label = QLabel(f"Ημερομηνία Εισαγωγής: {row[3]}")
                    supervisor_fname_lname_label = QLabel(
                        f"Όνοματεπώνυμο Επόπτη : {row[5]} {row[6]}"
                    )
                    supervisor_phone_label = QLabel(f"Τηλέφωνο Επόπτη : {row[7]}")
                    supervisor_email_label = QLabel(f"Email Επόπτη : {row[8]}")
                    specialty_name_label = QLabel("Αντικείμενα:")
                    specialty_list = QLabel(f"{row[9]}")
                    specialty_list.setStyleSheet("color: white;")
                    specialty_list.setWordWrap(True)
                    scroll_area1 = QScrollArea()

                    scroll_area1.setWidgetResizable(True)

                    specialties_widget = QWidget()
                    specialties_layout = QVBoxLayout()
                    specialties_layout.addWidget(specialty_list)
                    specialties_widget.setLayout(specialties_layout)
                    scroll_area1.setWidget(specialties_widget)
                    details_layout.addLayout(top_layout)
                    details_layout.addWidget(region_label)
                    details_layout.addWidget(insertion_date_label)
                    details_layout.addWidget(supervisor_fname_lname_label)
                    details_layout.addWidget(supervisor_phone_label)
                    details_layout.addWidget(supervisor_email_label)
                    if row["Student_ID"] is not None:
                        self.cursor.execute(
                            "SELECT Name,Surname,Phone,Email,AMA,Student_ID FROM STUDENT WHERE ID = ?",
                            (row["Student_ID"],),
                        )
                        self.stud = self.cursor.fetchone()
                        student_ID_key_label = QLabel(
                            f"ID Φοιτητή: {row['Student_ID']}"
                        )
                        student_ID_label = QLabel(
                            f"Αρ. Μητρώου Φοιτητή: {self.stud [5]}"
                        )
                        student_name_label = QLabel(
                            f"Ονοματεπώνυμο Φοιτητή: {self.stud[0]} {self.stud[1]}"
                        )
                        student_phone_label = QLabel(
                            f"Τηλέφωνο Φοιτητή: {self.stud[2]}"
                        )
                        student_email_label = QLabel(f"Email Φοιτητή: {self.stud[3]}")
                        details_layout.addWidget(student_ID_key_label)
                        details_layout.addWidget(student_ID_label)
                        details_layout.addWidget(student_name_label)
                        details_layout.addWidget(student_phone_label)
                        details_layout.addWidget(student_email_label)

                    details_layout.addWidget(specialty_name_label)
                    details_layout.addWidget(scroll_area1)

                    if row["Status"] == "Π":
                        let_go_button = QPushButton("Αποδεσμεύεση Θέσης")
                        let_go_button.clicked.connect(
                            lambda _, r=row[0]: self.let_go(r)
                        )
                        let_go_layout = (
                            QHBoxLayout()
                        )  # Χρησιμοποιούμε νέο layout για το κουμπί
                        # Προσθέτουμε κενό χώρο πριν το κουμπί
                        let_go_layout.addWidget(let_go_button)
                        let_go_layout.addStretch(1)  # Τοποθετούμε το κουμπί δεξιά
                        matching_button = QPushButton("Αντιστοίχηση Θέσης")
                        matching_button.clicked.connect(
                            lambda _, r=row[0]: self.view_students(pos_code=r)
                        )
                        let_go_layout.addWidget(matching_button)
                        details_layout.addLayout(let_go_layout)
                    elif row["Status"] == "Α":
                        del_match_button = QPushButton("Ακύρωση Αντιστοίχησης")
                        del_match_button.clicked.connect(
                            lambda _, r=row[0]: self.delete_matching(r)
                        )
                        del_match_layout = (
                            QHBoxLayout()
                        )  # Χρησιμοποιούμε νέο layout για το κουμπί
                        # Προσθέτουμε κενό χώρο πριν το κουμπί
                        del_match_layout.addWidget(del_match_button)
                        del_match_layout.addStretch(1)  # Τοποθετούμε το κουμπί δεξιά
                        set_on_button = QPushButton("Κατάσταση Θέσης σε Υπο-διενέργεια")
                        set_on_button.clicked.connect(
                            lambda _, r=row[0]: self.set_on_going_position(r)
                        )
                        del_match_layout.addWidget(set_on_button)
                        details_layout.addLayout(del_match_layout)
                    elif row["Status"] == "Υ":
                        success_button = QPushButton("Ολοκλήρωση θέσης επιτυχώς")
                        success_button.clicked.connect(
                            lambda _, r=row[0]: self.set_position_done(r, result=True)
                        )
                        success_button_layout = (
                            QHBoxLayout()
                        )  # Χρησιμοποιούμε νέο layout για το κουμπί
                        # Προσθέτουμε κενό χώρο πριν το κουμπί
                        success_button_layout.addWidget(success_button)
                        success_button_layout.addStretch(
                            1
                        )  # Τοποθετούμε το κουμπί δεξιά
                        fail_button = QPushButton("Η Θέση δεν ολοκληρώθηκε")
                        fail_button.clicked.connect(
                            lambda _, r=row[0]: self.set_position_done(r, result=False)
                        )
                        success_button_layout.addWidget(fail_button)
                        details_layout.addLayout(success_button_layout)
                    else:
                        evaluation_button = QPushButton("Αξιολόγηση Φοιτητή")
                        evaluation_button_layout = QHBoxLayout()

                        evaluation_button.clicked.connect(
                            lambda _, r=row["Student_ID"], pos_code=row[
                                0
                            ]: self.evaluation_student(r, pos_code)
                        )
                        evaluation_button_layout.addWidget(evaluation_button)
                        details_layout.addLayout(evaluation_button_layout)

                    details_group.setLayout(details_layout)
                    central_layout.addWidget(details_group)
        else:
            central_layout.addWidget(QLabel("Δεν βρέθηκαν επιλεγμένες Θέσεις"))
        # Προσθήκη του κεντρικού widget στο ScrollArea
        scroll_area.setWidget(central_widget)

        # Τελική διάταξη για το παράθυρο
        main_layout = QVBoxLayout(self.position_window)
        main_layout.addWidget(scroll_area)

        # Εμφάνιση του παραθύρου
        self.position_window.resize(600, 800)
        self.position_window.setWindowModality(
            Qt.WindowModality.ApplicationModal
        )  # Προσαρμογή μεγέθους παραθύρου
        self.position_window.show()
        # Εμφάνιση των επιλεγμένων θέσεων στο UI

    def set_position_done(self, pos_num, result):

        self.completion_widget = QWidget()
        self.completion_widget.setWindowTitle(f"Ολοκλήρωση Θέσης #{pos_num}")
        layout = QVBoxLayout()

        if result:
            title_label = QLabel("ΣΤΟΙΧΕΙΑ ΟΛΟΚΛΗΡΩΣΗΣ ΤΗΣ ΠΡΑΚΤΙΚΗΣ")
            title_label.setStyleSheet(
                "font-size: 16px; text-decoration: underline; font-weight: bold"
            )
            layout.addWidget(title_label)

            real_start_date_label = QLabel("ΗΜ/ΝΙΑ ΕΝΑΡΞΗΣ")
            self.real_start_date_picker = QDateEdit(calendarPopup=True)
            self.real_start_date_picker.setDate(
                QDate.currentDate()
            )  # Default date is today
            real_start_date_layout = QHBoxLayout()
            real_start_date_layout.addWidget(real_start_date_label)
            real_start_date_layout.addWidget(self.real_start_date_picker)
            layout.addLayout(real_start_date_layout)
            real_end_date_label = QLabel("ΗΜ/ΝΙΑ ΛΗΞΗΣ")
            self.real_end_date_picker = QDateEdit(calendarPopup=True)
            self.real_end_date_picker.setDate(
                QDate.currentDate()
            )  # Default date is today
            end_date_layout = QHBoxLayout()
            end_date_layout.addWidget(real_end_date_label)
            end_date_layout.addWidget(self.real_end_date_picker)
            layout.addLayout(end_date_layout)
            complete_button = QPushButton("Ολοκλήρωση Πρακτικής Επιτυχώς")
        else:

            # Αν το αποτέλεσμα είναι False, μόνο κουμπί "Ολοκλήρωση Θέσης ως Ακυρωμένη"
            complete_button = QPushButton("Ολοκλήρωση Θέσης ως Ακυρωμένη")

        complete_button.clicked.connect(
            lambda: self.complete_position(pos_num, final_result=result)
        )

        layout.addWidget(complete_button)
        self.completion_widget.setLayout(layout)
        self.completion_widget.setFixedSize(400, 300)
        self.completion_widget.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.completion_widget.show()

    def complete_position(self, pos_num, final_result):
        if not final_result:
            self.cursor.execute(
                "UPDATE Position set status='Χ' where position_number=? ", (pos_num,)
            )
            QMessageBox.warning(
                None, "Επιτυχία", "Η Κατάσταση της Θέσης άλλαξε σε Ακυρωμένη."
            )
            self.completion_widget.close()

        else:
            real_start_date = self.real_start_date_picker.date().toString("yyyy-MM-dd")
            real_end_date = self.real_end_date_picker.date().toString("yyyy-MM-dd")
            if real_end_date < real_start_date:
                QMessageBox.warning(
                    None,
                    "Αποτυχία",
                    "Η ημερομηνία έναρξης δεν πρέπει να είναι μεγαλύτερη από την ημερομηνία λήξης.",
                )
                return
            try:
                self.cursor.execute(
                    "UPDATE Position set status='Ο',Internship_Start_Date=?,Internship_End_Date=? where position_number=?",
                    (real_start_date, real_end_date, pos_num),
                )
                QMessageBox.warning(
                    None, "Επιτυχία", "Η Κατάσταση της Θέσης άλλαξε σε Ολοκληρωμένη."
                )
                self.completion_widget.close()
                self.position_window.close()
            except:
                QMessageBox.information(
                    None, "Αποτυχία", "Προέκυψε σφάλμα στην αλλαγή κατάστασης"
                )

    def set_on_going_position(self, pos_num):
        dialog_question = QMessageBox(self)
        dialog_question.setWindowTitle("Αλλαγή Κατάστασης Θέσης")
        dialog_question.setText(
            f"Θέλετε να αλλάξετε την κατάσταση της θέσης #{pos_num} σε 'Υπό Διενέργεια';"
        )
        dialog_question.setIcon(QMessageBox.Icon.Question)
        dialog_question.setStandardButtons(
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if dialog_question.exec() == QMessageBox.StandardButton.Yes:
            try:
                self.cursor.execute(
                    "UPDATE POSITION set status='Υ' where position_number=?", (pos_num,)
                )
                self.conn.commit()
                self.position_window.close()
            except:
                QMessageBox.information(
                    None, "Αποτυχία", "Προέκυψε σφάλμα στην αλλαγή κατάστασης"
                )

        else:
            QMessageBox.information(None, "Ακύρωση", "Η αλλαγή κατάστασης ακυρώθηκε.")

    def delete_matching(self, pos_num):
        dialog_question = QMessageBox()
        dialog_question.setWindowTitle("Ακύρωση Αντιστοίχησης")
        dialog_question.setText(
            f"Θέλετε να αλλάξετε την κατάσταση της θέσης #{pos_num} σε 'Προδεσμευμένη';"
        )
        dialog_question.setIcon(QMessageBox.Icon.Question)
        dialog_question.setStandardButtons(
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if dialog_question.exec() == QMessageBox.StandardButton.Yes:
            try:
                self.cursor.execute(
                    "DELETE  FROM MATCHING WHERE Position_Number = ?", (pos_num,)
                )
                self.cursor.execute(
                    "UPDATE POSITION SET Status = 'Π', Internship_Start_Date = NULL, Internship_End_Date = NULL WHERE Position_Number = ?",
                    (pos_num,),
                )
                self.conn.commit()
                self.position_window.close()
            except:
                QMessageBox.information(
                    None, "Αποτυχία", "Προέκυψε σφάλμα στην αλλαγή κατάστασης"
                )

        else:
            QMessageBox.information(None, "Ακύρωση", "Η αλλαγή κατάστασης ακυρώθηκε.")

    def let_go(self, pos_num):
        try:
            self.cursor.execute(
                "UPDATE Position set office_code=NULL,status='Ε' where position_number=?",
                (pos_num,),
            )
            self.conn.commit()
            QMessageBox.information(None, "Επιτυχία", "Η θέση αποδεσμεύτηκε")
            self.position_window.close()

        except:
            QMessageBox.warning(
                None, "Αποτυχία", "Προέκυψε κάποιο λάθος στην αποδέσμευση της θέσης."
            )

    def matching(self, pos_num, stud_id):
        self.matching_window = QWidget()
        self.matching_window.setWindowTitle(f"ΑΝΤΙΣΤΟΙΧΗΣΗ ΦΟΙΤΗΤΗ #{stud_id}")

        # Κεντρικό layout
        layout = QVBoxLayout()

        # Title Label with underline and bold
        title_label = QLabel("ΣΤΟΙΧΕΙΑ ΕΚΤΕΛΕΣΗΣ ΠΡΑΚΤΙΚΗΣ ΑΣΚΗΣΗΣ")
        title_label.setStyleSheet(
            "font-size: 16px; text-decoration: underline; font-weight: bold"
        )
        layout.addWidget(title_label)

        # Προβλεπόμενη Ημ/νια Έναρξης
        start_date_label = QLabel("ΠΡΟΒΛΕΠΟΜΕΝΗ ΗΜ/ΝΙΑ ΕΝΑΡΞΗΣ")
        self.start_date_picker = QDateEdit(calendarPopup=True)
        self.start_date_picker.setDate(QDate.currentDate())  # Default date is today
        start_date_layout = QHBoxLayout()
        start_date_layout.addWidget(start_date_label)
        start_date_layout.addWidget(self.start_date_picker)
        layout.addLayout(start_date_layout)

        # Προβλεπόμενη Ημ/νια Λήξης
        end_date_label = QLabel("ΠΡΟΒΛΕΠΟΜΕΝΗ ΗΜ/ΝΙΑ ΛΗΞΗΣ")
        self.end_date_picker = QDateEdit(calendarPopup=True)
        self.end_date_picker.setDate(QDate.currentDate())  # Default date is today
        end_date_layout = QHBoxLayout()
        end_date_layout.addWidget(end_date_label)
        end_date_layout.addWidget(self.end_date_picker)
        layout.addLayout(end_date_layout)

        # Τρόπος Χρηματοδότησης
        funding_label = QLabel("ΤΡΟΠΟΣ ΧΡΗΜΑΤΟΔΟΤΗΣΗΣ")
        self.funding_combo = QComboBox()
        self.funding_combo.addItems(["ΕΣΠΑ", "ΙΔΡΥΜΑ", "ΟΑΕΔ", "ΦΟΡΕΑΣ"])
        funding_layout = QHBoxLayout()
        funding_layout.addWidget(funding_label)
        funding_layout.addWidget(self.funding_combo)
        layout.addLayout(funding_layout)

        # Κουμπί Αποστολής
        submit_button = QPushButton("Επιβεβαίωση Επιλογής")
        submit_button.clicked.connect(lambda: self.update_table(pos_num, stud_id))
        layout.addWidget(submit_button)

        self.matching_window.setLayout(layout)
        self.matching_window.setFixedSize(600, 300)
        self.matching_window.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.matching_window.show()

    def update_table(self, pos_num, stud_id):
        if self.start_date_picker.date() > self.end_date_picker.date():
            QMessageBox.warning(
                None,
                "Αποτυχία",
                "Η ημερομηνία έναρξης δεν πρέπει να είναι μεγαλύτερη από την ημερομηνία λήξης.",
            )

        else:
            try:
                self.cursor.execute(
                    "SELECT Agency_AFM FROM POSITION WHERE Position_number=?",
                    (pos_num,),
                )
                afm = self.cursor.fetchone()
                self.cursor.execute(
                    "INSERT INTO MATCHING(Predicted_Start_Date,Predicted_End_Date,Payment_Method,Office_Code,Position_Number,Student_ID,Agency_AFM) VALUES(?,?,?,?,?,?,?)",
                    (
                        self.start_date_picker.date().toString("yyyy-MM-dd"),
                        self.end_date_picker.date().toString("yyyy-MM-dd"),
                        self.funding_combo.currentText(),
                        self.office_code,
                        pos_num,
                        stud_id,
                        afm[0],
                    ),
                )
                self.cursor.execute(
                    "UPDATE POSITION SET STATUS='Α' WHERE Position_number=?", (pos_num,)
                )
                QMessageBox.information(
                    None,
                    "Επιτυχία",
                    "Πραγματοποιήθηκε επιτυχώς η αντιστοίχηση της θέσης",
                )
                self.matching_window.close()
                self.student_window.close()
                self.position_window.close()
            except:
                QMessageBox.warning(
                    None,
                    "Αποτυχία",
                    "Προέκυψε κάποιο λάθος στην αντιστοιχηση της θέσης.",
                )

    def view_students(self, pos_code):
        self.cursor.execute("DROP View if exists Student_Office")
        self.cursor.execute(
            "CREATE VIEW IF NOT EXISTS Student_Office  AS SELECT S.ID,S.Name,S.Surname,S.Phone,S.Email,S.Student_ID,S.AMA,S.University_Title,S.Department_Title,D.office_code from STUDENT as S join DEPARTMENT as D on S.University_Title=D.University_Title and S.Department_Title=D.Title"
        )
        if not pos_code:

            self.cursor.execute(
                "Select * from Student_Office  where Office_Code=?", (self.office_code,)
            )
        else:
            self.cursor.execute(
                "Select * from Student_Office as S1 where Office_code=? and (S1.Department_Title,S1.University_Title) in (select S.department_title,S.university_title from Student_Office as S join POSITION_ACCESSIBLE_FROM_DEPT as P on S.department_title=P.Department_Title and S.University_Title=P.University_Title where P.position_number=? )",
                (self.office_code, pos_code),
            )
        rows = self.cursor.fetchall()

        self.student_window = QWidget()
        self.student_window.setWindowTitle("Φοιτητές")

        # Προσθήκη ScrollArea για υποστήριξη κύλισης
        scroll_area = QScrollArea(self.student_window)
        scroll_area.setWidgetResizable(True)
        central_widget = QWidget()
        central_layout = QVBoxLayout(central_widget)
        if rows:
            for row in rows:
                if row:
                    details_group = QGroupBox(f"Κωδικός #{row[0]}")
                    details_layout = QVBoxLayout()

                    if not pos_code:

                        title_button = QPushButton("Θέσεις Φοιτητή")
                        title_button.clicked.connect(
                            lambda _, r=row[0]: self.show_student_position(r)
                        )
                        top_layout = QHBoxLayout()
                        top_layout.addStretch()
                        top_layout.addWidget(title_button)
                    else:
                        match_button = QPushButton("Αντιστοίχηση Φοιτητή")
                        match_button.clicked.connect(
                            lambda _, r=row[0]: self.matching(pos_code, r)
                        )
                        top_layout = QHBoxLayout()
                        top_layout.addStretch()
                        top_layout.addWidget(match_button)

                    # self.cursor.execute("SELECT S.ID,S.Name,S.Surname,S.Phone,S.Email,S.Student_ID,S.AMA,S.University_Title,S.Department_Title from STUDENT as S join DEPARTMENT as D on S.University_Title=D.University_Title and S.Department_Title=D.Title where Office_Code=?",(self.office_code,))
                    student_name_label = QLabel(f"Ονοματεπώνυμο:{row[1]} {row[2]}")
                    phone_label = QLabel(f"Τηλέφωνο: {row[3]}")
                    email_label = QLabel(f"Email: {row[4]}")
                    am_label = QLabel(f"Αριθμός Μητρώου : {row[5]}")
                    ama_label = QLabel(f"ΑΜΑ : {row[6]}")
                    uni_label = QLabel(f"Πανεπιστήμιο : {row[7]}")
                    dep_label = QLabel(f"Τμήμα: {row[8]}")

                    # details_layout.addLayout(top_layout)

                    self.info1_label = QLabel("Στοιχεία Φοιτητή")
                    self.info1_label.setStyleSheet(
                        "font-size: 14px; text-decoration: underline;font-weight: bold"
                    )
                    self.info2_label = QLabel("Στοιχεία Τμήματος")
                    self.info2_label.setStyleSheet(
                        "font-size: 14px; text-decoration: underline;font-weight: bold"
                    )
                    details_layout.addWidget(self.info1_label)
                    details_layout.addWidget(student_name_label)
                    details_layout.addWidget(phone_label)
                    details_layout.addWidget(email_label)
                    details_layout.addWidget(am_label)
                    details_layout.addWidget(ama_label)
                    details_layout.addWidget(self.info2_label)
                    details_layout.addWidget(uni_label)
                    details_layout.addWidget(dep_label)

                    # Ορισμός layout στο GroupBox και προσθήκη στο κεντρικό layout
                    details_group.setLayout(details_layout)
                    central_layout.addWidget(details_group)
                    details_layout.addLayout(top_layout)

        else:
            central_layout.addWidget(
                QLabel(
                    "Δεν βρέθηκαν Φοιτητές εγγεγραμένοι για τα Τμήματα που Εκπροσωπείτε"
                )
            )
        # Προσθήκη του κεντρικού widget στο ScrollArea
        scroll_area.setWidget(central_widget)

        self.student_window.setWindowModality(Qt.WindowModality.ApplicationModal)
        # Τελική διάταξη για το παράθυρο
        main_layout = QVBoxLayout(self.student_window)
        main_layout.addWidget(scroll_area)
        self.student_window.resize(600, 600)  # Προσαρμογή μεγέθους παραθύρου
        self.student_window.show()

    def show_student_position(self, row):
        self.cursor.execute(
            "SELECT M.Position_Number,P.Status,P.Title,P.Region,A.AFM,A.Agency_Name,A.phone,A.Email,M.Student_ID,M.Predicted_Start_Date,M.Predicted_End_Date,P.internship_start_date,P.internship_end_date,P.Supervisor_First_Name,P.Supervisor_Last_Name,P.Supervisor_Email,P.Supervisor_Phone from( MATCHING as M join AGENCY as A on M.Agency_AFM=A.AFM )join POSITION as P on P.Position_Number=M.Position_Number where M.Student_ID=?",
            (row,),
        )
        rows = self.cursor.fetchall()
        self.student_position_window = QWidget()
        self.student_position_window.setWindowTitle("Θέσεις Φοιτητή")

        # Προσθήκη ScrollArea για υποστήριξη κύλισης
        scroll_area = QScrollArea(self.student_position_window)
        scroll_area.setWidgetResizable(True)

        central_widget = QWidget()
        central_layout = QVBoxLayout(central_widget)
        self.student_position_window.setWindowModality(
            Qt.WindowModality.ApplicationModal
        )
        # Για κάθε γραμμή (θέση) που επιστρέφει το query
        if rows:
            for row in rows:
                if row:

                    details_group = QGroupBox(f"Κωδικός Θέσης: #{row[0]}")
                    details_layout = QVBoxLayout()
                    details_group.setStyleSheet(
                        f"""
            QGroupBox {{
        background-color: {self.status_colors.get(row[1])};
    }}
    QGroupBox::title {{
        color: black;
        font-weight: bold;
            }}
            """
                    )

                    # Κουμπί για αναλυτικά στοιχεία θέσης
                    # top_layout = QHBoxLayout()
                    # top_layout.addStretch()
                    # top_layout.addWidget(title_button)

                    # Δημιουργία ετικετών για τα στοιχεία της θέσης
                    central_widget.setStyleSheet("QLabel { color: black; }")
                    title_label = QLabel(f"Τίτλος: {row[2]}")
                    location_label = QLabel(f"Τοποθεσία: {row[3]}")
                    if row[1] == "Ο":
                        date1_label = QLabel(f"Ημ/νία Έναρξης Πρακτικής:{row[9]}")
                        date2_label = QLabel(f"Ημ/νία Λήξης Πρακτικής:{row[10]}")
                    else:
                        date1_label = QLabel(
                            f"Προβλεπόμενη Ημ/νία Έναρξης Πρακτικής:{row[11]}"
                        )
                        date2_label = QLabel(
                            f"Προβλεπόμενη Ημ/νία Λήξης Πρακτικής:{row[12]}"
                        )
                    agency_afm_label = QLabel(f"Α.Φ.Μ. Φορέα: {row[4]}")
                    agency_name_label = QLabel(f"Όνομα Φορέα: {row[5]}")
                    agency_phone_label = QLabel(f"Τηλέφωνο Φορέα: {row[6]}")
                    agency_email_label = QLabel(f"Email Φορέα: {row[7]}")
                    agency_emailR_label = QLabel(f"Email: {row[15]}")
                    agency_nameR_label = QLabel(f"Ονοματεπώνυμο: {row[13]} {row[14]}")
                    agency_phoneR_label = QLabel(f"Τηλέφωνο: {row[16]}")

                    # Προσθήκη τίτλων για τις κατηγορίες
                    info1_label = QLabel("Στοιχεία Φορέα")
                    info1_label.setStyleSheet(
                        "font-size: 14px; text-decoration: underline;font-weight: bold"
                    )
                    info2_label = QLabel("Στοιχεία Επόπτη")
                    info2_label.setStyleSheet(
                        "font-size: 14px; text-decoration: underline;font-weight: bold"
                    )

                    details_layout.addWidget(title_label)
                    details_layout.addWidget(location_label)
                    details_layout.addWidget(date1_label)
                    details_layout.addWidget(date2_label)
                    details_layout.addWidget(info1_label)
                    details_layout.addWidget(agency_afm_label)
                    details_layout.addWidget(agency_name_label)
                    details_layout.addWidget(agency_phone_label)
                    details_layout.addWidget(agency_email_label)
                    details_layout.addWidget(info2_label)
                    details_layout.addWidget(agency_nameR_label)
                    details_layout.addWidget(agency_phoneR_label)
                    details_layout.addWidget(agency_emailR_label)

                    # Ορισμός layout στο QGroupBox
                    details_group.setLayout(details_layout)

                    # Εισαγωγή του QGroupBox στο κύριο layout
                    central_layout.addWidget(details_group)
        else:
            central_layout.addWidget(
                QLabel("Δεν βρέθηκαν Θέσεις που έχουν ανατεθεί σε αυτόν τον Φοιτητή")
            )

        # Προσθήκη του κεντρικού widget στο ScrollArea
        scroll_area.setWidget(central_widget)

        # Τελική διάταξη για το παράθυρο
        main_layout = QVBoxLayout(self.student_position_window)
        main_layout.addWidget(scroll_area)

        self.student_position_window.resize(700, 600)
        # Εμφάνιση του παραθύρου
        self.student_position_window.show()

    def view_all_positions(self):
        self.cursor.execute(" DROP VIEW IF EXISTS FREE_POSITIONS;")
        self.cursor.execute("DROP VIEW IF EXISTS FREE_POSITIONS_WITH_SPEC;")
        self.cursor.execute(
            "CREATE VIEW IF NOT EXISTS FREE_POSITIONS AS SELECT * FROM ((Position AS P JOIN AGENCY_WITH_RATING AS A ON P.Agency_AFM = A.AFM) join AGENCY AS AG ON AG.AFM = P.Agency_AFM) WHERE Status='Ε';"
        )
        self.cursor.execute(
            """
                       CREATE VIEW IF NOT EXISTS FREE_POSITIONS_WITH_SPEC AS
                       SELECT S.Position_Number,F.Title,F.region,F.Insertion_Date,F.Agency_Name,F.Supervisor_First_Name,F.Supervisor_Last_Name,F.Supervisor_Phone,F.Supervisor_Email, GROUP_CONCAT(S.Object_Name, ', '),F.Description,F.Duration,F.type,F.AFM
                        FROM FREE_POSITIONS AS F
                        JOIN SPECIALTY_POSITION AS S
                        ON F.Position_Number = S.Position_Number
                        GROUP BY F.Position_Number;
                                                        """
        )

        self.cursor.execute("SELECT * FROM FREE_POSITIONS_WITH_SPEC")
        rows = self.cursor.fetchall()

        self.cursor.execute(
            "SELECT Position_Number FROM FREE_POSITIONS_WITH_SPEC WHERE Position_Number in (SELECT PD.Position_Number from POSITION_ACCESSIBLE_FROM_DEPT as PD join DEPARTMENT as D on PD.Department_Title=D.Title and PD.University_Title=D.University_Title where D.Office_Code=?);",
            (self.office_code,),
        )
        position_numbers = self.cursor.fetchall()
        list_pos = []
        for position in position_numbers:
            for value in position:

                list_pos.append(value)
        # Δημιουργία βασικού παραθύρου για τις θέσεις
        self.position_window = QWidget()
        self.position_window.setWindowTitle("Όλες οι Ελεύθερες Θέσεις")

        # Προσθήκη ScrollArea για υποστήριξη κύλισης
        scroll_area = QScrollArea(self.position_window)
        scroll_area.setWidgetResizable(True)

        # Δημιουργία κεντρικού widget και layout για τις θέσεις
        central_widget = QWidget()
        central_layout = QVBoxLayout(central_widget)

        for row in rows:
            if row:
                details_group = QGroupBox(f"Θέση #{row[0]}")
                details_layout = QVBoxLayout()

                title_button = QPushButton(f"{row[1]}")
                title_button.clicked.connect(
                    lambda _, r=row: self.show_position_details(r)
                )
                top_layout = QHBoxLayout()
                top_layout.addWidget(title_button)
                top_layout.addStretch()
                if row[0] in list_pos:
                    self.get_button = QPushButton("Προδέσμευση Θέσης")
                    self.get_button.clicked.connect(
                        lambda _, r=row[0], btn=self.get_button: self.get_position(r, btn)
                    )
                    top_layout.addWidget(self.get_button)

                # SELECT S.Position_Number,F.Title,F.region,F.Insertion_Date,F.Agency_Name,F.Supervisor_First_Name,F.Supervisor_Last_Name,F.Supervisor_Phone,F.Supervisor_Email, GROUP_CONCAT(S.Object_Name, ', ')
                agency_name_label = QLabel(f"{row[4]}")
                region_label = QLabel(f"Περιοχή: {row[2]}")
                insertion_date_label = QLabel(f"Ημερομηνία Εισαγωγής: {row[3]}")
                supervisor_fname_lname_label = QLabel(
                    f"Όνοματεπώνυμο Επόπτη : {row[5]} {row[6]}"
                )
                supervisor_phone_label = QLabel(f"Τηλέφωνο Επόπτη : {row[7]}")
                supervisor_email_label = QLabel(f"Email Επόπτη : {row[8]}")

                details_layout.addLayout(top_layout)
                details_layout.addWidget(agency_name_label)

                details_layout.addWidget(region_label)
                details_layout.addWidget(insertion_date_label)
                details_layout.addWidget(supervisor_fname_lname_label)
                details_layout.addWidget(supervisor_phone_label)
                details_layout.addWidget(supervisor_email_label)

                # Ορισμός layout στο GroupBox και προσθήκη στο κεντρικό layout
                details_group.setLayout(details_layout)
                central_layout.addWidget(details_group)

        # Προσθήκη του κεντρικού widget στο ScrollArea
        scroll_area.setWidget(central_widget)

        # Τελική διάταξη για το παράθυρο
        main_layout = QVBoxLayout(self.position_window)
        main_layout.addWidget(scroll_area)

        self.position_window.setWindowModality(Qt.WindowModality.ApplicationModal)
        # Εμφάνιση του παραθύρου
        self.position_window.resize(700, 700)
        # Προσαρμογή μεγέθους παραθύρου
        self.position_window.show()

    def get_position(self, row, btn):
        btn.setEnabled(False)
        try:
            self.cursor.execute(
                "UPDATE Position SET Status='Π',office_code=? WHERE Position_Number=?",
                (self.office_code, row),
            )
            self.conn.commit()
            QMessageBox.information(None, "Επιτυχία", "Η θέση προδεσμεύτηκε επιτυχώς.")
            self.position_window.close()
            self.view_all_positions()
        except Exception as e:
            QMessageBox.warning(
                None,
                "Αποτυχία",
                f"Προέκυψε κάποιο λάθος στην προδέσμευση της θέσης.\n{e}",
            )

    def show_position_details(self, row):
        if row:
            # Δημιουργία παραθύρου λεπτομερειών
            self.details_window = QWidget()
            self.details_window.setWindowTitle(f"Λεπτομέρειες Θέσης #{row[0]}")

            details_layout = QVBoxLayout()
            agency_name_label = QLabel(f"{row[4]}")
            region_label = QLabel(f"Περιοχή: {row[2]}")
            description_label = QLabel(f"Περιγραφή: ")
            description = QLabel(f"{row['Description']}")
            description.setStyleSheet("color: white")
            description.setWordWrap(True)
            scroll_area2 = QScrollArea()
            scroll_area2.setWidgetResizable(True)
            description_widget = QWidget()
            description_layout = QVBoxLayout()
            description_layout.addWidget(description)
            description_widget.setLayout(description_layout)
            scroll_area2.setWidget(description_widget)
            duration_label = QLabel(f"Διάρκεια(σε μήνες): {row[11]}")
            type_label = QLabel(f"Είδος Θέσης: {row[12]}")
            insertion_date_label = QLabel(f"Ημερομηνία Εισαγωγής: {row[3]}")
            supervisor_fname_lname_label = QLabel(
                f"Όνοματεπώνυμο Επόπτη : {row[5]} {row[6]}"
            )
            supervisor_phone_label = QLabel(f"Τηλέφωνο Επόπτη : {row[7]}")
            supervisor_email_label = QLabel(f"Email Επόπτη : {row[8]}")
            specialty_label = QLabel("Αντικείμενα:")
            specialty_list = QLabel(f"{row[9]}")
            specialty_list.setWordWrap(True)
            scroll_area1 = QScrollArea()

            scroll_area1.setWidgetResizable(True)

            specialties_widget = QWidget()
            specialties_layout = QVBoxLayout()
            specialties_layout.addWidget(specialty_list)
            specialties_widget.setLayout(specialties_layout)

            scroll_area1.setWidget(specialties_widget)

            # Κουμπί για εμφάνιση στοιχείων φορέα
            agency_det_button = QPushButton("Στοιχεία Φορέα")
            agency_det_button.clicked.connect(
                lambda _, r=row: self.show_agency_details(row[13])
            )

            details_layout.addWidget(QLabel(f"Τίτλος: {row[1]}"))
            details_layout.addWidget(agency_name_label)
            details_layout.addWidget(description_label)
            details_layout.addWidget(scroll_area2)

            details_layout.addWidget(duration_label)
            details_layout.addWidget(type_label)
            details_layout.addWidget(region_label)
            details_layout.addWidget(insertion_date_label)
            details_layout.addWidget(supervisor_fname_lname_label)
            details_layout.addWidget(supervisor_phone_label)
            details_layout.addWidget(supervisor_email_label)
            details_layout.addWidget(specialty_label)
            details_layout.addWidget(scroll_area1)
            details_layout.addWidget(agency_det_button)
            self.details_window.setFixedSize(600, 600)
            self.details_window.setWindowModality(Qt.WindowModality.ApplicationModal)
            self.details_window.setLayout(details_layout)
            self.details_window.show()

    def show_agency_details(self, row):
        self.cursor.execute("SELECT * from Agency_With_rating where AFM=?", (row,))
        agency_details = self.cursor.fetchone()
        if agency_details:
            # Δημιουργία παραθύρου στοιχείων φορέα
            self.agency_window = QWidget()
            self.agency_window.setWindowTitle(f"Στοιχεία Φορέα - {agency_details[1]}")
            details_layout = QVBoxLayout()
            agency_name_label = QLabel(f"Όνομα Φορέα: {agency_details[1]}")
            agency_afm_label = QLabel(f"Α.Φ.Μ.: {agency_details[0]}")
            agency_location_label = QLabel(f"Περιοχή: {agency_details[2]}")
            agency_email_label = QLabel(f"Email: {agency_details[3]}")
            agency_type_label = QLabel(f"Είδος: {self.type_map.get(agency_details[4])}")
            agency_phone_label = QLabel(f"Τηλέφωνο: {agency_details[5]}")
            agency_rating_label = QLabel(f"Αξιολόγηση: {agency_details[6]}")
            details_layout.addWidget(agency_name_label)
            details_layout.addWidget(agency_afm_label)
            details_layout.addWidget(agency_location_label)
            details_layout.addWidget(agency_email_label)
            details_layout.addWidget(agency_type_label)
            details_layout.addWidget(agency_phone_label)
            details_layout.addWidget(agency_rating_label)
            self.agency_window.setWindowModality(Qt.WindowModality.ApplicationModal)
            self.agency_window.setFixedSize(300, 300)
            self.agency_window.setLayout(details_layout)
            self.agency_window.show()

    def evaluation_agency(self):
        self.cursor.execute(
            "Select DISTINCT Agency_afm,Office_code from Position where ( status='Χ' or status='Ο') and office_code=?",
            (self.office_code,),
        )
        rows = self.cursor.fetchall()
        self.agency_show_window = QWidget()
        self.agency_show_window.setWindowTitle("Φορείς Υποδοχής")

        # Προσθήκη ScrollArea για υποστήριξη κύλισης
        scroll_area = QScrollArea(self.agency_show_window)
        scroll_area.setWidgetResizable(True)

        central_widget = QWidget()
        central_layout = QVBoxLayout(central_widget)
        self.agency_show_window.setWindowModality(Qt.WindowModality.ApplicationModal)

        if rows:
            for row in rows:
                self.cursor.execute("Select * from Agency where AFM=?", (row[0],))
                agency_info = self.cursor.fetchone()
                details_group = QGroupBox(f"{agency_info['Agency_Name']}")
                details_layout = QVBoxLayout()

                # Δημιουργία ετικετών για τα στοιχεία της θέσης
                agency_afm_label = QLabel(f"Α.Φ.Μ. Φορέα: {agency_info['AFM']}")
                agency_name_label = QLabel(f"Όνομα Φορέα: {agency_info['Agency_Name']}")
                agency_phone_label = QLabel(f"Τηλέφωνο Φορέα: {agency_info['Phone']}")
                agency_email_label = QLabel(f"Email Φορέα: {agency_info['Email']}")
                agency_location_label = QLabel(f"Τοποθεσία: {agency_info['Location']}")
                agency_type_label = QLabel(
                    f"Τύπος: {self.type_map.get(agency_info['Type'])}"
                )
                agency_empc_label = QLabel(
                    f"Αριθμός Απασχολούμενων: {agency_info['Employee_Count']}"
                )
                agency_emailR_label = QLabel(
                    f"Email Υπευθύνου: {agency_info['Manager_Email']}"
                )
                agency_phoneR_label = QLabel(
                    f"Τηλέφωνο Υπευθύνου: {agency_info['Manager_Phone']}"
                )
                agency_nameR_label = QLabel(
                    f"Ονομα Υπευθύνου: {agency_info['Manager_Name']} {agency_info['Manager_Surname']}"
                )

                # Προσθήκη τίτλων για τις κατηγορίες
                info1_label = QLabel("Στοιχεία Φορέα")
                info1_label.setStyleSheet(
                    "font-size: 14px; text-decoration: underline;font-weight: bold"
                )
                info2_label = QLabel("Στοιχεία Υπεύθυνου Φορέα")
                info2_label.setStyleSheet(
                    "font-size: 14px; text-decoration: underline;font-weight: bold"
                )

                details_layout.addWidget(info1_label)
                details_layout.addWidget(agency_afm_label)
                details_layout.addWidget(agency_name_label)
                details_layout.addWidget(agency_phone_label)
                details_layout.addWidget(agency_email_label)
                details_layout.addWidget(agency_location_label)
                details_layout.addWidget(agency_type_label)
                details_layout.addWidget(agency_empc_label)
                details_layout.addWidget(info2_label)
                details_layout.addWidget(agency_nameR_label)
                details_layout.addWidget(agency_phoneR_label)
                details_layout.addWidget(agency_emailR_label)
                show_eval_button = QPushButton("Προβολή Αξιολογησης")
                show_eval_button.clicked.connect(
                    lambda _, r=agency_info["AFM"]: self.sumbit_evaluate_agency(
                        r, show=True
                    )
                )
                show_eval_button_layout = (
                    QHBoxLayout()
                )  # Χρησιμοποιούμε νέο layout για το κουμπί
                # Προσθέτουμε κενό χώρο πριν το κουμπί
                show_eval_button_layout.addWidget(show_eval_button)
                show_eval_button_layout.addStretch(1)  # Τοποθετούμε το κουμπί δεξιά
                evaluate_button = QPushButton("Αξιολόγηση")
                evaluate_button.clicked.connect(
                    lambda _, r=agency_info["AFM"]: self.sumbit_evaluate_agency(
                        r, show=False
                    )
                )
                show_eval_button_layout.addWidget(evaluate_button)
                details_layout.addLayout(show_eval_button_layout)

                # Ορισμός layout στο QGroupBox
                details_group.setLayout(details_layout)

                # Εισαγωγή του QGroupBox στο κύριο layout
                central_layout.addWidget(details_group)
        else:
            central_layout.addWidget(
                QLabel(
                    "Δεν βρέθηκαν Φορείς που έχουν ολοκληρώσει Θέσεις με το Γραφείο σας"
                )
            )

        # Προσθήκη του κεντρικού widget στο ScrollArea
        scroll_area.setWidget(central_widget)

        # Τελική διάταξη για το παράθυρο
        main_layout = QVBoxLayout(self.agency_show_window)
        main_layout.addWidget(scroll_area)

        # Ρύθμιση του παραθύρου ως Modal

        self.agency_show_window.resize(700, 600)
        # Εμφάνιση του παραθύρου
        self.agency_show_window.show()

    def sumbit_evaluate_agency(self, agency_afm, show):
        self.eval_dialog = QDialog(self)
        self.eval_dialog.setWindowTitle("Αξιολόγηση Φορέα")
        self.eval_dialog.setFixedSize(500, 600)
        self.eval_dialog.setWindowModality(Qt.WindowModality.ApplicationModal)

        # Κύριο layout
        layout = QVBoxLayout()

        # Τίτλος
        title_label = QLabel("Αξιολόγηση Φορέα")
        title_label.setStyleSheet(
            "font-size: 16px; font-weight: bold; text-decoration: underline"
        )
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        # Αξιολόγηση Φορέα

        agency_score_label = QLabel("Βαθμολογία (1-10):")
        agency_score_spinbox = QSpinBox()
        agency_score_spinbox.setRange(1, 10)
        agency_score_spinbox.setValue(5)  # Default value
        layout.addWidget(agency_score_label)
        layout.addWidget(agency_score_spinbox)

        agency_comment_label = QLabel("Σχόλια:")
        agency_comment_textedit = QTextEdit()
        agency_comment_textedit.setPlaceholderText(
            "Γράψτε τα σχόλιά σας για τον Φορέα εδώ..."
        )
        layout.addWidget(agency_comment_label)
        layout.addWidget(agency_comment_textedit)

        # Έλεγχος αν είναι "read-only"

        self.cursor.execute(
            "SELECT Office_Rates_Agency, Office_Comments_To_Agency FROM EVALUATION_AGENCY_OFFICE WHERE office_code = ? AND agency_afm = ?",
            (self.office_code, agency_afm),
        )
        rating = self.cursor.fetchone()
        if show:
            agency_comment_textedit.setEnabled(False)
            agency_score_spinbox.setEnabled(False)
            if rating is not None and rating[0] is not None:
                agency_score_spinbox.setValue(rating[0])
                agency_comment_textedit.setText(rating[1])
            else:
                QMessageBox.information(
                    None,
                    "Αξιολόγηση",
                    "Δεν έχετε υποβάλλει κάποια αξιολόγηση για τον συγκεκριμένο Φορέα",
                )
                return
            button_box = QDialogButtonBox(
                QDialogButtonBox.StandardButton.Ok
                | QDialogButtonBox.StandardButton.Cancel
            )
            layout.addWidget(button_box)

            button_box.accepted.connect(self.eval_dialog.accept)
            button_box.rejected.connect(self.eval_dialog.reject)

            # Ρύθμιση layout
            self.eval_dialog.setLayout(layout)
            self.eval_dialog.exec()
        else:
            # Κουμπιά OK και Ακύρωση
            button_box = QDialogButtonBox(
                QDialogButtonBox.StandardButton.Ok
                | QDialogButtonBox.StandardButton.Cancel
            )
            layout.addWidget(button_box)

            # Συνδέσεις κουμπιών
            button_box.accepted.connect(self.eval_dialog.accept)
            button_box.rejected.connect(self.eval_dialog.reject)

            # Ρύθμιση layout
            self.eval_dialog.setLayout(layout)

            # Εμφάνιση self.eval_dialog και αναμονή για την απάντηση του χρήστη
            if self.eval_dialog.exec():
                # Αν ο χρήστης πατήσει OK
                self.override_info = QDialog()
                self.override_info.setWindowTitle("Επικάλυψη Αξιολόγησης")
                self.override_info.setWindowModality(Qt.WindowModality.ApplicationModal)

                # Δημιουργία layout για το QDialog
                layout1 = QVBoxLayout(self.override_info)

                # Προσθήκη κειμένου με QLabel
                label = QLabel(
                    "Η Καινούρια αξιολόγηση θα αντικαταστήσει την προηγούμενή σας για τον Φορέα αν υπάρχει"
                )
                layout1.addWidget(label)

                # Δημιουργία κουμπιών OK και Cancel
                override_button_box = QDialogButtonBox(
                    QDialogButtonBox.StandardButton.Ok
                    | QDialogButtonBox.StandardButton.Cancel
                )
                override_button_box.accepted.connect(self.override_info.accept)
                override_button_box.rejected.connect(self.override_info.reject)
                layout1.addWidget(override_button_box)

                self.override_info.setLayout(layout1)

                # Εμφάνιση override_info και αναμονή για την απάντηση του χρήστη
                if self.override_info.exec():
                    # Αν ο χρήστης επιβεβαιώσει την αντικατάσταση
                    agency_score = agency_score_spinbox.value()
                    agency_comment = agency_comment_textedit.toPlainText()
                    try:
                        if rating is not None:
                            self.cursor.execute(
                                "UPDATE EVALUATION_AGENCY_OFFICE SET Office_Rates_Agency = ?, Office_Comments_To_Agency = ? WHERE office_code = ? AND agency_afm = ?",
                                (
                                    agency_score,
                                    agency_comment,
                                    self.office_code,
                                    agency_afm,
                                ),
                            )
                        else:
                            self.cursor.execute(
                                "Insert into EVALUATION_AGENCY_OFFICE(Agency_afm,office_code,Office_rates_agency,office_comments_to_agency) values(?,?,?,?)",
                                (
                                    agency_afm,
                                    self.office_code,
                                    agency_score,
                                    agency_comment,
                                ),
                            )
                        QMessageBox.information(
                            None, "Επιτυχία", "Η αξιολόγηση καταχωρήθηκε."
                        )
                        self.conn.commit()
                    except Exception as e:
                        QMessageBox.warning(
                            None, "Σφάλμα", f"Προέκυψε σφάλμα στην αξιολόγηση: {str(e)}"
                        )
                else:
                    QMessageBox.information(
                        None, "Ακύρωση", "Η αντικατάσταση ακυρώθηκε."
                    )

    def evaluation_student(self, stud_id, pos_code):

        self.cursor.execute(
            "Select Office_Rating_To_Student from position where position_number=?",
            (pos_code,),
        )
        rating = self.cursor.fetchone()
        if rating[0] is not None:
            QMessageBox.information(
                None,
                "Αξιολόγηση",
                "Εχετε ήδη αξιολογήσει τον φοιτητή για την συγκεκριμένη θέση.",
            )
            return
        self.eval_dialog = QDialog()
        self.eval_dialog.setWindowTitle("Αξιολόγηση Φοιτητή")
        self.eval_dialog.setFixedSize(500, 600)
        self.eval_dialog.setWindowModality(Qt.WindowModality.ApplicationModal)

        # Κύριο layout
        layout = QVBoxLayout()

        # Τίτλος
        title_label = QLabel("Αξιολόγηση Φοιτητή")
        title_label.setStyleSheet(
            "font-size: 16px; font-weight: bold; text-decoration: underline"
        )
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        student_score_label = QLabel("Βαθμολογία (1-10):")
        student_score_spinbox = QSpinBox()
        student_score_spinbox.setRange(1, 10)
        student_score_spinbox.setValue(5)  # Default value
        layout.addWidget(student_score_label)
        layout.addWidget(student_score_spinbox)

        student_comment_label = QLabel("Σχόλια:")
        student_comment_textedit = QTextEdit()
        student_comment_textedit.setPlaceholderText(
            "Γράψτε τα σχόλιά σας για τον Φοιτητή εδώ..."
        )
        layout.addWidget(student_comment_label)
        layout.addWidget(student_comment_textedit)

        # Κουμπιά OK και Ακύρωση
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        layout.addWidget(button_box)

        # Συνδέσεις κουμπιών
        button_box.accepted.connect(self.eval_dialog.accept)
        button_box.rejected.connect(self.eval_dialog.reject)

        # Ρύθμιση layout
        self.eval_dialog.setLayout(layout)

        # Εμφάνιση self.eval_dialog και αναμονή για την απάντηση του χρήστη
        if self.eval_dialog.exec():

            student_score = student_score_spinbox.value()
            student_comment = student_comment_textedit.toPlainText()
            try:

                self.cursor.execute(
                    "UPDATE Position SET Office_Comments_To_Student = ?,Office_Rating_To_Student = ? WHERE position_number=?",
                    (student_comment, student_score, pos_code),
                )
                QMessageBox.information(None, "Επιτυχία", "Η αξιολόγηση καταχωρήθηκε.")
                self.conn.commit()
            except Exception as e:
                QMessageBox.warning(
                    None, "Σφάλμα", f"Προέκυψε σφάλμα στην αξιολόγηση: {str(e)}"
                )
        else:
            QMessageBox.information(None, "Ακύρωση", "Η αξιολόγηση ακυρώθηκε.")
