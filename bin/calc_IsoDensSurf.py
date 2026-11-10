#!/usr/bin/env python

from qcp_density_operations.calc_IsoDensSurf.calc_IsoDensSurf import IsoDensSurf

if __name__=='__main__':
    description=None
    epilog=None

    isod_def=[ 0.001 ]
    gs_def=None

    def set_max_processes(n):
        import resource
        _, hard = resource.getrlimit(resource.RLIMIT_NPROC)
        resource.setrlimit(resource.RLIMIT_NPROC, (n, hard))


    import argparse; par=argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter,
        description=description, epilog=epilog)
    par.add_argument("INPUT", 
        help=f'File containing the density. Currently supported formats: FCHK')
    par.add_argument('--plot', action='store_true',
        help=f"Launch plot of the surface")
    par.add_argument('--grid_spacing', default=gs_def, type=float, nargs='*',
        help=f"Difference in cubical grid in [au] ({gs_def})")
    par.add_argument('--iso_dens', default=isod_def, type=float, nargs='*',
        help=f'Value of iso-density in [au] ({isod_def})')
    par.add_argument('-o','--output_name',
        help=f'Define name for output file')
    args=par.parse_args()

    fchk_file=args.INPUT
    do_plot=args.plot
    iso_dens=args.iso_dens
    grid_spacing=args.grid_spacing
    output_name=args.output_name

    IsoDensSurf(fchk_file, grid_spacing=grid_spacing, iso_dens=iso_dens, do_plot=do_plot, output_name=output_name)
