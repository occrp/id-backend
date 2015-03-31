# UK Companies House Import

The source was received as a PostgreSQL dump file. 

1. Load dump into PostgreSQL with pgdump_restore
2. Export tables using:
    `COPY <tablename> TO '/data/<tablename>.csv' DELIMITER ',' CSV HEADER;`
3. Run `cat uk_companies_house_setup.cql | neo4j-shell`
4. Run `split_and_insert.sh` for each table, like so:
    `./split_and_insert.sh <tablename>`

Do the tables in the following order, otherwise things will break:

1. cs_uk_directors
2. cs_uk_companies
3. cs_uk_trading_addresses
4. cs_uk_company_accounts
5. cs_uk_directorships
6. cs_uk_group_structure_ukcomp
7. cs_uk_group_structure_forcomp
