"""An exemplary procd client"""

import traceback
import yaml

from lib import Procd


try:
    with open("config.yaml", 'r') as f:
        raw_yaml = yaml.safe_load(f)
        # this address book also contains
        # a date of last interaction alongside each number
        address_book = [(str(contact["number"]), str(
            contact["last_interaction"]))
            for contact in raw_yaml["contacts"]]
        print("my address book: {}".format(address_book))
        my_phone_number = raw_yaml["my_phone_number"]
        procd_ip = raw_yaml["procd_ip"]
        dh_secret = raw_yaml["dh_secret"]
except:
    traceback.print_exc()

if __name__ == "__main__":
    try:
        pcd = Procd(phone_number=my_phone_number,
                    address_book_with_interactions=address_book,
                    procd_server=procd_ip,
                    private_client_secret=dh_secret)
        intersection = pcd.run()
        print("registered contacts: {}".format(intersection))
    except:
        traceback.print_exc()