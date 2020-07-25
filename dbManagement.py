#C.R.U.D.E = Create | Retrieve | Update | Delete | Enhanced
import pyodbc

ConnectionString = (r'CONNECTION-STRING-GOES-HERE')
#C = Create
SQLCreateStatement = (r"CREATE TABLE Person.PyTestingscript (pyID INT NOT NULL IDENTITY(1,1), FirstName varchar(50) NOT NULL, LastName varchar(50) NOT NULL, DateOfBirth DATE NULL, PRIMARY KEY (pyID))")
#R = Retrieve
SQLStatementAll = (r"SELECT * FROM Person.PyTestingscript")
SQLStatementSpecific = (r"SELECT FirstName as 'First Name', LastName as 'LastName' FROM Person.PyTest")
#U = Update
SQLStatementUpdate = (r"UPDATE Person.PyTest SET FirstName = 'Joe', LastName = 'Perry' WHERE pyID = ?")
SQLStatementInsert1 = (r"INSERT INTO Person.PyTestingscript (FirstName, LastName, DateOfBirth) Values ('Karen','Callercop', '04/15/1966')")
SQLStatementInsert2 = (r"INSERT INTO Person.PyTestingscript (FirstName, LastName, DateOfBirth) Values ('Jim','Ackerman', '01/03/1986')")
#D = Delete
SQLStatementDeleteRecord = (r"DELETE FROM Person.PyTest WHERE pyID = ?")
SQLStatementDeleteTable = (r"")
#E = Enhanced
SQLStoredProc = (r"EXEC dbo.uspGetEmployeeManagers @BusinessEntityID= ?;")

#C = Create
def dbCreate():
    strConnection = pyodbc.connect(ConnectionString)
    cursor = strConnection.cursor()
    cursor.execute(SQLCreateStatement)

    cursor.commit()

    return 

###----CREATE BLOCK----WORKS
#dbCreate()
###----CREATE BLOCK----WORKS

#R = Retrieve
def dbRetrieveData():
    strConnection = pyodbc.connect(ConnectionString)
    cursor = strConnection.cursor()
    cursor.execute(SQLStatementSpecific)

    columns = [column[0] for column in cursor.description]
    totalcolumns = len(columns)
    rows = [row for row in cursor.fetchall()]
    totalrows = len(rows)

    return totalcolumns, totalrows, columns, rows
###----RETRIEVE BLOCK----WORKS
#print(" ")
#for cn in range(len(dbRetrieveData()[2])):
#    print(dbRetrieveData()[2][cn])
#print(" ")
#for rn1 in range(len(dbRetrieveData()[3])):
#    for rn2 in range(len(dbRetrieveData()[3][0])):
#        print(dbRetrieveData()[3][rn1][rn2])
###----RETRIEVE BLOCK----WORKS

#U = Update
def UpdateFunction():
    def dbUpdateRecords():
        pyID = input('Enter record ID to be updated:')
        strConnection = pyodbc.connect(ConnectionString)
        cursor = strConnection.cursor()
        cursor.execute(SQLStatementUpdate, pyID)

        cursor.commit()
        if(cursor.rowcount == 0):
            SuccessMessage = ("No changes took place")
        elif(cursor.rowcount == 1):
            SuccessMessage = ("%s record updated" %(cursor.rowcount))
        else:
            SuccessMessage = ("%s records updated" %(cursor.rowcount))

        return SuccessMessage

    def dbInsertRecords():
        strConnection = pyodbc.connect(ConnectionString)
        cursor = strConnection.cursor()
        cursor.execute(SQLStatementInsert2)

        cursor.commit()
        if(cursor.rowcount == 0):
            SuccessMessage = ("No changes took place")
        elif(cursor.rowcount == 1):
            SuccessMessage = ("%s record updated" %(cursor.rowcount))
        else:
            SuccessMessage = ("%s records updated" %(cursor.rowcount))

        return SuccessMessage

    ToDo = input('Type U to update record, I to create new record.')
    if(ToDo == 'U'):
        dbUpdateRecords()
    elif(ToDo == 'I'):
        dbInsertRecords()
    else:
        Message = ("Invalid entry.")
###----UPDATE BLOCK----WORKS
print(UpdateFunction())
###----UPDATE BLOCK----WORKS

##D - Delete
#rID = input('Enter record ID to be deleted: ')
#def dbDeleteRecords(pyID=rID):
#    strConnection = pyodbc.connect(ConnectionString)
#    cursor = strConnection.cursor()
#    cursor.execute(SQLStatementDeleteRecord, pyID)
#    cursor.commit()
#    if(cursor.rowcount == 0):
#        SuccessMessage = ("No changes took place")
#    elif(cursor.rowcount == 1):
#        SuccessMessage = ("%s record deleted" %(cursor.rowcount))
#    else:
#        SuccessMessage = ("%s records deleted" %(cursor.rowcount))
#    return SuccessMessage
##----DELETE BLOCK----WORKS
#print(dbDeleteRecords())
##----DELETE BLOCK----WORKS

##E - Enhanced
#SQLStoredProcParams = input('Enter business entity ID: ')
#def dbExecuteStoredProc(Params=SQLStoredProcParams):
#    strConnection = pyodbc.connect(ConnectionString)
#    cursor = strConnection.cursor()
#    cursor.execute(SQLStoredProc, Params)
#
#    #rows = cursor.fetchall()
#    columns = [column[0] for column in cursor.description]
#    totalcolumns = len(columns)
#    rows = [row for row in cursor.fetchall()]
#    totalrows = len(rows)
#
#    return totalcolumns, totalrows, columns, rows
###----ENHANCED BLOCK----WORKS
#print(" ")
#for cn in range(len(dbExecuteStoredProc()[2])):
#    print(dbExecuteStoredProc()[2][cn])
#print(" ")
#for rn1 in range(len(dbExecuteStoredProc()[3])):
#    for rn2 in range(len(dbExecuteStoredProc()[3][0])):
#        print(dbExecuteStoredProc()[3][rn1][rn2])
###----ENHANCED BLOCK----WORKS