PYTHON=pyenv/bin/python
PIP=pyenv/bin/pip
MANAGE=pyenv/bin/python manage.py

web: $(PYTHON) static/bower_components
	$(MANAGE) runserver

$(PYTHON):
	virtualenv pyenv
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

static/bower_components:
	cd static
	bower install

clean:
	rm -rf pyenv
	find ./ -iname '*.pyc' -exec rm -rf '{}' \;
	rm -rf static/bower_components

testdata:
	./manage.py loaddata id/fixtures/* 
	./manage.py loaddata data/fixtures/*
	(cd data/importers/ID1_Import && python UserProfiles_to_DjangoUsers.py ../../exporters/raw/UserProfile.csv)
	(cd data/importers/ID1_Import && python Tickets_to_ID2Tickets.py ../../exporters/raw/Ticket.csv)


