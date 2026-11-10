
import os

TEST_TOPLEVEL=os.path.realpath( os.path.join( os.path.dirname(__file__), '..' ) )
assert os.path.basename(TEST_TOPLEVEL)=='tests', f"Wrong assignment of TEST_TOPLEVEL: {TEST_TOPLEVEL}"
TEST_DATA_DIR=os.path.realpath(os.path.join(TEST_TOPLEVEL,'test_data'))