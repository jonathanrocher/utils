""" 
multi-file search and replace
"""

import os
from distutils.dir_util import mkpath
import logging

logger = logging.getLogger()
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
logger.addHandler(console_handler)

def search_for_files(folder_path, extension_list = [".py"], 
                     exclude_file_list = []):
    """ Recusively search for the eligible files containing string1. 
        Apply this to all
        files with extension in extension_list and that are not in 
        exclude_file_list.
        If safe == True, a copy of the folder is created and both are kept
    """

    print("Now dealing with folder %s" % os.path.abspath(folder_path))
    content = os.listdir(folder_path)
    os.chdir(folder_path)

    # list of files eligible for replacement
    eligible_files = []

    for member in content:
        print("   Now dealing with %s" % os.path.abspath(member))
        if os.path.isfile(member):
            if file_to_apply(member, extension_list, 
                             exclude_file_list):
                print("      Adding %s to the list of eligible files" 
                      % member)
                eligible_files.append(os.path.abspath(member))
                print eligible_files
        elif os.path.isdir(member):
           eligible_files += search_for_files(member, 
                                              extension_list, 
                                              exclude_file_list)
        else:
            print("   Skipping %s." % os.path.abspath(member))

    return eligible_files


def file_to_apply(filename, extension_list, exclude_file_list):
    """ Has the filename an extension in extension_list and is it not 
        contained in the exclusion list?

        FIXME: make smarter filters
    """
    print("      testing %s" % filename)
    condition = (os.path.splitext(filename)[1] in extension_list
                 and filename not in exclude_file_list)
    
    return condition


def find_and_replace(filepath, new_filepath, string1, string2):
    """ Search for a string1 inside a text file. Replace by string2 and write 
    into a new file whose filepath is returned.

    FIXME: Most straightfoward strategy. There is probably a more efficient 
    way to do that!! 
    """

    num_occurences = 0
    print("Replacing '%s' by '%s' in %s ") % (string1,string2,filepath)
    try:
        f = open(filepath, "r")
    except Exception as e:
        raise IOError("Failed opening file with path %s with exception %s." % 
                      (filepath, e))
    content = f.read()
    while content.find(string1) != -1:
        num_occurences += 1
        offset = content.find(string1)
        new_content = content[offset]+string2+content[offset+len(string1)]
        content = new_content
    print "Found %s occurences of %s" % (num_occurences, string1)
    f.close()
    
    if num_occurences:
        print "Saving to ", new_filepath
        f = open(new_filepath, "w")
        f.write(content)
        f.close()

def main(folder_path, string1, string2 = "", extension_list = [".py"], 
         exclude_file_list = [], safe = True, postfix = "2"):
    """ Manages the search a replace behavior
    """
    # Create a copy of the folder. 
    eligible_files = search_for_files(folder_path,
                                      extension_list, 
                                      exclude_file_list = [])
    
    # FIXME: create the tree structure automatically and recursively
    print "eligible_files", eligible_files

    for files in eligible_files:
        if safe:
            target_filename = files.replace(folder_path,folder_path+postfix)
            if not os.path.exists(os.path.dirname(target_filename)):
                raise OSError("A new tree structure identical to the one to "
                             "replace must be created. The folder name %s "
                             "simply must be added the postfix %s" % 
                             (folder_path, postfix))
        else:
            target_filename = files

        find_and_replace(files, target_filename, string1, string2)
        
if __name__ == "__main__":
    # FIXME: use a nicer argparse interface
    import sys
    if len(sys.argv) < 3:
        logger.error("3 arguments must be provided to the multi-search-replace "
                     "utility. Only received %s." % len(sys.argv))

    else:
        folder_path = sys.argv[1]
        string1 = sys.argv[2]
        if len(sys.argv) >= 4:
            string2 = sys.argv[3]
            if len(sys.argv) >= 5:
                safe = sys.argv[4]
                if len(sys.argv) == 6:
                    postfix = sys.argv[5]
                else:
                    postfix = "2"
            else:
                safe = True
                postfix = "2"
        else:
            string2 = ""
            safe = True
            postfix = "2"

        main(folder_path, string1, string2, safe = safe)
