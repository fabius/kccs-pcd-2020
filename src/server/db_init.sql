-- table containing the hashed combinations 
CREATE TABLE IF NOT EXISTS hashes (hash BYTEA PRIMARY KEY, secret BYTEA);
CREATE index hashdex ON hashes(hash);