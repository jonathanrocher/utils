""" 
Recursively remove files from a folder based on include list and/or exclude 
list and/or extension list.

Usage: 
python recursiv_remove.py folder_path [safe [postfix [extension_list [exclude_file_list [include_file_list [verbose]]]]]]

The resulting files are in a folder located in the same place as 'folder_path' 
but named 'folder_path'+'postfix'.

TODO: create a setup.py with an entry point to have access to it from anywhere
TODO: Replace the positional argument type interface by an argparse or a traits 
GUI 
"""

import os
import shutil
from multi_search_replace import search_for_files, file_to_apply, \
    parse_extension_list, parse_string_list


def main(folder_path, extension_list = [".py"], 
         exclude_file_list = [], include_file_list = None, safe = True, 
         postfix = "2", verbose = False):
    """ Manages the search a remove behavior
    """
    # Create a copy of the folder. 
    folder_path = os.path.abspath(folder_path)
    containing_folder = os.path.split(folder_path)[1]

    eligible_files = search_for_files(folder_path,
                                      extension_list, 
                                      exclude_file_list = exclude_file_list, 
                                      include_file_list = include_file_list)
    
    # Create the whole directory structure. The eligible files will be 
    # overwritten later on
    if safe:
        target_folder = folder_path.replace(containing_folder, 
                                            containing_folder+postfix)
        if os.path.exists(target_folder):
            raise IOError("Target folder %s already exists. Aborting..." % 
                          target_folder)
        shutil.copytree(folder_path,target_folder)

    if eligible_files:
        for files in eligible_files:
            if safe:
                target_filename = files.replace(folder_path, 
                                                target_folder)
                if not os.path.exists(os.path.dirname(target_filename)):
                    raise OSError("The target filename %s doesn't exist but "
                                  "should. Investigate..." % target_filename)
                elif target_filename == files:
                    raise OSError("The target filepath %s should be different from "
                                  "the original filepath %s. Investigate..." 
                                  % (target_filename, files))
            else:
                target_filename = files

            os.remove(target_filename)
    else:
        print "No files found to remove"

    return

################################################################################
# Interface
################################################################################

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        raise OSError("2 arguments must be provided to the recursiv_remove"
                      " utility. Only received %s." % len(sys.argv))

    else:
        # This is horrible: replace with argparse or optparse
        folder_path = sys.argv[1]
        if len(sys.argv) >= 3:
            safe = bool(sys.argv[2])
            if len(sys.argv) >= 4:
                postfix = sys.argv[3]
                if len(sys.argv) >= 5:
                    extension_list = parse_extension_list(
                        parse_string_list(sys.argv[4]))
                    if len(sys.argv) >= 6:
                        exclude_file_list = parse_string_list(sys.argv[5])
                        if len(sys.argv) >= 7:
                            include_file_list = parse_string_list(
                                sys.argv[6])
                            if len(sys.argv) >= 8:
                                verbose = bool(sys.argv[7])
                            else:
                                verbose = False
                        else:
                            verbose = False
                            include_file_list = []
                    else:
                        verbose = False
                        include_file_list = []
                        exclude_file_list = []
                else:
                    verbose = False
                    include_file_list = []
                    exclude_file_list = []
                    extension_list = [".py"]
            else:
                verbose = False
                include_file_list = []
                exclude_file_list = []
                extension_list = [".py"]
                postfix = "2"
        else:
            verbose = False
            include_file_list = []
            exclude_file_list = []
            extension_list = [".py"]
            postfix = "2"
            safe = True

    #import pdb ; pdb.set_trace()
    main(folder_path = folder_path, safe = safe, extension_list = 
         extension_list, exclude_file_list = exclude_file_list,
         include_file_list = include_file_list)
