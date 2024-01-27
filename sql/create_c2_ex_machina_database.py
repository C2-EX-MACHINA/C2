from sqlite3 import connect

connection = connect("c2_ex_machina.db")
cursor = connection.cursor()
cursor.executescript(open("CREATE_C2_DATABASE.sql").read())
connection.commit()
cursor.close()
connection.close()
