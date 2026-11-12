
from .get_test_data_loc import TEST_DATA_DIR
import os, subprocess as sp

def load_dummy_file(file, dir=TEST_DATA_DIR, tar_dir=None):
    the_file=os.path.join(dir, file)
    linked_file=f"ln_{os.path.basename(the_file)}"
    if tar_dir is not None:
        linked_file=os.path.join(tar_dir,linked_file)
    p=sp.Popen(f"ln -s {the_file} {linked_file}", shell=True)
    p.communicate()
    the_file=linked_file
    assert os.path.isfile(the_file), f"Not a file {the_file}"

    return os.path.realpath(the_file)