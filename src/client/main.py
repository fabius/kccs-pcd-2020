import requests, json, hashlib, os
import psycopg2 as pg

try:
    BASE_URL             = os.environ["PCD_IP"]
    MY_PHONE_NUMBER      = os.environ["MY_PHONE_NUMBER"]
    CONTACTS_DB_HOST     = os.environ["CONTACTS_DB_HOST"]
    CONTACTS_DB_PORT     = os.environ["CONTACTS_DB_PORT"]
    CONTACTS_DB_NAME     = os.environ["CONTACTS_DB_NAME"]
    CONTACTS_DB_USERNAME = os.environ["CONTACTS_DB_USERNAME"]
    CONTACTS_DB_PASSWORD = os.environ["CONTACTS_DB_PASSWORD"]
except KeyError as key:
    print(f"Database connection cannot be established. {key} is unset! Please export it")
    exit(1)



if __name__ == "__main__":
    # construct a (fictitious) address book using a database for its phone numbers
    dbcon = pg.connect(
        host     = CONTACTS_DB_HOST,
        port     = CONTACTS_DB_PORT,
        dbname   = CONTACTS_DB_NAME,
        user     = CONTACTS_DB_USERNAME,
        password = CONTACTS_DB_PASSWORD)
    cursor = dbcon.cursor()
    cursor.execute("""
        SELECT number, last_interaction_utc 
        FROM contacts;
        """)
    address_book = [(str(contact[0]), str(contact[1])) for contact in cursor.fetchall()]
    dbcon.close()
    cursor.close()

    # construct 2 dictionaries of number combinations:
    # NOTE THAT LAST_INTERACTION IS JUST AN EXAMPLE OF ANY PRIVATELY DISCLOSED INFORMATION
    # 1 - MY_NUMBER followed by A_FRIENDS_NUMBER : "last_interaction"
    # 2 - A_FRIENDS_NUMBER followed by MY_NUMBER : "last_interaction"
    # this is done so that we don't get any false positivies when receiving the intersection
    # -> upload the first dict (my perspective)
    # -> check for intersections using the second dict (each friends perspective)
    my_combinations_dict      = {}
    friends_combinations_dict = {}
    for contact_number, contact_last_interaction in address_book:
        my_combination           = MY_PHONE_NUMBER + contact_number  + ':' + contact_last_interaction
        friend_combination       = contact_number  + MY_PHONE_NUMBER + ':' + contact_last_interaction
        my_combinations_dict     [hashlib.sha1(my_combination    .encode()).hexdigest()] = my_combination
        friends_combinations_dict[hashlib.sha1(friend_combination.encode()).hexdigest()] = friend_combination
    my_combinations_array      = [hash_val for hash_val in my_combinations_dict]
    friends_combinations_array = [hash_val for hash_val in friends_combinations_dict]


    # check for intersections
    # returns an array of already registered hashes
    resp = requests.get(f"http://{BASE_URL}/compare/", data=json.dumps(friends_combinations_array)).json()
    
    # the intersection (value for each corresponding key inside the dict) looks like:
    # ["FRIENDS_NUMBER""MY_NUMBER":"last_interaction"]
    # however we are only interested in the other parties' phone numbers
    result_numbers = [
        friends_combinations_dict[hash_val].replace(MY_PHONE_NUMBER, "").split(':')[0] 
        for hash_val in resp]
    # remove potential duplicates
    result_numbers = list(dict.fromkeys(result_numbers))
    print(f"intersection / registered friends: {result_numbers}")

    # register my hash combinations
    resp = requests.post(f"http://{BASE_URL}/compare/", data=json.dumps(my_combinations_array))
