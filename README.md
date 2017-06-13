# README

Tidy MyPics is a simple script to sort my wife photos base on EXIF information to put files in a date format folder structure /year/month/day/

## Usage

```bash

Usage:
  tidy_mypics.py --source /my/messy/files --target /my/tidy/space


  -h, --help            show this help message and exit
  -s SOURCE_FOLDER, --source SOURCE_FOLDER
                        Folder with the messy collection of photos
  -t TARGET_FOLDER, --target TARGET_FOLDER
                        Folder with the tidy collection of photos
  -i FOLDERS TO IGNORE [FOLDERS TO IGNORE ...], --ignore_folder FOLDERS TO IGNORE [FOLDERS TO IGNORE ...]
                        List of folders to ignore
  -u HODGEPODGE, --unclassified HODGEPODGE
                        Folder to store photos without valid information to
                        properly classify
  -m {move, copy}, --how-move {move, copy}
                        By default tidy_mypics just copy the source files to a
                        new location using a timestamp folder structure. if you
                        want to move it instead, use copy argument
  -v, --verbose         Print details about what file tidy_mypics are moving
                        or copying


```

## Dependencies
    - python 2.7
    - [EXIFread](https://pypi.python.org/pypi/ExifRead) Package to read Exif information

## ToDO
- Extract alternative information from file date creation?
- add option to name folders base on Localization (using GPS info)
- Add control of duplicates, check potential collisions scenarios
- Add more features
- Change EXIF reading packages
- Add option to write info
- ML, tagging ??
