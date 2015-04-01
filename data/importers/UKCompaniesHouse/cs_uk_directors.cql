// ==> cs_uk_directors.csv <==
// version,hns,suf,mname,dob,trp02,pnr,title,ptitle,fname,sname

USING PERIODIC COMMIT 1500
LOAD CSV WITH HEADERS FROM "file:%PATH%" as csvLine
MERGE (person:Person {
    dob: csvLine.dob,
    first_name: csvLine.fname,
    middle_names: csvLine.mname,
    last_name: csvLine.sname
})
ON CREATE SET 
    person.name_honours = csvLine.hns,
    person.name_suffix = csvLine.suf,
    person.title = csvLine.title,
    person :LegalPerson:UKPerson:CompaniesHouseData
ON MATCH SET person :LegalPerson:UKPerson:CompaniesHouseData
CREATE (chpnr:CompaniesHousePNR:CompaniesHouseData {
    uk_cs_pnr: csvLine.pnr
})-[:is]->(person)
;
