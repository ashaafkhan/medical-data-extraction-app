import os
import mysql.connector
from mysql.connector import Error
import streamlit as st


class DBUtility:
    def __init__(self) -> None:
        # Load DB config from environment variables with sensible defaults
        self.config = {
            'host': st.secrets.get('MDE_DB_HOST', 'localhost'),
            'database': st.secrets.get('MDE_DB_NAME', 'medical_data_db'),
            'user': st.secrets.get('MDE_DB_USER', 'root'),
            'password': st.secrets['MDE_DB_PASSWORD']
}
        self.connection = None
        self.cursor = None

    def get_connection_cursor(self):
        try:
            connection = mysql.connector.connect(
                host = self.config['host'],
                database = self.config['database'],
                user = self.config['user'],
                password = self.config['password']
            )
            if connection.is_connected():
                self.connection = connection
                # use a buffered cursor so callproc behaves more predictably
                self.cursor = connection.cursor(buffered=True)
                print(f"Connected to db '{self.config['database']}' as {self.config['user']}@{self.config['host']}")
                return True
        except Error as e:
            # print the exception so we can diagnose connection problems
            print("Error in connecting to db:", repr(e))
            return False

    def update_table(self, table, data):
        if not self.connection:
            self.get_connection_cursor()
        try:
            if self.connection and self.cursor:
                print(data)
                if table == 'patient':
                    sql = "INSERT INTO patients (name, phone, vaccin_status, medical_problems, insurance) VALUES (%s, %s, %s, %s, %s)"
                    self.cursor.execute(sql, data)
                elif table == 'prescription':
                    sql = "INSERT INTO prescriptions (name, address, medicines, directions, refill) VALUES (%s, %s, %s, %s, %s)"
                    self.cursor.execute(sql, data)
                else:
                    print(f"Unknown table '{table}' requested")
                    return False

                self.connection.commit()
                print(f"Data inserted into {table} successfully")
                return True
            else:
                print("Error: no DB connection/cursor available to execute queries")
                return False
        except Exception as e:
            print("Error in executing DB operation:", repr(e))
            return False
        finally:
            # close cursor first, then connection
            try:
                if self.cursor:
                    self.cursor.close()
            except Exception:
                pass
            try:
                if self.connection:
                    self.connection.close()
            except Exception:
                pass


if __name__ == "__main__":
    dbutility = DBUtility()
    data = ('Jon snow', '1234567890', 'Fully Vaccinated', 'Hypertension', 'HealthCarePlus')
    dbutility.update_table(table='patient', data=data)
