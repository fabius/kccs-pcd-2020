import random, sys, os, logging, datetime
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

def unique_numbers_array(numbers=[]) -> list:
    for i in range(int(sys.argv[1])):
        num = generate_unique_number(numbers)
        numbers.append(num)
        logging.debug(f"number {str(i).zfill(len(str(sys.argv[1])))}: {num}")
    return numbers

def dates_array(dates=[]) -> list:
    now = datetime.datetime.utcnow().replace(microsecond=0, second=0)
    for i in range(int(sys.argv[1])):
        date_to_append = now + datetime.timedelta(minutes=i)
        dates.append(date_to_append)
        logging.debug(f"date {str(i).zfill(len(str(sys.argv[1])))}: {date_to_append}")
    return dates



if __name__ == "__main__":
    contact_numbers = unique_numbers_array()
    contact_interaction_dates = dates_array()
    
    dbcon = pg.connect(
        host     = HASH_DB_HOST,
        port     = HASH_DB_PORT,
        dbname   = HASH_DB_NAME,
        user     = HASH_DB_USERNAME,
        password = HASH_DB_PASSWORD)
    cursor = dbcon.cursor()
    try:
        cursor.execute("""
            INSERT INTO contacts (number, last_interaction_utc)
            VALUES (UNNEST(%s),UNNEST(%s));
            """, (contact_numbers, contact_interaction_dates))
        logging.debug(f"inserted {sys.argv[1]} unique contacts")
    except pg.errors.UniqueViolation:
        app.logger.debug(f"A duplicate number hindered the insertion. Please make sure your database table is empty")
    dbcon.commit()
    dbcon.close()
    cursor.close()
        