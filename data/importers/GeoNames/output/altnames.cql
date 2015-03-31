USING PERIODIC COMMIT
LOAD CSV WITH HEADERS FROM "file:%PATH%" as csvLine
MERGE (geo:GeoName {geonameid: csvLine.geonameid})
CREATE (alt:AlternativeName {
	name: csvLine.name,
        source: "GeoNames"
})
CREATE (geo)-[:also_known_as]->(alt)
;

