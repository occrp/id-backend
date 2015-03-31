# UK Companies House Import

The source was received as a PostgreSQL dump file. 

1. Load dump into PostgreSQL with pgdump_restore
2. Export tables using:
    `COPY <tablename> TO '/data/<tablename>.csv' DELIMITER ',' CSV HEADER;`
3. Run `split_and_insert.sh` for each table, like so:
    `./split_and_insert.sh <tablename>`

