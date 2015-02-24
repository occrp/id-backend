#!/usr/bin/python
import sys
import os

from id.apis.podaci import *
from id.apis.osoba import *

import logging


class RobotBase:
	# Our basic robot, that establishes connections to Podaci 
	# and Osoba, and knows that there are such a thing as jobs
	# that need to be done.
	NAME = "Base Robot"	# The name of the robot
	VERSION = "0.0.0"	# Version number of the robot
	ROBOT_ID = "robot_0"	# Actions taken on Podaci or Osoba will be tagged to this ID

	def __init__(self):
		self.username = self.ROBOT_ID
		self.id = self.ROBOT_ID

		self.fs = FileSystem(user=self)
		self.poi = POIGraph(user=self)

	def log(self):
		raise NotImplementedError

	def run(self):
		while item = self.get_next_batch_item():
			self.process(item)

	def get_next_batch_item(self):	
		raise NotImplementedError

	def process(self, item):
		raise NotImplementedError



class RobotPodaciConsumerBase(RobotBase):
	# A base type of robot that finds a set of documents in Podaci
	# and does something exciting with them.
	MIME_FILTER = None
	META_FILTER = { "is_indexed": False, "is_entity_extracted": False }
	
	def get_next_batch_item(self):
		query = {} # FIXME
		self.fs.search(query)

class RobotOsobaConsumerBase(RobotBase):
	# A base type of robot that finds a set of nodes in Osoba and
	# does something exciting with them.
	pass

