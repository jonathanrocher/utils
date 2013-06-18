""" Walk through a source tree and prepend some text at the top.
"""
import os
from os.path import join

txt2prepend = '''
""" This is a copy of the same module from VMA version 1.*. It is brought into
VMA 2.* to be able to support reading the old file format.  
"""
# importing the old vma as the vma alias so that we don't have to change any of 
# the code below.
import vma.OLD_vma as vma
'''

def prepend_content(filename):
    """ Update one file by adding the text above to its beginning
    """
    f = open(filename, "r")
    content = f.read()
    f.close()
    try:
        f2 = open(filename, "w")
        f2.write(txt2prepend + "\n")
        f2.write(content)
        f2.close()
    except Exception as e:
        print "Something went wrong: %s" % e
        import IPython ; IPython.embed()

def apply_prepend_to_dir(dirname, ext_list = [".py"], 
                          elems2ignore = ["__init__.py"]):
    """ Recursively applying a prepending opertion to all files below
    """
    for filename in os.listdir(dirname):
        if filename in elems2ignore:
            continue
        filename = join(dirname, filename)
        is_eligible_file = (os.path.isfile(filename) and 
            os.path.splitext(filename)[1] in ext_list)
        if is_eligible_file:
            prepend_content(filename)
        elif os.path.isdir(filename):
            apply_prepend_to_dir(filename)
        else:
            print "Skipping %s" % filename
    return       