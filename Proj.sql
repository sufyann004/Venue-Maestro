-- Create Tables

-- Customer Table
CREATE TABLE Customer (
    CustCNIC NVARCHAR(15) PRIMARY KEY,
    CName NVARCHAR(MAX) NOT NULL,
    ContactNo NVARCHAR(MAX) NOT NULL,
    City NVARCHAR(MAX) NOT NULL
);

-- Hall Owner Table
CREATE TABLE HallOwner (
    OwnerCNIC NVARCHAR(15) PRIMARY KEY,
    OwnerName NVARCHAR(MAX) NOT NULL,
    PhoneNumber NVARCHAR(MAX) NOT NULL,
    City NVARCHAR(MAX) NOT NULL
);

-- Customer Credentials Table
CREATE TABLE CustCreds (
    CustCNIC NVARCHAR(15) PRIMARY KEY,
    CEmail NVARCHAR(MAX) NOT NULL,
    CPassword NVARCHAR(MAX) NOT NULL,
    FOREIGN KEY (CustCNIC) REFERENCES Customer(CustCNIC)
);

-- Owner Credentials Table
CREATE TABLE OwnerCreds (
    OwnerCNIC NVARCHAR(15) PRIMARY KEY,
    OEmail NVARCHAR(MAX) NOT NULL,
    OPassword NVARCHAR(MAX) NOT NULL,
    FOREIGN KEY (OwnerCNIC) REFERENCES HallOwner(OwnerCNIC)
);

-- Halls Table
CREATE TABLE Halls (
    Hall_ID INT IDENTITY(1,1) PRIMARY KEY,
    HallName NVARCHAR(MAX) NOT NULL,
    Area NVARCHAR(MAX) NOT NULL,
    City NVARCHAR(MAX) NOT NULL,
    Province NVARCHAR(MAX) NOT NULL,
    OwnerCNIC NVARCHAR(15) NOT NULL,
    FOREIGN KEY (OwnerCNIC) REFERENCES HallOwner(OwnerCNIC)
);

-- Time Slots Table
CREATE TABLE TimeSlots (
    Timeslot NVARCHAR(255) PRIMARY KEY,
    Price INT NOT NULL,
    Availability BIT NOT NULL
);

-- Hall Time Slots Table
CREATE TABLE Hall_TimeSlots (
    Hall_ID INT NOT NULL,
    Timeslot NVARCHAR(255) NOT NULL,
    Date DATE NOT NULL DEFAULT '1900-01-01',
    PRIMARY KEY (Hall_ID, Timeslot, Date),
    FOREIGN KEY (Hall_ID) REFERENCES Halls(Hall_ID),
    FOREIGN KEY (Timeslot) REFERENCES TimeSlots(Timeslot)
);

-- Bookings Table
CREATE TABLE Bookings (
    BookingID INT IDENTITY(1,1) PRIMARY KEY,
    Date DATE NOT NULL,
    TimeSlot NVARCHAR(255) NOT NULL,
    Price INT NOT NULL,
    Hall_ID INT NOT NULL,
    CustCNIC NVARCHAR(15) NOT NULL,
    OwnerCNIC NVARCHAR(15) NOT NULL,
    FOREIGN KEY (CustCNIC) REFERENCES Customer(CustCNIC),
    FOREIGN KEY (Hall_ID) REFERENCES Halls(Hall_ID),
    FOREIGN KEY (OwnerCNIC) REFERENCES HallOwner(OwnerCNIC),
    FOREIGN KEY (TimeSlot) REFERENCES TimeSlots(Timeslot)
);

-- Customer Owner Table
CREATE TABLE Cust_Owner (
    CustCNIC NVARCHAR(15) NOT NULL,
    OwnerCNIC NVARCHAR(15) NOT NULL,
    PRIMARY KEY (CustCNIC, OwnerCNIC),
    FOREIGN KEY (CustCNIC) REFERENCES Customer(CustCNIC),
    FOREIGN KEY (OwnerCNIC) REFERENCES HallOwner(OwnerCNIC)
);

