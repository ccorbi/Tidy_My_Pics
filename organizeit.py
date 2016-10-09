from __future__ import print_function

import os
from os import walk
import shutil

import exifread

def moveit(f,target):
    '''Get the name of the photo and the mouth that was taken and move it '''
    #Check if the folder exists, if not, it make it

    if not os.path.isdir(target):
        os.makedirs(target)

    shutil.move(f, target)
    return

def copyit(f, target):

    if not os.path.isdir(target):
        print('-'*30)
        os.makedirs(target)

    shutil.copy2(f, target)
    return

#It goes for each jpg in the run folder


def organize(source_pictures, target_folder, default_folder):

    if not os.path.isdir(target_folder):
        os.mkdir(target_folder)

    # Feed featrues to org photos
    for mistery_photo in source_pictures:
        print('*'*40)
        print(mistery_photo)
        exif_data = get_EXIF_features(mistery_photo)
        if exif_data['year'] != None:
            #copy
            target_folder_file =  '{0}/{1[year]}/{1[mouth]}/{1[day]}/'.format(target_folder, exif_data)

        else:
            #copy to miscellanian folder
            target_folder_file = '{}'.format(default_folder)
        print(mistery_photo)
        print(target_folder_file)
        copyit(mistery_photo, target_folder_file)

    return

def get_EXIF_features(f, features='default'):

    exif_data = dict()

    #open in binary mode
    photo = open(f,'rb')
    #Read  EXIF data
    tags = exifread.process_file(photo, details=False)
    #Extract time

    #Quick&Dirty to extract mouth
    ###NEED TO BE IMPROVED TO SUPORT year
    try:
        timestamp = tags['EXIF DateTimeOriginal'].values
        d, h = timestamp.split()
        exif_data['day'] = d.split(':')[2].strip()
        exif_data['mouth'] = d.split(':')[1].strip()
        exif_data['year'] = d.split(':')[0].strip()

        exif_data['hour'] = h.split(':')[0].strip()
        exif_data['min'] = h.split(':')[1].strip()
        exif_data['sec'] = h.split(':')[2].strip()


    except:
        # add logg
        # configuration file default photos
        print('error with {}'.format(f))
        exif_data['year'] = None

    return exif_data

def get_source_material(source_path):
    """Walk the source folder and select potential photos by extension.

    Parameters
    ----------
    source_path : str
        Source path

    Returns
    -------

    """
    source_files = list()
    common_extensions = ['JPG', 'CR2', 'ORF']
    for (dirpath, dirnames, filenames) in walk(source_path):
        for f in filenames:
            print(f)
            print(os.path.join(dirpath, f))
            file_extension = f[-3:]

            if file_extension.upper() in common_extensions:
                source_files.append(os.path.join(dirpath, f))

    return source_files

def main():

    source_path = './'
    default_folder = './To_class/'
    target_folder =  './tidy'

    # Walk Source folder and detect pictures
    source_pictures = get_source_material(source_path)
    print(source_pictures)
    organize(source_pictures, target_folder, default_folder)



if __name__ == '__main__':
    main()
