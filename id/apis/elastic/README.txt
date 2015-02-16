


SERVER SETUP: INSTALLATION

install java:
 apt-get install openjdk-6-jre openjdk-7-jre

 download .deb from http://www.elasticsearch.org/download/ and install

 copy in config files from the repo, to /etc/elasticsearch
  [htey may be in /opt/elasticsearch if you installed without the .deb]
 
 set up ec2 autodiscovery

 start elasticsearch:
   service elasticsearch start

 check elasticsearch is running:

$ curl http://localhost:9200/
{
  "ok" : true,
  "status" : 200,
  "name" : "Frost, Cordelia",
  "version" : {
    "number" : "0.90.5",
    "build_hash" : "c8714e8e0620b62638f660f6144831792b9dedee",
    "build_timestamp" : "2013-09-17T12:50:20Z",
    "build_snapshot" : false,
    "lucene_version" : "4.4"
  },
  "tagline" : "You Know, for Search"

 - install EC2 discovery plugin
 # cd /usr/share/elasticsearch
 # bin/plugin -install elasticsearch/elasticsearch-cloud-aws/1.15.0bin/plugin -install elasticsearch/elasticsearch-cloud-aws/1.15.0

 # 


Elastic search


SERVER SETUP: RUNNING
I have not yet automated/packaged the server setup.
So to configure (or even to deal with a reboot) you will need to:
 - start elasticsearch
     /opt/elasticsearch/bin/elasticsearch -f
   [-f to run in foreground, useful for debugging]
 - start the tika server (text contents)
   java -jar /opt/elasticsearch/lib/tika-app-1.4.jar -t --server 8010
 - start the tika server (metadata as json)
   java -jar /opt/elasticsearch/lib/tika-app-1.4.jar -j --server 8011


INGEST PROCESS
--------------

To ingest data, you need to use a function in the walklisting.py module
in this directory, e.g., via the Python REPL. This function is:

  recursive_upload(baseurl, tags, index, logfn, sample=None, **kwargs)

  where:

    baseurl: the URL to the documents, http://datatracker.org/something/etc
    tags: ?
    index: ?
    logfn: the filename of a logfile; '/dev/null', '/dev/stdout' etc
    sample: ?
    kwargs: ?



