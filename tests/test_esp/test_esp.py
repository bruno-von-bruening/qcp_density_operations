#!/usr/bin/env
from qc_density_operations.calc_esp.calc_esp import calc_esp
import subprocess as sp

import os.path

def load_dummy_file(file):
    dummy_path=os.path.realpath('../test_data')
    assert os.path.isdir(dummy_path), f"Not a directory: {dummy_path}"
    the_file=os.path.join(dummy_path, file)
    linked_file=f"ln_{os.path.basename(the_file)}"
    if os.path.islink(linked_file):
        os.unlink(linked_file)
    p=sp.Popen(f"ln -s {the_file} {linked_file}", shell=True)
    p.communicate()
    the_file=linked_file
    assert os.path.isfile(the_file), f"Not a file {the_file}"

    return the_file


def test_from_import():
    fchk_file=load_dummy_file('H2_HF_STO-3G.fchk')
    grid_file=load_dummy_file('H2_HF_STO-3G_surf.json')
    calc_esp(fchk_file, grid_file)

if __name__=='__main__':
    test_from_import()



