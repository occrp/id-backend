from neo4django.db import models

class OsobaObject(models.NodeModel):
    podaci_refs = models.StringArrayProperty()

class Person(OsobaObject):
    name = models.StringProperty()
    dob = models.DateProperty()
    nationality = models.StringArrayProperty()

    companies_owned = models.Relationship('Company', rel_type='owns')
    jobs = models.Relationship('Company', rel_type='works_for')
    organizations = models.Relationship('Organization', rel_type='member_of')
    emails = models.Relationship('EmailAddress', rel_type='has_address')
    phones = models.Relationship('PhoneNumber', rel_type='has_phoneno')

class SupernationalEntity(OsobaObject):
    name = models.StringProperty()

class Country(OsobaObject):
    name = models.StringProperty()

    international_orgs = models.Relationship('SupernationalEntity', rel_type='member_of')

class Company(OsobaObject):
    name = models.StringProperty()
    emails = models.Relationship('EmailAddress', rel_type='has_address')
    phones = models.Relationship('PhoneNumber', rel_type='has_phoneno')

class Organization(OsobaObject):
    name = models.StringProperty()
    emails = models.Relationship('EmailAddress', rel_type='has_address')
    phones = models.Relationship('PhoneNumber', rel_type='has_phoneno')

class Brand(OsobaObject):
    name = models.StringProperty()

class Building(OsobaObject):
    address = models.StringProperty()

class Property(OsobaObject):
    value = models.IntegerProperty()
    currency = models.StringProperty()

class Vehicle(Property):
    type = models.StringProperty()
    registration = models.StringProperty()
    color = models.StringProperty()

class Car(Vehicle):
    subtype = models.StringProperty()

class Plane(OsobaObject):
    pass

class Boat(OsobaObject):
    pass

class Land(OsobaObject):
    pass

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
    pass

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


# Property, StringProperty, EmailProperty, URLProperty,
#                         IntegerProperty, DateProperty, DateTimeProperty,
#                         ArrayProperty, StringArrayProperty, IntArrayProperty,
#                         URLArrayProperty, AutoProperty, BooleanProperty
#
#    friends = models.Relationship('self',rel_type='friends_with')
