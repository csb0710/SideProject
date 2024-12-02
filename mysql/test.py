import mysql.connector
from mysql.connector import Error

def initialize_database(connection):
    """Initializes the database with required tables, procedures, views, triggers, and events."""
    try:
        cursor = connection.cursor()

        # 1. 테이블 생성
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
        CREATE TABLE IF NOT EXISTS backup_employee_salary (
            id INT PRIMARY KEY,
            employee_name VARCHAR(100),
            department VARCHAR(100),
            salary DECIMAL(10, 2),
            backup_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # 2. 스토어드 프로시저 생성
        cursor.execute("""
        DELIMITER $$
        CREATE PROCEDURE backup_employee_data()
        BEGIN
            INSERT INTO backup_employee_salary (id, employee_name, department, salary)
            SELECT id, employee_name, department, salary
            FROM employee_salary
            ON DUPLICATE KEY UPDATE 
                employee_name = VALUES(employee_name),
                department = VALUES(department),
                salary = VALUES(salary),
                backup_at = CURRENT_TIMESTAMP;
        END$$
        DELIMITER ;
        """)

        # 3. 이벤트 스케줄러 생성
        cursor.execute("SET GLOBAL event_scheduler = ON;")
        cursor.execute("""
        CREATE EVENT IF NOT EXISTS daily_backup_event
        ON SCHEDULE EVERY 1 DAY
        STARTS CURRENT_TIMESTAMP + INTERVAL 1 MINUTE
        DO
        CALL backup_employee_data();
        """)

        # 4. 트리거 생성
        cursor.execute("""
        DELIMITER $$
        CREATE TRIGGER restore_deleted_data
        AFTER DELETE ON employee_salary
        FOR EACH ROW
        BEGIN
            INSERT INTO employee_salary (id, employee_name, department, salary)
            SELECT OLD.id, OLD.employee_name, OLD.department, OLD.salary
            WHERE NOT EXISTS (
                SELECT 1 FROM employee_salary WHERE id = OLD.id
            );
        END$$
        DELIMITER ;
        """)

        # 5. 뷰 생성
        cursor.execute("""
        CREATE OR REPLACE VIEW department_salary_summary AS
        SELECT 
            department,
            COUNT(*) AS employee_count,
            SUM(salary) AS total_salary
        FROM employee_salary
        GROUP BY department;
        """)

        connection.commit()
        print("Database initialized successfully.")

    except Error as e:
        print(f"Error during database initialization: {e}")



def insert_data(connection):
    """Inserts a new record into employee_salary."""
    employee_name = input("Enter employee name: ")
    department = input("Enter department: ")
    salary = float(input("Enter salary: "))

    try:
        cursor = connection.cursor()
        query = """
        INSERT INTO employee_salary (employee_name, department, salary)
        VALUES (%s, %s, %s);
        """
        cursor.execute(query, (employee_name, department, salary))
        connection.commit()
        print("Data inserted successfully.")
    except Error as e:
        print(f"Error inserting data: {e}")


def perform_backup(connection):
    """Calls the backup procedure to back up data."""
    try:
        cursor = connection.cursor()
        cursor.execute("CALL backup_employee_data();")
        connection.commit()
        print("Backup performed successfully.")
    except Error as e:
        print(f"Error performing backup: {e}")


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
        print(f"Error fetching department summary: {e}")


def delete_employee(connection):
    """Deletes an employee record to simulate recovery."""
    employee_id = int(input("Enter employee ID to delete: "))
    try:
        cursor = connection.cursor()
        query = "DELETE FROM employee_salary WHERE id = %s;"
        cursor.execute(query, (employee_id,))
        connection.commit()
        print(f"Employee with ID {employee_id} deleted. Trigger should restore it automatically.")
    except Error as e:
        print(f"Error deleting employee: {e}")


def main():
    """Main CLI loop."""
    connection = connect_to_database()
    if not connection:
        return
    initialize_database(connection)

    while True:
        print("\nMenu:")
        print("1. Insert Data")
        print("2. Perform Backup")
        print("3. View Department Summary")
        print("4. Delete Employee (Simulate Recovery)")
        print("5. Exit")
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
            print("Exiting...")
            connection.close()
            break
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()

