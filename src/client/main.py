import requests
import json
import hashlib
import os
import secrets
import logging
import traceback
import psycopg2 as pg

logging.basicConfig(level=logging.DEBUG)

try:
    BASE_URL = os.environ["PCD_IP"]
    MY_PHONE_NUMBER = os.environ["MY_PHONE_NUMBER"]
    db_cred = {
        "host": os.environ["CONTACTS_DB_HOST"],
        "port": os.environ["CONTACTS_DB_PORT"],
        "name": os.environ["CONTACTS_DB_NAME"],
        "username": os.environ["CONTACTS_DB_USERNAME"],
        "password": os.environ["CONTACTS_DB_PASSWORD"]
    }
except KeyError as key:
    logging.error(
        f"Database connection cannot be established. {key} is unset! Please export it")
    exit(1)

# Diffie Hellman parts
try:
    # p - for demonstration only! to be replaced by a secret (bigger prime)
    SHARED_PRIME = 23
    SHARED_BASE = 5  # g
    my_secret = int(os.environ["DH_SECRET"])  # a
except KeyError as key:
    logging.error(
        f"Diffie Hellman requires a private secret. {key} is unset! Please export it")
    exit(1)


if __name__ == "__main__":
    # construct a (fictitious) address book using a database for its phone
    # numbers
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
    address_book = [(str(contact[0]), str(contact[1]))
                    for contact in cursor.fetchall()]
    logging.info(f"my phone number: {MY_PHONE_NUMBER}")
    logging.info(f"my address book: {address_book}")
    dbcon.close()
    cursor.close()

    # construct 2 dictionaries of number combinations:
    # NOTE THAT LAST_INTERACTION IS JUST AN EXAMPLE OF ANY PRIVATELY DISCLOSED INFORMATION
    # 1 - MY_NUMBER followed by A_FRIENDS_NUMBER : "last_interaction"
    # 2 - A_FRIENDS_NUMBER followed by MY_NUMBER : "last_interaction"
    # this is done so that we don't get any false positivies when receiving the intersection
    # -> upload the first dict (my perspective)
    # -> check for intersections using the second dict (each friends perspective)
    my_combinations_dict = {}
    friends_combinations_dict = {}
    # construct a diffie hellman dict so that we can look for our friends combinations later
    # -> every participant POSTS
    #      1) his/her combinations
    #      2) those combinations with an appended secret
    # -> so that we can look for our desired key in the database
    dh_dict = {}
    for contact_number, contact_last_interaction in address_book:
        my_combination = MY_PHONE_NUMBER + contact_number + ':' + contact_last_interaction
        my_combination_hashed = hashlib.sha1(
            my_combination    .encode()).hexdigest()
        friend_combination = contact_number + \
            MY_PHONE_NUMBER + ':' + contact_last_interaction
        friend_combination_hashed = hashlib.sha1(
            friend_combination.encode()).hexdigest()
        my_combinations_dict[my_combination_hashed] = my_combination
        friends_combinations_dict[friend_combination_hashed] = friend_combination
        dh_dict[contact_number] = friend_combination_hashed
    my_combinations_array = [hash_val for hash_val in my_combinations_dict]
    friends_combinations_array = [
        hash_val for hash_val in friends_combinations_dict]
    sec = format((SHARED_BASE**my_secret) % SHARED_PRIME, 'x')
    print(f"len(sec) = {len(sec)}")
    sec = f"0{sec}" if len(sec)%2 else sec # even number of digits (postgres needs that)
    logging.info(f"secret: {sec}")
    logging.info(f"type:   {type(sec)}")
    secrets_to_send = [hash_val + sec for hash_val in my_combinations_array]
    array_to_post = my_combinations_array + secrets_to_send
    logging.info(f"mine:    {my_combinations_array}")
    logging.info(f"friends: {friends_combinations_array}")
    logging.info(f"secr:    {secrets_to_send}")

    # check for intersections
    # returns an array of already registered hashes
    compare_endpoint = f"http://{BASE_URL}/compare/"
    resp = requests.get(compare_endpoint, data=json.dumps(
        friends_combinations_array)).json()
    logging.info(f"GET {compare_endpoint}")
    logging.info(
        f"PAYLOAD: \n{json.dumps(friends_combinations_array, indent=2)}")

    # the intersection (value for each corresponding key inside the dict) looks like:
    # ["FRIENDS_NUMBER""MY_NUMBER":"last_interaction"]
    # however we are only interested in the other parties' phone numbers
    result_numbers = [
        friends_combinations_dict[hash_val].replace(
            MY_PHONE_NUMBER, "").split(':')[0]
        for hash_val in resp]
    # remove potential duplicates
    result_numbers = list(dict.fromkeys(result_numbers))
    result_numbers = list(filter(None, result_numbers))
    logging.info(f"intersection / registered friends: {result_numbers}")

    # addd their secret to each number
    numbers_and_secrets = []
    for number in result_numbers:
        resp_hash = requests.get(f"http://{BASE_URL}/secret/",
                                 data=json.dumps({"hash": dh_dict[number]})).json()
        secret = str()
        for hashed in resp_hash:
            temp = hashed[0][40:]
            secret = temp if len(temp) != 0 else secret
        numbers_and_secrets.append((number, secret))
    logging.info(f"numbers and secrets: {numbers_and_secrets}")
    try:
        his_secret = int(numbers_and_secrets[0][1], 16)
        logging.info(f"friends secret: {his_secret}")
        my_shared_secret = (his_secret**my_secret) % SHARED_PRIME
        logging.info(f"my shared secret: {my_shared_secret}")
    except Exception:
        traceback.print_exc()

    # register my hash combinations: list
    # 1) my hashed combinations: list
    # 2) hash + secret: list
    resp = requests.post(
        f"http://{BASE_URL}/compare/", data=json.dumps(array_to_post))
