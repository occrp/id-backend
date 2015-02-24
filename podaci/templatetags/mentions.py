from django_jinja import library
import jinja2
import re

mention = re.compile(r"@\[([^@]*)\]\(([\w\d]+):([A-Za-z0-9_-]+)\)")

@library.global_function
def parse_mentions(value):
	return re.sub(mention, "<a href=\"/podaci/\\2/\\3/\">\\1</a>", value)
