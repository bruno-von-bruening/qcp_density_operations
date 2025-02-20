#!/usr/bin/env python

import numpy as np
import os,sys,re,copy, time
import shutil, glob, json

from iodata import load_one
from gbasis.wrappers import from_iodata
from gbasis.evals.density import evaluate_density as gbasis_eval_dens

sys.path.insert(1, os.environ['SCR'])
import modules.mod_utils as m_util

avail_modi=['fortran','numpy']

def get_fortran_lib():
    lib_env_key='QC_DENSITY_OPERATIONS_LIB'
    if not lib_env_key in os.environ.keys(): 
        message='\n'.join([
            f"Cannot find environment variable: '{lib_env_key}\'",
            f"This variable is neccessary when running fortran code",
            f"To solve this issue either run this code with the \'numpy\' engine or consider adding the environement variable to your environment during the run (`export {lib_env_key}=<path-to-lib>`)"
        ])
        raise Exception(message)
    else:
        lib_dir=os.environ[lib_env_key]
        assert os.path.isdir(lib_dir), f"Provided library path in environment ({lib_env_key}) doe not exist: {lib_dir}"
        lib_name='libcalcesp.so'
        lib_path=os.path.join(lib_dir, lib_name)
        if not os.path.isfile(lib_path): raise Exception(f"Cannot find file {lib_name} in environment varibale path {lib_env_key}=\'{lib_dir}\'"+
                                                         f"\nConsider that this file should be compiled during installation (check compilation of this library)")
        return lib_path


def make_grid_object(inp, surface_values, energy_units, charge_violation):

    from qc_objects.objects.grids import interaction_map
    obj=interaction_map(inp=inp, scalars=surface_values, energy_units=energy_units, charge_violation=charge_violation)
    obj.gen_statistical_indicators()
    return obj

def make_integration_grid(mol_data):
    from grid.molgrid import MolGrid
    from grid.becke import BeckeWeights
    from grid.onedgrid import Trapezoidal
    from grid.rtransform import LinearFiniteRTransform

    from grid.onedgrid import GaussLegendre
    from grid.rtransform import BeckeRTransform

    n_rpoints = 400                         # Number of radial points
    oned_grid = GaussLegendre(npoints=n_rpoints)
    radial_grid = BeckeRTransform(0.0, R=1.).transform_1d_grid(oned_grid)

    #oned = Trapezoidal(n_rpoints)           # Trapezoidal grid of that size
    #rmin, R = 0.0, 0.5                      # Parameters for the Becke radial transform
    #rgrid = LinearFiniteRTransform(rmin, 10).transform_1d_grid(oned)


    aim_weights = BeckeWeights()


    atcoords = mol_data.atcoords
    atnums = mol_data.atnums

    molgrid = MolGrid.from_preset(atnums, atcoords, rgrid=radial_grid, preset="insane", aim_weights=BeckeWeights() )#, store=True)
    return molgrid.points, molgrid.weights
def evaluate_density(mol_data, grid):
    ao_basis = from_iodata(mol_data)
    rdm = mol_data.one_rdms["scf"]
    rho = gbasis_eval_dens(rdm, ao_basis, grid)
    #rho_mesh=rho.reshape(tuple(shape))
    #points_mesh=grid.reshape( (*shape, 3) )
    return rho #points_mesh, rho_mesh

def calc_esp(fchk_file,input, do_plot=True, drop=True, output_name=None, engine='fortran'):
    def process_input(input):
        vertices, points, input_type =[None, None, None]
        def check_file(input):
            assert os.path.isfile(input), f'Provided String {points}, but is not a file!'
            if input.lower().endswith('.json'):
                input_type='surface.json'
                with open(input, 'r') as rd:
                    content=json.load(rd)
                try:
                    vertices=content['vertices']
                    faces=content['faces']
                except Exception as ex:
                    raise Exception(f"Cannot read content of file {input}: {ex}")
            else:
                raise Exception(f"File does not end with .json: {input}")
            return vertices, faces, input_type
        if isinstance(input, str):
            vertices, faces, input_type=check_file(input)
        elif isinstance(input, dict):
            assert all([x in input.keys() for x in ['vertices','faces']])
            vertices=input['vertices']
            faces=input['faces']
        elif isinstance(input, (list, type(np.array([])))):
            vertices=input
        else:
            raise Exception(f"Invalid type of vertices {type(vertices)}")
        

        return np.array(vertices), np.array(faces), input_type
    def esp_calc(points, integration_points, integration_weights, density, engine='fortran'):

        print(f"Number of points {len(points)}, number of density points {len(density)}")
        import numpy as np
        if engine=='fortran':
            import ctypes

            calc_lib=get_fortran_lib()
            flib= ctypes.cdll.LoadLibrary(calc_lib)

            calc_esp_f90 = flib.calculate_esp

            ar_ty=ctypes.POINTER(ctypes.c_double)
            calc_esp_f90.argtypes= [ 
                # legnth , eval_points, integration_points, integration_weights, density, esp
                ctypes.c_int, ctypes.c_int, ar_ty, ar_ty, ar_ty, ar_ty, ar_ty ]
            #calc_esp_f90.restype = ctypes.c_double

            esp=[0.0 for i in range(len(density)) ]
            array_type=ctypes.c_double * len(points)
            def nparray_to_ctypes(array):
                array=copy.deepcopy(array)
                shape=array.shape
                data_type=ctypes.c_double
                for x in list(shape)[::-1]:
                    data_type=(data_type*x)
                array = (data_type)(*array)# (*(tuple(i) for i in array))
                return array
            points_c=nparray_to_ctypes(points.reshape(-1))
            integration_points_c=nparray_to_ctypes(integration_points.reshape(-1))
            integration_weights_c=nparray_to_ctypes(integration_weights.reshape(-1))
            density_c=nparray_to_ctypes(density.reshape(-1))
            esp=nparray_to_ctypes(np.array([0.0 for x in range(len(points))]))
            
            calc_esp_f90( int(len(points)), len(density), points_c, integration_points_c, integration_weights_c, density_c, esp)
            esp=np.ctypeslib.as_array(esp, shape=None)
        elif engine=='numpy':
            esp=[]
            for position in points:
                distances=integration_points-position
                distances=np.linalg.norm(distances, axis=1)
                distances=np.reciprocal(distances)
                distances[distances > 1000] = 0.
                
                elst=distances * density
                elst=np.dot(elst, integration_weights)
                esp.append(elst)
            esp=np.array(esp)
        else:
            raise Exception(f"Modus is not valid: {modus}  -> choose from {avail_modi}")
    



        #average.argtypes= [ ctypes.POINTER(ctypes.c_double), ctypes.c_int ]
        #average.restype= ctypes.c_double
        #values= [1., 2. ,30.]
        #array_type = ctypes.c_double * len(values)
        #values_c = array_type( * values )
        #b = average( values_c, 3)


        #values_np = np.array(values)
        #values_c = values_np.ctypes.data_as(ctypes.POINTER(ctypes.c_double))

        #b =average( values_c , 3)



        ##############
        return esp
    print(f"All units are in au")
    results={'files':{'esp-maps':{}}}
    # Load fchk file
    fchk_file=m_util.process_file(fchk_file) # copy if symlink gunzip etc.
    mol_data = load_one(fchk_file)

    # Make density grid
    start=time.time()
    integration_points, integration_weights=make_integration_grid(mol_data)
    print(f"Make integration grid: {time.time()-start} [s] (number of points={len(integration_points)})")
    # Get density on grid
    start=time.time()
    density=evaluate_density(mol_data, integration_points)
    n_elec=mol_data.charge+np.sum(mol_data.atnums)
    charge_violation=np.abs(np.dot(density,integration_weights)-n_elec)
    charge_thres=1.e-4
    assert np.abs(charge_violation)<charge_thres, f"Charge violation is {charge_violation}, larger than {charge_thres} {n_elec}"
    print(f"Density eval: {time.time()-start} [s]")
    
    for inp in input:
        # Load surface
        assert isinstance(inp, str) 
        points,faces, input_type = process_input(inp)
        print(f"Loaded file {inp} Number of points to be evaluated: {len(points)}")

        # Calculate ESP
        start=time.time()
        esp=esp_calc(points, integration_points, integration_weights, density, engine=engine)
        print(f"ESP eval: {time.time()-start} [s]")

        # Convert energy
        def convert_energy(esp, energy_units='kJ/mol'):
            if energy_units.lower() in ['kj/mol']:
                au_in_kjmol=2625.5002
                esp*=au_in_kjmol
            elif energy_units.lower() in ['au']:
                pass
            else:
                raise Exception()
            print(f"ESP in range: {min(esp)} to {max(esp)} [in {energy_units}]")
            return esp
        energy_units='kJ/mol'
        esp=convert_energy(esp, energy_units=energy_units)

        if do_plot:
            import matplotlib.pyplot as plt
            from matplotlib import cm
            from mpl_toolkits.mplot3d.art3d import Poly3DCollection

            fig = plt.figure(figsize=(8,6))
            ax = fig.add_subplot(111,projection='3d')

            new_esp=copy.deepcopy(esp)
            new_esp[ esp<0.45]=None

            #print(points.shape)
            mesh = Poly3DCollection(points[faces])
            mesh.set_edgecolor('k')
            mesh.set_facecolor('white')
            #ax.add_collection3d(mesh)
            ax.scatter(*points.T, c=cm.hsv(.9*(new_esp-min(new_esp))/(max(new_esp)-min(new_esp))), marker='.', alpha=.5)
            plt.show()
        if drop:
            surface_values=esp.tolist()
            if True:
                obj=make_grid_object(inp, surface_values, energy_units, charge_violation)
                drop_di=obj.model_dump()
            else:
                if input_type=='surface.json':
                    with open(inp,'r') as rd:
                        drop_di=json.load(rd)
                    drop_di.update({'surface_values':esp.tolist()})
                    drop_di.update({'energy_units':energy_units})
                    drop_di['meta'].update({'charge_violation':charge_violation           
                    })
                else:
                    raise Exception()
            # Enrich grid folder by adding 
            if isinstance(output_name, type(None)):
                drop_path=inp.replace('-surf.json', '-mapsurf.json')
            else:
                drop_path=output_name.replace('.json','')+'.json'
            with open(drop_path,'w') as wr:
                json.dump(drop_di, wr)
            isod=drop_di['meta']['iso_density_value']
            results['files']['esp-maps'].update({isod:drop_path})
    with open('results.json','w') as wr:        
        json.dump(results, wr)
    return esp

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
