// ==> cs_uk_group_structure.csv <==
// version,gs002,regnum,safenum,name,holdnum,
// level,org,kfin,ultholdnum
// Here we split the input into two sets:
//   - Companies registered in UK (just link them)
//   - Companies registered elsewhere (need to create them)

// UK companies held in UK
USING PERIODIC COMMIT 400
LOAD CSV WITH HEADERS FROM "file:%PATH%" as csvLine
MERGE (company:UKCompany {uk_cs_id: csvLine.org})
MERGE (holding:UKCompany {uk_cs_id: csvLine.holdnum})
MERGE (ultimateholding:UKCompany {uk_cs_id: csvLine.ultholdnum})
SET company.creditsafe_id = csvLine.safenum
CREATE (holding)-[:owns]->(company)
CREATE (ultimateholding)-[:ultimately_holds]->(company)
;
