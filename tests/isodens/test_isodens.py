#!/usr/bin/env
from qcp_density_operations.calc_IsoDensSurf.calc_IsoDensSurf import IsoDensSurf
import subprocess as sp, os

import sys

TOP=os.path.join(os.path.dirname(os.path.realpath(__file__)),'..' )
sys.path.insert(1, TOP)
from python_helpers.get_file import load_dummy_file

def test_from_import():
    fchk_file=load_dummy_file('H2_HF_STO-3G.fchk')
    IsoDensSurf(fchk_file=fchk_file, grid_spacing=0.1, iso_dens=0.001)

if __name__=='__main__':
    test_from_import()



