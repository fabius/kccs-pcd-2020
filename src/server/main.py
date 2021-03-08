"""private robust contact discovery server"""

import json
import traceback
import psycopg2 as pg
from flask import Flask, request
import yaml

with open("config.yaml", 'r') as f:
    raw_yaml = yaml.safe_load(f)
    db_cred = raw_yaml["hash_db"]

app = Flask(__name__)

# provide 2 endpoints:
# 1 - check for intersections and return them
# 2 - register combinations


@app.route("/compare/", methods=["GET", "POST"])
def compare():
    dbcon = pg.connect(host=db_cred["host"],
                       port=db_cred["port"],
                       dbname=db_cred["dbname"],
                       user=db_cred["username"],
                       password=db_cred["password"])
    cursor = dbcon.cursor()

    data = json.loads(request.data)
    app.logger.debug(f"request data: {data}")

    if request.method == "POST":
        if type(data) != list:
            return "provide an array of hashes"
        else:
            try:
                raw = data
                combination = [r[:40] for r in raw]
                secret = [r[40:] for r in raw]
                print(f"raw: {raw}")
                print(f"len(raw): {len(raw[0])}")
                print(f"combination: {combination}")
                print(f"secret: {secret}")
                for entry in data:
                    combination = entry[:40]
                    secret = entry[40:]
                    cursor.execute(
                        """
                        INSERT INTO hashes (hash, secret)
                        VALUES (DECODE(%s, 'hex'), DECODE(%s, 'hex'))
                        ON CONFLICT (hash)
                        DO UPDATE SET hash = EXCLUDED.hash;
                        """, (combination, secret))
            except pg.errors.UniqueViolation:
                app.logger.debug("Hash already exists")
                traceback.print_exc()
            dbcon.commit()
            dbcon.close()
            cursor.close()
            return "OK"

    elif request.method == "GET":
        try:
            cursor.execute(
                """
                SELECT ENCODE(hash::BYTEA, 'hex') 
                FROM hashes 
                WHERE ENCODE(hash::BYTEA, 'hex') = ANY(%s);
                """, (data, ))
            intersection = [current[0] for current in cursor.fetchall()]
        except pg.errors.InvalidTextRepresentation:
            intersection = []
        except pg.errors.InFailedSqlTransaction:
            pass
        cursor.close()
        dbcon.close()
        app.logger.debug(f"intersection: {intersection}")
        status_code = 200 if len(intersection) != 0 else 404
        app.logger.debug(status_code)
        return json.dumps(intersection)


@app.route("/secret/", methods=["GET"])
def return_secret():
    app.logger.debug("\n\nSECRET\n\n")
    dbcon = pg.connect(host=db_cred["host"],
                       port=db_cred["port"],
                       dbname=db_cred["dbname"],
                       user=db_cred["username"],
                       password=db_cred["password"])
    cursor = dbcon.cursor()

    data = json.loads(request.data)
    app.logger.debug(f"request data: {data}")
    requested_hash = data["hash"]
    app.logger.debug(f"request hash: {requested_hash}")

    try:
        cursor.execute(
            """
select encode(hash::bytea,'hex'),encode(secret::bytea,'hex') from hashes;
            """, (requested_hash, ))
        all_data = cursor.fetchall()
        app.logger.debug(f"all_data: {all_data}")
        intersection = [x[1] for x in all_data if x[0] == requested_hash]
    except pg.errors.InvalidTextRepresentation:
        intersection = []
    except pg.errors.InFailedSqlTransaction:
        intersection = []
    cursor.close()
    dbcon.close()
    app.logger.debug(f"secrets to send back: {intersection}")
    status_code = 200 if len(intersection) != 0 else 404
    app.logger.debug(status_code)
    return json.dumps(intersection), status_code


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
