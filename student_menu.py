import sys
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
import sqlite3
from sqlite3 import Error
from datetime import datetime
from PyQt6.QtCore import Qt
from datetime import date
from register_student_dialog import Register_Student_Dialog


class StudentMenu(QMainWindow):
    def __init__(self, student_id, conn, cursor, regions, startapp):
        super().__init__()
        self.student_id = student_id
        self.conn = conn
        self.cursor = cursor
        self.regions = regions
        self.Startapp = startapp
        self.initUI()
        self.type_map = {"Δ": "Δημόσιος", "Ι": "Ιδιωτικός", "Μ": "Μ.Κ.Ο", "Α": "Αλλο"}
        self.status_colors = {
            "Ε": "lightblue",
            "Π": "white",
            "Α": "darkviolet",
            "Υ": "yellow",
            "Ο": "green",
            "Χ": "red",
        }

    def initUI(self):
        layout = QVBoxLayout()

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        self.label = QLabel("Επιλέξτε μία από τις παρακάτω επιλογές:")
        layout.addWidget(self.label)

        self.button1 = QPushButton("Στοιχεία Φοιτητή")
        self.button1.clicked.connect(self.view_student_details)
        layout.addWidget(self.button1)

        self.button2 = QPushButton("Προβολή θεσεών μου")
        self.button2.clicked.connect(self.view_positions)
        layout.addWidget(self.button2)

        self.button3 = QPushButton("Προβολή όλων Ελεύθερων θεσεων")
        self.button3.clicked.connect(self.view_all_positions)
        layout.addWidget(self.button3)

        self.button4 = QPushButton("Προβολή αγαπημένων θεσεων")
        self.button4.clicked.connect(self.view_favorites)
        layout.addWidget(self.button4)

        self.button5 = QPushButton("Έξοδος")
        self.button5.clicked.connect(self.exit)
        layout.addWidget(self.button5)

        central_widget.setLayout(layout)

        self.setFixedSize(750, 300)
        self.setWindowTitle("Μενού Φοιτητή")

    def exit(self):
        for widget in QApplication.topLevelWidgets():
            if widget is self.Startapp and isinstance(widget, QMainWindow):
                widget.show()
        self.close()

    def view_student_details(self):
        self.cursor.execute("SELECT * FROM Student WHERE id=?", (self.student_id,))
        row = self.cursor.fetchone()
        if row:
            self.dialog = Register_Student_Dialog(self.cursor, self.regions)
            self.dialog.setWindowTitle("Στοιχεία Φοιτητή")
            self.dialog.username_input.setText(f"{row[6]}")
            self.dialog.password_input.setText(f"{row[7]}")
            self.dialog.am_input.setText(f"{row[4]}")
            self.dialog.phone_input.setText(f"{row[3]}")
            self.dialog.email_input.setText(f"{row[5]}")
            self.dialog.fname_input.setText(f"{row[1]}")
            self.dialog.lname_input.setText(f"{row[2]}")
            self.dialog.ama_input.setText(f"{row[8]}")
            self.dialog.uni_input.setCurrentText(f"{row[10]}")
            self.dialog.dep_input.setCurrentText(f"{row[9]}")
            self.dialog.username_input.setReadOnly(True)
            self.dialog.password_input.setReadOnly(True)
            self.dialog.phone_input.setReadOnly(True)
            self.dialog.email_input.setReadOnly(True)
            self.dialog.fname_input.setReadOnly(True)
            self.dialog.lname_input.setReadOnly(True)
            self.dialog.ama_input.setReadOnly(True)
            self.dialog.am_input.setReadOnly(True)
            self.dialog.uni_input.setEnabled(not True)
            self.dialog.dep_input.setEnabled(not True)
            self.dialog.edit_button.setVisible(True)
            self.dialog.edit_button.clicked.connect(self.set_details_editable)
            self.edit_pressed = False
        else:
            QMessageBox.warning(None, "Αποτυχία", "Δεν βρέθηκαν στοιχεία")
            return
        if (
            self.dialog.exec() == QDialog.DialogCode.Accepted
            and self.edit_pressed == True
        ):
            student_info = self.dialog.get_info()
            if student_info != None:
                try:
                    self.cursor.execute(
                        "UPDATE STUDENT set Name=?,Surname=?,Phone=?,Student_ID=?,Email=?,Username=?,Password=?,AMA=? where ID=?",
                        student_info[:-2] + [self.student_id],
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

    def set_details_editable(self):
        self.dialog.edit_button.setEnabled(False)
        self.dialog.username_input.setReadOnly(False)
        self.dialog.password_input.setReadOnly(False)
        self.dialog.phone_input.setReadOnly(False)
        self.dialog.email_input.setReadOnly(False)
        self.dialog.fname_input.setReadOnly(False)
        self.dialog.lname_input.setReadOnly(False)
        self.dialog.ama_input.setReadOnly(False)
        self.edit_pressed = True

    def view_positions(self):
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
        self.cursor.execute(
            """
       SELECT *,group_concat(S.Object_Name,', ') as Specialties,P.agency_afm as AFM
	   FROM Matching as M join Position as P on M.position_number=P.Position_Number join Specialty_Position as S on S.Position_Number=P.Position_Number
	   WHERE M.Student_ID=?
	   GROUP BY M.Position_Number;  """,
            (self.student_id,),
        )
        rows = self.cursor.fetchall()
        self.student_position_window = QWidget()
        self.student_position_window.setWindowTitle("Οι Θέσεις μου")

        # Προσθήκη ScrollArea για υποστήριξη κύλισης
        scroll_area = QScrollArea(self.student_position_window)
        scroll_area.setWidgetResizable(True)

        # Δημιουργία κεντρικού widget και layout για τις θέσειςS
        central_widget = QWidget()
        central_layout = QVBoxLayout(central_widget)
        if rows:
            for row in rows:
                if row:
                    details_group = QGroupBox(f"Θέση #{row['Position_number']}")
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

                    # Κουμπί τίτλου που καλεί τη show_student_position_details
                    title_button = QPushButton(f"{row['title']}")
                    title_button.setStyleSheet("font-size:14px;color:white")
                    central_widget.setStyleSheet("QLabel { color: black; }")
                    top_layout = QHBoxLayout()
                    title_button.clicked.connect(
                        lambda _, r=row: self.show_position_details(r)
                    )
                    top_layout.addWidget(title_button)

                    # SELECT S.Position_Number,F.Title,F.region,F.Insertion_Date,F.Agency_Name,F.Supervisor_First_Name,F.Supervisor_Last_Name,F.Supervisor_Phone,F.Supervisor_Email, GROUP_CONCAT(S.Object_Name, ', ')
                    region_label = QLabel(f"Περιοχή: {row['Region']}")
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

                    supervisor_fname_lname_label = QLabel(
                        f"Όνοματεπώνυμο Επόπτη : {row['Supervisor_First_Name']} {row['Supervisor_Last_Name']}"
                    )
                    supervisor_phone_label = QLabel(
                        f"Τηλέφωνο Επόπτη : {row['Supervisor_phone']}"
                    )
                    supervisor_email_label = QLabel(
                        f"Email Επόπτη : {row['Supervisor_email']}"
                    )
                    specialties_label = QLabel("Αντικείμενα:")
                    specialty_list = QLabel(f"{row['Specialties']}")
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
                    details_layout.addWidget(date1_label)
                    details_layout.addWidget(date2_label)

                    details_layout.addWidget(supervisor_fname_lname_label)
                    details_layout.addWidget(supervisor_phone_label)
                    details_layout.addWidget(supervisor_email_label)
                    details_layout.addWidget(specialties_label)
                    details_layout.addWidget(scroll_area1)
                    if (
                        row["Status"] in ["Ο", "Χ"]
                        and row["Agency_Rating"] is None
                        and row["Office_Rating"] is None
                    ):
                        evaluation_button = QPushButton(
                            "Αξιολόγηση Φορέα και Γραφείου Πρακτικής"
                        )
                        evaluation_button.clicked.connect(
                            lambda _, r=row["position_number"]: self.evaluation(r)
                        )
                        details_layout.addWidget(evaluation_button)

                    # Ορισμός layout στο GroupBox και προσθήκη στο κεντρικό layout
                    details_group.setLayout(details_layout)
                    central_layout.addWidget(details_group)
        else:
            central_layout.addWidget(QLabel("Δεν βρέθηκαν αντιστοιχισμένες Θέσεις"))

        # Προσθήκη του κεντρικού widget στο ScrollArea
        scroll_area.setWidget(central_widget)

        # Τελική διάταξη για το παράθυρο
        main_layout = QVBoxLayout(self.student_position_window)
        main_layout.addWidget(scroll_area)

        self.student_position_window.setWindowModality(
            Qt.WindowModality.ApplicationModal
        )
        # Εμφάνιση του παραθύρου
        self.student_position_window.resize(700, 700)
        # Προσαρμογή μεγέθους παραθύρου
        self.student_position_window.show()

    def evaluation(self, pos_code):
        self.cursor.execute(
            "Select Office_rating from Matching where position_number=?", (pos_code,)
        )

        # Δημιουργία του παραθύρου
        self.eval_dialog = QDialog(self)
        self.eval_dialog.setWindowTitle(f"Αξιολόγηση για τη Θέση #{pos_code}")
        self.eval_dialog.setFixedSize(500, 600)
        self.eval_dialog.setWindowModality(Qt.WindowModality.ApplicationModal)

        # Κύριο layout
        layout = QVBoxLayout()

        # Τίτλος
        title_label = QLabel("Αξιολόγηση Φορέα και Γραφείου Πρακτικής")
        title_label.setStyleSheet(
            "font-size: 16px; font-weight: bold; text-decoration: underline"
        )
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        # Αξιολόγηση Φορέα
        agency_label = QLabel("Φορέας")
        agency_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(agency_label)

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

        # Αξιολόγηση Γραφείου
        office_label = QLabel("Γραφείο Πρακτικής")
        office_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(office_label)

        office_score_label = QLabel("Βαθμολογία (1-10):")
        office_score_spinbox = QSpinBox()
        office_score_spinbox.setRange(1, 10)
        office_score_spinbox.setValue(1)
        layout.addWidget(office_score_label)
        layout.addWidget(office_score_spinbox)
        office_comment_label = QLabel("Σχόλια:")
        office_comment_textedit = QTextEdit()
        office_comment_textedit.setPlaceholderText(
            "Γράψτε τα σχόλιά σας για το Γραφείο εδώ..."
        )
        layout.addWidget(office_comment_label)
        layout.addWidget(office_comment_textedit)

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
            # Αν ο χρήστης πατήσει OK
            agency_score = agency_score_spinbox.value()
            agency_comment = agency_comment_textedit.toPlainText()
            office_score = office_score_spinbox.value()
            office_comment = office_comment_textedit.toPlainText()
            try:
                self.cursor.execute(
                    "UPDATE MATCHING SET Agency_rating=?,Agency_comments=?,Office_rating=?,Office_comments=? where position_number=?",
                    (
                        agency_score,
                        agency_comment,
                        office_score,
                        office_comment,
                        pos_code,
                    ),
                )
                QMessageBox.information(None, "Επιτυχία", "Η αξιολόγηση καταχωρήθηκε.")
            except:
                QMessageBox.warning(None, "Σφάλμα", "Προέκυψε σφάλμα στην αξιολόγηση.")

        else:
            # Αν ο χρήστης πατήσει Ακύρωση
            QMessageBox.information(None, "Ακύρωση", "Η αξιολόγηση ακυρώθηκε.")

    def view_all_positions(self):
        self.cursor.execute(" DROP VIEW IF EXISTS FREE_POSITIONS;")
        self.cursor.execute("DROP VIEW IF EXISTS FREE_POSITIONS_WITH_SPEC;")
        self.cursor.execute(
            """
                       CREATE INDEX  IF NOT EXISTS"idx_free_positions_spec" ON "POSITION" (
                        "Position_Number",
                    "Agency_AFM",
                    "Status"
                                );"""
        )
        self.cursor.execute(
            "CREATE VIEW IF NOT EXISTS FREE_POSITIONS AS SELECT * FROM ((Position AS P JOIN AGENCY_WITH_RATING AS A ON P.Agency_AFM = A.AFM) join AGENCY AS AG ON AG.AFM = P.Agency_AFM) WHERE Status='Ε';"
        )
        self.cursor.execute(
            """
                       CREATE VIEW IF NOT EXISTS  FREE_POSITIONS_WITH_SPEC   AS
                       SELECT S.Position_Number,F.Title,F.region,F.Insertion_Date,F.Agency_Name,F.Supervisor_First_Name,F.Supervisor_Last_Name,F.Supervisor_Phone,F.Supervisor_Email, GROUP_CONCAT(S.Object_Name, ', ') as SPECIALTIES,F.Description,F.Duration,F.type,F.AFM
                        FROM FREE_POSITIONS AS F
                        JOIN SPECIALTY_POSITION AS S
                        ON F.Position_Number = S.Position_Number
                        GROUP BY F.Position_Number;
                                                        """
        )

        self.cursor.execute("SELECT * FROM FREE_POSITIONS_WITH_SPEC")
        rows = self.cursor.fetchall()

        # Δημιουργία βασικού παραθύρου για τις θέσεις
        self.position_window = QWidget()
        self.position_window.setWindowTitle("Όλες οι Ελεύθερες Θέσεις")

        # Προσθήκη ScrollArea για υποστήριξη κύλισης
        scroll_area = QScrollArea(self.position_window)
        scroll_area.setWidgetResizable(True)

        # Δημιουργία κεντρικού widget και layout για τις θέσεις
        central_widget = QWidget()
        central_layout = QVBoxLayout(central_widget)

        if rows:
            for row in rows:
                if row:
                    details_group = QGroupBox(f"Θέση #{row[0]}")
                    details_layout = QVBoxLayout()

                    # Κουμπί τίτλου που καλεί τη show_position_details
                    title_button = QPushButton(f"{row[1]}")
                    top_layout = QHBoxLayout()
                    top_layout.addWidget(title_button)
                    like_button = QPushButton("Προσθηκη στα Αγαπημένα")
                    top_layout.addStretch()
                    if self.is_favorite(row):
                        like_button.setText("Αφαίρεση από τα Αγαπημένα")
                    else:
                        like_button.setText("Προσθήκη στα Αγαπημένα")

                    title_button.clicked.connect(
                        lambda _, r=row: self.show_position_details(r)
                    )
                    like_button.clicked.connect(lambda _, r=row: self.add_favorites(r))
                    top_layout.addWidget(like_button)

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
        else:
            central_layout.addWidget(QLabel("Δεν Βρέθηκαν Ελεύθερες"))

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

    def show_position_details(self, row):
        if row:
            # Δημιουργία παραθύρου λεπτομερειών
            self.details_window = QWidget()
            self.details_window.setWindowTitle(
                f"Λεπτομέρειες Θέσης #{row['position_number']}"
            )

            details_layout = QVBoxLayout()
            region_label = QLabel(f"Περιοχή: {row['region']}")
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

            duration_label = QLabel(f"Διάρκεια(σε μήνες): {row['duration']}")
            type_label = QLabel(f"Είδος Θέσης: {row['type']}")
            insertion_date_label = QLabel(
                f"Ημερομηνία Εισαγωγής: {row['insertion_date']}"
            )
            supervisor_fname_lname_label = QLabel(
                f"Όνοματεπώνυμο Επόπτη : {row['Supervisor_First_Name']} {row['Supervisor_Last_Name']}"
            )
            supervisor_phone_label = QLabel(
                f"Τηλέφωνο Επόπτη : {row['Supervisor_Phone']}"
            )
            supervisor_email_label = QLabel(f"Email Επόπτη : {row['Supervisor_email']}")
            specialty_label = QLabel("Αντικείμενα:")
            specialty_list = QLabel(f"{row['Specialties']}")
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
                lambda _, r=row: self.show_agency_details(row["AFM"])
            )

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
            details_layout.addWidget(specialty_label)
            details_layout.addWidget(scroll_area1)
            details_layout.addWidget(agency_det_button)
            self.details_window.setFixedSize(400, 400)
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

    def is_favorite(self, row):
        self.cursor.execute(
            "SELECT * FROM Favorites WHERE Student_ID = ? AND Position_Number = ? AND Agency_AFM = ?",
            (self.student_id, row[0], row[13]),
        )
        return self.cursor.fetchone() is not None

    def add_favorites(self, row):
        if self.is_favorite(row):
            # Αφαίρεση από τα αγαπημένα
            self.cursor.execute(
                "DELETE FROM Favorites WHERE Student_ID = ? AND Position_Number = ? AND Agency_AFM = ?",
                (self.student_id, row[0], row[13]),
            )

            QMessageBox.information(
                None, "Αγαπημένα", "Η θέση αφαιρέθηκε από τα αγαπημένα."
            )
        else:
            # Προσθήκη στα αγαπημένα
            self.cursor.execute(
                "INSERT INTO Favorites(Student_ID, Position_Number, Agency_AFM) VALUES (?, ?, ?)",
                (self.student_id, row[0], row[13]),
            )

            QMessageBox.information(
                None, "Αγαπημένα", "Η θέση προστέθηκε στα αγαπημένα."
            )

        # Αποθήκευση αλλαγών
        self.conn.commit()

        # Ενημέρωση κειμένου κουμπιού
        like_button = self.sender()  # Παίρνει το κουμπί που κάλεσε τη συνάρτηση
        if like_button:
            if self.is_favorite(row):
                like_button.setText("Αφαίρεση από τα Αγαπημένα")
            else:
                like_button.setText("Προσθήκη στα Αγαπημένα")

    def view_favorites(self):
        # Ερώτημα για φιλτράρισμα αγαπημένων θέσεων του φοιτητή
        self.cursor.execute(
            """
            SELECT *
            FROM Favorites AS F
            JOIN FREE_POSITIONS_WITH_SPEC AS P ON P.position_number=F.position_number
            WHERE F.student_id = ?
        """,
            (self.student_id,),
        )
        favorite_positions = self.cursor.fetchall()

        # Δημιουργία παραθύρου
        self.position_window = QWidget()
        self.position_window.setWindowTitle("Αγαπημένες Θέσεις")

        scroll_area = QScrollArea(self.position_window)
        scroll_area.setWidgetResizable(True)

        central_widget = QWidget()
        central_layout = QVBoxLayout(central_widget)

        if not favorite_positions:
            central_layout.addWidget(QLabel("Δεν υπάρχουν αγαπημένες θέσεις."))

        for position in favorite_positions:
            details_group = QGroupBox(f"Θέση #{position[1]}")
            details_layout = QVBoxLayout()

            # Τίτλος
            title_button = QPushButton(f"{position[4]}")
            title_button.clicked.connect(
                lambda _, pos=position: self.show_position_details(pos)
            )

            # Λεπτομέρειες
            agency_name_label = QLabel(f"Φορέας: {position[7]}")
            region_label = QLabel(f"Περιοχή: {position[5]}")
            specialty_name_label = QLabel("Αντικείμενα:")
            specialty_list = QLabel(f"{position[12]}")
            specialty_list.setWordWrap(True)
            scroll_area1 = QScrollArea()

            scroll_area1.setWidgetResizable(True)

            specialties_widget = QWidget()
            specialties_layout = QVBoxLayout()
            specialties_layout.addWidget(specialty_list)
            specialties_widget.setLayout(specialties_layout)

            scroll_area1.setWidget(specialties_widget)
            supervisor_label = QLabel(f"Επόπτης: {position[8]} {position[9]}")
            supervisor_phone_label = QLabel(f"Τηλέφωνο Επόπτη : {position[10]}")
            supervisor_email_label = QLabel(f"Email Επόπτη : {position[11]}")

            # Προσθήκη στο layout
            details_layout.addWidget(title_button)
            details_layout.addWidget(agency_name_label)
            details_layout.addWidget(region_label)
            details_layout.addWidget(specialty_name_label)
            details_layout.addWidget(scroll_area1)
            details_layout.addWidget(supervisor_label)
            details_layout.addWidget(supervisor_phone_label)
            details_layout.addWidget(supervisor_email_label)

            details_group.setLayout(details_layout)
            central_layout.addWidget(details_group)

        scroll_area.setWidget(central_widget)

        main_layout = QVBoxLayout(self.position_window)
        main_layout.addWidget(scroll_area)
        self.position_window.resize(600, 800)
        self.position_window.show()
