# Google AppEngine Data Export and Import

To get data from Google AppEngine to our own database, we need a couple of things:
 1. a working investigative-dashboard-2 django app
 2. old investigative dashboard sources
 3. Google AppEngine Python SDK

## Requirements

Old Investigative Dashboard sources:
```
 git clone https://github.com/occrp/investigative-dashboard.git
```

Google AppEngine Python SDK:
 1. go to https://cloud.google.com/appengine/downloads
 2. download "Google AppEngine SDK for Python"
 3. unzip it to a folder (we'll assume `google_appengine` in the directory where `id` and `id2` sources landed)

*Warning: Google App Engine currently contains [a bug](https://code.google.com/p/googleappengine/issues/detail?id=12214) that makes it unusable with our script*. It is adviseable to use an older version of Google App Engine.

Investigative Dashboard 2 sources:
```
 git clone https://github.com/occrp/investigative-dashboard-2.git
```

Now, make sure the database and Django app are in a working state:
```
 cd investigative-dashboard-2
 ./manage.py syncdb
```

You're ready to go.

## Export/Import

Exporting the data, and then importing them into our own database consists of a few steps:
 1. export data as CSV from Google AppEngine
 2. import UserProfile data
 3. import Ticket data
 4. import TicketUpdates data
 5. import TicketCharges data

And yes, we do have nice scripts for everything.

### Export

Assuming you're in the `investigative-dashboard-2` code directory:
```
 cd data/exporters
```

The `bigtable-export.sh` script will tell you how to run it if you run it:
```
 ./bigtable-export.sh 
 
 Please identify the source environment (either `--prod`, or `--dev`) as the first argument.

 Usage:
   ./bigtable-export.sh (--prod|--dev) <path-to-old-investigative-dashboard-source> <path-to-google-app-engine-sdk> <output-directory>
```

So, to export the development version data make sure you have Google AppEngine login credentials handy, and run:
```
 ./bigtable-export.sh --dev ../../../investigative-dashboard ../../../google_appengine ../../../exported-data
```

For production data change `--dev` to `--prod` in the above example. Either way, you should land up with several CSV files in the `exported-data` directory.

### Import

Once you have the data in the `/exported-data/` directory, time to import them. Assuming you start with a clean slate (i.e. the Django environment is not yet set-up), you will first have to run:
```
 cd ../../ # to get back to the investigative-dashboard-2 code directory root
 ./manage.py syncdb
```

This will setu-up the Django database and system, as required by import scripts. The scripts are located in `data/importers` subdirectory of the `investigative-dashboard-2` code directory:
```
 cd data/importers/ID1_Import/
```

First, we need to import UserProfile data:
```
 python UserProfiles_to_DjangoUsers.py ../../../../exported-data/UserProfile.csv
```

Next, Ticket data:
```
 python Tickets_to_ID2Tickets.py ../../../../exported-data/Ticket.csv
```

Then, TicketUpdates data:
```
 python TicketUpdates_to_ID2TicketUpdates.py ../../../../exported-data/TicketUpdate.csv
```

Finally, TicketCharges data:
```
 python TicketCharges_to_ID2TicketCharges.py ../../../../exported-data/TicketCharge.csv
```

If everything goes well (it should), you will have UserProfile, Ticket and TicketUpdate data in the database, and (depending on imported data) a couple of new files in the `exported-data` directory. These are [pickled](https://docs.python.org/2/library/pickle.html)) Python data structures (dicts or lists).

The files are:
 - `UserProfile.gkeys`/`Ticket.gkeys` - map old Google AppEngine ids to emails (in case of UserProfile) or new database ids (in case of Ticket), and are needed by the import scripts themselves;
 - `UserProfile.missing`/`Ticket.missing` - these contain old Google AppEngine ids that were references in other imported data sets that could be found in the data (i.e. Ticket ids referenced in TicketUpdate data, but not present in Ticket export data, etc); **important**: data items that reference missing IDs (i.e. a TicketUpdate that references a missing Ticket) *are dropped upon import*, please review missing IDs and items referencing them after the import in original `CSV` data files;
 - `Ticket.drivefolderids` - map Google Drive folder ids to imported Ticket ids in the database, for further reference and use with Podaci file import scripts.
 
Once everything is imported, you can safely move to [importing Google Drive files into Podaci](GDriveToPodaci/README.md)
