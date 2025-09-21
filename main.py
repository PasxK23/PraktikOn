# -*- coding: utf-8 -*-
import sys
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
import sqlite3
from sqlite3 import Error
from datetime import datetime
from PyQt6.QtCore import Qt
from datetime import date
from startapp import StartApp
from student_menu import StudentMenu
from agency_menu import AgencyMenu
from office_menu import OfficeMenu
from register_agency_dialog import Register_Agency_Dialog
from register_student_dialog import Register_Student_Dialog
from register_office_dialog import Register_Office_Dialog


if __name__ == "__main__":
    import sys

    regions = [
        "Αγία Παρασκευή",
        "Άγιος Νικόλαος",
        "Αγρίνιο",
        "Αθήνα",
        "Αίγιο",
        "Αλεξάνδρεια",
        "Αλεξανδρούπολη",
        "Αλμυρός",
        "Αμαλιάδα",
        "Ἀμαλιούπολις",
        "Αμύνταιο",
        "Αμφιλοχία",
        "Άμφισσα",
        "Ανάπλι",
        "Ανδραβίδα",
        "Άργος",
        "Αργοστόλι",
        "Αρναία",
        "Άρτα",
        "Άστρος",
        "Βέροια",
        "Βίλια",
        "Βίλλια",
        "Βόλος",
        "Βραχώρι",
        "Βύλλια",
        "Γιανιτσά",
        "Γιαννιτσά",
        "Διδυμότειχο",
        "Δράμα",
        "Έδεσσα",
        "Ελασσόνα",
        "Επανομή",
        "Ερμούπολη",
        "Ζητούνι",
        "Ηγουμενίτσα",
        "Ηράκλειο",
        "Θεσσαλονίκη",
        "Θήβα",
        "Θρακομακεδόνες",
        "Ιωάννινα",
        "Καβάλα",
        "Καλαμάτα",
        "Καλαμπάκα",
        "Καλλιδρόμη",
        "Καρδίτσα",
        "Καρπενήσι",
        "Καρπενίσι",
        "Καστοριά",
        "Κατερίνη",
        "Κερατέα",
        "Κερατιά",
        "Κέρκυρα",
        "Κιάτο",
        "Κιλκίς",
        "Κοζάνη",
        "Κομοτηνή",
        "Κόνιτσα",
        "Κόρθος",
        "Κόρινθος",
        "Κορωπί",
        "Κρέστενα",
        "Κυπαρισσία",
        "Λαμία",
        "Λάρισα",
        "Λευκάδα",
        "Ληξούρι",
        "Λιβαδιά",
        "Λουτράκι",
        "Μάνδρα",
        "Μαντίνεια",
        "Μεγαλόπολη",
        "Μεσολόγγι",
        "Μεσσήνη",
        "Μολάοι",
        "Μονεμβασιά",
        "Μυτιλήνη",
        "Ναύπλιο",
        "Ξάνθη",
        "Ορεστιάδα",
        "Πάργα",
        "Πάτρα",
        "Πειραιάς",
        "Πέλιννα",
        "Περαίας",
        "Πρέβεζα",
        "Πτολεμαΐδα",
        "Πύλος",
        "Πύργος",
        "Ρέθυμνο",
        "Ρίο",
        "Σαλαμίνα",
        "Σαλονίκη",
        "Σέρραι",
        "Σέρρες",
        "Σητεία",
        "Σουφλί",
        "Σπάρτη",
        "Σταγοί",
        "Τίρναβος",
        "Τρίκαλα",
        "Τρίπολη",
        "Τρίπολις",
        "Τριπολιτσά",
        "Τύρναβος",
        "Φάρσαλα",
        "Φέρσαλα",
        "Φλώρινα",
        "Χαλκίδα",
        "Χανιά",
        "Χίος",
        "Ωραιόκαστρο",
    ]
    conn = sqlite3.connect(
        "praktikon.db", isolation_level=None, check_same_thread=False
    )

    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    app = QApplication(sys.argv)
    font = QFont("Arial", 10)
    app.setFont(font)

    window = StartApp(conn, cursor, regions)
    window.show()
    exit_code = app.exec()
    cursor.execute(" DROP VIEW IF EXISTS   AGENCY_POSITIONS;")
    cursor.execute("DROP VIEW IF EXISTS AGENCY_POSITIONS_WITH_SPEC;")
    cursor.execute("DROP VIEW IF EXISTS SELECTED_POSITIONS")
    cursor.execute(" DROP VIEW IF EXISTS FREE_POSITIONS;")
    cursor.execute("DROP VIEW IF EXISTS FREE_POSITIONS_WITH_SPEC;")

    cursor.execute("DROP View if exists Student_Office")
    cursor.execute("DROP View if exists Students_Positions")
    sys.exit(exit_code)

    conn.close()
