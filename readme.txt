

This folder contains a few utilities for dealing with files recursively 
on the filesystem:
* multi_search_replace does a search and replace recusively in all the 
files satisfying certain conditions (extension, name in an include list 
or not in a exclude list)

* recursiv_remove removes all files satisfying the same type of 
conditions.

This can (should?) be done using the safe mode, meaning that a new 
folder is created as a copy of the one to be worked on.

The folder 'test_folder' is there for testing of these scripts.

For information or feature request, contact: 
Jonathan Rocher <jrocher@enthought.com>
