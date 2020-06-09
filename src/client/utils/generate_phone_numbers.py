import random, sys, os
import psycopg2 as pg

try:
    HASH_DB_HOST = os.environ["HASH_DB_HOST"]
    HASH_DB_PORT = os.environ["HASH_DB_PORT"]
    HASH_DB_NAME = os.environ["HASH_DB_NAME"]
    HASH_DB_USERNAME = os.environ["HASH_DB_USERNAME"]
    HASH_DB_PASSWORD = os.environ["HASH_DB_PASSWORD"]
except KeyError as ke:
    print(f"Database connection cannot be established. {ke} is unset! Please export it")
    exit(1)


if __name__ == "__main__":
    for i in range(int(sys.argv[1])):
        dbcon = pg.connect(
        host=HASH_DB_HOST,
        port=HASH_DB_PORT,
        dbname=HASH_DB_NAME,
        user=HASH_DB_USERNAME,
        password=HASH_DB_PASSWORD)
        cursor = dbcon.cursor()
        num = random.randint(10000000000, 99999999999)
        cursor.execute("""
            INSERT INTO contacts (number)
            VALUES (%s)
            ON CONFLICT DO NOTHING;
            """, [num])
        dbcon.commit()
        dbcon.close()
        cursor.close()
        