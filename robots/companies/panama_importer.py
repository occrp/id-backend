from robots.robotbase import RobotPodaciConsumerBase
from robots.mixins import HTMLReaderMixin


class PanamaImporter(RobotPodaciConsumerBase, HTMLReaderMixin):
        MIME_FILTER = "text/html"
        META_FILTER = { 
		"is_indexed": False,
		"is_entity_extracted": False,
		"extra": { "dataset": "Panama Corporate Registry" }
	}

	def extract_data(self):
		pass

	def extract_entities(self):
		pass



