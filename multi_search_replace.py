""" 
multi-file search and replace
"""

import os
from distutils.dir_util import mkpath
import distutils
import shutil

def search_for_files(folder_path, extension_list = [".py"], 
                     exclude_file_list = []):
    """ Recusively search for the eligible files containing string1. 
        Apply this to all
        files with extension in extension_list and that are not in 
        exclude_file_list.
        If safe == True, a copy of the folder is created and both are kept
    """

    logger.info("Now dealing with folder %s" % os.path.abspath(folder_path))
    content = os.listdir(folder_path)
    os.chdir(folder_path)

    # list of files eligible for replacement
    eligible_files = []
    # stores the folder structure to recreate it if necessary
    locations = [folder_path]

    for member in content:
        logger.info("   Now dealing with %s" % os.path.abspath(member))
        if os.isfile(member):
            if file_to_apply(member, extension_list, 
                             exclude_file_list):
                eligible_files += os.path.abspath(member)
        elif os.isdir(member):
           output = search_for_files(member, 
                                     extension_list, 
                                     exclude_file_list)
           eligible_files += output[0]
           locations += output[1]
        else:
            logger.info("   Skipping %s." % os.path.abspath(member))

    return eligible_files, locations


def file_to_apply(filename, extension_list, exclude_file_list):
    """ Has the filename an extension in extension_list and is it not 
        contained in the exclusion list?
    """
    return (os.path.splitext(member)[1] in extension_list 
            and member not in exclude_file_list)


def search_and_replace(filepath, new_filepath, string1, string2):
    """ Search for a string1 inside a text file. Replace by string2 and write 
    into a new file whose filepath is returned.

    FIXME: Most straightfoward strategy. There is probably a more efficient 
    way to do that!! 
    """

    num_occurences = 0    
    try:
        f = open(filepath, "r")
    except Exception as e:
        raise IOError("Failed opening file with path %s with exception %s." % 
                      (filepath, e))
    content = f.read()
    while content.find(string1) != -1:
        num_occurences += 1
        location = content.find(string1)
        new_content = content[location]+string2+content[location+len(string1)]
        content = new_content
    f.close()

    f = open(new_filepath, "w")
    f.write(content)
    f.close()

def main(folder_path, string1, string2 = "", extension_list = [".py"], 
         exclude_file_list = [], safe = True, new_name = "2"):
    # Create a copy of the folder. 
    target = folder_path+new_name
    mkpath(target)

    eligible_files, locations = search_for_files(folder_path, string1, 
                                                 extension_list, 
                                                 exclude_file_list = [])
    locations = set(locations)

    # create new tree structure


    for files in eligible_files:
        search_and_replace(files, files)
        
