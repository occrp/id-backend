# Exporting from Google Drive and importing into Podaci

Once you [set-up a working environment](../../README.md) and [imports all data from Google AppEngine to the database](../README.md), you can download and import all Google Drive files and folders into Podaci.

The export/import has two phases:
1. export/import Ticket-related files and folders;
2. export/import everything else.

## Requirements

You need `pycrypto` and `google-api-python-client` Python modules:
```
 pip install pycrypto
 pip install --upgrade google-api-python-client
```

They are *not* installed by default in the dockerized environment, as they are not used by any other part of the system.

## Exporting/importing Ticket-related files and folders

The `GDriveToPodaci.py` script handles this part. It uses (old) `investigative-dashboard` credentials, so make sure you have access to (old) `investigative-dashboard` code. Running the script without parameters will output some basic usage info:
```
 $ python GDrive_to_Podaci.py
 
 Run via:
         GDrive_to_Podaci.py </path/to/legacy-investigative-dashboard> <drive-folder-ids-file-path> [--keep]
 
 Temporary files are being saved in:
         /tmp/id_gdrive_downloads/<folder-id>/<individual-filenames>
 
 Optional --keep parameter makes the script not delete the downloaded files after Podaci import
```

**Warning: there is a *lot* of data on Google Drive**. The script deletes each file after successful import to Podaci, so it should need the `/tmp` direcotry to be able to hold all those files, *unless `--keep` is passed*.

However, Podaci keeps the files in the configured directory (see [`settings.py`](../../settings/settings.py), so make sure you have ample amount of free space there.

And yes, it will take *a lot* of time.

Old Google Folder IDs and File IDs are being saved in ElasticSearch database as file metadata, as `legacyGoogleFileId` and `legacyGoogleFileId` fields, respectively. These are being used while downloading the rest of files from Google Drive to make sure that files are not downloaded twice.

## Exporting/importing the rest of files

TODO: TBD