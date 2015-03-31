// ==> cs_uk_directors.csv <==
// version,hns,suf,mname,dob,trp02,pnr,title,ptitle,fname,sname

USING PERIODIC COMMIT 500
LOAD CSV WITH HEADERS FROM "file:%PATH%" as csvLine
CREATE UNIQUE (person:Person {
    dob: csvLine.dob,
    first_name: csvLine.fname,
    middle_names: csvLine.mname,
    last_name: csvLine.sname,
    name_honours: csvLine.hns,
    name_suffix: csvLine.suf,
    title: csvLine.title
})
SET person :LegalPerson:UKPerson:CompaniesHouseData
CREATE (chpnr:CompaniesHousePNR:CompaniesHouseData {
    uk_cs_pnr: csvLine.pnr
})
CREATE (chpnr)-[:is]->(person)
;
