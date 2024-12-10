import os
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

load_dotenv()
MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE")

# 데이터베이스 연결 함수
def connect_to_database():
    try:
        connection = mysql.connector.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD
        )
        if connection.is_connected():
            print("✅ Successfully connected to the database!")
            cursor = connection.cursor()
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {MYSQL_DATABASE};")
            connection.commit()

            connection.database = MYSQL_DATABASE
            print(f"Connected to database: {MYSQL_DATABASE}")
            return connection
    except Error as e:
        print(f"❌ Error connecting to database: {e}")
        return None


def initialize_database(connection):
    """Initializes the database with required tables, procedures, triggers, and events."""
    try:
        cursor = connection.cursor()

        # 1. Event Scheduler 활성화
        cursor.execute("SET GLOBAL event_scheduler = ON;")
        print("✅ Event Scheduler has been enabled.")

        # 2. 테이블 생성
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS employee_salary (
            id INT AUTO_INCREMENT PRIMARY KEY,
            employee_name VARCHAR(100),
            department VARCHAR(100),
            salary DECIMAL(10, 2),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS deleted_employee_backup (
            id INT PRIMARY KEY,
            employee_name VARCHAR(100),
            department VARCHAR(100),
            salary DECIMAL(10, 2),
            deleted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # 3. 트리거 생성
        cursor.execute("DROP TRIGGER IF EXISTS log_deleted_data;")
        cursor.execute("""
        CREATE TRIGGER log_deleted_data
        AFTER DELETE ON employee_salary
        FOR EACH ROW
        BEGIN
            INSERT INTO deleted_employee_backup (id, employee_name, department, salary, deleted_at)
            VALUES (OLD.id, OLD.employee_name, OLD.department, OLD.salary, CURRENT_TIMESTAMP)
            ON DUPLICATE KEY UPDATE
                employee_name = VALUES(employee_name),
                department = VALUES(department),
                salary = VALUES(salary),
                deleted_at = VALUES(deleted_at);
        END;
        """)

        # 4. 복구용 프로시저 생성
        cursor.execute("DROP PROCEDURE IF EXISTS restore_employee_data;")
        cursor.execute("""
        CREATE PROCEDURE restore_employee_data(IN employee_id INT)
        BEGIN
            DECLARE employee_exists INT;
            SELECT COUNT(*) INTO employee_exists
            FROM employee_salary
            WHERE id = employee_id;

            IF employee_exists = 0 THEN
                INSERT INTO employee_salary (id, employee_name, department, salary)
                SELECT id, employee_name, department, salary
                FROM deleted_employee_backup
                WHERE id = employee_id;

                DELETE FROM deleted_employee_backup WHERE id = employee_id;
            END IF;
        END;
        """)

        # 5. 백업용 프로시저 생성
        cursor.execute("DROP PROCEDURE IF EXISTS backup_employee_data;")
        cursor.execute("""
        CREATE PROCEDURE backup_employee_data()
        BEGIN
            INSERT INTO deleted_employee_backup (id, employee_name, department, salary, deleted_at)
            SELECT id, employee_name, department, salary, CURRENT_TIMESTAMP
            FROM employee_salary
            ON DUPLICATE KEY UPDATE
                employee_name = VALUES(employee_name),
                department = VALUES(department),
                salary = VALUES(salary),
                deleted_at = VALUES(deleted_at);
        END;
        """)

        # 6. 백업 테이블 정리 이벤트 생성
        cursor.execute("DROP EVENT IF EXISTS reset_deleted_backup;")
        cursor.execute("""
        CREATE EVENT reset_deleted_backup
        ON SCHEDULE EVERY 1 DAY
        STARTS CURRENT_TIMESTAMP + INTERVAL 1 DAY
        DO
        TRUNCATE TABLE deleted_employee_backup;
        """)

        # 7. 뷰 생성 (부서별 급여 요약)
        cursor.execute("""
        CREATE OR REPLACE VIEW department_salary_summary AS
        SELECT
            department,
            COUNT(*) AS employee_count,
            SUM(salary) AS total_salary
        FROM employee_salary
        GROUP BY department;
        """)
        
        # 8. 사원 목록 뷰 생성
        cursor.execute("""
        CREATE OR REPLACE VIEW employee_list_view AS
        SELECT
            id,
            employee_name AS name,
            department
        FROM employee_salary
        ORDER BY id;
        """)

        connection.commit()
        print("✅ Database initialized successfully.")

    except Error as e:
        print(f"❌ Error during database initialization: {e}")
    finally:
        cursor.close()


def insert_data(connection):
    """Inserts a new record into employee_salary."""
    try:
        employee_name = input("Enter employee name: ").strip()
        if not employee_name:
            raise ValueError("Employee name cannot be empty.")
        
        department = input("Enter department: ").strip()
        if not department:
            raise ValueError("Department cannot be empty.")
        
        salary = input("Enter salary: ").strip()
        if not salary.isdigit():
            raise ValueError("Salary must be a valid number.")
        salary = float(salary)

        cursor = connection.cursor()
        query = """
        INSERT INTO employee_salary (employee_name, department, salary)
        VALUES (%s, %s, %s);
        """
        cursor.execute(query, (employee_name, department, salary))
        connection.commit()
        print("✅ Data inserted successfully.")
    except ValueError as ve:
        print(f"❌ Input error: {ve}")
    except Error as e:
        print(f"❌ Error inserting data: {e}")


def delete_employee(connection):
    """Deletes an employee record to simulate recovery."""
    try:
        employee_id = input("Enter employee ID to delete: ").strip()
        if not employee_id.isdigit():
            raise ValueError("Employee ID must be a valid number.")
        employee_id = int(employee_id)

        cursor = connection.cursor()
        query = "DELETE FROM employee_salary WHERE id = %s;"
        cursor.execute(query, (employee_id,))
        connection.commit()
        print(f"✅ Employee with ID {employee_id} deleted. Trigger should restore it automatically.")
    except ValueError as ve:
        print(f"❌ Input error: {ve}")
    except Error as e:
        print(f"❌ Error deleting employee: {e}")


def perform_backup(connection):
    """Calls the backup procedure to back up data."""
    try:
        cursor = connection.cursor()
        cursor.execute("CALL backup_employee_data();")
        connection.commit()
        print("✅ Backup performed successfully.")
    except Error as e:
        print(f"❌ Error performing backup: {e}")


def view_department_summary(connection):
    """Displays department-wise salary summary."""
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM department_salary_summary;")
        rows = cursor.fetchall()
        print("Department | Employee Count | Total Salary")
        for row in rows:
            print(f"{row[0]} | {row[1]} | {row[2]}")
    except Error as e:
        print(f"❌ Error fetching department summary: {e}")
        
def view_employee_list(connection):
    """Displays a list of employees with their ID, name, and department."""
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM employee_list_view;")
        rows = cursor.fetchall()
        print("ID | Name             | Department")
        print("-" * 40)
        for row in rows:
            print(f"{row[0]:<3} | {row[1]:<16} | {row[2]}")
    except Error as e:
        print(f"❌ Error fetching employee list: {e}")


def restore_specific_employee(connection):
    """Restores specific employee data using a stored procedure."""
    try:
        employee_id = input("Enter the employee ID to restore: ").strip()
        if not employee_id.isdigit():
            raise ValueError("Employee ID must be a valid number.")
        employee_id = int(employee_id)

        cursor = connection.cursor()
        cursor.execute("CALL restore_employee_data(%s);", (employee_id,))
        connection.commit()

        print(f"✅ Employee with ID {employee_id} restored successfully.")
    except ValueError as ve:
        print(f"❌ Input error: {ve}")
    except Error as e:
        print(f"❌ Error restoring employee: {e}")


def main():
    connection = connect_to_database()
    if not connection:
        return
    try:
        initialize_database(connection)
        while True:
            print("\nMenu:")
            print("1. Insert Data")
            print("2. Perform Backup")
            print("3. View Department Summary")
            print("4. Delete Employee (Simulate Recovery)")
            print("5. Restore Specific Employee")
            print("6. View Employee List")
            print("7. Exit")
            choice = input("Enter your choice: ")

            if choice == "1":
                insert_data(connection)
            elif choice == "2":
                perform_backup(connection)
            elif choice == "3":
                view_department_summary(connection)
            elif choice == "4":
                delete_employee(connection)
            elif choice == "5":
                restore_specific_employee(connection)
            elif choice == "6":
                view_employee_list(connection)
            elif choice == "7":
                print("Exiting...")
                break
            else:
                print("❌ Invalid choice. Please try again.")
    finally:
        if connection.is_connected():
            connection.close()
            print("✅ Connection closed.")

if __name__ == "__main__":
    main()
