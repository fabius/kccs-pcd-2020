-- table containing the hashed combinations 
CREATE TABLE IF NOT EXISTS hashes (hash BYTEA PRIMARY KEY);
CREATE index hashdex ON hashes(hash);

-- address book 
CREATE TABLE IF NOT EXISTS contacts (number BIGINT PRIMARY KEY, last_interaction_utc TIMESTAMP);
CREATE index numdex ON contacts(number);
