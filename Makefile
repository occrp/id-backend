PYTHON=`pwd`/pyenv/bin/python
PIP=`pwd`/pyenv/bin/pip
MANAGE=`pwd`/pyenv/bin/python manage.py


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
	$(MANAGE) loaddata accounts/fixtures/*
	$(MANAGE) loaddata data/fixtures/*
	(cd data/importers/ID1_Import && $(PYTHON) UserProfiles_to_DjangoUsers.py ../../exporters/raw/UserProfile.csv)
	(cd data/importers/ID1_Import && $(PYTHON) Tickets_to_ID2Tickets.py ../../exporters/raw/Ticket.csv)


