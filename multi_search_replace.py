""" 
Multi-file search and replace. 

Usage: 
python multi_search_replace.py folder_path string1 [string2 [safe [postfix [extension_list [exclude_file_list [include_file_list [verbose]]]]]]]

The resulting files are in a folder located in the same place as 'folder_path' 
but named 'folder_path'+'postfix'.

TODO: create a setup.py with an entry point to have access to it from anywhere
TODO: Replace the positional argument type interface by an argparse or a traits 
GUI 
"""

import os
import shutil
import warnings
import numpy as np

def search_for_files(folder_path, extension_list = [".py"], 
                     exclude_file_list = [], include_file_list = None, 
                     verbose = False):
    """ Recusively search for the eligible files containing string1. 
        Apply this to all files with extension in extension_list and that are 
        not in exclude_file_list.
        If safe == True, a copy of the folder is created and both are kept
    """

    if verbose:
        print("Now exploring folder %s" % os.path.abspath(folder_path))
    
    try:
        content = os.listdir(folder_path)
    except Exception as e:
        raise OSError("The folder_path couldnt be found (exception: %s)" % e)
    if verbose:
        print("Content:\n%s" % content)

    os.chdir(folder_path)
    # list of files eligible for replacement
    eligible_files = []

    for member in content:
        member = os.path.abspath(member)
        #print "member", member
        if os.path.isfile(member):
            if file_to_apply(member, extension_list, 
                             exclude_file_list = exclude_file_list, 
                             include_file_list = include_file_list):
                print("      Adding %s to the eligible files" 
                      % member)
                eligible_files.append(os.path.abspath(member))
        elif os.path.isdir(member):
            eligible_files += search_for_files(
               folder_path = member, 
               extension_list = extension_list, 
               exclude_file_list = exclude_file_list,
               include_file_list = include_file_list)
            os.chdir(folder_path)
        else:
            print("   Skipping %s since it is neither a file nor a directory." 
                  % os.path.abspath(member))
    return eligible_files

################################################################################
# File selection
################################################################################

def file_to_apply(filename, extension_list, exclude_file_list, 
                  include_file_list, verbose = False):
    """ Test if a given file is eligible for a given action. 
        Must have the correct extension AND
        - be in the include_file_list (with or without extension)
        OR
        - not be in the exclude_file_list (with or without extension)
        if only 1 list is provided.

        Returns:
        - bool
    """
    print "testing", filename
    if include_file_list == [] and exclude_file_list == []:
        condition = (os.path.splitext(filename)[1] in extension_list)
    elif include_file_list != [] and exclude_file_list == []:
        condition = (os.path.splitext(filename)[1] in extension_list
                 and (os.path.split(filename)[1] in include_file_list 
                      or os.path.splitext(os.path.split(filename)[1])[0] 
                      in include_file_list ))
    elif include_file_list == [] and exclude_file_list != []:
        condition = (os.path.splitext(filename)[1] in extension_list
                     and (os.path.split(filename)[1] not in exclude_file_list 
                          or os.path.splitext(os.path.split(filename)[1])[0] 
                          not in exclude_file_list))
    else:
        raise ValueError("Both an exclude list and include list were provided."
                         "Please clarify by using either or None. Currently, "
                         "include = %s, exclude = %s" 
                         % (exclude_file_list, include_file_list))
    return condition


def find_and_replace(filepath, new_filepath, string1, string2, verbose = False):
    """ Search for a string1 inside a text file. Replace by string2 and write 
    into a new file whose filepath is returned.

    FIXME: Most straightfoward strategy. There is probably a more efficient 
    way to do that!! 
    """

    num_occurences = 0
    if verbose:
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
        new_content = content[:offset]+string2+content[offset+len(string1):]
        content = new_content
    f.close()
    
    if num_occurences:
        print("*** Found %s occurences of %s in %s. ***" % 
              (num_occurences, string1, filepath))
        #print "Saving to ", new_filepath
        f = open(new_filepath, "w")
        f.write(content)
        f.close()

    return num_occurences

################################################################################
# Main
################################################################################

def main(folder_path, string1, string2 = "", extension_list = [".py"], 
         exclude_file_list = [], include_file_list = None, safe = True, 
         postfix = "2", verbose = False):
    """ Manages the search a replace behavior
    """
    # Create a copy of the folder. 
    folder_path = os.path.abspath(folder_path)
    containing_folder = os.path.split(folder_path)[1]
    
    eligible_files = search_for_files(folder_path,
                                      extension_list, 
                                      exclude_file_list = exclude_file_list, 
                                      include_file_list = include_file_list)
    if eligible_files:
        occurences = np.empty(len(eligible_files), dtype = np.int)
    # Create the whole directory structure. The eligible files will be 
    # overwritten later on
    if safe:
        target_folder = folder_path.replace(containing_folder, 
                                            containing_folder+postfix)
        if os.path.exists(target_folder):
            raise IOError("Target folder %s already exists. Aborting..." % 
                          target_folder)
        shutil.copytree(folder_path,target_folder)
        
    for index, files in enumerate(eligible_files):
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

        occurences[index] = find_and_replace(files, target_filename, string1, 
                                             string2)
    
    if occurences.max() == 0:
        print "No occurence of the string requested was found."

    return
    

################################################################################
# Formatting of inputs
################################################################################

def parse_string_list(string):
    """ Converts a list in the form of a string to a list of strings. If the 
        argument given is not a list looking object ("[ something ]"), there is 
        only 1 element in the list so create a list with it.
    """
    my_list = []
    if string.startswith("[") and string.endswith("]"):
        string = string.replace("[","")
        string = string.replace("]","")
        my_list = string.split(",")

        if my_list == [""]:
            my_list = []

    else:
        my_list = [string]

    return my_list

def parse_extension_list(ext_list):
    """ Make sure the list of extensions has the right format: each extension 
        must start with a dot. If it doesn't, add it. If the extension is 4 
        char or more, issue a warning.
    """
    output = []
    for ext in ext_list:
        if len(ext) >= 4:
            warnings.warn("The extension %s has more than 4 characters: was "
                          "that a typo?")
        if ext.startswith("."):
            output.append(ext)
        else:
            output.append("."+ext)
    return output

################################################################################
# Interface
################################################################################

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        raise OSError("3 arguments must be provided to the multi-search-replace"
                      " utility. Only received %s." % len(sys.argv))

    else:
        folder_path = sys.argv[1]
        string1 = sys.argv[2]
        if len(sys.argv) >= 4:
            string2 = sys.argv[3]
            if len(sys.argv) >= 5:
                safe = bool(sys.argv[4])
                if len(sys.argv) >= 6:
                    postfix = sys.argv[5]
                    if len(sys.argv) >= 7:
                        extension_list = parse_extension_list(
                            parse_string_list(sys.argv[6]))
                        if len(sys.argv) >= 8:
                            exclude_file_list = parse_string_list(sys.argv[7])
                            if len(sys.argv) >= 9:
                                include_file_list = parse_string_list(
                                    sys.argv[8])
                                if len(sys.argv) >= 10:
                                    verbose = bool(sys.argv[9])
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
        else:
            verbose = False
            include_file_list = []
            exclude_file_list = []
            extension_list = [".py"]
            postfix = "2"            
            safe = True
            string2 = ""

        #import pdb ; pdb.set_trace()
        main(folder_path = folder_path, string1 = string1, string2 = string2, 
             safe = safe, extension_list = extension_list, exclude_file_list = 
             exclude_file_list, include_file_list = include_file_list)
