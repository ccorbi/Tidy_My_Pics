from __future__ import print_function

import os
import argparse
import shutil
import hashlib
import exifread
from tqdm import tqdm


def hashfile(path, blocksize = 65536):
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

def moveit(f, target, verbose=False):
    """Get the name of the photo and the month that was taken and move it.

    """
    # Check if the folder exists, if not, it make it

    if not os.path.isdir(target):
        os.makedirs(target)
    if verbose:
        print('Move {} to {}'.format(f, target))
    shutil.move(f, target)
    return


def copyit(f, target, verbose=False):

    if not os.path.isdir(target):
        os.makedirs(target)
    if verbose:
        print('Copy {} to {}'.format(f, target))
    shutil.copy2(f, target)
    return

# It goes for each jpg in the run folder

def mock_tqdm(*args, **kwargs):
    if args:
        return args[0]
    return kwargs.get('iterable', None)

def tidyup(messy_pictures, target_folder, default_folder, **kargs):

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

        if exif_data['year'] != None:
            # Set target folder to target/year/month/day/
            target_folder_file = '{0}/{1[year]}/{1[month]}/{1[day]}/'.format(
                target_folder, exif_data)
        else:
            # copy to default folder for further manual class
            target_folder_file = '{}'.format(default_folder)

        if verbose:
            copyit(mistery_photo, target_folder_file, verbose)
        else:
            pbar.update(1)
            copyit(mistery_photo, target_folder_file)

    if not verbose:
        pbar.close()

    return


def get_EXIF_features(f, features='default', verbose=False):

    exif_data = dict()

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


def find_photos(source_path, common_extensions=('JPG', 'CR2', 'ORF', 'ARW'), ignore = []):
    """Walk the source folder and select potential photos by extension.

    Parameters
    ----------
    source_path : str
        Source path

    Returns
    -------

    """
    source_files = list()

    for (dirpath, dirnames, filenames) in os.walk(source_path):
        for f in filenames:
            if f.upper().endswith(common_extensions):
                source_files.append(os.path.join(dirpath, f))

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
    parser.add_argument('-d', '--default_folder', action="store", dest="default_folder",
                        default='Unclassfied', help='Folder to store photos without \
                        valid information to properlly classify')

    parser.add_argument('-m', '--move', action="store_true",
                        dest="move",
                        help="By default %prog  just copy the source files to a new a tify"
                        "folder struture, if you want to move it insted, activate this option")

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
