USING PERIODIC COMMIT
LOAD CSV WITH HEADERS FROM "file:%PATH%" as csvLine
MERGE (country:Country {iso: csvLine.countrycode})
CREATE (road:Road {
	geonameid: csvLine.geonameid, 
	name: csvLine.name, 
	asciiname: csvLine.asciiname, 
	latitude: toFloat(csvLine.latitude), 
	longitude: toFloat(csvLine.longitude), 
	featureclass: csvLine.featureclass, 
	featurecode: csvLine.featurecode, 
	cc2: csvLine.cc2, 
	admin1code: csvLine.admin1code, 
	admin2code: csvLine.admin2code, 
	admin3code: csvLine.admin3code, 
	admin4code: csvLine.admin4code, 
	population: toInt(csvLine.population), 
	elevation: toFloat(csvLine.elevation), 
	dem: csvLine.dem, 
	timezone: csvLine.timezone, 
	modification_date: csvLine.modification_date,
	source: csvLine.source
})
CREATE (road)-[:is_in]->(country);
