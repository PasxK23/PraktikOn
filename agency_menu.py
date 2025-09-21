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


class AgencyMenu(QMainWindow):
    def __init__(self, agency_afm, conn, cursor, regions, startapp):
        self.conn = conn
        self.cursor = cursor
        self.regions = regions
        self.agency_afm = agency_afm
        self.Startapp = startapp
        conn.commit()
        super().__init__()
        self.setWindowTitle("Μενού Φορέα")
        self.setGeometry(100, 100, 400, 300)

        self.cursor.execute("SELECT * FROM Agency WHERE Afm=?", (self.agency_afm,))
        row = self.cursor.fetchone()

        if row:
            agency_name = row["Agency_Name"]
            self.agency_name_label = QLabel(f"{agency_name}")
        # Ετικέτα με το AFM
        self.afm_label = QLabel(f"Α.Φ.Μ.: {self.agency_afm}")

        title_label = QLabel(agency_name)
        title_font = QFont("Arial", 20)
        title_label.setFont(title_font)
        title_label.setStyleSheet("font-weight: bold;")

        # Δημιουργία υποτίτλου (AFM κάτω αριστερά)
        self.afm_label.setFont(QFont("Arial", 12))
        self.afm_label.setStyleSheet("color: gray;")
        bottom_layout = QHBoxLayout()
        bottom_layout.addWidget(self.afm_label)
        bottom_layout.addStretch()

        # Κεντρικό layout
        layout = QVBoxLayout()
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout.addWidget(title_label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addLayout(bottom_layout)

        # Κουμπιά επιλογών
        self.add_position_button = QPushButton("Προσθήκη νέας θέσης")
        self.add_position_button.clicked.connect(self.add_position)
        layout.addWidget(self.add_position_button)

        self.view_positions_button = QPushButton("Προβολή θέσεών μου")
        self.view_positions_button.clicked.connect(self.view_agency_positions)
        layout.addWidget(self.view_positions_button)

        self.view_agency_details_button = QPushButton("Στοιχεία Φορέα")
        self.view_agency_details_button.clicked.connect(self.view_agency_details)
        layout.addWidget(self.view_agency_details_button)

        self.view_agency_rating_button = QPushButton("Αξιολόγηση Γραφείου Πρακτικής")
        self.view_agency_rating_button.clicked.connect(self.evaluation_office)
        layout.addWidget(self.view_agency_rating_button)

        self.exit_button = QPushButton("Έξοδος")
        self.exit_button.clicked.connect(self.exit)
        layout.addWidget(self.exit_button)
        self.setFixedSize(750, 300)
        central_widget.setLayout(layout)

    def evaluation_office(self):
        self.cursor.execute(
            "Select DISTINCT Agency_afm,Office_code from Position where (status='Χ' or status='Ο') and agency_afm=?",
            (self.agency_afm,),
        )
        rows = self.cursor.fetchall()
        self.office_show_window = QWidget()
        self.office_show_window.setWindowTitle("Γραφεία Πρακτικής")

        # Προσθήκη ScrollArea για υποστήριξη κύλισης
        scroll_area = QScrollArea(self.office_show_window)
        scroll_area.setWidgetResizable(True)

        central_widget = QWidget()
        central_layout = QVBoxLayout(central_widget)
        self.office_show_window.setWindowModality(Qt.WindowModality.ApplicationModal)

        if rows:
            for row in rows:
                self.cursor.execute(
                    "Select *,  GROUP_CONCAT(D.title,', ') As Departments From Internship_Office As O Join Department As D On D.Office_Code = O.Office_Code where O.office_code=? Group By O.Office_Code;",
                    (row[1],),
                )
                office_info = self.cursor.fetchone()
                details_group = QGroupBox(f"Κωδικός:{office_info['Office_code']}")
                details_layout = QVBoxLayout()

                # Δημιουργία ετικετών για τα στοιχεία της γραφείου
                office_address_label = QLabel(f"Διεύθυνση: {office_info['Address']}")
                office_phone_label = QLabel(f"Τηλέφωνο : {office_info['Phone']}")
                office_email_label = QLabel(f"Email : {office_info['Email']}")
                office_uni_label = QLabel(
                    f"Πανεπιστήμιο: {office_info['University_title']}"
                )
                office_dep_label = QLabel(f"Τμήματα: {office_info['Departments']}")
                office_emailR_label = QLabel(
                    f"Email Υπευθύνου: {office_info['Responsible_Email']}"
                )
                office_phoneR_label = QLabel(
                    f"Τηλέφωνο Υπευθύνου: {office_info['Responsible_Phone']}"
                )
                office_nameR_label = QLabel(
                    f"Ονομα Υπευθύνου: {office_info['Responsible_First_Name']} {office_info['Responsible_Last_name']}"
                )

                info1_label = QLabel("Στοιχεία Γραφείου")
                info1_label.setStyleSheet(
                    "font-size: 14px; text-decoration: underline;font-weight: bold"
                )
                info2_label = QLabel("Στοιχεία Υπεύθυνου Γραφείου")
                info2_label.setStyleSheet(
                    "font-size: 14px; text-decoration: underline;font-weight: bold"
                )
                info3_label = QLabel("Τμήματα που Εκπροσωπεί")
                info3_label.setStyleSheet(
                    "font-size: 14px; text-decoration: underline;font-weight: bold"
                )

                details_layout.addWidget(info1_label)

                details_layout.addWidget(office_address_label)
                details_layout.addWidget(office_phone_label)
                details_layout.addWidget(office_email_label)
                details_layout.addWidget(info2_label)
                details_layout.addWidget(office_nameR_label)
                details_layout.addWidget(office_phoneR_label)
                details_layout.addWidget(office_emailR_label)
                details_layout.addWidget(info3_label)
                details_layout.addWidget(office_uni_label)
                details_layout.addWidget(office_dep_label)

                show_eval_button = QPushButton("Προβολή Αξιολογησης")
                show_eval_button.clicked.connect(
                    lambda _, r=office_info["Office_code"]: self.sumbit_evaluate_office(
                        r, show=True
                    )
                )
                show_eval_button_layout = QHBoxLayout()
                show_eval_button_layout.addWidget(show_eval_button)
                show_eval_button_layout.addStretch(1)  # Τοποθετούμε το κουμπί δεξιά
                evaluate_button = QPushButton("Αξιολόγηση")
                evaluate_button.clicked.connect(
                    lambda _, r=office_info["Office_code"]: self.sumbit_evaluate_office(
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
        main_layout = QVBoxLayout(self.office_show_window)
        main_layout.addWidget(scroll_area)

        self.office_show_window.resize(700, 600)
        # Εμφάνιση του παραθύρου
        self.office_show_window.show()

    def sumbit_evaluate_office(self, office_code, show):
        self.eval_dialog = QDialog(self)
        self.eval_dialog.setWindowTitle("Αξιολόγηση Γραφείου")
        self.eval_dialog.setFixedSize(500, 800)
        self.eval_dialog.setWindowModality(Qt.WindowModality.ApplicationModal)

        # Κύριο layout
        layout = QVBoxLayout()

        # Τίτλος
        title_label = QLabel("Αξιολόγηση  Γραφείου")
        title_label.setStyleSheet(
            "font-size: 16px; font-weight: bold; text-decoration: underline"
        )
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        office_score_label = QLabel("Βαθμολογία (1-10):")
        office_score_spinbox = QSpinBox()
        office_score_spinbox.setRange(1, 10)
        office_score_spinbox.setValue(5)  # Default value
        layout.addWidget(office_score_label)
        layout.addWidget(office_score_spinbox)

        office_comment_label = QLabel("Σχόλια:")
        office_comment_textedit = QTextEdit()
        office_comment_textedit.setPlaceholderText(
            "Γράψτε τα σχόλιά σας για το Γραφείο εδώ..."
        )
        layout.addWidget(office_comment_label)
        layout.addWidget(office_comment_textedit)

        self.cursor.execute(
            "SELECT Agency_Rates_Office, Agency_Comments_To_Office FROM EVALUATION_AGENCY_OFFICE WHERE office_code = ? AND agency_afm = ?",
            (office_code, self.agency_afm),
        )
        rating = self.cursor.fetchone()

        if show:
            office_comment_textedit.setEnabled(False)
            office_score_spinbox.setEnabled(False)
            if rating is not None and rating[0] is not None:
                office_score_spinbox.setValue(rating[0])
                office_comment_textedit.setText(rating[1])
            else:
                QMessageBox.information(
                    None,
                    "Αξιολόγηση",
                    "Δεν έχετε υποβάλλει κάποια αξιολόγηση για το συγκεκριμένο Γραφείο",
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
                    office_score = office_score_spinbox.value()
                    office_comment = office_comment_textedit.toPlainText()
                    try:
                        if rating is not None:
                            self.cursor.execute(
                                "UPDATE EVALUATION_AGENCY_OFFICE SET Agency_Rates_Office = ?, Agency_Comments_To_Office= ? WHERE office_code = ? AND agency_afm = ?",
                                (
                                    office_score,
                                    office_comment,
                                    office_code,
                                    self.agency_afm,
                                ),
                            )
                        else:
                            self.cursor.execute(
                                "Insert into EVALUATION_AGENCY_OFFICE(Agency_afm,office_code,agency_rates_office,agency_comments_to_office) values(?,?,?,?)",
                                (
                                    self.agency_afm,
                                    office_code,
                                    office_score,
                                    office_comment,
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

    def exit(self):
        for widget in QApplication.topLevelWidgets():
            if widget is self.Startapp and isinstance(widget, QMainWindow):
                widget.show()
        self.close()

    def add_position(self):
        self.cursor.execute("SELECT MAX(Position_Number) FROM Position")
        max_position = self.cursor.fetchone()[0]
        self.position_counter = max_position

        self.position_counter = self.position_counter + 1
        self.position_window = QWidget()
        self.position_window.setWindowTitle("Εισάγετε Νέα Θέση")
        self.position_window.setFixedSize(800, 600)
        scroll_area = QScrollArea(self.position_window)
        scroll_area.setWidgetResizable(True)

        # Εσωτερικό widget για το scroll area
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)

        # Δημιουργία form layout
        layout = QFormLayout()

        self.title = QLineEdit()
        self.description = QTextEdit()
        self.duration_months = QSpinBox()
        self.duration_months.setMinimum(0)
        self.duration_months.setMaximum(10000)
        position_types = ["Πλήρες Απασχόληση", "Μερική Απασχόληση", "Αδιάφορο"]
        self.position_type = QComboBox()
        self.position_type.addItem("Κάνετε επιλογή")
        self.position_type.model().item(0).setEnabled(False)
        self.position_type.addItems(position_types)
        self.uni_list = QListWidget()
        self.uni_list.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)

        self.cursor.execute("SELECT title FROM University")
        universities = self.cursor.fetchall()
        for (university,) in universities:
            self.uni_list.addItem(university)
        # Δυναμική λίστα για τμήματα ανά πανεπιστήμιο
        self.department_widgets = (
            {}
        )  # Λεξικό για να αποθηκεύονται τα department comboboxes

        self.uni_list.itemSelectionChanged.connect(self.update_departments)
        self.cursor.execute("Select Name from SPECIALTY")
        specialties = self.cursor.fetchall()
        self.spec_input = QComboBox()
        self.spec_input.setEditable(True)
        self.spec_input.lineEdit().setReadOnly(True)

        # Δημιουργία QListWidget για το dropdown
        self.list_widget = QListWidget()
        self.checkbox_items = {}
        for specialty in specialties:
            self.add_multi_select_item(specialty[0])
        self.spec_input.setModel(self.list_widget.model())
        self.spec_input.setView(self.list_widget)
        self.region = QComboBox()
        self.region.addItems(self.regions)
        self.supervisor_fname = QLineEdit()
        self.supervisor_lname = QLineEdit()
        self.supervisor_phone = QLineEdit()
        self.supervisor_phone.setMaxLength(10)
        self.supervisor_email = QLineEdit()
        self.insertion_date = date.today()
        self.add_section_label(layout, "Στοιχεία Θέσης")
        layout.addRow(QLabel("Τίτλος Θέσης:"), self.title)
        layout.addRow(QLabel("Περιγραφή Θέσης:"), self.description)
        layout.addRow(QLabel("Διάρκεια σε Μήνες:"), self.duration_months)
        layout.addRow(QLabel("Είδος Θέσης:"), self.position_type)
        layout.addRow(QLabel("Περιοχή:"), self.region)
        layout.addRow(QLabel("Αντικείμενα:"), self.spec_input)
        layout.addRow(QLabel("Πανεπιστήμια:"), self.uni_list)

        self.department_layout = QVBoxLayout()
        layout.addRow(QLabel("Τμήματα:"), self.department_layout)
        self.add_section_label(layout, "Στοιχεία Επόπτη")
        layout.addRow(QLabel("Όνομα Επόπτη:"), self.supervisor_fname)
        layout.addRow(QLabel("Επώνυμο Επόπτη:"), self.supervisor_lname)
        layout.addRow(QLabel("Τηλέφωνο Επόπτη:"), self.supervisor_phone)
        layout.addRow(QLabel("Email Επόπτη:"), self.supervisor_email)
        scroll_area.setWidget(scroll_widget)

        self.submit_button = QPushButton("Καταχώρηση Θέσης")
        self.submit_button.clicked.connect(self.submit_position)
        layout.addWidget(self.submit_button)

        scroll_layout.addLayout(layout)
        scroll_area.setWidget(scroll_widget)
        main_layout = QVBoxLayout()
        main_layout = QVBoxLayout(self.position_window)
        main_layout.addWidget(scroll_area)
        self.position_window.setLayout(main_layout)
        self.position_window.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.position_window.show()

    def add_multi_select_item(self, text):
        list_item = QListWidgetItem(self.list_widget)
        checkbox = QCheckBox(text)
        self.list_widget.setItemWidget(list_item, checkbox)
        self.checkbox_items[text] = checkbox
        checkbox.stateChanged.connect(self.update_multi_select_line_edit)

    def update_multi_select_line_edit(self):
        selected_items = [
            text for text, cb in self.checkbox_items.items() if cb.isChecked()
        ]
        self.spec_input.lineEdit().setText(", ".join(selected_items))

    def update_departments(self):
        # Καθαρισμός του layout για τμήματα
        for widget in self.department_widgets.values():
            widget.hide()

        selected_universities = [item.text() for item in self.uni_list.selectedItems()]

        for university in selected_universities:
            if university not in self.department_widgets:
                # Δημιουργία νέου QListWidget για τα τμήματα αυτού του πανεπιστημίου
                list_widget = QListWidget()
                list_widget.setSelectionMode(
                    QAbstractItemView.SelectionMode.MultiSelection
                )
                self.department_widgets[university] = list_widget

                # Φόρτωση τμημάτων από τη βάση
                self.cursor.execute(
                    "SELECT title FROM Department WHERE university_title = ?",
                    (university,),
                )
                departments = self.cursor.fetchall()
                for (department,) in departments:
                    list_widget.addItem(department)

                self.department_layout.addWidget(list_widget)

            # Εμφάνιση του QListWidget για το επιλεγμένο πανεπιστήμιο
            self.department_widgets[university].show()

    def add_section_label(self, layout, text):
        label = QLabel(text)
        label.setStyleSheet(
            "font-size: 14px; text-decoration: underline;font-weight: bold"
        )
        layout.addRow(label)

    def submit_position(self):
        try:
            # Εισαγωγή των ειδικοτήτων στη βάση
            selected_specialties = [
                text for text, cb in self.checkbox_items.items() if cb.isChecked()
            ]
            for specialty in selected_specialties:
                self.cursor.execute(
                    "INSERT INTO SPECIALTY_POSITION (Position_Number, Agency_AFM, Object_Name) VALUES (?, ?, ?)",
                    (self.position_counter, self.agency_afm, specialty),
                )

            # Εισαγωγή πανεπιστημίων και τμημάτων
            selected_universities = [
                item.text() for item in self.uni_list.selectedItems()
            ]
            for university in selected_universities:
                if university in self.department_widgets:
                    selected_departments = [
                        item.text()
                        for item in self.department_widgets[university].selectedItems()
                    ]
                    for department in selected_departments:
                        self.cursor.execute(
                            "INSERT INTO POSITION_ACCESSIBLE_FROM_DEPT (Position_Number, University_Title, Department_Title, Agency_AFM) VALUES (?, ?, ?,?)",
                            (
                                self.position_counter,
                                university,
                                department,
                                self.agency_afm,
                            ),
                        )

            # Εισαγωγή της κύριας θέσης στη βάση
            self.cursor.execute(
                """
                INSERT INTO POSITION (
                    Position_Number, Title, Description, Duration, Type, Region, Agency_AFM, Insertion_Date,
                    Supervisor_First_Name, Supervisor_Last_Name, Supervisor_Phone, Supervisor_Email
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    self.position_counter,
                    self.title.text(),
                    self.description.toPlainText(),
                    self.duration_months.value(),
                    self.position_type.currentText(),
                    self.region.currentText(),
                    self.agency_afm,
                    self.insertion_date.strftime("%Y-%m-%d"),
                    self.supervisor_fname.text(),
                    self.supervisor_lname.text(),
                    self.supervisor_phone.text(),
                    self.supervisor_email.text(),
                ),
            )

            # Εμφάνιση μηνύματος επιτυχίας
            QMessageBox.information(None, "Επιτυχία", "Η θέση προστέθηκε με επιτυχία.")

            # Κλείσιμο του παραθύρου
            self.position_window.close()

        except Exception as e:
            # Εμφάνιση μηνύματος λάθους
            QMessageBox.critical(
                self.position_window, "Σφάλμα", f"Παρουσιάστηκε σφάλμα: {str(e)}"
            )

    def show_position_details(self, row):
        if row[10] == "Ε":  # Έλεγχος κατάστασης 'Επεξεργασία'
            self.cursor.execute(
                """
                SELECT P.*,
                    GROUP_CONCAT(D.Title) AS Departments,
                    GROUP_CONCAT(D.University_Title) AS Universities
                FROM (AGENCY_POSITIONS_WITH_SPEC AS P
                    JOIN POSITION_ACCESSIBLE_FROM_DEPT AS PD ON P.Position_Number = PD.Position_Number)
                    JOIN DEPARTMENT AS D
                    ON D.Title = PD.Department_Title AND D.University_Title = PD.University_Title
                WHERE P.Position_Number = ?
                GROUP BY P.Position_Number
                """,
                (row[0],),
            )

            pos = self.cursor.fetchone()

            if pos:
                self.position_window = QWidget()
                self.position_window.setWindowTitle("Επεξεργασία Θέσης")
                self.position_window.setFixedSize(800, 600)

                scroll_area = QScrollArea(self.position_window)
                scroll_area.setWidgetResizable(True)

                scroll_widget = QWidget()
                scroll_layout = QVBoxLayout(scroll_widget)

                layout = QFormLayout()

                # Τίτλος Θέσης
                self.title = QLineEdit()
                self.title.setText(pos["Title"])
                self.title.setReadOnly(True)
                layout.addRow(QLabel("Τίτλος Θέσης:"), self.title)

                # Περιγραφή Θέσης
                self.description = QTextEdit()
                self.description.setText(pos["Description"])
                self.description.setReadOnly(True)
                layout.addRow(QLabel("Περιγραφή Θέσης:"), self.description)

                self.duration_months = QSpinBox()
                self.duration_months.setValue(int(pos["Duration"]))
                self.duration_months.setMinimum(0)
                self.duration_months.setMaximum(10000)
                self.duration_months.setReadOnly(True)
                layout.addRow(QLabel("Διάρκεια σε Μήνες:"), self.duration_months)

                self.position_type = QComboBox()
                position_types = ["Πλήρες Απασχόληση", "Μερική Απασχόληση", "Αδιάφορο"]

                self.position_type.addItems(position_types)
                self.position_type.setCurrentText(pos["Type"])
                self.position_type.setEnabled(False)
                layout.addRow(QLabel("Είδος Θέσης:"), self.position_type)

                # Περιοχή
                self.region = QComboBox()
                self.region.addItems(self.regions)
                self.region.setCurrentText(pos["Region"])
                self.region.setEnabled(False)
                layout.addRow(QLabel("Περιοχή:"), self.region)

                # Στοιχεία Επόπτη
                self.supervisor_fname = QLineEdit()
                self.supervisor_fname.setText(pos["Supervisor_First_Name"])
                self.supervisor_fname.setReadOnly(True)
                layout.addRow(QLabel("Όνομα Επόπτη:"), self.supervisor_fname)

                self.supervisor_lname = QLineEdit()
                self.supervisor_lname.setText(pos["Supervisor_Last_Name"])
                self.supervisor_lname.setReadOnly(True)
                layout.addRow(QLabel("Επώνυμο Επόπτη:"), self.supervisor_lname)

                self.supervisor_phone = QLineEdit()
                self.supervisor_phone.setText(pos["Supervisor_Phone"])
                self.supervisor_phone.setReadOnly(True)
                layout.addRow(QLabel("Τηλέφωνο Επόπτη:"), self.supervisor_phone)

                self.supervisor_email = QLineEdit()
                self.supervisor_email.setText(pos["Supervisor_Email"])
                self.supervisor_email.setReadOnly(True)
                layout.addRow(QLabel("Email Επόπτη:"), self.supervisor_email)
                # Ειδικότητες
                self.spec_list = QListWidget()
                self.spec_list.setSelectionMode(
                    QAbstractItemView.SelectionMode.MultiSelection
                )
                selected_specialties = (
                    pos["Specialties"].split(", ") if pos["Specialties"] else []
                )

                self.cursor.execute("SELECT Name FROM SPECIALTY")
                specialties = self.cursor.fetchall()

                for specialty in specialties:
                    specialty_name = specialty[0]  # Εξαγωγή ονόματος ειδικότητας
                    item = QListWidgetItem(specialty_name)
                    if specialty_name in selected_specialties:
                        item.setSelected(True)
                    self.spec_list.addItem(item)

                self.spec_list.setEnabled(False)
                layout.addRow(QLabel("Αντικείμενα:"), self.spec_list)

                # Δημιουργία της λίστας για τα Πανεπιστήμια
                self.uni_list = QListWidget()
                self.uni_list.setSelectionMode(
                    QAbstractItemView.SelectionMode.MultiSelection
                )

                selected_universities = (
                    pos["Universities"].split(", ") if pos["Universities"] else []
                )

                self.cursor.execute("SELECT Title FROM UNIVERSITY")
                universities = self.cursor.fetchall()

                for university in universities:
                    university_name = university[0]  # Εξαγωγή ονόματος πανεπιστημίου
                    item = QListWidgetItem(university_name)
                    if university_name in selected_universities:
                        item.setSelected(True)
                    self.uni_list.addItem(item)

                self.uni_list.setEnabled(False)
                layout.addRow(QLabel("Πανεπιστήμια:"), self.uni_list)

                # Δυναμική λίστα για Τμήματα
                self.department_widgets = {}
                self.department_layout = QVBoxLayout()

                # Ενημέρωση τμημάτων για τα επιλεγμένα Πανεπιστήμια
                self.update_departments_for_selected_universities(
                    selected_universities, pos
                )
                layout.addRow(QLabel("Τμήματα:"), self.department_layout)

                self.uni_list.itemSelectionChanged.connect(
                    lambda: self.update_departments_for_selected_universities(
                        [item.text() for item in self.uni_list.selectedItems()], pos
                    )
                )

                # Κουμπί Επεξεργασίας
                self.edit_button = QPushButton("Επεξεργασία")
                self.edit_button.clicked.connect(self.enable_editing)
                layout.addWidget(self.edit_button)

                # Κουμπί Υποβολής
                self.submit_button = QPushButton("Υποβολή")
                self.submit_button.setEnabled(False)
                self.submit_button.clicked.connect(
                    lambda: self.submit_changes(
                        pos,
                        self.title.text(),
                        self.description.toPlainText(),
                        self.duration_months.value(),
                        self.position_type.currentText(),
                        self.region.currentText(),
                        self.supervisor_fname.text(),
                        self.supervisor_lname.text(),
                        self.supervisor_phone.text(),
                        self.supervisor_email.text(),
                    )
                )
                layout.addWidget(self.submit_button)

                scroll_layout.addLayout(layout)
                scroll_area.setWidget(scroll_widget)

                main_layout = QVBoxLayout()
                main_layout.addWidget(scroll_area)
                self.position_window.setLayout(main_layout)
                self.position_window.setWindowModality(
                    Qt.WindowModality.ApplicationModal
                )
                self.position_window.show()
        elif row[10] == "Π":
            self.details_window = QWidget()
            self.details_window.setWindowTitle(f"Λεπτομέρειες Θέσης #{row[0]}")

            details_layout = QVBoxLayout()
            # Προβολή λεπτομερειών της θέσης
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
            duration_label = QLabel(f"Διάρκεια: {row[12]}")
            type_label = QLabel(f"Είδος Θέσης: {row[13]}")
            insertion_date_label = QLabel(f"Ημερομηνία Εισαγωγής: {row[3]}")
            office_code_label = QLabel(f"Κωδικός Γραφείου: {row[16]}")
            supervisor_fname_lname_label = QLabel(
                f"Όνοματεπώνυμο Επόπτη : {row[5]} {row[5]}"
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
            details_layout.addWidget(QLabel(f"Τίτλος: {row[1]}"))
            details_layout.addWidget(description_label)
            details_layout.addWidget(scroll_area2)
            details_layout.addWidget(duration_label)
            details_layout.addWidget(type_label)
            details_layout.addWidget(region_label)
            details_layout.addWidget(insertion_date_label)
            if row[10] == "Π":
                details_layout.addWidget(office_code_label)
            details_layout.addWidget(supervisor_fname_lname_label)
            details_layout.addWidget(supervisor_phone_label)
            details_layout.addWidget(supervisor_email_label)
            details_layout.addWidget(specialty_name_label)
            details_layout.addWidget(scroll_area1)
            office_code_details_button = QPushButton("Στοιχεία Γραφείου Πρακτικής")
            office_code_details_button.clicked.connect(
                lambda _, r=row["Office_Code"]: self.view_office_details(r)
            )
            details_layout.addWidget(office_code_details_button)

            self.details_window.setLayout(details_layout)
            self.details_window.setWindowModality(Qt.WindowModality.ApplicationModal)

            self.details_window.show()

        else:
            # Δημιουργία παραθύρου λεπτομερειών
            self.details_window = QWidget()
            self.details_window.setWindowTitle(f"Λεπτομέρειες Θέσης #{row[0]}")

            details_layout = QVBoxLayout()
            # Προβολή λεπτομερειών της θέσης
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
            duration_label = QLabel(f"Διάρκεια: {row[12]}")
            type_label = QLabel(f"Είδος Θέσης: {row[13]}")
            insertion_date_label = QLabel(f"Ημερομηνία Εισαγωγής: {row[3]}")
            office_code_label = QLabel(f"Κωδικός Γραφείου: {row[16]}")
            supervisor_fname_lname_label = QLabel(
                f"Όνοματεπώνυμο Επόπτη : {row[5]} {row[6]}"
            )
            supervisor_phone_label = QLabel(f"Τηλέφωνο Επόπτη : {row[7]}")
            supervisor_email_label = QLabel(f"Email Επόπτη : {row[8]}")
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
            self.cursor.execute(
                "SELECT Name, Surname, Phone, Email, AMA, Student_ID FROM STUDENT WHERE ID = ?",
                (row[15],),
            )
            self.stud = self.cursor.fetchone()

            # Έλεγχος αν το αποτέλεσμα είναι None
            if self.stud is None:
                # Εμφάνιση μήνυματος αν δεν βρέθηκε ο φοιτητής
                student__ID_label = QLabel("Ο φοιτητής με αυτό το ID δεν βρέθηκε.")
                student_name_label = QLabel("Ο φοιτητής δεν βρέθηκε.")
                student_phone_label = QLabel("Δε διαθέσιμα στοιχεία τηλεφώνου.")
                student_email_label = QLabel("Δε διαθέσιμα στοιχεία email.")
                student_ama_label = QLabel("Δε διαθέσιμα στοιχεία ΑΜΑ.")
            else:
                # Αν βρέθηκε ο φοιτητής, εμφανίζουμε τα δεδομένα του
                student__ID_label = QLabel(
                    f"Αρ. Μητρώου Φοιτητή: {self.stud['Student_ID']}"
                )
                student_name_label = QLabel(
                    f"Ονοματεπώνυμο Φοιτητή: {self.stud['Name']} {self.stud['Surname']}"
                )
                student_phone_label = QLabel(f"Τηλέφωνο Φοιτητή: {self.stud['Phone']}")
                student_email_label = QLabel(f"Email Φοιτητή: {self.stud['Email']}")
                student_ama_label = QLabel(f"Α.Μ.Α. Φοιτητή: {self.stud['AMA']}")

            # Προσθήκη των λεπτομερειών στη διάταξη
            details_layout.addWidget(QLabel(f"Τίτλος: {row[1]}"))
            details_layout.addWidget(description_label)
            details_layout.addWidget(scroll_area2)
            details_layout.addWidget(duration_label)
            details_layout.addWidget(type_label)
            details_layout.addWidget(region_label)
            details_layout.addWidget(insertion_date_label)
            details_layout.addWidget(office_code_label)
            details_layout.addWidget(supervisor_fname_lname_label)
            details_layout.addWidget(supervisor_phone_label)
            details_layout.addWidget(supervisor_email_label)
            details_layout.addWidget(student__ID_label)
            details_layout.addWidget(student_name_label)
            details_layout.addWidget(student_phone_label)
            details_layout.addWidget(student_email_label)
            details_layout.addWidget(student_ama_label)
            details_layout.addWidget(specialty_label)
            details_layout.addWidget(scroll_area1)
            office_code_details_button = QPushButton("Στοιχεία Γραφείου Πρακτικής")
            office_code_details_button.clicked.connect(
                lambda _, r=row["Office_Code"]: self.view_office_details(r)
            )
            details_layout.addWidget(office_code_details_button)

            self.details_window.setLayout(details_layout)
            self.details_window.setWindowModality(Qt.WindowModality.ApplicationModal)

            self.details_window.show()

    def view_office_details(self, off_code):
        self.cursor.execute(
            "Select * from Internship_office where Office_code=?", (off_code,)
        )
        office_details = self.cursor.fetchone()
        if office_details:
            # Δημιουργία παραθύρου στοιχείων φορέα
            self.office_window = QWidget()
            self.office_window.setWindowTitle(f"Στοιχεία Γραφείου")
            details_layout = QVBoxLayout()
            office_code_label = QLabel(f"Κωδικός: {office_details['Office_code']}")
            office_addr_label = QLabel(f"Διεύθυνση: {office_details['Address']}")
            info2_label = QLabel("Στοιχεία Υπεύθυνου Γραφείου")
            info2_label.setStyleSheet(
                "font-size: 14px; text-decoration: underline;font-weight: bold"
            )
            office_email_label = QLabel(f"Email: {office_details['Email']}")
            office_emailR_label = QLabel(
                f"Email Υπευθύνου: {office_details['Responsible_Email']}"
            )
            office_phoneR_label = QLabel(
                f"Τηλέφωνο Υπευθύνου: {office_details['Responsible_Phone']}"
            )
            office_nameR_label = QLabel(
                f"Ονομα Υπευθύνου: {office_details['Responsible_First_Name']} {office_details['Responsible_Last_name']}"
            )
            office_phone_label = QLabel(f"Τηλέφωνο: {office_details['Phone']}")

            details_layout.addWidget(office_code_label)
            details_layout.addWidget(office_addr_label)

            details_layout.addWidget(office_email_label)
            details_layout.addWidget(office_phone_label)
            details_layout.addWidget(info2_label)
            details_layout.addWidget(office_nameR_label)
            details_layout.addWidget(office_phoneR_label)
            details_layout.addWidget(office_emailR_label)

            self.office_window.setWindowModality(Qt.WindowModality.ApplicationModal)
            self.office_window.setFixedSize(450, 450)
            self.office_window.setLayout(details_layout)
            self.office_window.show()

    def update_departments_for_selected_universities(self, selected_universities, pos):
        # Καθαρισμός προηγούμενων τμημάτων
        for widget in self.department_widgets.values():
            widget.hide()

        for university in selected_universities:
            if university not in self.department_widgets:
                list_widget = QListWidget()
                list_widget.setSelectionMode(
                    QAbstractItemView.SelectionMode.MultiSelection
                )
                self.department_widgets[university] = list_widget

                self.cursor.execute(
                    "SELECT Title FROM Department WHERE University_Title = ?",
                    (university,),
                )
                departments = self.cursor.fetchall()
                for (department,) in departments:
                    item = QListWidgetItem(department)
                    list_widget.addItem(item)

                self.department_layout.addWidget(list_widget)

            self.department_widgets[university].show()

    def enable_editing(self):
        """Ενεργοποίηση επεξεργασίας"""
        self.title.setReadOnly(False)
        self.description.setReadOnly(False)
        self.duration_months.setReadOnly(False)
        self.position_type.setEnabled(True)
        self.region.setEnabled(True)
        self.supervisor_fname.setReadOnly(False)
        self.supervisor_lname.setReadOnly(False)
        self.supervisor_phone.setReadOnly(False)
        self.supervisor_phone.setMaxLength(10)
        self.supervisor_email.setReadOnly(False)
        self.spec_list.setEnabled(True)
        self.uni_list.setEnabled(True)
        self.edit_button.setEnabled(False)
        self.submit_button.setEnabled(True)

    def submit_changes(
        self,
        pos,
        title,
        description,
        duration_months,
        position_type,
        region,
        supervisor_fname,
        supervisor_lname,
        supervisor_phone,
        supervisor_email,
    ):

        # Ενημέρωση βάσης δεδομένων για τη θέση
        try:
            # Υποθέτουμε σύνδεση στη βάση δεδομένων
            self.cursor.execute(
                """UPDATE Position SET Title=?, Description=?, Duration=?, Type=?, Region=?,
                Supervisor_First_Name=?, Supervisor_Last_Name=?, Supervisor_Phone=?, Supervisor_Email=? WHERE Position_Number=?""",
                (
                    title,
                    description,
                    duration_months,
                    position_type,
                    region,
                    supervisor_fname,
                    supervisor_lname,
                    supervisor_phone,
                    supervisor_email,
                    pos["Position_Number"],
                ),
            )

            # Αντιγραφή των επιλεγμένων τμημάτων
            selected_universities = [
                item.text() for item in self.uni_list.selectedItems()
            ]
            selected_departments = {
                university: [
                    item.text()
                    for item in self.department_widgets[university].selectedItems()
                ]
                for university in selected_universities
            }

            # Ανάκτηση του Agency_AFM από τη βάση δεδομένων για το Position
            self.cursor.execute(
                "SELECT Agency_AFM FROM Position WHERE Position_Number = ?",
                (pos["Position_Number"],),
            )
            agency_afm = self.cursor.fetchone()[0]

            # Αφαίρεση των προηγούμενων συνδέσεων με τμήματα
            self.cursor.execute(
                "DELETE FROM POSITION_ACCESSIBLE_FROM_DEPT WHERE Position_Number = ?",
                (pos["Position_Number"],),
            )

            # Εισαγωγή νέων συνδέσεων θέσης-τμήματος στον πίνακα POSITION_ACCESSIBLE_FROM_DEPT
            for university, departments in selected_departments.items():
                for department in departments:
                    self.cursor.execute(
                        """INSERT INTO POSITION_ACCESSIBLE_FROM_DEPT (Position_Number, Department_Title, University_Title, Agency_AFM)
                        VALUES (?, ?, ?, ?)""",
                        (pos["Position_Number"], department, university, agency_afm),
                    )

            # Αφαίρεση των προηγούμενων specialty associations
            self.cursor.execute(
                "DELETE FROM SPECIALTY_POSITION WHERE Position_Number = ?",
                (pos["Position_Number"],),
            )

            # Εισαγωγή νέων specialty associations στον πίνακα SPECIALTY_POSITION
            selected_specialties = [
                item.text() for item in self.spec_list.selectedItems()
            ]
            for specialty in selected_specialties:
                self.cursor.execute(
                    """INSERT INTO SPECIALTY_POSITION (Position_Number, Object_Name, Agency_AFM)
                    VALUES (?, ?, ?)""",
                    (pos["Position_Number"], specialty, agency_afm),
                )
            # Επιβεβαίωση της επιτυχίας
            QMessageBox.information(None, "Επιτυχία", "Η θέση ενημερώθηκε με επιτυχία.")
            self.position_window.close()
        except Exception as e:
            # Εμφάνιση μηνύματος λάθους σε περίπτωση αποτυχίας
            QMessageBox.warning(None, "Σφάλμα", f"Αποτυχία ενημέρωσης: {e}")

    def view_agency_positions(self):
        status_colors = {
            "Ε": "lightblue",
            "Π": "white",
            "Α": "darkviolet",
            "Υ": "yellow",
            "Ο": "green",
            "Χ": "red",
        }
        self.cursor.execute(" DROP VIEW IF EXISTS    AGENCY_POSITIONS;")
        self.cursor.execute("DROP VIEW IF EXISTS AGENCY_POSITIONS_WITH_SPEC;")
        agency_afm = self.agency_afm
        query = f"""
        CREATE VIEW IF NOT EXISTS AGENCY_POSITIONS AS
        SELECT *
        FROM
        (Position AS P
        JOIN AGENCY_WITH_RATING AS A ON P.Agency_AFM = A.AFM
        JOIN AGENCY AS AG ON AG.AFM = P.Agency_AFM
        Left JOIN MATCHING AS M ON M.Agency_AFM = AG.AFM AND P.Position_Number = M.Position_Number AND P.Office_Code = M.Office_Code )
        WHERE P.Agency_AFM = '{agency_afm}';
        """

        # Εκτέλεση του query
        self.cursor.execute(query)
        self.cursor.execute(
            """
            CREATE VIEW IF NOT EXISTS AGENCY_POSITIONS_WITH_SPEC AS
            SELECT S.Position_Number,A.Title,A.region,A.Insertion_Date,A.Agency_Name,A.Supervisor_First_Name,A.Supervisor_Last_Name,A.Supervisor_Phone,A.Supervisor_Email, GROUP_CONCAT(S.Object_Name, ', ') as SPECIALTIES,A.Status,A.Description,A.Duration,A.type,A.AFM, A.Student_ID, A.Office_Code
            FROM AGENCY_POSITIONS AS A
            JOIN SPECIALTY_POSITION AS S
            ON A.Position_Number = S.Position_Number
            GROUP BY A.Position_Number;
            """
        )

        self.cursor.execute("SELECT * FROM AGENCY_POSITIONS_WITH_SPEC")

        rows = self.cursor.fetchall()

        self.position_window = QWidget()
        self.position_window.setWindowTitle("Όλες οι Θέσεις")

        scroll_area = QScrollArea(self.position_window)
        scroll_area.setWidgetResizable(True)

        central_widget = QWidget()
        central_layout = QVBoxLayout(central_widget)

        for row in rows:
            if row:

                details_group = QGroupBox(f"Θέση #{row[0]}")
                details_group.setStyleSheet(
                    f"""
            QGroupBox {{
        background-color: {status_colors.get(row[10])};
    }}
    QGroupBox::title {{
        color: black; /* Μαύρο χρώμα */
        font-weight: bold; /* Προαιρετικό: bold */
            }}
            """
                )

                details_layout = QVBoxLayout()

                title_button = QPushButton(f"{row[1]}")
                title_button.clicked.connect(
                    lambda _, r=row: self.show_position_details(r)
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
                if row["Student_ID"] is not None:
                    self.cursor.execute(
                        "SELECT Name,Surname,Phone,Email,AMA,Student_ID FROM STUDENT WHERE ID = ?",
                        (row[15],),
                    )
                    self.stud = self.cursor.fetchone()
                    student_ID_label = QLabel(f"Αρ. Μητρώου Φοιτητή: {self.stud [5]}")
                    student_name_label = QLabel(
                        f"Ονοματεπώνυμο Φοιτητή: {self.stud[0]} {self.stud[1]}"
                    )
                    student_phone_label = QLabel(f"Τηλέφωνο Φοιτητή: {self.stud[2]}")
                    student_email_label = QLabel(f"Email Φοιτητή: {self.stud[3]}")
                    student_ama_label = QLabel(f"Α.Μ.Α. Φοιτητή: {self.stud[4]}")
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
                details_layout.addLayout(top_layout)
                details_layout.addWidget(region_label)
                details_layout.addWidget(insertion_date_label)
                details_layout.addWidget(supervisor_fname_lname_label)
                details_layout.addWidget(supervisor_phone_label)
                details_layout.addWidget(supervisor_email_label)
                if row["Student_ID"] is not None:
                    details_layout.addWidget(student_ID_label)
                    details_layout.addWidget(student_name_label)
                    details_layout.addWidget(student_phone_label)
                    details_layout.addWidget(student_email_label)
                    details_layout.addWidget(student_ama_label)
                details_layout.addWidget(specialty_name_label)
                details_layout.addWidget(scroll_area1)

                details_group.setLayout(details_layout)
                central_layout.addWidget(details_group)

        # Προσθήκη του κεντρικού widget στο ScrollArea
        scroll_area.setWidget(central_widget)

        # Τελική διάταξη για το παράθυρο
        main_layout = QVBoxLayout(self.position_window)
        main_layout.addWidget(scroll_area)

        # Εμφάνιση του παραθύρου
        self.position_window.resize(600, 800)
        self.position_window.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.position_window.show()

    def view_agency_details(self):
        self.cursor.execute("SELECT * FROM Agency WHERE Afm=?", (self.agency_afm,))
        row = self.cursor.fetchone()
        if row:
            self.dialog = Register_Agency_Dialog(self.cursor, self.regions)
            self.dialog.setWindowTitle("Στοιχεία Φορέα")
            self.dialog.username_input.setText(f"{row[3]}")
            self.dialog.password_input.setText(f"{row[4]}")
            self.dialog.AFM_input.setText(f"{row[0]}")
            self.dialog.phone_input.setText(f"{row[8]}")
            self.dialog.phoneR_input.setText(f"{row[10]}")
            self.dialog.email_input.setText(f"{row[5]}")
            self.dialog.emailR_input.setText(f"{row[9]}")
            self.dialog.fname_input.setText(f"{row[11]}")
            self.dialog.lname_input.setText(f"{row[12]}")
            self.dialog.Aname_input.setText(f"{row[1]}")
            self.dialog.Location_input.setCurrentText(f"{row[2]}")
            self.dialog.type_input.setCurrentText(f"{self.dialog.type_map.get(row[6])}")
            self.dialog.empc_input.setValue(int(row[7]))
            self.dialog.username_input.setReadOnly(True)
            self.dialog.password_input.setReadOnly(True)
            self.dialog.phone_input.setReadOnly(True)
            self.dialog.email_input.setReadOnly(True)
            self.dialog.AFM_input.setReadOnly(True)
            self.dialog.fname_input.setReadOnly(True)
            self.dialog.lname_input.setReadOnly(True)
            self.dialog.phoneR_input.setReadOnly(True)
            self.dialog.Aname_input.setReadOnly(True)
            self.dialog.emailR_input.setReadOnly(True)
            self.dialog.type_input.setEnabled(not True)
            self.dialog.empc_input.setEnabled(not True)
            self.dialog.Location_input.setEnabled(not True)
            self.dialog.edit_button.setVisible(True)
            self.dialog.edit_button.clicked.connect(self.set_details_editable)
            self.edit_pressed = False
        if (
            self.dialog.exec() == QDialog.DialogCode.Accepted
            and self.edit_pressed == True
        ):
            agency_info = self.dialog.get_info()
            if agency_info != None:
                try:
                    self.cursor.execute(
                        "UPDATE Agency set Location=?,Username=?,Password=?,Email=?,Type=?,Employee_Count=?,Phone=?,Manager_Email=?,Manager_Phone=?,Manager_Name=?,Manager_Surname=? where AFM=?",
                        agency_info[2:] + [self.agency_afm],
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
                    elif "AFM" in error_message:
                        QMessageBox.warning(
                            None, "Σφάλμα", " Ο ΑΦΜ υπάρχει ήδη καταχωρημένος!"
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
        self.dialog.phoneR_input.setReadOnly(False)
        self.dialog.emailR_input.setReadOnly(False)
        self.dialog.type_input.setEnabled(not False)
        self.dialog.empc_input.setEnabled(not False)
        self.dialog.Location_input.setEnabled(not False)
        self.edit_pressed = True
