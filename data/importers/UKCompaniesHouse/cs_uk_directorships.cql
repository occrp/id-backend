// ==> cs_uk_directorships.csv <==
// version,poscode,resdate_str,func,pnr,trp03,org,
// funcode,pos,sec,active,resdate,appdate,id
USING PERIODIC COMMIT 200
LOAD CSV WITH HEADERS FROM "file:%PATH%" as csvLine
MERGE (company:UKCompany {uk_cs_id: csvLine.org})
MERGE (person:UKPerson {uk_cs_pnr: csvLine.pnr})
CREATE (person)-[:director_of {
        date_appointed:     csvLine.appdate,
        date_resigned:      csvLine.resdate,
        function:           csvLine.func,
        position:           csvLine.pos
    }]->(company)
;
