import sqlite3
import random
import json
from sqlite3 import Error
from datetime import timedelta
from datetime import date


# Σύνδεση στη βάση δεδομένων
db_path = "praktikon.db"
connection = sqlite3.connect(db_path)
cursor = connection.cursor()


try:
    # Απενεργοποίηση των περιορισμών για να επιτραπεί η διαγραφή δεδομένων
    cursor.execute("PRAGMA foreign_keys = OFF;")

    # Λήψη όλων των προβολών (views)
    cursor.execute("SELECT name FROM sqlite_master WHERE type = 'view';")
    views = cursor.fetchall()

    # Διαγραφή όλων των προβολών
    for view_name in views:
        cursor.execute(f"DROP VIEW IF EXISTS {view_name[0]};")
        print(f"View {view_name[0]} διαγράφηκε.")

    # Λήψη όλων των πινάκων
    cursor.execute("SELECT name FROM sqlite_master WHERE type = 'table';")
    tables = cursor.fetchall()

    # Διαγραφή δεδομένων από όλους τους πίνακες
    for table_name in tables:
        cursor.execute(f"DELETE FROM {table_name[0]};")
        print(f"Δεδομένα από τον πίνακα {table_name[0]} διαγράφηκαν.")

    # Επαναφορά των auto-increment counters
    cursor.execute("DELETE FROM sqlite_sequence;")
    print("Τα auto-increment counters επαναφέρθηκαν.")

    connection.commit()
    print("Όλες οι διαγραφές ολοκληρώθηκαν επιτυχώς.")

except Exception as e:
    print(f"Σφάλμα κατά τη διαγραφή δεδομένων και προβολών: {e}")


try:
    cursor.execute("PRAGMA foreign_keys = ON;")
    cursor.execute(
        """
CREATE TABLE IF NOT EXISTS "UNIVERSITY" (
    "Title" varchar NOT NULL,
    PRIMARY KEY("Title")
);
"""
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS "AGENCY" (
"AFM"	integer NOT NULL,
"Agency_Name"	varchar NOT NULL,
"Location"	string NOT NULL,
"Username"	varchar NOT NULL UNIQUE,
"Password"	varchar NOT NULL,
"Email"	varchar NOT NULL,
"Type"	varchar NOT NULL,
"Employee_Count"	integer,
"Phone"	varchar,
"Manager_Email"	varchar NOT NULL,
"Manager_Phone"	varchar,
"Manager_Name"	varchar NOT NULL,
"Manager_Surname"	varchar NOT NULL,
PRIMARY KEY("AFM"),
CONSTRAINT "PASS_CHECK" CHECK(LENGTH(CAST("Password" AS TEXT)) > 5),
CONSTRAINT "AFM_CHECK" CHECK(LENGTH(CAST("AFM" AS TEXT)) = 9),
CONSTRAINT "TYPE_CHECK" CHECK("Type" IN ('Δ', 'Μ', 'Α', 'Ι'))
        );
    """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS "INTERNSHIP_OFFICE" (
"Office_Code"	integer NOT NULL,
"Phone"	varchar,
"Email"	varchar NOT NULL,
"Address"	varchar,
"Username"	varchar NOT NULL UNIQUE,
"Password"	varchar NOT NULL,
"Responsible_First_Name"	varchar NOT NULL,
"Responsible_Last_Name"	varchar NOT NULL,
"Responsible_Email"	varchar NOT NULL,
"Responsible_Phone"	varchar,
PRIMARY KEY("Office_Code" AUTOINCREMENT),
CONSTRAINT "PASS_CHECK" CHECK(LENGTH(CAST("Password" AS TEXT)) > 5)
);
    """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS "DEPARTMENT" (
"Title"	varchar NOT NULL,
"Office_Code"	integer,
"University_Title"	varchar NOT NULL,
PRIMARY KEY("Title","University_Title"),
FOREIGN KEY("Office_Code") REFERENCES "INTERNSHIP_OFFICE"("Office_Code") ON UPDATE CASCADE ON DELETE SET NULL,
FOREIGN KEY("University_Title") REFERENCES "UNIVERSITY"("Title") ON UPDATE CASCADE ON DELETE CASCADE
);
    """
    )

    cursor.execute(
        """
        CREATE TABLE  IF NOT EXISTS "STUDENT" (
"ID"	integer NOT NULL,
"Name"	varchar NOT NULL,
"Surname"	varchar NOT NULL,
"Phone"	varchar,
"Student_ID"	INTEGER NOT NULL,
"Email"	varchar NOT NULL,
"Username"	varchar NOT NULL UNIQUE,
"Password"	varchar NOT NULL,
"AMA"	integer NOT NULL UNIQUE,
"Department_Title"	varchar,
"University_Title"	varchar,
PRIMARY KEY("ID" AUTOINCREMENT),
FOREIGN KEY("Department_Title","University_Title") REFERENCES "DEPARTMENT"("Title","University_Title") ON UPDATE CASCADE ON DELETE SET NULL,
CONSTRAINT "PASS_CHECK" CHECK(LENGTH(CAST("Password" AS TEXT)) > 5),
CONSTRAINT "AMA_CHECK" CHECK(LENGTH(CAST("AMA" AS TEXT)) = 8)
);
    """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS "EVALUATION_AGENCY_OFFICE" (
"Agency_AFM"	integer NOT NULL,
"Office_Code"	integer NOT NULL,
"Office_Rates_Agency"	integer,
"Office_Comments_To_Agency"	text,
"Agency_Rates_Office"	integer,
"Agency_Comments_To_Office"	text,
PRIMARY KEY("Agency_AFM","Office_Code"),
FOREIGN KEY("Agency_AFM") REFERENCES "AGENCY"("AFM") ON UPDATE CASCADE ON DELETE RESTRICT,
FOREIGN KEY("Office_Code") REFERENCES "INTERNSHIP_OFFICE"("Office_Code") ON UPDATE CASCADE ON DELETE RESTRICT
);
    """
    )
    cursor.execute(
        """
        CREATE TABLE  IF NOT EXISTS "POSITION" (
"Position_Number"	integer NOT NULL,
"Title"	varchar NOT NULL,
"Description"	TEXT,
"Duration"	varchar NOT NULL,
"Type"	varchar NOT NULL,
"Region"	string NOT NULL,
"Status"	string DEFAULT 'Ε',
"Internship_Start_Date"	date,
"Internship_End_Date"	date,
"Agency_AFM"	INTEGER NOT NULL,
"Insertion_Date"	date NOT NULL,
"Office_Comments_To_Student"	text,
"Office_Rating_To_Student"	integer,
"Office_Code"	integer,
"Agency_Rating_To_Student"	integer,
"Agency_Comments_To_Student"	text,
"Supervisor_First_Name"	varchar NOT NULL,
"Supervisor_Last_Name"	varchar NOT NULL,
"Supervisor_Phone"	varchar,
"Supervisor_Email"	varchar NOT NULL,
PRIMARY KEY("Position_Number","Agency_AFM"),
FOREIGN KEY("Agency_AFM") REFERENCES "AGENCY"("AFM") ON UPDATE CASCADE ON DELETE CASCADE,
FOREIGN KEY("Office_Code") REFERENCES "INTERNSHIP_OFFICE"("Office_Code") ON UPDATE CASCADE ON DELETE SET NULL,
CONSTRAINT "STATUS_CHECK" CHECK("Status" IN ('Ε', 'Π', 'Α', 'Υ', 'Ο', 'Χ')),
CONSTRAINT "DATE_CHECK" CHECK("Internship_Start_Date" < "Internship_End_Date")
);
    """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS "FAVORITES" (
"Student_ID"	integer NOT NULL,
"Position_Number"	integer NOT NULL,
"Agency_AFM"	INTEGER NOT NULL,
PRIMARY KEY("Student_ID","Position_Number","Agency_AFM"),
FOREIGN KEY("Agency_AFM","Position_Number") REFERENCES "POSITION"("Agency_AFM","Position_Number") ON UPDATE CASCADE ON DELETE CASCADE,
FOREIGN KEY("Student_ID") REFERENCES "STUDENT"("ID") ON UPDATE CASCADE ON DELETE CASCADE
);
    """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS "MATCHING" (
"Predicted_Start_Date"	date NOT NULL,
"Predicted_End_Date"	date NOT NULL,
"Payment_Method"	text NOT NULL,
"Office_Code"	INTEGER NOT NULL,
"Position_Number"	INTEGER NOT NULL,
"Student_ID"	integer NOT NULL,
"Agency_Rating"	INTEGER,
"Agency_Comments"	TEXT,
"Office_Rating"	INTEGER,
"Office_Comments"	TEXT,
"Agency_AFM"	integer NOT NULL,
PRIMARY KEY("Office_Code","Student_ID","Position_Number","Agency_AFM"),
FOREIGN KEY("Office_Code") REFERENCES "INTERNSHIP_OFFICE"("Office_Code") ON DELETE SET NULL ON UPDATE CASCADE,
FOREIGN KEY("Position_Number","Agency_AFM") REFERENCES "Position"("Position_Number","Agency_AFM") ON DELETE CASCADE ON UPDATE CASCADE,
FOREIGN KEY("Student_ID") REFERENCES "STUDENT"("ID") ON DELETE RESTRICT ON UPDATE CASCADE,
CONSTRAINT "DATE_CHECK" CHECK("Predicted_Start_Date" < "Predicted_End_Date"),
CONSTRAINT "PAYMENT_CHECK" CHECK("Payment_Method" IN ('ΕΣΠΑ', 'ΙΔΡΥΜΑ', 'ΟΑΕΔ', 'ΦΟΡΕΑΣ'))
);
    """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS "POSITION_ACCESSIBLE_FROM_DEPT" (
"Position_Number"	integer NOT NULL,
"Department_Title"	varchar NOT NULL,
"University_Title"	varchar NOT NULL,
"Agency_AFM"	INTEGER NOT NULL,
PRIMARY KEY("Position_Number","Department_Title","University_Title","Agency_AFM"),
FOREIGN KEY("Agency_AFM","Position_Number") REFERENCES "POSITION"("Agency_AFM","Position_Number") ON UPDATE CASCADE ON DELETE CASCADE,
FOREIGN KEY("Department_Title","University_Title") REFERENCES "DEPARTMENT"("Title","University_Title") ON UPDATE CASCADE ON DELETE CASCADE
);
    """
    )
    cursor.execute(
        """
CREATE TABLE IF NOT EXISTS "SPECIALTY" (
    "Name" varchar NOT NULL,
    PRIMARY KEY("Name")
);
"""
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS "SPECIALTY_POSITION" (
"Position_Number"	INTEGER NOT NULL,
"Agency_AFM"	integer NOT NULL,
"Object_Name"	varchar NOT NULL,
PRIMARY KEY("Position_Number","Agency_AFM","Object_Name"),
FOREIGN KEY("Agency_AFM","Position_Number") REFERENCES "POSITION"("Agency_AFM","Position_Number") ON UPDATE CASCADE ON DELETE CASCADE,
FOREIGN KEY("Object_Name") REFERENCES "SPECIALTY"("Name") ON UPDATE CASCADE ON DELETE CASCADE
);
    """
    )
    cursor.execute(
        "CREATE VIEW IF NOT EXISTS AGENCY_WITH_RATING AS SELECT A.AFM,A.Agency_Name,A.Location,A.Email,A.Type,A.Phone,AVG(MATCHING.Agency_Rating) AS Rating FROM AGENCY AS A LEFT JOIN MATCHING ON A.AFM=MATCHING.Agency_AFM GROUP BY A.AFM"
    )

    connection.commit()
    print("Οι πίνακες δημιουργήθηκαν επιτυχώς.")
except Exception as e:
    print(f"Σφάλμα κατά τη δημιουργία των πινάκων: {e}")
# Φόρτωση δεδομένων από αρχεία


def load_names(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read().splitlines()


male_names = load_names(r"males.txt")
female_names = load_names(r"females.txt")
male_surnames = load_names(r"malesepitheta.txt")
female_surnames = load_names(r"femalesepitheta.txt")

with open("universities_departments.json", "r", encoding="utf-8") as file_unis:
    universities_departments = json.load(file_unis)

with open("antikeimena.json", "r", encoding="utf-8") as file_objects:
    specialties = json.load(file_objects)


# Δημιουργία εγγραφών
def generate_random_records():
    gender_choice = random.choice(["male", "female"])
    if gender_choice == "male":
        name = random.choice(male_names)
        surname = random.choice(male_surnames)
    else:
        name = random.choice(female_names)
        surname = random.choice(female_surnames)
    return name, surname


def generate_random_dates():
    year = random.randint(2022, 2024)
    start_date = date(year, random.randint(1, 5), random.randint(1, 15))
    end_date = start_date + timedelta(days=random.choice([90, 180, 365]))
    return start_date, end_date


def generate_random_pred_dates():
    year = random.randint(2025, 2026)
    start_date = date(year, random.randint(1, 5), random.randint(1, 15))
    end_date = start_date + timedelta(days=random.choice([90, 180, 365]))
    return start_date, end_date


try:
    off_codes = []
    # Εισαγωγή Πανεπιστημίων, Τμημάτων και Ειδικοτήτων
    for university, departments in universities_departments.items():
        cursor.execute("INSERT INTO UNIVERSITY (Title) VALUES (?);", (university,))
        for department in departments:
            cursor.execute(
                "INSERT INTO DEPARTMENT (Title, University_Title) VALUES (?, ?);",
                (department, university),
            )
    for specialty in specialties:
        cursor.execute("INSERT INTO SPECIALTY (Name) VALUES (?);", (specialty,))

    for i in range(400):
        afm = 100000000 + i
        agency_name = f"Agency_{i}"
        location = random.choice(
            [
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
        )
        username = f"Agency_user{i}"
        password = f"Agency_pass{i}"
        email = f"Agency_{i}@gmail.com"
        agency_type = random.choice(["Δ", "Ι", "Α", "Μ"])
        employee_count = random.randint(1, 1000)
        phone = 6945000000 + i
        manager_email = f"Manager_{i}@gmail.com"
        manager_phone = 6940000000 + i
        manager_name, manager_surname = generate_random_records()

        cursor.execute(
            """
            INSERT INTO AGENCY (AFM, Agency_Name, Location, Username, Password, Email, Type, Employee_Count, Phone, Manager_Email, Manager_Phone, Manager_Name, Manager_Surname)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """,
            (
                afm,
                agency_name,
                location,
                username,
                password,
                email,
                agency_type,
                employee_count,
                phone,
                manager_email,
                manager_phone,
                manager_name,
                manager_surname,
            ),
        )

    office_per_university = {}
    office_counter = 0
    for university, departments in universities_departments.items():
        office_per_university[university] = []
        office_codes = []  # Λίστα για αποθήκευση των γραφείων του πανεπιστημίου
        for _ in range(min(1, len(departments)//2)):  # Μέγιστο 1 γραφεία ανά πανεπιστήμιο
            office_code = office_counter
            office_counter += 1
            office_phone = 6970000000 + office_code
            office_address = random.choice(
                [
                    "Οδός Αριστοτέλους 15",
                    "Οδός Κολοκοτρώνη 23",
                    "Οδός Ερμού 8",
                    "Οδός Σταδίου 14",
                    "Οδός Εθνικής Αντιστάσεως 32",
                    "Οδός Παπανικολή 5",
                    "Οδός Ακρωτηρίου 12",
                    "Οδός Κύπρου 18",
                    "Οδός Αποστόλου Παύλου 21",
                    "Οδός Μεγάλου Αλεξάνδρου 7",
                    "Οδός Νικηφόρου Φωκά 19",
                    "Οδός Πλαστήρα 3",
                    "Οδός Βενιζέλου 9",
                    "Οδός Τρικούπη 27",
                    "Οδός Αγίου Νικολάου 11",
                    "Οδός Κωνσταντίνου Καραμανλή 6",
                    "Οδός Καραϊσκάκη 20",
                    "Οδός Ηρακλείου 4",
                    "Οδός Διονυσίου Σολωμού 15",
                    "Οδός Γεωργίου Παπανδρέου 8",
                    "Οδός Ευριπίδου 16",
                    "Οδός Μιλτιάδη Μακρυγιάννη 12",
                    "Οδός Ιωάννη Καποδίστρια 10",
                    "Οδός Σαπφούς 18",
                    "Οδός Ομήρου 22",
                    "Οδός Θεμιστοκλέους 13",
                    "Οδός Λεωφόρος Δημοκρατίας 2",
                    "Οδός Ελευθερίου Βενιζέλου 30",
                    "Οδός Αλκμήνης 24",
                    "Οδός Ιπποκράτους 19",
                    "Οδός Φιλίππου 28",
                    "Οδός Ζαχαρία Παπαντωνίου 17",
                ]
            )
            office_email = f"Office_{office_code}@gmail.com"
            office_username = f"Office_user{office_code}"
            office_password = f"Office_pass{office_code}"
            (of_first_name, of_last_name) = generate_random_records()
            office_responsible_fname = of_first_name
            office_responsible_lname = of_last_name
            office_responsible_email = f"Responsible{office_code}@gmail.com"
            office_responsible_phone = 6975000000 + office_code

            # Εισαγωγή στη βάση
            cursor.execute(
                """
                INSERT INTO INTERNSHIP_OFFICE (Office_Code, Phone, Email, Username, Password, Address, Responsible_First_Name, Responsible_Last_Name, Responsible_Email, Responsible_Phone)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?,? );
                """,
                (
                    office_code,
                    office_phone,
                    office_email,
                    office_username,
                    office_password,
                    office_address,
                    office_responsible_fname,
                    office_responsible_lname,
                    office_responsible_email,
                    office_responsible_phone,
                ),
            )
            office_codes.append(office_code)  # Αποθήκευση του γραφείου
            office_per_university[university].append(office_code)

        # Εναλλαγή τμημάτων στα γραφεία
        for idx, department in enumerate(departments):
            if random.random() < 0.4:
                cursor.execute(
                    """
                    UPDATE DEPARTMENT
                    SET Office_Code = NULL
                    WHERE Title = ? AND University_Title = ?;
                    """,
                    (department, university),
                )
            else:
                assigned_office_code = office_codes[idx % len(office_codes)]
                cursor.execute(
                    """
                    UPDATE DEPARTMENT
                    SET Office_Code = ?
                    WHERE Title = ? AND University_Title = ?;
                    """,
                    (assigned_office_code, department, university),
                )

    for i in range(1, 1000):
        st_ID = 100000 + i
        (st_first_name, st_last_name) = generate_random_records()
        student_fname = st_first_name
        student_lname = st_last_name
        student_email = f"Student{i}@gmail.com"
        student_phone = 6948500000 + i
        st_student_ID = 100 + i
        student_username = f"Student_user{i}"
        student_password = f"Sudent_pass{i}"
        student_AMA = 30000000 + i
        chosen_university = ""
        chosen_department = ""
        university = random.choice(list(universities_departments.keys()))

        department_title = random.choice(universities_departments[university])

        for code in office_per_university.get(university, []):

            if code is not None:
                chosen_university = university
                chosen_department = department_title

                cursor.execute(
                    "SELECT Office_Code FROM DEPARTMENT WHERE Title=? AND University_Title=? AND Office_Code IS NOT NULL",
                    (department_title, university),
                )
                result = cursor.fetchone()
                if result:
                    office_code = result[0]
                    off_codes.append(office_code)
                else:
                    break

            else:
                continue
        if office_code is None:
            continue
        cursor.execute(
            """
            INSERT INTO STUDENT (Name, Surname, Phone, Student_ID, Email, Username, Password, AMA, Department_Title, University_Title)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """,
            (
                student_fname,
                student_lname,
                student_phone,
                st_student_ID,
                student_email,
                student_username,
                student_password,
                student_AMA,
                chosen_department,
                chosen_university,
            ),
        )

    # Εισαγωγή 3000 POSITION
    for i in range(2000):
        position_number = i + 1
        title = random.choice(specialties)
        description = f"Description_{i}"
        duration = random.randint(1, 12)
        office_code = random.choice(off_codes)
        position_type = random.choice(
            ["Πλήρες Απασχόληση", "Μερική Απασχόληση", "Αδιάφορο"]
        )
        region = random.choice(
            [
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
        )
        status = random.choice(["Ε", "Π", "Α", "Υ", "Ο", "Χ"])
        insertion_date = generate_random_dates()[0]
        supervisor_fname, supervisor_lname = generate_random_records()
        supervisor_phone = 6950000000 + i
        supervisor_email = f"Supervisor_{i}@gmail.com"

        # Fetch unique student ID
        cursor.execute("SELECT DISTINCT ID FROM STUDENT ORDER BY RANDOM() LIMIT 1;")
        st_ID = cursor.fetchone()[0]

        # Fetch unique agency AFM
        cursor.execute("SELECT DISTINCT AFM FROM AGENCY ORDER BY RANDOM() LIMIT 1;")
        agency_afm = cursor.fetchone()[0]

        used_combinations1 = set()
        # Insert POSITION based on status
        if status == "Ε":
            cursor.execute(
                """
                INSERT INTO POSITION (Position_Number,Title, Description, Duration, Type, Region, Status, Agency_AFM, Insertion_Date, Supervisor_First_Name, Supervisor_Last_Name, Supervisor_Phone, Supervisor_Email)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    position_number,
                    title,
                    description,
                    duration,
                    position_type,
                    region,
                    status,
                    agency_afm,
                    insertion_date,
                    supervisor_fname,
                    supervisor_lname,
                    supervisor_phone,
                    supervisor_email,
                ),
            )
        elif status in ["Π", "Α", "Υ"]:
            cursor.execute(
                """
                INSERT INTO POSITION (Position_Number, Title, Description, Duration, Type, Office_Code, Region, Status, Agency_AFM, Insertion_Date, Supervisor_First_Name, Supervisor_Last_Name, Supervisor_Phone, Supervisor_Email)
                VALUES (?,?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    position_number,
                    title,
                    description,
                    duration,
                    position_type,
                    office_code,
                    region,
                    status,
                    agency_afm,
                    insertion_date,
                    supervisor_fname,
                    supervisor_lname,
                    supervisor_phone,
                    supervisor_email,
                ),
            )
        elif status in ["Χ"]:
            office_rating_to_student = random.randint(0, 10)
            agency_rating_to_student = random.randint(0, 10)
            office_comments_to_student = (
                "Καθόλου ικανοποιημένος!"
                if office_rating_to_student < 4
                else (
                    "Μέτρια ικανοποιημένος!"
                    if office_rating_to_student < 6
                    else (
                        "Ικανοποιημένος!"
                        if office_rating_to_student < 9
                        else "Πολύ ικανοποιημένος!"
                    )
                )
            )
            agency_comments_to_student = (
                "Καθόλου ικανοποιημένος!"
                if agency_rating_to_student < 4
                else (
                    "Μέτρια ικανοποιημένος!"
                    if agency_rating_to_student < 6
                    else (
                        "Ικανοποιημένος!"
                        if agency_rating_to_student < 9
                        else "Πολύ ικανοποιημένος!"
                    )
                )
            )

            cursor.execute(
                """
                INSERT INTO POSITION (Position_Number, Title, Description, Duration, Type, Region, Status,   Agency_AFM, Insertion_Date, Office_Code, Office_Comments_To_Student, Office_Rating_To_Student, Agency_Rating_To_Student, Agency_Comments_To_Student, Supervisor_First_Name, Supervisor_Last_Name, Supervisor_Phone, Supervisor_Email)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    position_number,
                    title,
                    description,
                    duration,
                    position_type,
                    region,
                    status,
                    agency_afm,
                    insertion_date,
                    office_code,
                    office_comments_to_student,
                    office_rating_to_student,
                    agency_rating_to_student,
                    agency_comments_to_student,
                    supervisor_fname,
                    supervisor_lname,
                    supervisor_phone,
                    supervisor_email,
                ),
            )

            combination1 = (office_code, agency_afm)

            if combination1 in used_combinations1:
                continue  # Αν ο συνδυασμός υπάρχει ήδη, παράκαμψη
            else:
                used_combinations1.add(combination1)
            cursor.execute(
                """
                SELECT COUNT(*) FROM EVALUATION_AGENCY_OFFICE
                WHERE Agency_AFM = ? AND Office_Code = ?;
                """,
                (agency_afm, office_code),
            )
            if cursor.fetchone()[0] == 0:
                cursor.execute(
                    """
                    INSERT INTO EVALUATION_AGENCY_OFFICE (Agency_AFM, Office_Code, Office_Rates_Agency, Office_Comments_To_Agency, Agency_Rates_Office, Agency_Comments_To_Office)
                    VALUES (?, ?, ?, ?, ?, ?);
                    """,
                    (
                        agency_afm,
                        office_code,
                        office_rating_to_student,
                        office_comments_to_student,
                        agency_rating_to_student,
                        agency_comments_to_student,
                    ),
                )

        else:  # Status 'Ο'
            (start_date, end_date) = generate_random_dates()
            Internship_Start_Date = start_date
            Internship_End_Date = end_date

            office_rating_to_student = random.randint(0, 10)
            agency_rating_to_student = random.randint(0, 10)
            office_comments_to_student = (
                "Καθόλου ικανοποιημένος!"
                if office_rating_to_student < 4
                else (
                    "Μέτρια ικανοποιημένος!"
                    if office_rating_to_student < 6
                    else (
                        "Ικανοποιημένος!"
                        if office_rating_to_student < 9
                        else "Πολύ ικανοποιημένος!"
                    )
                )
            )
            agency_comments_to_student = (
                "Καθόλου ικανοποιημένος!"
                if agency_rating_to_student < 4
                else (
                    "Μέτρια ικανοποιημένος!"
                    if agency_rating_to_student < 6
                    else (
                        "Ικανοποιημένος!"
                        if agency_rating_to_student < 9
                        else "Πολύ ικανοποιημένος!"
                    )
                )
            )

            cursor.execute(
                """
                INSERT INTO POSITION (Position_Number, Title, Description, Duration, Type, Region, Status, Internship_Start_Date, Internship_End_Date, Agency_AFM, Insertion_Date, Office_Code, Office_Comments_To_Student, Office_Rating_To_Student, Agency_Rating_To_Student, Agency_Comments_To_Student, Supervisor_First_Name, Supervisor_Last_Name, Supervisor_Phone, Supervisor_Email)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    position_number,
                    title,
                    description,
                    duration,
                    position_type,
                    region,
                    status,
                    Internship_Start_Date,
                    Internship_End_Date,
                    agency_afm,
                    insertion_date,
                    office_code,
                    office_comments_to_student,
                    office_rating_to_student,
                    agency_rating_to_student,
                    agency_comments_to_student,
                    supervisor_fname,
                    supervisor_lname,
                    supervisor_phone,
                    supervisor_email,
                ),
            )

            combination1 = (office_code, agency_afm)

            if combination1 in used_combinations1:
                continue  # Αν ο συνδυασμός υπάρχει ήδη, παράκαμψη
            else:
                used_combinations1.add(combination1)
            cursor.execute(
                """
                SELECT COUNT(*) FROM EVALUATION_AGENCY_OFFICE
                WHERE Agency_AFM = ? AND Office_Code = ?;
                """,
                (agency_afm, office_code),
            )
            if cursor.fetchone()[0] == 0:
                cursor.execute(
                    """
                    INSERT INTO EVALUATION_AGENCY_OFFICE (Agency_AFM, Office_Code, Office_Rates_Agency, Office_Comments_To_Agency, Agency_Rates_Office, Agency_Comments_To_Office)
                    VALUES (?, ?, ?, ?, ?, ?);
                    """,
                    (
                        agency_afm,
                        office_code,
                        office_rating_to_student,
                        office_comments_to_student,
                        agency_rating_to_student,
                        agency_comments_to_student,
                    ),
                )

            # cursor.execute("INSERT INTO EVALUATION_AGENCY_OFFICE (Agency_AFM, Office_Code, Office_Rates_Agency, Office_Comments_To_Agency, Agency_Rates_Office, Agency_Comments_To_Office) VALUES (?, ?, ?, ?, ?, ?);",(agency_afm, office_code, office_rating_to_student,office_comments_to_student ,agency_rating_to_student, agency_comments_to_student))

        # Insert POSITION_ACCESSIBLE_FROM_DEPT
        counter = 0
        counter1 = 0
        for university, departments in universities_departments.items():
            max_specialties = max(1, len(specialties))
            max_deps = max(1, len(departments))
            for department in departments:
                counter = counter + 1
                a = random.randint(1, 2)
                b = random.randint(3, max_deps)
                if counter < random.randint(1, 2):
                    continue
                elif counter > random.randint(a, b):
                    counter = 0
                    break
                cursor.execute(
                    """
                    INSERT INTO POSITION_ACCESSIBLE_FROM_DEPT (Position_Number, Department_Title, University_Title, Agency_AFM)
                    VALUES (?, ?, ?, ?);
                    """,
                    (position_number, department, university, agency_afm),
                )

        # Insert SPECIALTY_POSITION
        for specialty in specialties:
            counter1 = counter1 + 1
            if counter1 < random.randint(1, 8):
                continue
            elif counter1 > random.randint(9, random.randint(10, max_specialties)):
                break
            cursor.execute(
                "INSERT INTO SPECIALTY_POSITION (Object_Name, Agency_AFM, Position_Number) VALUES (?, ?, ?);",
                (specialty, agency_afm, position_number),
            )
        # Insert FAVORITES
        if random.choice([True, False]):
            cursor.execute(
                "INSERT INTO FAVORITES (Student_ID, Position_Number, Agency_AFM) VALUES (?, ?, ?);",
                (st_ID, position_number, agency_afm),
            )
    # Select all active positions from the POSITION table
    cursor.execute(
        """
    SELECT Position_Number, Office_Code, Agency_AFM, Status
    FROM POSITION
    WHERE Status IN ('Α', 'Υ', 'Ο', 'Χ');
    """
    )
    positions = cursor.fetchall()  # Επιστρέφει λίστα από tuples

    cursor.execute(
        """
        SELECT ID
        FROM STUDENT;
        """
    )
    st_IDs = cursor.fetchall()

    # Έλεγχος αν οι λίστες είναι κενές
    if not positions or not st_IDs:
        print("No positions or students available for matching.")
    else:
        used_combinations = set()  # Χρησιμοποιημένοι συνδυασμοί πρωτευόντων κλειδιών
        used_positions = set()
        st_IDs = [
            id_tuple[0] for id_tuple in st_IDs
        ]  # Μετατροπή λίστας tuples σε απλή λίστα
        random_positions = random.sample(
            positions, len(positions)
        )  # Τυχαία επιλογή 900 θέσεων

        for position in random_positions:
            position_number, office_code, agency_afm, status = position

            for _ in range(random.randint(1, 3)):  # 1-3 matchings ανά θέση
                st_ID = random.choice(st_IDs)  # Επιλογή τυχαίου Student_ID

                # Δημιουργία συνδυασμού κλειδιών
                combination = (office_code, st_ID, position_number, agency_afm)

                if combination in used_combinations:
                    continue  # Αν ο συνδυασμός υπάρχει ήδη, παράκαμψη

                used_combinations.add(combination)  # Προσθήκη συνδυασμού στο σύνολο

                if position_number in used_positions:
                    continue
                used_positions.add(position_number)

                payment_method = random.choice(["ΕΣΠΑ", "ΙΔΡΥΜΑ", "ΟΑΕΔ", "ΦΟΡΕΑΣ"])
                agency_rating = random.randint(1, 10)
                office_rating = random.randint(1, 10)
                agency_comments = "Καλό" if agency_rating > 5 else "Μέτριο"
                office_comments = "Εξαιρετικό" if office_rating > 8 else "Αποδεκτό"

                if status in ["Α"]:

                    predicted_start_date, predicted_end_date = (
                        generate_random_pred_dates()
                    )
                    predicted_start_date = predicted_start_date.strftime("%Y-%m-%d")
                    predicted_end_date = predicted_end_date.strftime("%Y-%m-%d")
                    cursor.execute(
                        """
                        INSERT INTO MATCHING (Predicted_End_Date, Predicted_Start_Date, Payment_Method, Office_Code, Position_Number, Student_ID, Agency_AFM)
                        VALUES (?, ?, ?, ?, ?, ?, ?);
                        """,
                        (
                            predicted_end_date,
                            predicted_start_date,
                            payment_method,
                            office_code,
                            position_number,
                            st_ID,
                            agency_afm,
                        ),
                    )

                if status in ["Υ"]:
                    predicted_start_date, predicted_end_date1 = generate_random_dates()
                    predicted_start_date1, predicted_end_date = (
                        generate_random_pred_dates()
                    )
                    predicted_start_date = predicted_start_date.strftime("%Y-%m-%d")
                    predicted_end_date = predicted_end_date.strftime("%Y-%m-%d")
                    cursor.execute(
                        """
                        INSERT INTO MATCHING (Predicted_End_Date, Predicted_Start_Date, Payment_Method, Office_Code, Position_Number, Student_ID, Agency_AFM)
                        VALUES (?, ?, ?, ?, ?, ?, ?) ;
                        """,
                        (
                            predicted_end_date,
                            predicted_start_date,
                            payment_method,
                            office_code,
                            position_number,
                            st_ID,
                            agency_afm,
                        ),
                    )
                elif status in ["Ο", "Χ"]:
                    predicted_start_date, predicted_end_date = generate_random_dates()
                    predicted_start_date = predicted_start_date.strftime("%Y-%m-%d")
                    predicted_end_date = predicted_end_date.strftime("%Y-%m-%d")
                    cursor.execute(
                        """
                        INSERT INTO MATCHING (Predicted_End_Date, Predicted_Start_Date, Payment_Method, Office_Code, Position_Number, Student_ID, Agency_Rating, Agency_Comments, Office_Rating, Office_Comments, Agency_AFM)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                        """,
                        (
                            predicted_end_date,
                            predicted_start_date,
                            payment_method,
                            office_code,
                            position_number,
                            st_ID,
                            agency_rating,
                            agency_comments,
                            office_rating,
                            office_comments,
                            agency_afm,
                        ),
                    )

    connection.commit()
    print("Εγγραφή ολοκληρώθηκε επιτυχώς!")
except Error as e:
    print(f"Σφάλμα: {e}")
finally:
    connection.close()
    print("Η βάση δεδομένων έκλεισε.")
