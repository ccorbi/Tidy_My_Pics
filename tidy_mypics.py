from __future__ import print_function

import os
import argparse
import shutil
import hashlib
import string
import random
import re


import exifread
from tqdm import tqdm
#from multiprocessing import Pool, Value


def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    """Random string generator.

    Original code from:
    http://stackoverflow.com/questions/2257441/random-string-generation-with-upper-case-letters-and-digits-in-python

    Parameters
    ----------

    size : int
        size of the random string

    chars : array_type
        bag of chars to randomly sample

    Returns
    -------
    str
    a string made from random selection of chars

    """
    return ''.join(random.choice(chars) for _ in range(size))


def rename_dupl_photo(mistery_photo):
    """

    Parameters
    ----------

    Returns
    -------

    """

    extension = os.path.splitext(mistery_photo['filename'])[1]
    dupid = '.' + id_generator() + extension # .jpg

    new_name = mistery_photo['filename'].replace(extension, dupid)

    # just in case, check if there is a collision
    f = os.path.join(mistery_photo['dir'], new_name)
    if os.path.isfile(f):
        new_name = rename_dupl_photo(mistery_photo)

    return new_name

def hashfile(path, blocksize=65536):
    """Hash a file.

    Parameters
    ----------

    Returns
    -------

    """
    afile = open(path, 'rb')
    hasher = hashlib.md5()
    buf = afile.read(blocksize)
    while len(buf) > 0:
        hasher.update(buf)
        buf = afile.read(blocksize)
    afile.close()
    return hasher.hexdigest()


def place_photo_in(mistery_photo, target, mover, verbose=False):
    """

    Parameters
    ----------

    Returns
    -------

    """
    if not os.path.isdir(target):
        os.makedirs(target)

    f = os.path.join(mistery_photo['dir'], mistery_photo['filename'])

    if os.path.isfile(os.path.join(target, mistery_photo['filename'])):
        # is a duplicate? if yes, skip it
        hash_dest = hashfile(os.path.join(target, mistery_photo['filename']))
        hash_source = hashfile(f)
        if hash_dest == hash_source:
            return
        else:
            # if not change name
            mistery_photo['filename'] = rename_dupl_photo(mistery_photo)
            target += mistery_photo['filename']

    mover(f, target )

    return

# It goes for each jpg in the run folder
def folder_format(exif_data, mistery_photo, target_folder, hodgepodge):
    """

    Parameters
    ----------

    Returns
    -------

    """
    if exif_data['year'] is not None:
        # Set target folder to target/year/month/day/
        # keep information of the folder, usefull to quick identification of events
        event = strip_date_info(mistery_photo['parent_folder'])

        target_folder_file = '{0}/{1[year]}/{1[year]}-{1[month]}/{1[year]}-{1[month]}-{1[day]}_{2}/'.format(
            target_folder, exif_data, event)
    else:
        # copy to unclassified folder
        # do not touch folder name
        target_folder_file = '{}/{}/{}'.format(target_folder, hodgepodge, mistery_photo['dir'])


    return target_folder_file


def strip_date_info(parent):
    # these are the date format date I would like to remove
    # tailored for my and my wifes folders
    # customize this for you own mess
    for date_pattern in [r'[A-Z][a-z]{2} \d+, \d+', r'\d+-\d+-\d+', r'\d+-\d+']:
        match = re.search(date_pattern, parent)
        if match:
            parent = parent[:match.start()] + parent[match.end():]

        if parent:
            return parent.lower()
        else:
            return 'anna'



def mock_tqdm(*args, **kwargs):
    """

    Parameters
    ----------

    Returns
    -------

    """
    if args:
        return args[0]
    return kwargs.get('iterable', None)


def tidyup(messy_pictures, target_folder, hodgepodge, **kargs):
    """

    Parameters
    ----------
    messy_pictures : array_type
        list with file path and name info

    target_folder : str
        Main folder to move/copy the files in the data format folders

    hodgepodge : str
        Main folder to move/copy photos missing  EXIF information

    Returns
    -------

    """
    # can i us a decorator for this?
    # and for copy or move?
    if kargs.get('verbose'):
        verbose = True
    else:
        pbar = tqdm(total=len(messy_pictures))
        verbose = False

    # select action .. thinking to refactor to a class
    if kargs.get('how') == 'move':
        mover =  shutil.move
    else:
        mover =  shutil.copy2

    # Loop over items and get features to organize photos
    for mistery_photo in messy_pictures:
        # get features to class, so far this only use shot date
        exif_data = get_EXIF_features(mistery_photo, verbose)
        # write a tidy folder
        target_folder_file = folder_format(exif_data,
                                           mistery_photo,
                                           target_folder,
                                           hodgepodge)
        # user feedback
        if verbose:
            print('{}\n{} -> {}'.format(mistery_photo['filename'],
                                        mistery_photo['dir'],
                                        target_folder_file))
        else:
            pbar.update(1)
        # action
        place_photo_in(mistery_photo, target_folder_file, mover, verbose=verbose)


    if not verbose:
        pbar.close()

    return


def get_EXIF_features(mistery_photo, features='default', verbose=False):
    """ Extract EXIF info from the photo

    Parameters
    ----------
    mistery_photo : str
        path of the target file

    Returns
    -------
    dictionary

    """
    exif_data = dict()

    f = os.path.join(mistery_photo['dir'], mistery_photo['filename'])
    # open in binary mode
    photo = open(f, 'rb')
    # Read  EXIF data
    tags = exifread.process_file(photo, details=False)
    # Extract time

    # Quick&Dirty to extract month
    # NEED TO BE IMPROVED TO SUPORT year
    try:
        timestamp = tags['EXIF DateTimeOriginal'].values
        d, h = timestamp.split()
        exif_data['day'] = d.split(':')[2].strip()
        exif_data['month'] = d.split(':')[1].strip()
        exif_data['year'] = d.split(':')[0].strip()

        exif_data['hour'] = h.split(':')[0].strip()
        exif_data['min'] = h.split(':')[1].strip()
        exif_data['sec'] = h.split(':')[2].strip()

    except:
        # add log
        # configuration file default photos
        if verbose:
            print('error with {}'.format(f))

        exif_data['year'] = None

    return exif_data


def find_photos(source_path, common_extensions=('JPG', 'CR2', 'ORF', 'ARW', 'TIFF', 'DNG'), ignore=[]):
    """Walk the source folder and select potential photos by extension.

    Parameters
    ----------
    source_path : str
        Source path

    Returns
    -------

    """
    # combinedignored = re.compile('|'.join('(?:{0})'.format(x) for x in ignore))
    # use endswith , ignore must be a tuple then
    # if ignore and dirpath.endswith(ignore):
    # for duplication, at the end cll the same funciton

    source_files = list()

    for (dirpath, dirnames, filenames) in os.walk(source_path):
        for f in filenames:
            if f.upper().endswith(common_extensions):
                # source_files.append(os.path.join(dirpath, f))
                parent = os.path.basename(os.path.normpath(dirpath))
                source_files.append({'dir':dirpath,
                                     'filename':f,
                                     'parent_folder':parent})

    return source_files


def get_options():
    """Get arguments from command line.

    Parameters
    ----------

    Returns
    -------

    """
    parser = argparse.ArgumentParser(description="""
    Simple tool to unmess your photos.

    Usage:
    tidy_mypics --source /my/messy/photos/ --target /my/tidy/photos/

    """)

    parser.add_argument('-s', '--source', action="store",
                        dest="source_folder", help='Folder with \
                        the messy collection of photos', required=True)

    parser.add_argument('-t', '--target', action="store",
                        dest="target_folder", help='Folder with \
                        the tidy collection of photos', required=True)

    # Advanced Setup & Optional Arguments
    # ignore multiple and ignore-file
    # behaivour wiht no info, features, copy or move, duplicates
    parser.add_argument('-i', '--ignore_folder', action="store", dest="folders to ignore",
                            help='List of folders to ignore', nargs='+')

    parser.add_argument('-u', '--unclassified', action="store", dest="hodgepodge",
                        default='unclassified', help='Folder to store photos without \
                        valid information to properly classify')

    parser.add_argument('-m', '--how-move', action="store",
                        dest="how", choices=['move', 'copy'], default='copy',
                        help="By default tidy_mypics  just copy the source files to a new location"
                        "using a timestamp folder structure. if you want to move it instead, "
                        "use copy argument")

    parser.add_argument('-v', '--verbose', action="store_true",
                        dest="verbose",
                        help="Print details about what file tidy_mypics are moving or copying")

    options = parser.parse_args()

    return options


def main():

    # Read argtments & defaults values
    opts = get_options()

    # Walk Source folder and detect pictures
    messy_pictures = find_photos(opts.source_folder)
    # unmess the library
    print('Found {} messy photos'.format(len(messy_pictures)))
    tidyup(messy_pictures, **opts.__dict__)


if __name__ == '__main__':
    main()
