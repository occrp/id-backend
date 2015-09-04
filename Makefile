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
