# Lab book
This document shall grant insights on the development/thought process and how measurements were taken.



## Q: Which hashing algorithm is used for this matching service and why?
Due to collisions being pointless to brute force as you would not gain any knowledge about the phone numbers originally combined and hashed, any algorithm with a nice balance between speed and length of the calculated hash is reasonable.

SHA1 is being used. MD5 would have been fine as well. 



## Q: Consider 2 billion users. How much disk space is required to store those hashes?
1. Let's figure out how many hashes are going to be stored first. The amount of hashes to be stored depends on:

    * amount of users (=> 2 billion: [WhatsApp statistics](https://www.statista.com/statistics/260819/number-of-monthly-active-whatsapp-users/))
    * average number of contacts each user has in his address book ([WeChat statistics](https://www.statista.com/statistics/387665/wechat-china-contact-list-size/) => 200 as a starting point)

    So we are going to store an approximate amount of 2.000.000.000 * 200 = **400.000.000.000 hashes**.

2. How much disk space is taken up by 1.000.000 hashes?

    I created a fictitious address book (["contacts" table](db_structure.sql)) containing 1.000.000 contacts using the [generate_phone_numbers.py utility](src/client/utils/generate_phone_numbers.py). 

    ```bash
    kccs-pcd-2020/src/client$ pipenv run python3 utils/generate_phone_numbers.py 1000000
    ```

    To generate the corresponding hashes I ran the client image:

    ```bash
    docker pull fabiandeifuss/pcd-client:latest 
    docker run --rm -it \
        -e PCD_IP \
        -e MY_PHONE_NUMBER \
        -e CONTACTS_DB_HOST \
        -e CONTACTS_DB_PORT \
        -e CONTACTS_DB_NAME \
        -e CONTACTS_DB_USERNAME \
        -e CONTACTS_DB_PASSWORD \
        fabiandeifuss/pcd-client:latest
    ```

    The amount of disk space taken up by those 1.000.000 hashes can be figured out using a PostgreSQL query:
    
    ```sql
    postgres=# SELECT PG_SIZE_PRETTY(PG_TOTAL_RELATION_SIZE('hashes')) AS size_of_hash_table;
    size_of_hash_table 
    --------------------
    127 MB
    (1 row)
    ```

3. How much disk space is required to store 400.000.000.000 hashes?

    Approximately 400.000 * 127 MB = **50.8 TB**
    


## Q: How time consuming is an upload of 1.000 contacts?
**The following tests were done having both client and server on the same network!**

1. Assuming the hashed combinations do not exist yet and the PCD-server has to insert all of them:

    * make sure both tables ["contacts" and "hashes"](db.structure.sql) are empty
    * generate 1.000 numbers
    * time the execution of the client image

    ```sql
    DELETE FROM hashes;
    DELETE FROM contacts;
    ```

    ```bash
    kccs-pcd-2020/src/client$ pipenv run python3 utils/generate_contacts.py 1000
    ```

    ```bash
    docker pull fabiandeifuss/pcd-client:latest 
    time docker run --rm -it \
        -e PCD_IP \
        -e MY_PHONE_NUMBER \
        -e CONTACTS_DB_HOST \
        -e CONTACTS_DB_PORT \
        -e CONTACTS_DB_NAME \
        -e CONTACTS_DB_USERNAME \
        -e CONTACTS_DB_PASSWORD \
        fabiandeifuss/pcd-client:latest
    ```

    result: There are no stored hashes, hence no returned intersection.

    ```bash
    []

    real    0m15,557s
    user    0m0,029s
    sys     0m0,058s
    ```

    However when passing through an array of hashes rather than doing a POST request for every single hash ([commit](https://github.com/fabiandeifuss/kccs-pcd-2020/commit/c228c34588fa89f699fa6d0ac8580d3a7c38d052)), the time of execution is improved dramatically:

    result:

    ```bash
    []
    
    real    0m0,901s
    user    0m0,779s
    sys     0m0,098s
    ```

2. Assuming all of our hashed combinations are already present:

    No measurable difference for 1.000 hashes.

    result:
    
    ```bash
    []

    real    0m0,908s
    user    0m0,811s
    sys     0m0,074s    
    ```



## Q: How long does it take to compute a specific pre-image for a desired hash?
The calculation is analogue to [this article](https://thycotic.force.com/support/s/article/Calculating-Password-Complexity)

On a modern computer (6 core, 2.8 GHz), it takes 0.00063 milliseconds to compute a SHA1 hash (= 6.3e-7 seconds).

This translates to 1.5e+6 hashes per second.

Assuming the desired preimage is achieved after half of the possible combinations (preimage complexity of 10e+20 without salt), it would take approximately 1.000.000 years to get the desired hash.

Calculation: (6.3e-7 \* 1e+20) / (60\*60\*24\*7\*52\*2)

A comparable VM rental on MS Azure would cost about 2.000.000.000 $ 



## Q: How can we salt a last_interaction?
Assumption: the last_interaction is a **timestamp** which is perfectly accurate and in sync on both devices.

The most pragmatic way to salt a last_interaction information between two parties is by **salting it both ways**: 

* my_phone_number + contact_phone_number + last_interaction
* contact_phone_number + my_phone_number + last_interaction

Why is that important though? When querying for known intersections on the database (and posting our hashes), we do not want any **false positives** just because we registered a hashed combination ourselves. By hashing two distinct combinations, we get two distinct hashes respectively which can be used to identify whether or not a contact registered himself.



## Q: How can a key be exchanged so that two parties can confirm each others identity?
Diffie Hellman is perfectly feasible in this scenario. However **WE CAN NOT** just post each parties public secret linked to their phone number. That would defeat the whole purpose of this project. Yet there is a way to get a hold of each others public secret without exposing the corresponding phone number (whether that would be in plain text or hashed).

Remember we can suppress false positives by hashing our combinations in two ways. This way it is possible to just append the public secret to those hashes known by both parties.

So we end up having two hashes for each perspective:

* hashed_combination
  * this one is known by both parties and can be identified
* hashed_combination + public secret
  * this one is foreign, but we know the hashed_combination. 

To access the secret we can scan the database for values that are known to us and figure out if there are any hashes that start with that specific hexadecimal number. The ending bits represent the public secret!

Diffie Hellman key exchange is now possible.
