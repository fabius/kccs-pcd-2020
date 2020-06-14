import random, sys, os, logging
import psycopg2 as pg

logging.basicConfig(level=logging.DEBUG)

try:
    HASH_DB_HOST = os.environ["HASH_DB_HOST"]
    HASH_DB_PORT = os.environ["HASH_DB_PORT"]
    HASH_DB_NAME = os.environ["HASH_DB_NAME"]
    HASH_DB_USERNAME = os.environ["HASH_DB_USERNAME"]
    HASH_DB_PASSWORD = os.environ["HASH_DB_PASSWORD"]
except KeyError as ke:
    print(f"Database connection cannot be established. {ke} is unset! Please export it")
    exit(1)



def generate_unique_number(numbers: list) -> int:
    num = random.randint(1000000000, 9999999999)
    if num in numbers:
        logging.debug(f"{num} already exists. Generating a new number")
        num = generate_unique_number(numbers)
    return num



if __name__ == "__main__":
    dbcon = pg.connect(
        host     = HASH_DB_HOST,
        port     = HASH_DB_PORT,
        dbname   = HASH_DB_NAME,
        user     = HASH_DB_USERNAME,
        password = HASH_DB_PASSWORD)
    cursor = dbcon.cursor()
    
    numbers_to_insert = []
    for i in range(int(sys.argv[1])):
        num = generate_unique_number(numbers_to_insert)
        numbers_to_insert.append(num)
        logging.debug(f"number {str(i).zfill(len(str(sys.argv[1])))}: {num}")
    logging.debug(f"inserting numbers: {numbers_to_insert}")
    try:
        cursor.execute("""
            INSERT INTO contacts (number)
            VALUES (UNNEST(%s));
            """, (numbers_to_insert,))
    except pg.errors.UniqueViolation:
        app.logger.debug(f"A duplication hindered the insertion. Please make sure your database table is empty")
    dbcon.commit()
    dbcon.close()
    cursor.close()
        