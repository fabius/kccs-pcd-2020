import os
import traceback
import psycopg2 as pg


# construct a (fictitious) address book
# using a database for its phone numbers
try:
    db_cred = {
        "host": os.environ["CONTACTS_DB_HOST"],
        "port": os.environ["CONTACTS_DB_PORT"],
        "name": os.environ["CONTACTS_DB_NAME"],
        "username": os.environ["CONTACTS_DB_USERNAME"],
        "password": os.environ["CONTACTS_DB_PASSWORD"]
    }
except KeyError as key:
    print(
        f"Database connection cannot be established. {key} is unset! Please export it")
    traceback.print_exc()
    exit(1)
dbcon = pg.connect(
    host=db_cred["host"],
    port=db_cred["port"],
    dbname=db_cred["name"],
    user=db_cred["username"],
    password=db_cred["password"])
cursor = dbcon.cursor()
cursor.execute("""
    SELECT number, last_interaction_utc
    FROM contacts;
    """)
# this address book also contains a date of last interaction alongside each number
address_book = [(str(contact[0]), str(contact[1]))
                for contact in cursor.fetchall()]
print(f"my address book: {address_book}")
dbcon.close()
cursor.close()


if __name__ == "__main__":
    from lib import Procd
    pcd = Procd(phone_number=os.environ["MY_PHONE_NUMBER"],
                address_book_with_interactions=address_book,
                procd_server=os.environ["PCD_IP"],
                private_client_secret=os.environ["DH_SECRET"])
    intersection = pcd.run()
    print(f"registered contacts: {intersection}")
