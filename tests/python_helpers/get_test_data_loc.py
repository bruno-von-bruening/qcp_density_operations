
import os


from functools import wraps

TEST_TOPLEVEL=os.path.realpath( os.path.join( os.path.dirname(__file__), '..' ) )
assert os.path.basename(TEST_TOPLEVEL)=='tests', f"Wrong assignment of TEST_TOPLEVEL: {TEST_TOPLEVEL}"
TEST_DATA_DIR=os.path.realpath(os.path.join(TEST_TOPLEVEL,'test_data'))


# Use this to change to test dir
# with chdir(TEST_TOPLEVEL,')
from qcp_global_utils.convenience.chdir import chdir

@wraps(chdir)
def to_test_subdir(x, make_if_not_exists=True):
    the_dir=os.path.join(TEST_TOPLEVEL,x) if not x.startswith('/') else x
    if not os.path.isdir(the_dir): 
        if make_if_not_exists: os.mkdir(the_dir)
        else: raise ValueError(f"Not a dir: {the_dir}")

    return chdir(the_dir)