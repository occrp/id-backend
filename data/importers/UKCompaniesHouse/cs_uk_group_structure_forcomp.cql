// ==> cs_uk_group_structure.csv <==
// version,gs002,regnum,safenum,name,holdnum,
// level,org,kfin,ultholdnum
// Here we split the input into two sets:
//   - Companies registered in UK (just link them)
//   - Companies registered elsewhere (need to create them)

// Foreign companies held in UK
USING PERIODIC COMMIT 400
LOAD CSV WITH HEADERS FROM "file:%PATH%" as csvLine
MERGE (holding:UKCompany {uk_cs_id: csvLine.holdnum})
MERGE (ultimateholding:UKCompany {uk_cs_id: csvLine.ultholdnum})
MERGE (country:Country {isocode: csvLine.countrycode})
CREATE UNIQUE (company:Company {
    name:             csvLine.name,
    creditsafe_id:    csvLine.name,
})
SET company :CompaniesHouseData
CREATE (company)-[:registered_in]->(country)
CREATE (holding)-[:owns]->(company)
CREATE (ultimateholding)-[:ultimately_holds]->(company)
;
