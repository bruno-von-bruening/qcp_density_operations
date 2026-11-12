#!/usr/bin/env
from qcp_density_operations.calc_esp.calc_esp import calc_esp
import subprocess as sp
import sys, os

TOP=os.path.join(os.path.dirname(os.path.realpath(__file__)),'..' )
sys.path.insert(1, TOP)
from python_helpers.get_file import load_dummy_file

THIS_DIR=os.path.dirname( os.path.abspath(__file__))



from python_helpers.get_test_data_loc import to_test_subdir



def test_from_import():
    fchk_file=load_dummy_file('H2_HF_STO-3G.fchk', tar_dir=THIS_DIR)
    grid_file=load_dummy_file('H2_HF_STO-3G_surf.json', tar_dir=THIS_DIR)
    with to_test_subdir('test_esp'):
        calc_esp(fchk_file, grid_file)

if __name__=='__main__':
    test_from_import()



