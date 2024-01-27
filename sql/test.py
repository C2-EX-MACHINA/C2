from sqlite3 import connect

connection = connect("test.db")
cursor = connection.cursor()
cursor.executescript(open("CREATE_C2_DATABASE.sql").read())
cursor.executescript(open("test.sql").read())
connection.commit()
cursor.execute("SELECT * FROM InstancesToAgents;")
for instance in cursor.fetchall():
    print(instance)
cursor.close()
connection.close()
