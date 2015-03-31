// ==> cs_uk_companies.csv <==
// version,sic07desc,tradpost,sic07,inc,name,aorder,add2,
// trad2,add1,trad1,add4,trad4,trp01,org,add3,trad3,descr,
// rec_status,web,stat,type,volag,dissdate,acc_type,post,
// admin,liq_status,charnum

USING PERIODIC COMMIT 200
LOAD CSV WITH HEADERS FROM "file:%PATH%" as csvLine
MERGE (uk:Country {iso: "UK"})
CREATE (company:LegalPerson:Company:UKCompany:CompaniesHouseData {
    name: csvLine.name,
    incorporation_date: csvLine.inc,
    dissolution_date: csvLine.dissdate,
    is_liquidated: csvLine.liq_status,
    in_receivership: csvLine.rec_status,

    uk_cs_id: csvLine.org,
})
CREATE UNIQUE (sic07:SIC07:CompaniesHouseData {
    sic07code: csvLine.sic07,
    description: csvLine.sic07code
})
CREATE UNIQUE (regaddress:Address {
    addr1: csvLine.trad1,
    addr2: csvLine.trad2,
    addr3: csvLine.trad3,
    addr4: csvLine.trad4,
    postcode: csvline.tradpost
})
SET regaddress :CompaniesHouseData
CREATE UNIQUE (mainaddress:Address {
    addr1: csvLine.trad1,
    addr2: csvLine.trad2,
    addr3: csvLine.trad3,
    addr4: csvLine.trad4,
    postcode: csvline.tradpost
})
SET mainaddress :CompaniesHouseData
CREATE (company)-[:registered_in]->(country)
CREATE (company)-[:registered_at]->(regaddress)
CREATE UNIQUE (company)-[:has_address]->(mainaddress)
CREATE UNIQUE (company)-[:main_address]->(mainaddress)
CREATE (company)-[:sic07code]->(sic07)
CREATE (company)-[:website]->(Website: {
    url: csvLine.web,
})
;
