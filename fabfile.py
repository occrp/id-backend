import os
import time
# import requests
from fabric.api import run, env, cd, settings
from fabric.api import parallel, put


DEPLOY_DIR = '/srv/tools/id'
# to use deploy keys, this is a configured connection in
# /root/.ssh/config on the servers:
REPO_URL = 'git@id2-deploy:occrp/investigative-dashboard-2.git'
# see: https://stackoverflow.com/questions/4565700

env.user = "root"
env.key_filename = os.environ.get("OCCRP_KEY_FILE")


def staging():
    env.hosts = ['woodward.occrp.org']


def production():
    env.hosts = ['pine.occrp.org']


def deploy():
    checkout()
    with cd(DEPLOY_DIR):
        run("docker-compose build")
        run("docker-compose stop")
        run("docker-compose rm -f")
        run("docker-compose up -d postgres")
        # let postgres boot
        time.sleep(5)
        run("docker-compose run --rm web python manage.py migrate --noinput")
        # run("docker-compose run --rm web python manage.py collectstatic")
        run("docker-compose up -d web")


@parallel
def checkout():
    with settings(warn_only=True):
        if run("test -d %s" % DEPLOY_DIR).failed:
            run("git clone -q %s %s" % (REPO_URL, DEPLOY_DIR))
    with cd(DEPLOY_DIR):
        run("git reset --hard HEAD")
        run("git pull -q")
    put("%s.env" % env.hosts[0],
        "%s/id.env" % DEPLOY_DIR)
