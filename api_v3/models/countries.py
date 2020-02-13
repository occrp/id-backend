from iso3166 import countries

COUNTRIES = (
    ('', '-----------'),
) + tuple([
    (country.alpha2, country.name) for country in countries
])
