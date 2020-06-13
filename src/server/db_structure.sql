create table if not exists hashes (hash BYTEA primary key);
create index hashdex on hashes (hash);

create table if not exists contacts (number BIGINT primary key);
create index numdex on contacts(number);
