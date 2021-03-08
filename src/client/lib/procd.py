import traceback
import requests
import json
import hashlib
import secrets
from typing import List


class Procd:
    """Privacy respecting contact discovery"""

    SHARED_PRIME = 23
    SHARED_BASE = 5

    # also contains a last date of interaction
    # [(number1, date1), (number2, date2)]
    address_book = list()
    phone_number = str()
    procd_server = str()
    _private_client_secret = int()

    def __init__(self, phone_number: str,
                 address_book_with_interactions: List[tuple],
                 procd_server: str, private_client_secret: int):
        """
        Args:
            phone_number (str): the caller's own phone number
            address_book_with_interactions (list): a list of tuples
                containing (contact_number, last_interaction_date)
            procd_server (str): IP_address:port of your desired procd server instance
            private_client_secret (int): the caller's private diffie hellman secret
        """
        print("Instanciating Procd...")
        self.phone_number = phone_number
        self.address_book = address_book_with_interactions
        self.procd_server = procd_server
        self._private_client_secret = int(private_client_secret)

    def run(self):
        """
        Post all computed combinations of:
            - the caller's own phone number,
            - a contact's phone number,
            - the corresponding date of last interaction
            to your desired procd server instance.

        Returns:
            list: a list of all registered contacts;
                an empty list if none were found
        """
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
        for contact_number, contact_last_interaction in self.address_book:
            my_combination = self.phone_number + \
                contact_number + ':' + contact_last_interaction
            my_combination_hashed = hashlib.sha1(
                my_combination.encode()).hexdigest()
            friend_combination = contact_number + \
                self.phone_number + ':' + contact_last_interaction
            friend_combination_hashed = hashlib.sha1(
                friend_combination.encode()).hexdigest()
            my_combinations_dict[my_combination_hashed] = my_combination
            friends_combinations_dict[
                friend_combination_hashed] = friend_combination
            dh_dict[contact_number] = friend_combination_hashed
        my_combinations_array = [hash_val for hash_val in my_combinations_dict]
        friends_combinations_array = [
            hash_val for hash_val in friends_combinations_dict
        ]
        sec = format((self.SHARED_BASE**self._private_client_secret) %
                     self.SHARED_PRIME, 'x')
        print(f"len(sec) = {len(sec)}")
        # even number of digits (postgres needs that)
        sec = f"0{sec}" if len(sec) % 2 else sec
        print(f"secret: {sec}")
        print(f"type:   {type(sec)}")
        secrets_to_send = [
            hash_val + sec for hash_val in my_combinations_array
        ]
        array_to_post = my_combinations_array + secrets_to_send
        print(f"mine:    {my_combinations_array}")
        print(f"friends: {friends_combinations_array}")
        print(f"secr:    {secrets_to_send}")

        # check for intersections
        # returns an array of already registered hashes
        compare_endpoint = f"http://{self.procd_server}/compare/"
        resp = requests.get(
            compare_endpoint,
            data=json.dumps(friends_combinations_array)).json()
        print(f"GET {compare_endpoint}")
        print(f"PAYLOAD: \n{json.dumps(friends_combinations_array, indent=2)}")

        # the intersection (value for each corresponding key inside the dict) looks like:
        # ["FRIENDS_NUMBER""MY_NUMBER":"last_interaction"]
        # however we are only interested in the other parties' phone numbers
        result_numbers = [
            friends_combinations_dict[hash_val].replace(self.phone_number,
                                                        "").split(':')[0]
            for hash_val in resp
        ]
        # remove potential duplicates
        result_numbers = list(dict.fromkeys(result_numbers))
        result_numbers = list(filter(None, result_numbers))
        print(f"intersection / registered friends: {result_numbers}")

        # addd their secret to each number
        numbers_and_secrets = []
        for number in result_numbers:
            print(f"sending hash: {dh_dict[number]}")
            resp_secret = requests.get(f"http://{self.procd_server}/secret/",
                                       data=json.dumps(
                                           {"hash": dh_dict[number]})).json()
            print(f"response secret: {resp_secret}")
            secret = resp_secret[0]
            numbers_and_secrets.append((number, secret))
        print(f"numbers and secrets: {numbers_and_secrets}")
        try:
            his_secret = int(numbers_and_secrets[0][1], 16)
            print(f"friends secret: {his_secret}")
            my_shared_secret = (
                his_secret**self._private_client_secret) % self.SHARED_PRIME
            print(f"my shared secret: {my_shared_secret}")
        except Exception:
            traceback.print_exc()

        # register my hash combinations: list
        # 1) my hashed combinations: list
        # 2) hash + secret: list
        print(my_combinations_array)
        print(secrets_to_send)
        print(array_to_post)
        requests.post(f"http://{self.procd_server}/compare/",
                      data=json.dumps(secrets_to_send))
        return [contact[0] for contact in numbers_and_secrets]
