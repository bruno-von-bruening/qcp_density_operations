
#!/usr/bin/env python
import os

from qc_density_operations.calc_esp.calc_esp import calc_esp 
from qc_density_operations.calc_esp.calc_esp import avail_modi

if __name__=='__main__':
    description=f""" Evaluates the ESP on vertices of a given surface
    Currently this surface can only be provided as json object compute by the calc_IsoDensSurf.py script
    Multiple surfaces may be provided
    """
    import argparse; par=argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter,
        description=None,
        epilog=None)
    par.add_argument("--dens",
        help=f"Provide Density (as fchk file)")
    par.add_argument('--surf', nargs='+',
        help=f"Surface(s) (as grid file or json file)")
    par.add_argument('-output_name',
        help=f"File name to drop map to")
    engine_choices=avail_modi
    par.add_argument('-engine', choices=engine_choices, default='fortran',
        help=f"Choice of engine with thich to evaluate esp integrals")
    
    args=par.parse_args()
    fchk_file=args.dens
    assert os.path.isfile(fchk_file), f"Provided value is not a file: {fchk_file}"
    surface_file=args.surf
    assert all([os.path.isfile(x) for x in surface_file]), f"Provided value is not a file: {surface_file}"
    output_name=args.output_name
    engine=args.engine

    calc_esp(fchk_file, surface_file, do_plot=False, drop=True, output_name=output_name, engine=engine)