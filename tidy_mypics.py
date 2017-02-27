from __future__ import print_function

import os
import argparse
import shutil
import hashlib
import string
import random


import exifread
from tqdm import tqdm
#from multiprocessing import Pool, Value

def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    """Random string generator.

    from: http://stackoverflow.com/questions/2257441/random-string-generation-with-upper-case-letters-and-digits-in-python

    Parameters
    ----------

    Returns
    -------

    """
    return ''.join(random.choice(chars) for _ in range(size))


def rename_dupl_photo(loc_file_info):

    extension = os.path.splitext(loc_file_info[1])[1]
    dupid = '.' + id_generator() + extension

    new_name = loc_file_info[1].replace(extension, dupid)

    # just in case, check if there is a collision
    f = os.path.join(loc_file_info[0], new_name)
    if os.path.isfile(f):
        new_name = rename_dupl_photo(loc_file_info)

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


def place_photo_in(loc_file_info, target, verbose=False, how='copy', **kargs):

    if not os.path.isdir(target):
        os.makedirs(target)

    f = os.path.join(loc_file_info[0], loc_file_info[1])

    if os.path.isfile(os.path.join(target, loc_file_info[1])):
        # is a duplicate? if yes, skip
        hash_dest = hashfile(os.path.join(target, loc_file_info[1]))
        hash_source = hashfile(f)
        if hash_dest== hash_source:
            return
        else:
            # change name
            loc_file_info[1] = rename_dupl_photo(loc_file_info)
            pass


    if verbose:
        print('{} -> {}'.format(f, target))

    if how=='move':
        mover =  shutil.move
    else:
        mover =  shutil.copy2

    mover(f, target)
    return

# It goes for each jpg in the run folder


def mock_tqdm(*args, **kwargs):
    if args:
        return args[0]
    return kwargs.get('iterable', None)


def tidyup(messy_pictures, target_folder, hodgepodge, **kargs):

    # can i us a decorator for this?
    # and for copy or move?
    if kargs.get('verbose'):
        verbose = True
    else:
        pbar = tqdm(total=len(messy_pictures))
        verbose = False

    # Feed featrues to org photos
    for mistery_photo in messy_pictures:
        # get features to class, so far this only use shot date
        exif_data = get_EXIF_features(mistery_photo, verbose)

        if exif_data['year'] is not None:
            # Set target folder to target/year/month/day/
            target_folder_file = '{0}/{1[year]}/{1[year]}-{1[month]}/{1[year]}-{1[month]}-{1[day]}/'.format(
                target_folder, exif_data)
        else:
            # copy to unclassfied folder
            target_folder_file = '{}/{}'.format(hodgepodge, mistery_photo[0])

        if verbose:
            place_photo_in(mistery_photo, target_folder_file, verbose=True, **kargs)
        else:
            pbar.update(1)
            place_photo_in(mistery_photo, target_folder_file, **kargs)

    if not verbose:
        pbar.close()

    return


def get_EXIF_features(loc_file_info, features='default', verbose=False):

    exif_data = dict()

    f = os.path.join(loc_file_info[0], loc_file_info[1])
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


def find_photos(source_path, common_extensions=('JPG', 'CR2', 'ORF', 'ARW', 'TIFF'), ignore=[]):
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
                source_files.append([dirpath, f])

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

    Usage Demultiplexation:
    %prog --source /my/messy/photos/ --target /my/tidy/photos/

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

    parser.add_argument('-u', '--unclassfied', action="store", dest="hodgepodge",
                        default='Unclassfied', help='Folder to store photos without \
                        valid information to properlly classify')

    parser.add_argument('-m', '--how-move', action="store",
                        dest="how", choices=['move', 'copy'], default='dump',
                        help="By default %prog  just copy the source files to a new location"
                        "using a timestamp folder struture. if you want to move it insted, "
                        "use copy argument")

    parser.add_argument('-v', '--verbose', action="store_true",
                        dest="verbose",
                        help="Print details about what file %prog are moving or copying")

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
