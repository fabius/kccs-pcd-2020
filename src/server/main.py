import psycopg2 as pg
import os, json, time
from flask import Flask, jsonify, request, abort, Response, make_response

try:
    HASH_DB_HOST     = os.environ["HASH_DB_HOST"]
    HASH_DB_PORT     = os.environ["HASH_DB_PORT"]
    HASH_DB_NAME     = os.environ["HASH_DB_NAME"]
    HASH_DB_USERNAME = os.environ["HASH_DB_USERNAME"]
    HASH_DB_PASSWORD = os.environ["HASH_DB_PASSWORD"]
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
        host     = HASH_DB_HOST,
        port     = HASH_DB_PORT,
        dbname   = HASH_DB_NAME,
        user     = HASH_DB_USERNAME,
        password = HASH_DB_PASSWORD)
    cursor = dbcon.cursor()

    data = json.loads(request.data)
    app.logger.debug(f"request data: {data}")

    if request.method == "POST":
        if type(data) != str:
            return "provide a single hash"
        else:
            try:
                cursor.execute("""
                    INSERT INTO hashes (hash)
                    VALUES (DECODE(%s, 'hex'));
                    """, [data])
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
        print(status_code)
        return json.dumps(intersection)
    


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
    