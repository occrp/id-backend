from neo4django.db import models

class OsobaObject(models.NodeModel):
    podaci_refs = models.StringArrayProperty()

class Person(OsobaObject):
    name = models.StringProperty()
    dob = models.DateProperty()
    nationality = models.StringArrayProperty()

    companies = models.Relationship('Company', rel_type='owns')
    organizations = models.Relationship('Organization', rel_type='member_of')

class Company(OsobaObject):
    name = models.StringProperty()

class Brand(OsobaObject):
    name = models.StringProperty()

class Organization(OsobaObject):
    name = models.StringProperty()

class Government(OsobaObject):
    name = models.StringProperty()

class Building(OsobaObject):
    address = models.StringProperty()

class Property(OsobaObject):
    value = models.IntegerProperty()

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

class Trinket(OsobaObject):
    pass

class Event(OsobaObject):
    start_date = models.DateTimeProperty()
    end_date = models.DateTimeProperty()
    location = models.StringProperty()		# ??

    description = models.StringProperty()

    attendees = models.Relationship('Person', rel_type='attended')


# Property, StringProperty, EmailProperty, URLProperty,
#                         IntegerProperty, DateProperty, DateTimeProperty,
#                         ArrayProperty, StringArrayProperty, IntArrayProperty,
#                         URLArrayProperty, AutoProperty, BooleanProperty
#
#    friends = models.Relationship('self',rel_type='friends_with')
