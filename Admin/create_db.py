import mysql.connector

connection = mysql.connector.connect(host='localhost',
                                     port='3306',
                                     user='KEEHUIYEE',
                                     password='KeE-0924')

cursor = connection.cursor()

cursor.execute('SHOW DATABASES;')
records = cursor.fetchall()
for r in records:
    print(r)

cursor.close()
connection.close()