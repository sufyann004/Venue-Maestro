# Importing essential modules
from PyQt6 import QtWidgets, uic
from PyQt6.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QMessageBox
import sys
from datetime import datetime
import pyodbc

# Main Window Class for User Type Selection
class UI(QtWidgets.QMainWindow):
    def __init__(self):
        super(UI, self).__init__()
        uic.loadUi("Type.ui", self)  # Load the Type.ui file
        self.UserTypeNext.clicked.connect(self.handle_user_type)

    def handle_user_type(self):
        if self.UserType.currentText() == "Customer":
            self.OpenCustLogin()
        else:
            self.OpenOwnerLogin()

    def OpenCustLogin(self):
        self.cust_login_window = Customer()
        self.cust_login_window.show()
        # self.close()  # Close the current window

    def OpenOwnerLogin(self):
        self.owner_login_window = Owner()
        self.owner_login_window.show()
        # self.close()  # Close the current window

# Customer Login Window
class Customer(QtWidgets.QMainWindow):
    def __init__(self):
        super(Customer, self).__init__()
        uic.loadUi("LoginPage.ui", self)
        self.CustSignUp.clicked.connect(self.OpenCustReg)
        self.Login.clicked.connect(self.CustLogin)

    def OpenCustReg(self):
        self.cust_reg_window = CustomerReg("signup")
        self.cust_reg_window.show()
        self.close()  # Close the current window

    def OpenCustDash(self,CNIC):
        self.cust_dash_window = CustDashboard(CNIC)
        self.cust_dash_window.show()
        # self.close()  # Close the current window

    def CustLogin(self):
        email = self.EmailInput.toPlainText()
        password = self.PasswordInput.toPlainText()

        if any(not field for field in [email, password]): # Checks if any field is left out
            self.show_warning_NoData()
            return

        # Database connection
        
        server = 'DESKTOP-DGTJ37N'
        database = 'DBMSS'
        connection_string = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;'
        connection = pyodbc.connect(connection_string)
        cursor = connection.cursor()

        # SQL query to validate login credentials
        login_query = """
        SELECT COUNT(*) 
        FROM CustCreds 
        WHERE CEmail = ? AND CPassword = ?
        """
        cursor.execute(login_query, (email, password))
        result = cursor.fetchone()

        if result[0] == 1:  # Login successful
            QMessageBox.information(self, "Success", "Login successful! Welcome!")
            # Retrieve the logged in Customer CNIC
            query = "SELECT CustCNIC FROM CustCreds WHERE CEmail = ?"
            cursor.execute(query, (email))
            result = cursor.fetchone()
            CNIC = result[0]
            self.OpenCustDash(CNIC)
        else:  # Invalid credentials
            QMessageBox.warning(self, "Error", "Invalid email or password. Please try again.")
    
    
        cursor.close()
        connection.close()

    def show_warning_NoData(self):
        QMessageBox.warning(self, "Error", "All fields are not filled.")



class CustomerReg(QtWidgets.QMainWindow): #Customer SignUp Window
    def __init__(self, mode="signup", cnic=None):
        super(CustomerReg, self).__init__()
        uic.loadUi("Sign Up and Acoount Update.ui", self)

        self.mode = mode
        self.CNIC = cnic

        temp = "Customer"
        self.UserType.setPlainText(temp)
        self.UserType.setDisabled(True)
        #Check if a user is updating details or signing up
        if self.mode == "signup":
            self.SignUp.setText("Sign Up")
        else:
            self.SignUp.setText("Update")
            self.load_data()

        self.SignUp.clicked.connect(self.UpdOrSignUp)

    def load_data(self):
        # Fetch customer details from the database and populate the fields
        server = 'DESKTOP-DGTJ37N'
        database = 'DBMSS'
        connection_string = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;'

        connection = pyodbc.connect(connection_string)
        cursor = connection.cursor()

        query = """SELECT CName, ContactNo, City, CEmail, CPassword FROM Customer JOIN CustCreds ON Customer.CustCNIC = CustCreds.CustCNIC WHERE Customer.CustCNIC = ?"""
        cursor.execute(query, (self.CNIC))
        result = cursor.fetchone()

        
        self.CustName.setPlainText(result[0])
        self.CustContact.setPlainText(result[1])
        self.CustCity.setPlainText(result[2])
        self.CustEmail.setPlainText(result[3])
        self.Pswrd.setPlainText(result[4])
        self.CnfrmPswrd.setPlainText(result[4])
        self.CustCNIC.setPlainText(self.CNIC)
        self.CustCNIC.setDisabled(True)
        connection.close()

    def UpdOrSignUp(self):
        name = self.CustName.toPlainText()
        cnic = self.CustCNIC.toPlainText() 
        email = self.CustEmail.toPlainText()
        contact = self.CustContact.toPlainText()
        city = self.CustCity.toPlainText()
        password = self.Pswrd.toPlainText()
        cnfrmpassword = self.CnfrmPswrd.toPlainText()

        if any(not field for field in [name, email, contact, city]):
            self.show_warning_NoData()
            return

        if password != cnfrmpassword:
            self.show_warning_pswrd()
            return

        server = 'DESKTOP-DGTJ37N'
        database = 'DBMSS'
        connection_string = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;'
        connection = pyodbc.connect(connection_string)
        cursor = connection.cursor()

        if self.mode == "signup":
            sql_query = """
            INSERT INTO Customer (CustCNIC, CName, ContactNo, City)
            VALUES (?, ?, ?, ?)
            """
            sql_query2 = """
            INSERT INTO CustCreds (CustCNIC, CEmail, CPassword)
            VALUES (?, ?, ?)
            """
            cursor.execute(sql_query, (cnic, name, contact, city))
            cursor.execute(sql_query2, (cnic, email, password))
        else:
            update_query1 = """
            UPDATE Customer
            SET CName = ?, ContactNo = ?, City = ?
            WHERE CustCNIC = ?
            """
            update_query2 = """
            UPDATE CustCreds
            SET CEmail = ?, CPassword = ?
            WHERE CustCNIC = ?
            """
            cursor.execute(update_query1, (name, contact, city, cnic))
            cursor.execute(update_query2, (email, password, cnic))

        connection.commit()
        connection.close()
        if self.mode == "update":
            QtWidgets.QMessageBox.information(  #MessageBox displaying Acc updated
                self, 
                "Success", 
                "Account updated successfully!"
            )
        else: 
            QtWidgets.QMessageBox.information( #MessageBox displaying Acc created
                self, 
                "Success", 
                "Sign-up successful!"
            )
        self.close()


    def show_warning_pswrd(self):
        QtWidgets.QMessageBox.warning(
            self, 
            "Error", 
            "Password and Confirm Password are not the same."
        )

    def show_warning_NoData(self):
        QtWidgets.QMessageBox.warning(
            self, 
            "Error", 
            "All fields are not filled."
        )


class CustDashboard(QtWidgets.QMainWindow):
    def __init__(self, CNIC):
        super(CustDashboard, self).__init__()
        uic.loadUi("Dashboard.ui", self)
        self.CNIC=CNIC
        self.book_a_hall.clicked.connect(self.OpenBookAHall)  # Connect the button to the booking function
        self.my_bookings.clicked.connect(self.CustBookings) # Connect the button to the Customer Exisitng booking function
        self.acc_settings.clicked.connect(self.UpdateAcc) #Connect to Update account functions
        self.close_d.clicked.connect(self.close)
        server = 'DESKTOP-DGTJ37N'
        database = 'DBMSS'
        connection_string = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;'
        connection = pyodbc.connect(connection_string)
        cursor = connection.cursor()
        cursor.execute("SELECT CName FROM Customer WHERE CustCNIC = ?", (self.CNIC))
        result = cursor.fetchone()
        Namee = result[0]
        self.CustName.setText(Namee)
        self.CustName.setDisabled(True)
        self.UserType.setDisabled(True)
    def OpenBookAHall(self):
        self.book_a_hall_window = BookAHall(self.CNIC)  # Create an instance of BookAHall
        self.book_a_hall_window.show()  # Show the booking window
        # self.close()  # Close the current dashboard window
    def CustBookings(self):
        self.mybookings = CustomerBookings(self.CNIC)  # Create an instance of CustomerBooking
        self.mybookings.show()  # Show the Mybookings window
        # self.close()  # Close the current dashboard window
    def UpdateAcc(self):
        self.Update_window = CustomerReg("update",self.CNIC)  # Create an instance of BookAHall
        self.Update_window.show() 
# Customer Bookings Window
class CustomerBookings(QtWidgets.QDialog):
    def __init__(self,CNIC):
        super(CustomerBookings, self).__init__()
        uic.loadUi("My Bookings.ui", self)
        self.CNIC=CNIC
        self.closee.clicked.connect(self.close) #Close WIndow
        self.delete_booking.clicked.connect(self.Delete_booking) # Connect the button to the delete booking function
        server = 'DESKTOP-DGTJ37N'
        database = 'DBMSS'
        connection_string = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;'
        connection = pyodbc.connect(connection_string)
        cursor = connection.cursor()
        query = """
        SELECT B.BookingID, H.HallName, concat(H.Area, ' ,', H.City, ' ,', H.Province) AS Address, Date, TimeSlot, 
        Price FROM Halls H JOIN Bookings B on H.Hall_ID = B.Hall_ID
        WHERE CustCNIC = ?
        """
        cursor.execute(query, (self.CNIC))
        rows = cursor.fetchall()

        self.Booking_list.setRowCount(0)
        for row in rows:
            row_position = self.Booking_list.rowCount()
            self.Booking_list.insertRow(row_position)
            for column, data in enumerate(row):
                self.Booking_list.setItem(row_position, column, QTableWidgetItem(str(data)))

    def Delete_booking(self):
        selected_row = self.Booking_list.currentRow()
        if selected_row >= 0:
            booking_id = int(self.Booking_list.item(selected_row, 0).text())
            server = 'DESKTOP-DGTJ37N'
            database = 'DBMSS'
            connection_string = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;'
            connection = pyodbc.connect(connection_string)
            cursor = connection.cursor()

            query1 = """
            DECLARE @Datee DATE;
            DECLARE @Timeslot VARCHAR(10);
            DECLARE @HallID INT;

            
            SELECT @Datee = Date, @Timeslot = Timeslot, @HallID = Hall_ID
            FROM Bookings
            WHERE BookingID = ?;

            
            UPDATE ts
            SET ts.Availability = 1
            FROM TimeSlots ts
            JOIN Hall_TimeSlots hts ON ts.Timeslot = hts.Timeslot
            WHERE hts.Hall_ID = @HallID AND hts.Date = @Datee AND hts.Timeslot = @Timeslot;
            """
            query2 = """
            DELETE FROM Bookings
            WHERE BookingID = ?;
            """
            cursor.execute(query1, (booking_id))
            cursor.execute(query2, (booking_id))
            connection.commit()
            QMessageBox.information(self, "Delete", "Booking Removed")
            
        else:
            QMessageBox.warning(self, "Error", "Please select a booking to delete.")
        
# Owner 
class Owner(QtWidgets.QMainWindow):
    def __init__(self):
        super(Owner, self).__init__()
        uic.loadUi("LoginPage.ui", self)
        self.CustSignUp.clicked.connect(self.OpenOwnerReg)
        self.Login.clicked.connect(self.OwnerLogin)
        

    def OpenOwnerReg(self):
        self.owner_reg_window = OwnerReg("signup")
        self.owner_reg_window.show()
        # self.close()  # Close the current window

    def OpenOwnerDash(self, CNIC):
        self.owner_dash_window = OwnerDashboard(CNIC)
        self.owner_dash_window.show()
        # self.close()  # Close the current window

    def OwnerLogin(self):
        email = self.EmailInput.toPlainText()
        password = self.PasswordInput.toPlainText()

        if any(not field for field in [email, password]):
            self.show_warning_NoData()
            return

        # Database connection
        
        server = 'DESKTOP-DGTJ37N'
        database = 'DBMSS'
        connection_string = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;'
        connection = pyodbc.connect(connection_string)
        cursor = connection.cursor()

        # SQL query to validate login credentials
        login_query = """
        SELECT COUNT(*) 
        FROM OwnerCreds 
        WHERE OEmail = ? AND OPassword = ?
        """
        cursor.execute(login_query, (email, password))
        result = cursor.fetchone()

        if result[0] == 1:  # Login successful
            QMessageBox.information(self, "Success", "Login successful! Welcome!")
            # Retrieve the logged in Owner CNIC
            query = "SELECT OwnerCNIC FROM OwnerCreds WHERE OEmail = ?"
            cursor.execute(query, (email))
            result = cursor.fetchone()
            CNIC = result[0]
            self.OpenOwnerDash(CNIC)
        else:  # Invalid credentials
            QMessageBox.warning(self, "Error", "Invalid email or password. Please try again.")
    
        cursor.close()
        connection.close()

    def show_warning_NoData(self):
        QMessageBox.warning(self, "Error", "All fields are not filled.")


class OwnerReg(QtWidgets.QMainWindow):
    def __init__(self, mode="signup", cnic=None): #CNIC passed for updating. If None and mode = signup, it's a new owner
        super(OwnerReg, self).__init__()
        uic.loadUi("Sign Up and Acoount Update.ui", self)

        self.mode = mode
        self.CNIC = cnic

        temp = "Owner"
        self.UserType.setPlainText(temp)
        self.UserType.setDisabled(True)

        if self.mode == "signup":
            self.SignUp.setText("Sign Up")
        else:
            self.SignUp.setText("Update")
            self.load_data()

        self.SignUp.clicked.connect(self.UpdOrSignUp)

    def load_data(self):
        # Fetch owner details from the database and populate the fields
        server = 'DESKTOP-DGTJ37N'
        database = 'DBMSS'
        connection_string = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;'

        connection = pyodbc.connect(connection_string)
        cursor = connection.cursor()

        query = """SELECT OwnerName, PhoneNumber, City, OEmail, OPassword 
                   FROM HallOwner 
                   JOIN OwnerCreds ON HallOwner.OwnerCNIC = OwnerCreds.OwnerCNIC 
                   WHERE HallOwner.OwnerCNIC = ?"""
        cursor.execute(query, (self.CNIC,))
        result = cursor.fetchone()

        self.CustName.setPlainText(result[0]) #Populating UI fields
        self.CustContact.setPlainText(result[1])
        self.CustCity.setPlainText(result[2])
        self.CustEmail.setPlainText(result[3])
        self.Pswrd.setPlainText(result[4])
        self.CnfrmPswrd.setPlainText(result[4])
        self.CustCNIC.setPlainText(self.CNIC)
        self.CustCNIC.setDisabled(True)
        connection.close()

    def UpdOrSignUp(self):
        name = self.CustName.toPlainText() #Taking input
        cnic = self.CustCNIC.toPlainText()
        email = self.CustEmail.toPlainText()
        contact = self.CustContact.toPlainText()
        city = self.CustCity.toPlainText()
        password = self.Pswrd.toPlainText()
        cnfrmpassword = self.CnfrmPswrd.toPlainText()

        if any(not field for field in [name, email, contact, city]):
            self.show_warning_NoData()
            return

        if password != cnfrmpassword:
            self.show_warning_pswrd()
            return

        server = 'DESKTOP-DGTJ37N'
        database = 'DBMSS'
        connection_string = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;'
        connection = pyodbc.connect(connection_string)
        cursor = connection.cursor()

        if self.mode == "signup":
            sql_query = """
            INSERT INTO HallOwner (OwnerCNIC, OwnerName, PhoneNumber, City)
            VALUES (?, ?, ?, ?)
            """
            sql_query2 = """
            INSERT INTO OwnerCreds (OwnerCNIC, OEmail, OPassword)
            VALUES (?, ?, ?)
            """
            cursor.execute(sql_query, (cnic, name, contact, city))
            cursor.execute(sql_query2, (cnic, email, password))
        else:
            update_query1 = """
            UPDATE HallOwner
            SET OwnerName = ?, PhoneNumber = ?, City = ?
            WHERE OwnerCNIC = ?
            """
            update_query2 = """
            UPDATE OwnerCreds
            SET OEmail = ?, OPassword = ?
            WHERE OwnerCNIC = ?
            """
            cursor.execute(update_query1, (name, contact, city, cnic))
            cursor.execute(update_query2, (email, password, cnic))

        connection.commit()
        connection.close()

        if self.mode == "update":
            QtWidgets.QMessageBox.information(
                self,
                "Success",
                "Account updated successfully!"
            )
        else:
            QtWidgets.QMessageBox.information(
                self,
                "Success",
                "Sign-up successful!"
            )
        self.close()

    def show_warning_pswrd(self):
        # Display the warning box
        QtWidgets.QMessageBox.warning(
            self,
            "Error",
            "Password and Confirm Password are not the same."
        )

    def show_warning_NoData(self):
        # Display the warning box
        QtWidgets.QMessageBox.warning(
            self,
            "Error",
            "All fields are not filled."
        )

class OwnerDashboard(QtWidgets.QMainWindow):
    def __init__(self, CNIC):
        self.CNIC=CNIC # Store CNIC for use within this class
        super(OwnerDashboard, self).__init__()
        uic.loadUi("dashboard_owner.ui", self)
        self.my_halls.clicked.connect(self.OpenHall_list)
        self.acc_settings.clicked.connect(self.UpdAcc)
        self.add_a_hall.clicked.connect(self.AddHall)
        self.manage_hall_bookings.clicked.connect(self.OpenManageBookings)
        self.close_o.clicked.connect(self.close)
        server = 'DESKTOP-DGTJ37N'
        database = 'DBMSS'
        connection_string = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;'
        connection = pyodbc.connect(connection_string)
        cursor = connection.cursor()
        cursor.execute("SELECT OwnerName FROM HallOwner WHERE OwnerCNIC = ?", (self.CNIC))
        result = cursor.fetchone()
        Namee = result[0]
        self.OName.setPlainText(Namee)
        self.OName.setDisabled(True)
        self.UserType.setDisabled(True)

    def UpdAcc(self):
        self.UpdateAcc = OwnerReg("update",self.CNIC)  #PAssing CNICs for further use
        self.UpdateAcc.show()

    def OpenHall_list(self):
        self.my_halls_window = Hall_list(self.CNIC)
        self.my_halls_window.show()
        # self.close()  # Close the current window
    
    def AddHall(self):
        self.add_halls_window = Add_Hall(self.CNIC)
        self.add_halls_window.show()
        # self.close()  # Close the current window

    def OpenManageBookings(self):
        self.view_bookings_window = ViewBookings(self.CNIC)
        self.view_bookings_window.show()
        # self.close()  # Close the current window

class Hall_list(QtWidgets.QMainWindow):
    def __init__(self, CNIC):
        super(Hall_list, self).__init__()
        uic.loadUi("My Halls.ui", self)
        self.CNIC = CNIC
        self.Hall_list.setColumnCount(6)  # Set the number of columns
        self.Hall_list.setHorizontalHeaderLabels(["Hall ID", "Hall Name", "Province", "City", "Price", "Timeslot"]) #Setting Titles for GUI
        self.load_halls()
        self.edit_hall.clicked.connect(self.OpenEditHall)
        self.edit_hall_2.clicked.connect(self.delete_hall)
        self.close_my_hall.clicked.connect(self.close)

    def load_halls(self):
        # Load the halls for the logged-in owner
        server = 'DESKTOP-DGTJ37N'
        database = 'DBMSS'
        connection_string = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;'
        connection = pyodbc.connect(connection_string)
        cursor = connection.cursor()

        OwnerCNIC = self.CNIC  # Replace with actual logged-in owner's CNIC
        query = """
        SELECT distinct h.Hall_ID, h.HallName, h.Province, h.City, t.Price, ht.Timeslot
        FROM Halls h 
        JOIN Hall_Timeslots ht ON h.Hall_ID = ht.Hall_ID 
        JOIN TimeSlots t ON ht.Timeslot = t.Timeslot 
        WHERE h.OwnerCNIC = ?
        """
        cursor.execute(query, (OwnerCNIC,))
        rows = cursor.fetchall()

        self.Hall_list.setRowCount(0)
        for row in rows:
            row_position = self.Hall_list.rowCount()
            self.Hall_list.insertRow(row_position)
            for column, data in enumerate(row):
                self.Hall_list.setItem(row_position, column, QTableWidgetItem(str(data)))

    def OpenEditHall(self):
        selected_row = self.Hall_list.currentRow()
        if selected_row >= 0:
            hall_id = self.Hall_list.item(selected_row, 0).text()
            self.edit_hall_window = EditHall(hall_id)
            self.edit_hall_window.show()
            # self.close()  # Close the current window
        else:
            QMessageBox.warning(self, "Error", "Please select a hall to edit.")
    def delete_hall(self):
        
        # Get the selected row
        selected_row = self.Hall_list.currentRow()
        if selected_row < 0:
            # Create a QMessageBox instance to show the warning
            QMessageBox.warning(self, "Warning", "Please select a hall to delete.")
            return

        # Get the Hall ID from the selected row
        hall_id_item = self.Hall_list.item(selected_row, 0)  # Assuming Hall_ID is in the first column
        if hall_id_item is None:
            QMessageBox.warning(self, "Warning", "Could not retrieve Hall ID.")
            return
        
        hall_id = hall_id_item.text()

        # Connect to the database
        server = 'DESKTOP-DGTJ37N'
        database = 'DBMSS'
        connection_string = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;'
        connection = pyodbc.connect(connection_string)
        cursor = connection.cursor()

        # Execute the delete queries
        delete_time_slots_query = """DELETE FROM Hall_TimeSlots
                                        WHERE Timeslot IN (
                                        SELECT ht.Timeslot
                                        FROM Hall_TimeSlots ht
                                        JOIN TimeSlots t ON ht.Timeslot = t.Timeslot
                                        WHERE ht.Hall_ID = ?) and Hall_ID = ?"""
        delete_from_bookings ="DELETE FROM Bookings WHERE Hall_ID = ?"
        delete_hall_query = "DELETE FROM Halls WHERE Hall_ID = ?"

        # Deleting from Hall_TimeSlots
        cursor.execute(delete_time_slots_query, (hall_id, hall_id))
        cursor.execute(delete_from_bookings, (hall_id))
        # Deleting from Halls
        cursor.execute(delete_hall_query, (hall_id))

        # Commit the changes to databse
        connection.commit()
        QMessageBox.information(self, "Success", "Hall deleted successfully.")
        self.load_halls()
        cursor.close()
        connection.close()
        # Refresh the hall list to reflect changes
        self.load_halls()

class Add_Hall(QtWidgets.QMainWindow):
    def __init__(self, cnic, parent=None):
        super(Add_Hall, self).__init__(parent)
        uic.loadUi("AddEditHall.ui", self)  # Load the UI for adding a hall
        
        self.Owner_CNIC = cnic # Store the owner's CNIC
        self.AddUpdate.clicked.connect(self.add_hall)

    def add_hall(self):
        hall_name = self.HallName.toPlainText()
        area = self.Area.toPlainText()
        city = self.City.toPlainText()
        province = self.Province.toPlainText()
        day_price = self.DayPrice.toPlainText()
        night_price = self.NightPrice.toPlainText()

        if any(not field for field in [hall_name, area, city, province, day_price, night_price]):
            self.show_warning("All fields must be filled!")
            return

        server = 'DESKTOP-DGTJ37N'
        database = 'DBMSS'
        connection_string = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;'
        connection = pyodbc.connect(connection_string)
        cursor = connection.cursor()

        
        # Step 1: Insert into Halls
        insert_hall_query = """
        INSERT INTO Halls (OwnerCNIC, HallName, Area, City, Province)
        VALUES (?, ?, ?, ?, ?);
        """
        cursor.execute(insert_hall_query, (self.Owner_CNIC, hall_name, area, city, province))
        connection.commit()  # Commit to ensure the Hall_ID is available

        cursor.execute("SELECT Top 1 Hall_ID from Halls where OwnerCNIC=? Order by Hall_ID desc", (self.Owner_CNIC)) #Fetch newly added Hall ID. Couldn't fetch it from scope identity.
        result=cursor.fetchone()
        hall_id=result[0]
        if not hall_id: #If no row is returned, it means the insert query failed.
            raise Exception("Failed to retrieve Hall_ID after insertion.")

        # The below query uses the SQL MERGE statement to upsert (update or insert) records into the TimeSlots table:
        # - If a record with the same Hall_ID and TimeSlot exists, update it.
        # - If a record with the same Hall_ID but different TimeSlot does not exist, insert
        #   a new record with the given TimeSlot.
        upsert_timeslot_query = """
        MERGE INTO TimeSlots AS target 
        USING (VALUES (?, ?), (?, ?)) AS source(Timeslot, Price)
        ON target.Timeslot = source.Timeslot
        WHEN MATCHED THEN 
            UPDATE SET Price = source.Price, Availability = 1
        WHEN NOT MATCHED THEN
            INSERT (Timeslot, Price, Availability)
            VALUES (source.Timeslot, source.Price, 1);
        """
        cursor.execute(upsert_timeslot_query, ('Day', day_price, 'Night', night_price))

        # Step 3: Insert into Hall_TimeSlots
        insert_hall_timeslot_query = """
        INSERT INTO Hall_TimeSlots (Hall_ID, Timeslot, Date)
        VALUES (?, ?, ?), (?, ?, ?);
        """
        current_date = '2024-12-03'  # Replace with dynamic date if required
        cursor.execute(insert_hall_timeslot_query, (hall_id, 'Day', current_date, hall_id, 'Night', current_date))

        connection.commit()
        self.show_info("Hall added successfully!")
        connection.close()



    def show_info(self, message):
        QtWidgets.QMessageBox.information(self, "Info", message)

    def show_warning(self, message):
        QtWidgets.QMessageBox.warning(self, "Warning", message)

class EditHall(QtWidgets.QMainWindow):
    def __init__(self, hall_id):
        super(EditHall, self).__init__()
        uic.loadUi("AddEditHall.ui", self)
        self.hall_id = hall_id
        self.load_hall_details()
        self.AddUpdate.clicked.connect(self.update_hall)
        

    def load_hall_details(self):
        server  = 'DESKTOP-DGTJ37N'
        database = 'DBMSS'
        connection_string = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;'
        connection = pyodbc.connect(connection_string)
        cursor = connection.cursor()

        query = "SELECT HallName, Area, City, Province FROM Halls WHERE Hall_ID = ?"
        cursor.execute(query, (self.hall_id,))
        hall_details = cursor.fetchone()

        if hall_details:
            self.HallName.setPlainText(hall_details[0])
            self.Area.setPlainText(hall_details[1])
            self.City.setPlainText(hall_details[2])
            self.Province.setPlainText(hall_details[3])

    def update_hall(self):
        hall_name = self.HallName.toPlainText()
        area = self.Area.toPlainText()
        city = self.City.toPlainText()
        province = self.Province.toPlainText()
        day_price = self.DayPrice.toPlainText()
        night_price = self.NightPrice.toPlainText()

        server = 'DESKTOP-DGTJ37N'
        database = 'DBMSS'
        connection_string = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;'
        connection = pyodbc.connect(connection_string)
        cursor = connection.cursor()

        update_hall_query = """
        UPDATE Halls 
        SET HallName = ?, Area = ?, City = ?, Province = ?
        WHERE Hall_ID = ?
        """
        cursor.execute(update_hall_query, (hall_name, area, city, province, self.hall_id))

        update_day_price_query = """
        UPDATE TimeSlots 
        SET Price = ? 
        WHERE Timeslot = 'Day' AND Timeslot IN (SELECT Timeslot FROM Hall_Timeslots WHERE Hall_ID = ?)
        """
        cursor.execute(update_day_price_query, (day_price, self.hall_id))

        update_night_price_query = """
        UPDATE TimeSlots 
        SET Price = ? 
        WHERE Timeslot = 'Night' AND Timeslot IN (SELECT Timeslot FROM Hall_Timeslots WHERE Hall_ID = ?)
        """
        cursor.execute(update_night_price_query, (night_price, self.hall_id))

        connection.commit()
        QMessageBox.information(self, "Success", "Hall details updated successfully!")
        # self.close()

class ViewBookings(QtWidgets.QDialog):
    def __init__(self, CNIC):
        super(ViewBookings, self).__init__()
        self.CNIC = CNIC
        uic.loadUi("ViewBookings.ui", self)
        self.bookings_table.setColumnCount(6)  # Set the number of columns
        self.bookings_table.setHorizontalHeaderLabels(["Hall ID", "Booking ID", "Customer Name", "Date", "Timeslot", "Price"])
        self.load_bookings()
        self.edit_booking.clicked.connect(self.OpenEditBooking)
        self.deletebooking.clicked.connect(self.DeleteBooking)
        self.close_view_bookings.clicked.connect(self.close)
        self.view_booking.clicked.connect(self.view_bookings)
    def view_bookings(self):
        
        selected_row = self.bookings_table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Warning", "Please select a booking to view.")
            return

        # Get the Booking ID from the selected row
        booking_id = self.bookings_table.item(selected_row, 1).text()  # Assuming Booking ID is in the first column
        if booking_id is None:
            QMessageBox.warning(self, "Warning", "Could not retrieve Booking ID.")
            return
        self.booking_details_window = BookingDetails(booking_id, self.CNIC, mode="view")
        self.booking_details_window.show()
    def load_bookings(self):
        server = 'DESKTOP-DGTJ37N'
        database = 'DBMSS'
        connection_string = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;'
        connection = pyodbc.connect(connection_string)
        cursor = connection.cursor()

        OwnerCNIC = self.CNIC  # Replace with actual logged-in owner's CNIC
        query = """
        SELECT b.Hall_ID, b.BookingID, c.CName, b.Date, b.Timeslot, b.Price
        FROM Bookings b 
        JOIN Customer c ON b.CustCNIC = c.CustCNIC 
        WHERE b.OwnerCNIC = ?
        """
        cursor.execute(query, (OwnerCNIC))
        rows = cursor.fetchall()

        self.bookings_table.setRowCount(0)
        for row in rows:
            row_position = self.bookings_table.rowCount()
            self.bookings_table.insertRow(row_position)
            for column, data in enumerate(row):
                self.bookings_table.setItem(row_position, column, QTableWidgetItem(str(data)))

    def OpenEditBooking(self):
        selected_row = self.bookings_table.currentRow()
        if selected_row >= 0:
            booking_id = self.bookings_table.item(selected_row, 1).text()
            self.edit_booking_window = BookingDetails(booking_id, self.CNIC, mode="edit")
            self.edit_booking_window.show()
            # self.close()  # Close the current window
        else:
            QMessageBox.warning(self, "Error", "Please select a booking to edit.")

    def DeleteBooking(self):
        selected_row = self.bookings_table.currentRow()
        if selected_row >= 0:
            booking_id = int(self.bookings_table.item(selected_row, 1).text())
            server = 'DESKTOP-DGTJ37N'
            database = 'DBMSS'
            connection_string = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;'
            connection = pyodbc.connect(connection_string)
            cursor = connection.cursor()

            query1 = """
            DECLARE @Datee DATE;
            DECLARE @Timeslott VARCHAR(10);
            DECLARE @HallID INT;

            
            SELECT @Datee = Date, @Timeslott = Timeslot, @HallID = Hall_ID
            FROM Bookings
            WHERE BookingID = ?;

            
            UPDATE ts
            SET ts.Availability = 1
            FROM TimeSlots ts
            JOIN Hall_TimeSlots hts ON ts.Timeslot = hts.Timeslot
            WHERE hts.Hall_ID = @HallID AND hts.Date = @Datee AND hts.Timeslot = @Timeslott;
            """
            query2 = """
            DELETE FROM Bookings
            WHERE BookingID = ?;
            """
            cursor.execute(query1, (booking_id))
            cursor.execute(query2, (booking_id))
            connection.commit()
            QMessageBox.information(self, "Delete", "Booking Removed")
            self.load_bookings()
        else:
            QMessageBox.warning(self, "Error", "Please select a booking to delete.")

class BookingDetails(QtWidgets.QDialog):
    def __init__(self, booking_id, CNIC, mode="view"):
        super(BookingDetails, self).__init__()
        uic.loadUi("BookingDetails.ui", self)
        self.booking_id = booking_id
        self.CNIC = CNIC
        self.mode = mode  # Default to 'view' mode
        self.load_booking_details()
        self.updatebutton.clicked.connect(self.update_booking)

        # Setup mode based on the parameter passed
        if self.mode == "view":
            self.set_view_mode()  # Disable editing
        elif self.mode == "edit":
            self.set_edit_mode()  # Enable editing and show update button

    def load_booking_details(self):
        server = 'DESKTOP-DGTJ37N'
        database = 'DBMSS'
        connection_string = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;'
        connection = pyodbc.connect(connection_string)
        cursor = connection.cursor()

        query = """
        SELECT c.CName, c.ContactNo, b.CustCNIC, h.HallName, b.Price, b.Timeslot
        FROM Bookings b 
        JOIN Customer c ON b.CustCNIC = c.CustCNIC 
        JOIN Halls h ON h.OwnerCNIC = b.OwnerCNIC 
        WHERE BookingID = ?
        """
        cursor.execute(query, (self.booking_id,))
        booking_details = cursor.fetchone()

        if booking_details:
            self.CustomerName.setText(booking_details[0])
            self.ContactNo.setText(booking_details[1])
            self.cnic.setText(booking_details[2])
            self.HallName.setText(booking_details[3])
            self.Price.setText(str(booking_details[4]))

            # Set the radio button based on the timeslot
            if booking_details[5] == "Day":
                self.Day.setChecked(True)
            else:
                self.Night.setChecked(True)

    def set_view_mode(self):
        # Disable all fields and buttons related to updating
        self.CustomerName.setDisabled(True)
        self.ContactNo.setDisabled(True)
        self.cnic.setDisabled(True)
        self.HallName.setDisabled(True)
        self.Price.setDisabled(True)
        self.Day.setDisabled(True)
        self.Night.setDisabled(True)
        self.updatebutton.setDisabled(True)  # Disable the update button

    def set_edit_mode(self):
        # Enable fields for editing and enable the update button
        self.CustomerName.setDisabled(False)
        self.ContactNo.setDisabled(False)
        self.cnic.setDisabled(False)
        self.HallName.setDisabled(False)
        self.Price.setDisabled(False)
        self.Day.setDisabled(False)
        self.Night.setDisabled(False)
        self.updatebutton.setDisabled(False)  

    def update_booking(self):
        # Your code to update booking details goes here
        contact_no = self.ContactNo.text()
        price = self.Price.text()
        timeslot = "Day" if self.Day.isChecked() else "Night"

        server = 'DESKTOP-DGTJ37N'
        database = 'DBMSS'
        connection_string = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;'
        connection = pyodbc.connect(connection_string)
        cursor = connection.cursor()

        update_booking_query = """
        UPDATE Bookings
        SET Price = ?, Timeslot = ?
        WHERE BookingID = ?
        """
        cursor.execute(update_booking_query, (price, timeslot, self.booking_id))
        connection.commit()

        QMessageBox.information(self, "Success", "Booking details updated successfully!")
        # self.close()  # Close the window after successful update


class BookAHall(QtWidgets.QDialog):  # Change QMainWindow to QDialog
    def __init__(self, CNIC):
        super(BookAHall, self).__init__()
        uic.loadUi("Book a Hall.ui", self)
        self.CNIC=CNIC
        self.province_select.currentIndexChanged.connect(self.populate_Hall_list)
        self.city_select.currentIndexChanged.connect(self.populate_Hall_list)
        self.area_select.currentIndexChanged.connect(self.populate_Hall_list)
        self.book.clicked.connect(self.OpenBookingCalendar)
        self.close_book.clicked.connect(self.close)

    def populate_Hall_list(self):
        server = 'DESKTOP-DGTJ37N'
        database = 'DBMSS'
        connection_string = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;'
        
        try:
            # Establish the database connection
            connection = pyodbc.connect(connection_string)
            cursor = connection.cursor()
            
            # Get the selected values from the dropdowns
            province = self.province_select.currentText() if self.province_select.currentText() != "Select Province" else ""
            city = self.city_select.currentText() if self.city_select.currentText() != "Select City" else ""
            area = self.area_select.currentText() if self.area_select.currentText() != "Select Area" else ""

            # SQL query with parameter markers for filtering based on selections
            query = """
            SELECT * 
            FROM Halls
            WHERE 
                (Province = ? OR ? IS NULL OR ? = '') 
                AND (City = ? OR ? IS NULL OR ? = '') 
                AND (Area = ? OR ? IS NULL OR ? = '')
            """

            # Execute the query with the parameters
            cursor.execute(query, (province, province,province, city, city,city, area, area,area))
            rows = cursor.fetchall()

            # Clear the Hall_list before populating new data
            self.hall_list.setRowCount(0)

            # Populate the Hall_list with the fetched data
            for row in rows:
                row_position = self.hall_list.rowCount()
                self.hall_list.insertRow(row_position)
                for column, data in enumerate(row):
                    self.hall_list.setItem(row_position, column, QTableWidgetItem(str(data)))

        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            # Cleanup: Close cursor and connection
            cursor.close()
            connection.close()
    def OpenBookingCalendar(self):
        selected_row = self.hall_list.currentRow()
        if selected_row >= 0:
            hall_id = self.hall_list.item(selected_row, 0).text()
            hall_id=int(hall_id)
            self.booking_calendar_window = BookingCalendar(hall_id, self.CNIC)
            self.booking_calendar_window.show()  # Use exec() for dialogs
            # self.close()  # Close the current window
        else:
            QMessageBox.warning(self, "Error", "Please select a hall to proceed.")

class BookingCalendar(QtWidgets.QDialog):
    def __init__(self, hall_id, CNIC):
        super(BookingCalendar, self).__init__()
        uic.loadUi("Booking Calendar.ui", self)
        self.hall_id = hall_id
        self.selected_date = None
        self.CNIC=CNIC
        self.booking_calendar.clicked.connect(self.update_selected_date)
        self.proceed.clicked.connect(self.open_book_hogaya)
        self.close_c.clicked.connect(self.close)
    def update_selected_date(self):
        self.selected_date = self.booking_calendar.selectedDate().toString("yyyy-MM-dd")

    def open_book_hogaya(self):

        if not self.selected_date:
            QMessageBox.warning(self, "Error", "Please select a date before proceeding.")
            return

    
        # Format the selected date
        formatted_date = datetime.strptime(self.selected_date, "%Y-%m-%d").date()

        # Database connection
        server = 'DESKTOP-DGTJ37N'
        database = 'DBMSS'
        connection_string = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;'
        connection = pyodbc.connect(connection_string)
        cursor = connection.cursor()

        # Check if rows exist for this Hall_ID and Date
        check_query = """
        SELECT COUNT(*) 
        FROM Hall_TimeSlots 
        WHERE Hall_ID = ? AND Date = ?
        """
        cursor.execute(check_query, (self.hall_id, formatted_date))
        rows_exist = cursor.fetchone()[0]

        # If no rows exist, insert default availability
        if rows_exist == 0:
            insert_query = """
            INSERT INTO Hall_TimeSlots (Hall_ID, Timeslot, Date)
            VALUES (?, 'Day', ?)
            """
            insert_query2 = """
            INSERT INTO Hall_TimeSlots (Hall_ID, Timeslot, Date)
            VALUES(?, 'Night', ?)
            """
            cursor.execute(insert_query, (self.hall_id, formatted_date))
            cursor.execute(insert_query2, (self.hall_id, formatted_date))
            connection.commit()

        # Check if there is availability
        availability_query = """
        SELECT COUNT(*) 
        FROM Hall_TimeSlots ht
        WHERE ht.Hall_ID = ? 
        AND ht.Date = ? 
        """
        cursor.execute(availability_query, (self.hall_id, formatted_date))
        availability_count = cursor.fetchone()[0]

        if availability_count > 0:
            # Proceed to book if slots are available
            self.book_hogaya_window = BookHogaya(self.hall_id, formatted_date, self.CNIC)
            self.book_hogaya_window.show()
            # self.close()
        else:
            QMessageBox.warning(self, "Error", "No available time slots for the selected date.")
            cursor.close()
            connection.close()

class BookHogaya(QtWidgets.QDialog):  # Ensure this matches the UI file's top-level widget
    def __init__(self, hall_id, selected_date, CNIC):
        super(BookHogaya, self).__init__()
        uic.loadUi("Book hogaya.ui", self)  # Ensure the filename matches exactly
        self.CNIC=CNIC
        self.hall_id = hall_id
        self.selected_date = selected_date
        self.confirm_booking.clicked.connect(self.Confirm_booking)
        self.day_select.toggled.connect(self.check_privacy_policy)
        self.night_select.toggled.connect(self.check_privacy_policy)

    def check_privacy_policy(self):
        self.confirm_booking.setEnabled(self.privacy_policy_check.isChecked())

    def Confirm_booking(self):
        if not self.privacy_policy_check.isChecked():
            QMessageBox.warning(self, "Error", "You must accept the privacy policy to confirm the booking.")
            return

        timeslot = 'Day' if self.day_select.isChecked() else 'Night'
        price = self.get_price(timeslot, self.hall_id, self.selected_date)

        try:
            server = 'DESKTOP-DGTJ37N'
            database = 'DBMSS'
            connection_string = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;'
            connection = pyodbc.connect(connection_string)
            cursor = connection.cursor()
            cursor.execute("SELECT COUNT(*) FROM Bookings WHERE Hall_ID=? and Date = ? and TimeSlot=?", (self.hall_id, self.selected_date, timeslot))
            result = cursor.fetchone()[0]
            if result > 0:
                QMessageBox.warning(self, "Error", "Time slot already booked for the selected date")
                cursor.close
                return
                
            cursor.execute("SELECT OwnerCNIC FROM Halls WHERE Hall_ID = ?", (self.hall_id))
            result = cursor.fetchone()
            OCNIC = result[0]
            # Insert booking
            insert_query = """
            INSERT INTO Bookings (Date, Timeslot, Price, Hall_ID, CustCNIC, OwnerCNIC)
            VALUES (?, ?, ?, ?, ?, ?)
            """
            cursor.execute(insert_query, (self.selected_date, timeslot, price, self.hall_id, self.CNIC, OCNIC))  # Replace with actual CNICs
            connection.commit()

            # Update availability
            update_query = """
            UPDATE TimeSlots
            SET Availability = 0
            WHERE Timeslot = ?
            AND Timeslot IN (
                SELECT Timeslot
                FROM Hall_TimeSlots
                WHERE Hall_ID = ?
                AND Date = ?
            )
            AND ? IN (
                SELECT Date
                FROM Bookings
                WHERE Hall_ID = ?
                AND Timeslot = ?
            )
            """
            cursor.execute(update_query, (timeslot, self.hall_id, self.selected_date, self.selected_date, self.hall_id, timeslot))
            connection.commit()

            QMessageBox.information(self, "Success", "Booking completed successfully!")
            # self.close()
        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"An error occurred: {str(e)}")
        finally:
            cursor.close()
            connection.close()

    import pyodbc

    def get_price(self, timeslot, HallId, Date):
        server = 'DESKTOP-DGTJ37N'
        database = 'DBMSS'
        connection_string = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;'
        connection = pyodbc.connect(connection_string)
        cursor = connection.cursor()

        query = """
        SELECT T.Price
        FROM Hall_TimeSlots HT
        JOIN TimeSlots T ON HT.Timeslot = T.Timeslot
        WHERE HT.Hall_ID = ? AND HT.Timeslot = ? AND HT.Date = ?
        """
        
        # Execute the query with the provided parameters
        cursor.execute(query, (HallId, timeslot, Date))

        # Fetch the result
        result = cursor.fetchone()

        if result:
            # Return the price if the result is found
            return result[0]
        else:
            # Return None if no matching record is found
            return None
       


def main():
    app = QApplication(sys.argv)
    window = UI()  # Start with the User Type Selection window
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()