import psycopg


DATABASE_URL = (
    "postgresql://payment_user:payment_password"
    "@localhost:5432/payment_db"
)


def get_connection():
    return psycopg.connect(DATABASE_URL)


if __name__ == "__main__":
    with get_connection() as connection:
        print("Database connection successful!")