import os
import mysql.connector
from mysql.connector import Error
from datetime import datetime
from dotenv import load_dotenv
import typer

load_dotenv()

MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE")

app = typer.Typer()

# --- 데이터베이스 연결 함수 ---
def connect_to_db():
    try:
        connection = mysql.connector.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DATABASE
        )
        print("✅ Successfully connected to MySQL!")
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"❌ Error connecting to MySQL: {e}")
        return None


def initialize_database():
    connection = connect_to_db()
    if connection:
        cursor = connection.cursor()
        # 데이터베이스 초기 설정
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS employees (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                position VARCHAR(255) NOT NULL,
                salary FLOAT NOT NULL,
                hire_date DATE NOT NULL
            );
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS salary_backup (
                id INT AUTO_INCREMENT PRIMARY KEY,
                employee_id INT NOT NULL,
                name VARCHAR(255) NOT NULL,
                position VARCHAR(255) NOT NULL,
                salary FLOAT NOT NULL,
                backup_date DATETIME NOT NULL
            );
            """
        )
        # 스토어드 프로시저 생성 (백업 수행)
        cursor.execute(
            """
            CREATE OR REPLACE PROCEDURE BackupSalaries()
            BEGIN
                INSERT INTO salary_backup (employee_id, name, position, salary, backup_date)
                SELECT id, name, position, salary, NOW() FROM employees;
            END;
            """
        )
        # 이벤트 스케줄러 설정 (1분마다 백업)
        cursor.execute(
            """
            CREATE EVENT IF NOT EXISTS BackupEvent
            ON SCHEDULE EVERY 1 MINUTE
            DO CALL BackupSalaries();
            """
        )
        # 뷰 생성 (직원 정보 요약)
        cursor.execute(
            """
            CREATE OR REPLACE VIEW EmployeeSummary AS
            SELECT id, name, position, salary
            FROM employees;
            """
        )
        connection.commit()
        print("✅ Database initialized successfully!")
        connection.close()


# --- 기능 구현 ---
@app.command()
def add_employee(name: str, position: str, salary: float):
    """직원 추가"""
    connection = connect_to_db()
    if connection:
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO employees (name, position, salary, hire_date) VALUES (%s, %s, %s, %s)",
            (name, position, salary, datetime.now().date()),
        )
        connection.commit()
        print(f"✅ Employee '{name}' added successfully!")
        connection.close()


@app.command()
def view_employees():
    """직원 목록 보기"""
    connection = connect_to_db()
    if connection:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM EmployeeSummary")
        employees = cursor.fetchall()
        print("📋 Employee List:")
        for emp in employees:
            print(
                f"ID: {emp['id']}, Name: {emp['name']}, Position: {emp['position']}, Salary: {emp['salary']}"
            )
        connection.close()


@app.command()
def delete_employee(emp_id: int):
    """직원 삭제 (트리거로 복구 테스트)"""
    connection = connect_to_db()
    if connection:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM employees WHERE id = %s", (emp_id,))
        connection.commit()
        print(f"✅ Employee with ID '{emp_id}' deleted successfully!")
        connection.close()


@app.command()
def view_backups():
    """백업 데이터 보기"""
    connection = connect_to_db()
    if connection:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM salary_backup")
        backups = cursor.fetchall()
        print("📋 Backup Data:")
        for backup in backups:
            print(
                f"Employee ID: {backup['employee_id']}, Name: {backup['name']}, "
                f"Position: {backup['position']}, Salary: {backup['salary']}, Backup Date: {backup['backup_date']}"
            )
        connection.close()

@app.command()
def init_db():
    """데이터베이스 초기화 명령"""
    initialize_database()

# --- 메인 ---
if __name__ == "__main__":
    app()

