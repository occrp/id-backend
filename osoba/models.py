from neo4django.db import models

#### 
#
#  The OCCRP graph ontology
#
#
####

class OsobaObject(models.NodeModel):
    """A base object that most models will inherit from"""
    podaci_refs = models.StringArrayProperty()
    source = models.StringProperty()

class LegalPersonObject(OsobaObject):
    """Any legal person. Not to be used directly; is parent for Person and Company"""
    companies_owned = models.Relationship('Company', rel_type='owns')
    land_owned = models.Relationship('Land', rel_type='owns')
    property_owned = models.Relationship('Property', rel_type='owns')
    boats_owned = models.Relationship('Boat', rel_type='owns')
    planes_owned = models.Relationship('Plane', rel_type='owns')
    cars_owned = models.Relationship('Car', rel_type='owns')
    brands_owned = models.Relationship('Brand', rel_type='owns')
    lawsuits = models.Relationship('Person', rel_type='party_to')
    emails = models.Relationship('EmailAddress', rel_type='has_address')
    phones = models.Relationship('PhoneNumber', rel_type='has_phoneno')


class Person(LegalPersonObject):
    """A human."""
    name = models.StringProperty()
    dob = models.DateProperty()

    nationality = models.Relationship('Country', rel_type='is_national_of')
    residency = models.Relationship('Country', rel_type='is_resident_of')

    knows = models.Relationship('Person', rel_type='knows')
    colleagues = models.Relationship('Person', rel_type='works_with')
    family = models.Relationship('Person', rel_type='related_to')

    jobs = models.Relationship('Company', rel_type='works_for')
    organizations = models.Relationship('Organization', rel_type='member_of')
    emails = models.Relationship('EmailAddress', rel_type='has_address')
    phones = models.Relationship('PhoneNumber', rel_type='has_phoneno')

class SupernationalEntity(OsobaObject):
    """A supernational entity, like EU, NATO or ASEAN"""
    name = models.StringProperty()

class Language(models.NodeModel):
    names = models.StringArrayProperty()
    iso = models.StringProperty()

class Country(OsobaObject):
    """A single country."""
    geonameid = models.StringProperty()
    name = models.StringProperty()
    iso = models.StringProperty()
    iso3 = models.StringProperty()
    isonumeric = models.StringProperty()
    fips = models.StringProperty()
    country = models.StringProperty()
    capital = models.StringProperty()
    area = models.FloatProperty()
    population = models.IntegerProperty()
    continent = models.StringProperty()
    tld = models.StringProperty()
    currencycode = models.StringProperty()
    currencyname = models.StringProperty()
    phone = models.StringProperty()
    postal_code_format = models.StringProperty()
    postal_code_regex = models.StringProperty()
    equivalentfipscode = models.StringProperty()

    languages = models.Relationship('Language', rel_type='language_spoken')
    neighbours = models.Relationship('Country', rel_type='borders')
    international_orgs = models.Relationship('SupernationalEntity', rel_type='member_of')
    wars = models.Relationship('Country', rel_type='at_war_with')

class GeonameObject(OsobaObject):
    """All Geoname objects inherity from this class."""
    source = models.StringProperty()

    geonameid = models.StringProperty()
    name = models.StringProperty()
    asciiname = models.StringProperty()
    latitude = models.StringProperty()
    longitude = models.StringProperty()
    featurecode = models.StringProperty()
    admin1code = models.StringProperty()
    admin2code = models.StringProperty()
    admin3code = models.StringProperty()
    admin4code = models.StringProperty()
    population = models.FloatProperty()
    elevation = models.FloatProperty()
    dem = models.StringProperty()
    timezone = models.StringProperty()
    modification_date = models.DateTimeProperty()

    countrycode = models.Relationship('Country', rel_type='is_in')
    alternatenames = models.Relationship('AlternativeName', rel_type='also_known_as')

class AlternativeName(models.NodeModel):
    """Alternative names for places, as per Geoname"""
    source = models.StringProperty()
    name = models.StringProperty()
    alternateNameId = models.IntegerProperty()  # the id of this alternate name, int
    isolanguage = models.Relationship('Language', rel_type='in_language') # iso 639 language code 2- or 3-characters; 4-characters 'post' for postal codes and 'iata','icao' and faac for airport codes, fr_1793 for French Revolution names,  abbr for abbreviation, link for a website, varchar(7)
    isPreferred  = models.BooleanProperty() # '1', if this alternate name is an official/preferred name
    isShort      = models.BooleanProperty() # '1', if this is a short name like 'California' for 'State of California'
    isColloquial = models.BooleanProperty() # '1', if this alternate name is a colloquial or slang term
    isHistoric   = models.BooleanProperty() # '1', if this alternate name is historic and was used in the past

class City(GeonameObject):
    pass

class Region(GeonameObject):
    pass

class WaterBody(GeonameObject):
    pass

class Area(GeonameObject):
    pass

class Place(GeonameObject):
    pass

class Road(GeonameObject):
    pass

class Location(GeonameObject):
    pass

class Elevation(GeonameObject):
    pass

class UnderSea(GeonameObject):
    pass

class Vegetation(GeonameObject):
    pass

class Address(OsobaObject):
    line1 = models.StringProperty()
    line2 = models.StringProperty()
    line3 = models.StringProperty()
    line4 = models.StringProperty()
    city = models.Relationship('City', rel_type='is_in')
    state = models.Relationship('Place', rel_type='is_in')
    postcode = models.StringProperty()


class Company(LegalPersonObject):
    name = models.StringProperty()
    incorporation_date = models.DateProperty()
    dissolution_date = models.DateProperty()    
    is_liquidated: models.BooleanProperty(),
    in_receivership: models.BooleanProperty(),

class Organization(OsobaObject):
    name = models.StringProperty()
    emails = models.Relationship('EmailAddress', rel_type='has_address')
    phones = models.Relationship('PhoneNumber', rel_type='has_phoneno')

class Brand(OsobaObject):
    name = models.StringProperty()

class Building(OsobaObject):
    address = models.Relationship('Address', rel_type='has_address')

class Property(OsobaObject):
    value = models.IntegerProperty()
    currency = models.StringProperty()

class Vehicle(Property):
    type = models.StringProperty()
    registration = models.StringProperty()
    color = models.StringProperty()

class Car(Vehicle):
    subtype = models.StringProperty()

class Plane(Vehicle):
    name = models.StringProperty()

class Boat(Vehicle):
    name = models.StringProperty()

class Land(OsobaObject):
    location = models.StringProperty()
    parcel_id = models.StringProperty()
    assessment_year = models.IntegerProperty()
    land_purpose = models.StringProperty()
    land_size = models.FloatProperty()  # Square meters

class Lawsuit(OsobaObject):
    pass

class Contract(OsobaObject):
    pass

class Tender(OsobaObject):
    number = models.StringProperty()
    value = models.IntegerProperty()
    currency = models.StringProperty()

class Auction(OsobaObject):
    number = modles.StringProperty()
    starting_bid = models.IntegerProperty()
    currency = models.StringProperty()

class Trinket(OsobaObject):
    description = models.StringProperty()

class Event(OsobaObject):
    start_date = models.DateTimeProperty()
    end_date = models.DateTimeProperty()
    location = models.StringProperty()		# ??

    description = models.StringProperty()

    attendees = models.Relationship('Person', rel_type='attended')

class PhoneNumber(OsobaObject):
    number = models.StringProperty()

class EmailAddress(OsobaObject):
    address = models.StringProperty()


# class CompanyAccount
# date
# accounts_format
# tangible_assets
# netwrth
# stock
# number_of_months
# taxation
# increase_in_cash
# sundry_reserves
# pl_accout_reserves
# trade_debtors
# trade_creditors
# liabilities_contingent
# liabilities_current
# liabilities_long_term
# liabilities_misc_current
# liabilities_total
# assets_current
# assets_fixed_total
# assets_intangible
# assets_other_current
# assets_net
# assets_total
# profits_gross
# profits_before_tax
# profits_after_tax
# profits_operating
# profits_retained
# loans_long_term
# loans_short_term
# bank_overdraft
# bank_overdraft_and_long_term_loans
# director_emoluments
# cashflow_net_from_financing
# cashflow_net_before_financing
# capital_employed
# assets_total_current
# cost_of_sales
# working_capital
# interest_payments
# exports
# currency
# depreciation
# employees_number
# accounts_type
# accounts_format
# accounts_status
# revaluation_reserve
# paid_up_equity
# turnover
# wages
# dividends_payable
# operations_net_cashflow
# consolidated_accounts
# shareholder_funds
# audit_fee


# Property, StringProperty, EmailProperty, URLProperty,
# IntegerProperty, DateProperty, DateTimeProperty,
# ArrayProperty, StringArrayProperty, IntArrayProperty,
# URLArrayProperty, AutoProperty, BooleanProperty