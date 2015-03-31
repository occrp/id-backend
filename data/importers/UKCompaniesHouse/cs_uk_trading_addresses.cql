// ==> cs_uk_trading_addresses.csv <==
// version,_id,tradpost,trad1,trad4,tel,td001,org,tps,trad2,trad3

USING PERIODIC COMMIT 200
LOAD CSV WITH HEADERS FROM "file:%PATH%" as csvLine
MERGE (c:Country {iso:"UK"})
MERGE (company:UKCompany {uk_cs_id: csvLine.org})
CREATE UNIQUE (address:Address {
    addr1: csvLine.trad1,
    addr2: csvLine.trad2,
    addr3: csvLine.trad3,
    addr4: csvLine.trad4,
    postcode: csvline.tradpost,
})
CREATE UNIQUE (company)-[:has_address]->(address)
CREATE UNIQUE (address)-[:is_in]->(c)
CREATE UNIQUE (telephone:PhoneNumber) {
    number: csvLine.tel
})
CREATE (company)-[:has_phonenumber]->(telephone)
;
