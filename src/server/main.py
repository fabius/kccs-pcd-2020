import psycopg2 as pg
import os, json, time
from flask import Flask, jsonify, request, abort, Response, make_response

try:
    db_cred = {
        "host"     : os.environ["HASH_DB_HOST"],
        "port"     : os.environ["HASH_DB_PORT"],
        "name"     : os.environ["HASH_DB_NAME"],
        "username" : os.environ["HASH_DB_USERNAME"],
        "password" : os.environ["HASH_DB_PASSWORD"]
    }
except KeyError as key:
    print(f"Database connection cannot be established. {key} is unset! Please export it")
    exit(1)

app = Flask(__name__)

# provide 2 endpoints:
# 1 - check for intersections and return them
# 2 - register combinations
@app.route("/compare/", methods=["GET", "POST"])
def compare():
    dbcon = pg.connect(
        host     = db_cred["host"],
        port     = db_cred["port"],
        dbname   = db_cred["name"],
        user     = db_cred["username"],
        password = db_cred["password"])
    cursor = dbcon.cursor()

    data = json.loads(request.data)
    app.logger.debug(f"request data: {data}")

    if request.method == "POST":
        if type(data) != list:
            return "provide an array of hashes"
        else:
            try:
                cursor.execute("""
                    INSERT INTO hashes (hash)
                    VALUES (DECODE(UNNEST(%s), 'hex'))
                    ON CONFLICT (hash)
                    DO UPDATE SET hash = EXCLUDED.hash;
                    """, (data,))
            except pg.errors.UniqueViolation:
                app.logger.debug(f"Hash {data} already exists")
            dbcon.commit()
            dbcon.close()
            cursor.close()
            return json.dumps(data) 

    elif request.method == "GET":
        try:
            cursor.execute("""
                SELECT ENCODE(hash::BYTEA, 'hex') 
                FROM hashes 
                WHERE ENCODE(hash::BYTEA, 'hex') = ANY(%s);
                """, (data,))
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
    


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0")
    