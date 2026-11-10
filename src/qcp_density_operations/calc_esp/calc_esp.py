from . import *

from qcp_objects.objects.grids import interaction_map
from qcp_density_operations.density_eval.density_eval import load_one, make_integration_grid, evaluate_density

from qcp_global_utils.environment.file_handling import temporary_file
from qcp_global_utils.information.tracker import Tracker

from .calc_esp_ext import process_input, esp_rho_calc, esp_nuc_calc

avail_modi=['fortran','numpy']

def get_fortran_lib():
    """ If fortran engine was chosen this requires providing the path to a fortran libarary """
    lib_env_key='DENSITY_OPERATIONS_LIB'
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
    """ Create a grid object from qcp_objects library """
    obj=interaction_map(inp=inp, scalars=surface_values, energy_units=energy_units, charge_violation=charge_violation)
    # evaluate statitical indicators
    obj.gen_statistical_indicators()
    return obj

@validate_call
def calc_esp(
    fchk_file:file|List[file],input:file|List[file], 
    charge_thres=1.e-4,
    do_plot=False, drop=True, output_name=None, engine='fortran'
):
    """ """
    if not isinstance(input, list):
        input=[ input ]
    if engine in ['fortran']:
        calc_lib=get_fortran_lib()
    else:
        calc_lib=None
    tracker=Tracker()

    results={'files':{'esp-maps':{}}}
    # Load fchk file
    tmp_file=temporary_file(fchk_file,copy=True)
    mol_data = load_one(tmp_file.file)
    tracker.add_time_point('Loaded FCHK Data')
    try:

        # Make density grid
        integration_points, integration_weights=make_integration_grid(mol_data)
        
        tracker.add_time_point('Made Integration Grid')
        tracker.add_period(print=True)

        # Get density on grid
        density=evaluate_density(mol_data, integration_points)

        def check_density(mol_data,density, integration_weights):
            n_elec=float(mol_data.charge+np.sum(mol_data.atnums))
            charge_violation=float(np.abs(np.dot(density,integration_weights)-n_elec))
            return n_elec, charge_violation
        n_elec, charge_violation=check_density(mol_data, density, integration_weights)
        assert np.abs(charge_violation)<charge_thres, f"Charge violation is {charge_violation}, larger than {charge_thres} {n_elec}"
        # Save information about the density grid (coudl add info about the grid parameters)
        results.update({'density_grid': {'num_integration_points': len(integration_points), 'number_of_electrons':n_elec, 'charge_violation':charge_violation }})

        tracker.add_time_point('Density Evaluation')
        tracker.add_period(print=True)
        
        for i,inp in enumerate(input):
            tmp_inp=temporary_file(inp, copy=True)
            inp=tmp_inp.file
            try:
                # Load surface
                points,faces, input_type = process_input(inp)
                print(f"Loaded file {inp} Number of points to be evaluated: {len(points)}")

                # Calculate ESP
                tracker.add_time_point(f"Start ESP Evaluation (#{i}) for {inp}")
                rho_esp=esp_rho_calc(points, integration_points, integration_weights, density, engine=engine, calc_lib=calc_lib)
                nuc_esp=esp_nuc_calc(points, nuclear_coordinates=mol_data.atcoords, nuclear_charges=mol_data.atnums)

                tracker.add_time_point(f"End ESP Evaluation (#{i}) for {inp}")
                tracker.add_period(print=True)

                # Convert energy
                @validate_call
                def convert_energy(esp: pdtc_ndarray, energy_units='kJ/mol'):
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
                esp=-1.*rho_esp+nuc_esp
                nuc_esp=convert_energy(esp, energy_units=energy_units)

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
                        drop_path=os.path.basename(tmp_inp.source).replace('_surf.json','').replace('.json','')+ '_mapsurf.json'
                    else:
                        drop_path=output_name.replace('.json','')+'.json'
                    with open(drop_path,'w') as wr:
                        json.dump(drop_di, wr)
                    isod=drop_di['meta']['iso_density_value']
                    num_vertices=drop_di['meta']['num_vertices']
                    num_faces=drop_di['meta']['num_faces']
                    try:
                        spacing=drop_di['meta']['grid_spacing']
                    except Exception as ex:
                        print('Key spacing is not in info')
                        spacing=None
                    results['files']['esp-maps'].update({drop_path:{
                        'isodensity_value':isod,
                        'surface_file': input[i],
                        'spacing':  spacing,
                        'num_faces': num_faces,
                        'num_vertices': num_vertices,
                    }
                    })
                tmp_inp.remove_tmp()
            except Exception as ex:
                tmp_inp.remove_tmp()
                print(f"Removed temporary file {tmp_inp.file}")
                raise Ellipsis(ex)
        with open('results.yaml','w') as wr:        
            results.update({'timings':tracker.timings_dic(),'info':tracker.info_dic()})
            yaml.dump(results, wr)
        tmp_file.remove_tmp(verbose=True)
        return esp
    except Exception as ex:
        if os.path.isfile(tmp_file.temporary):
            tmp_file.remove_tmp(verbose=True)
        raise Exception(ex)

