CREATE INDEX ON :Country(name);
CREATE INDEX ON :Country(iso);

CREATE INDEX ON :Region(name);
CREATE INDEX ON :WaterBody(name);
CREATE INDEX ON :Area(name);
CREATE INDEX ON :Place(name);
CREATE INDEX ON :Road(name);
CREATE INDEX ON :Location(name);
CREATE INDEX ON :Elevation(name);
CREATE INDEX ON :UnderSea(name);
CREATE INDEX ON :Vegetation(name);

CREATE INDEX ON :Region(asciiname);
CREATE INDEX ON :WaterBody(asciiname);
CREATE INDEX ON :Area(asciiname);
CREATE INDEX ON :Place(asciiname);
CREATE INDEX ON :Road(asciiname);
CREATE INDEX ON :Location(asciiname);
CREATE INDEX ON :Elevation(asciiname);
CREATE INDEX ON :UnderSea(asciiname);
CREATE INDEX ON :Vegetation(asciiname);

CREATE INDEX ON :GeoName(geonameid);
CREATE CONSTRAINT ON (geo:GeoName) ASSERT geo.geonameid IS UNIQUE;

CREATE CONSTRAINT ON (country:Country) ASSERT country.iso IS UNIQUE;

USING PERIODIC COMMIT
LOAD CSV WITH HEADERS FROM "file:/home/id/server/id2/data/importers/GeoNames/output/countries.csv" as csvLine
CREATE (:Country {
	iso: csvLine.iso,
	iso3: csvLine.iso3, 
	isonumeric: csvLine.isonumeric, 
	fips: csvLine.fips, 
	country: csvLine.country, 
	capital: csvLine.capital,
	area: toFloat(csvLine.area), 
	population: toInt(csvLine.population),
	continent: csvLine.continent, 
	tld: csvLine.tld, 
	currencycode: csvLine.currencycode,
	currencyname: csvLine.currencyname, 
	phone: csvLine.phone, 
	postal_code_format: csvLine.postal_code_format, 
	postal_code_regex: csvLine.postal_code_regex,
	languages: csvLine.languages, 
	geonameid: toInt(csvLine.geonameid),
	neighbours: csvLine.neighbours, 
	equivalentfipscode: csvLine.equivalentfipscode,
	source: csvLine.source
});

########################################################
## Regions

USING PERIODIC COMMIT
LOAD CSV WITH HEADERS FROM "file:/home/id/server/id2/data/importers/GeoNames/output/regions.csv" as csvLine
MERGE (country:Country {iso: csvLine.countrycode})
CREATE (region:Region {
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
CREATE (region)-[:is_in]->(country);

########################################################
## Water Bodies

USING PERIODIC COMMIT
LOAD CSV WITH HEADERS FROM "file:/home/id/server/id2/data/importers/GeoNames/output/waterbodies.csv" as csvLine
MERGE (country:Country {iso: csvLine.countrycode})
CREATE (waterbody:WaterBody {
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
CREATE (waterbody)-[:is_in]->(country);


########################################################
## Areas

USING PERIODIC COMMIT
LOAD CSV WITH HEADERS FROM "file:/home/id/server/id2/data/importers/GeoNames/output/areas.csv" as csvLine
MERGE (country:Country {iso: csvLine.countrycode})
CREATE (area:Area {
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
CREATE (area)-[:is_in]->(country)


########################################################
## Places

USING PERIODIC COMMIT
LOAD CSV WITH HEADERS FROM "file:/home/id/server/id2/data/importers/GeoNames/output/places.csv" as csvLine
MERGE (country:Country {iso: csvLine.countrycode})
CREATE (place:Place {
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
CREATE (place)-[:is_in]->(country)
;


########################################################
## Road

USING PERIODIC COMMIT
LOAD CSV WITH HEADERS FROM "file:/home/id/server/id2/data/importers/GeoNames/output/roads.csv" as csvLine
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
CREATE (road)-[:is_in]->(country)



########################################################
## Location

USING PERIODIC COMMIT
LOAD CSV WITH HEADERS FROM "file:/home/id/server/id2/data/importers/GeoNames/output/locations.csv" as csvLine
MERGE (country:Country {iso: csvLine.countrycode})
CREATE (location:Location {
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
CREATE (location)-[:is_in]->(country)



########################################################
## Elevation

USING PERIODIC COMMIT
LOAD CSV WITH HEADERS FROM "file:/home/id/server/id2/data/importers/GeoNames/output/elevation.csv" as csvLine
MERGE (country:Country {iso: csvLine.countrycode})
CREATE (elevation:Elevation {
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
CREATE (elevation)-[:is_in]->(country)


########################################################
## UnderSea

USING PERIODIC COMMIT
LOAD CSV WITH HEADERS FROM "file:/home/id/server/id2/data/importers/GeoNames/output/undersea.csv" as csvLine
MERGE (country:Country {iso: csvLine.countrycode})
CREATE (undersea:UnderSea {
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
CREATE (undersea)-[:is_in]->(country)


########################################################
## Vegetation

USING PERIODIC COMMIT
LOAD CSV WITH HEADERS FROM "file:/home/id/server/id2/data/importers/GeoNames/output/vegetation.csv" as csvLine
MERGE (country:Country {iso: csvLine.countrycode})
CREATE (vegetation:Vegetation {
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
CREATE (vegetation)-[:is_in]->(country)


########################################################
## Alternative Names

USING PERIODIC COMMIT
LOAD CSV WITH HEADERS FROM "file:%PATH%" as csvLine
MERGE (geo:GeoName {geonameid: csvLine.geonameid})
CREATE (alt:AlternativeName {
	name: csvLine.name;
})
CREATE (geo)-[:also_known_as]->(alt)
