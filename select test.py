#! python
import pyodbc

conn = pyodbc.connect(
        'Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=./NHL-Players.accdb;')
cursor = conn.cursor()

