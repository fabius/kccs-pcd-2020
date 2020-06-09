import requests, json, hashlib, os
import psycopg2 as pg

try:
    BASE_URL         = os.environ["PCD_IP"]
    MY_PHONE_NUMBER  = os.environ["MY_PHONE_NUMBER"]
    HASH_DB_HOST     = os.environ["HASH_DB_HOST"]
    HASH_DB_PORT     = os.environ["HASH_DB_PORT"]
    HASH_DB_NAME     = os.environ["HASH_DB_NAME"]
    HASH_DB_USERNAME = os.environ["HASH_DB_USERNAME"]
    HASH_DB_PASSWORD = os.environ["HASH_DB_PASSWORD"]
except KeyError as key:
    print(f"Database connection cannot be established. {key} is unset! Please export it")
    exit(1)

dbcon = pg.connect(
    host     = HASH_DB_HOST,
    port     = HASH_DB_PORT,
    dbname   = HASH_DB_NAME,
    user     = HASH_DB_USERNAME,
    password = HASH_DB_PASSWORD)
cursor = dbcon.cursor()
cursor.execute("""
    SELECT number 
    FROM contacts;
    """)
address_book = [str(nums[0]) for nums in cursor.fetchall()]
dbcon.close()
cursor.close()

my_combinations_dict      = {}
friends_combinations_dict = {}
for contact in address_book:
    my_combination     = MY_PHONE_NUMBER + contact
    friend_combination = contact         + MY_PHONE_NUMBER
    my_combinations_dict     [hashlib.sha1(my_combination    .encode()).hexdigest()] = my_combination
    friends_combinations_dict[hashlib.sha1(friend_combination.encode()).hexdigest()] = friend_combination
my_combinations_array      = [hash_val for hash_val in my_combinations_dict]
friends_combinations_array = [hash_val for hash_val in friends_combinations_dict]



if __name__ == "__main__":
    resp = requests.get(f"{BASE_URL}/compare/", data=json.dumps(friends_combinations_array)).json()
    
    result_numbers = [
        friends_combinations_dict[hash_val].replace(MY_PHONE_NUMBER, "") 
        for hash_val in resp]
    result_numbers = list(dict.fromkeys(result_numbers))
    print(result_numbers)

    for element in my_combinations_array:
        requests.post(f"{BASE_URL}/compare/", data=json.dumps(element))
        