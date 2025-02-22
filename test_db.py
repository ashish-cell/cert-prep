import psycopg2

def test_connection():
    try:
        conn = psycopg2.connect(
            dbname="quiz_app",
            user="postgres",
            password="Diehard10*",
            host="localhost"
        )
        print("Connection successful!")
        conn.close()
    except Exception as e:
        print(f"Connection failed: {str(e)}")

if __name__ == "__main__":
    test_connection()
