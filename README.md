# README

Tidy MyPics is a simple script to sort photos, so far  use  EXIF information to fetch the shot date and base on that copy the photo to a new folder, based on that information  /year/month/day/

## Usage

```bash

  tidy_mypics.py --source /my/messy/files --target /my/tidy/space


    Options:
      -h --help         Show this screen.
      --version         Show version.
      --default_folder  Folder to store files without valid EXIF information
                        (by default: ./Unclassfied)

´´´

## Dependencies

    - [EXIFread](exifread) Package to read Exif information

## ToDO
- Add option to chose to move or copy files
- add option to name folders base on Localization (using GPS info)
- Add control of duplicates, check potential collisions scenarios
- Add more features
- Change EXIF reading packages
- Add option to write info
- ML, tagging ??
