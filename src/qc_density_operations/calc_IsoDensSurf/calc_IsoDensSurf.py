
from . import *
import numpy as np #, pandas as pd
import os,sys,re,copy, time #log,copy
import shutil, glob, json
from functools import partial

from iodata import load_one
from gbasis.wrappers import from_iodata
from gbasis.evals.density import evaluate_density as gbasis_eval_dens
from skimage import measure

#sys.path.insert(1, os.environ['SCR'])
#import modules.mod_utils as m_util

def generate_grid(coordinates, grid_space=0.1, margin_size=5):
    """ Takes data of molecules """

    # The usual numpy indexing is  z,x,y (this would require remapping later), to avoid that we just use the regular indexing
    my_mesh=partial(np.meshgrid, indexing='ij')

    # Get minimum and maximum values between 
    mins=np.min(coordinates, axis=0)-np.ones(3)*margin_size
    maxs=np.max(coordinates, axis=0)+np.ones(3)*margin_size
    distance=maxs-mins

    #x_vals, y_vals, z_vals=[ np.linspace(min, max, num=int(max-min/params['grid_space']), endpoint=True, dtype=np.float32 ) for min, max  in zip(mins,maxs)]
    x_vals, y_vals, z_vals=[ np.arange(min, max, grid_space, dtype=np.float64 ) for min, max  in zip(mins,maxs)]
    #shape=[len(x) for x in [x_vals, y_vals, z_vals]]

    points_mesh=my_mesh(x_vals, y_vals, z_vals)
    x_vals, y_vals, z_vals = [ val.flatten() for i,val in enumerate(points_mesh) ]
    points=np.array([x_vals, y_vals, z_vals]).T

    # could filter points
    dims= np.array([ [(c(x)) for x in [x_vals, y_vals, z_vals] ] for c in [min,max] ])
    return points, points_mesh, dims 

def evaluate_density(mol_data, grid, slice_size=5.e4):
    ao_basis = from_iodata(mol_data)
    rdm = mol_data.one_rdms["scf"]
    ### Do to memory reason we should evaluate the density slice wise (process dies for too large grids)
    print(f"Slice size is {slice_size}, in case this process crashes reduce this number (smaller memory usage)")
    if len(grid)>slice_size:
        rho=[]
        slices=[ [ int(j*slice_size),  int(min( (j+1)*slice_size,len(grid))) ] for j in range(int(len(grid)/slice_size)+2) if (j)*slice_size<len(grid)]
        for slice in slices:
            print(f"Computing slice of density evaluation: {slice}")
            rho+=gbasis_eval_dens(rdm, ao_basis, grid[slice[0]:slice[1],:]).tolist()
        rho=np.array(rho)
    else:
        rho = gbasis_eval_dens(rdm, ao_basis, grid)
    return rho #points_mesh, rho_mesh

def marching_cubes(rho_mesh, iso_dens):
    verts, faces, normals, values = measure.marching_cubes(rho_mesh, iso_dens)
    return verts, faces

def drop_surface(mol_data, verts, faces, grid_spacing, iso_dens_val, file_name=None, fchk_file=None):
    
    if isinstance(fchk_file, type(None)):
        raise Exception()
    # Get multiplicity
    #fchk_file=m_util.process_file(fchk_file)
    with open(fchk_file,'r') as rd:
        lines=rd.readlines()
        results=[ i for i,l in enumerate(lines) if l.startswith('Multiplicity')]
        assert len(results)==1
        try:
            multiplicty=int(lines[results[0]].split()[2])
        except Exception as ex:
            raise Exception(f"Cannot find valid integer multiplicty on line {lines[results[0]]}")
    data={
        'data_type':'surface',
        'vertices':verts.tolist(),
        'faces':faces.tolist(),
        'length_units': 'BOHR',
        'molecule':{
            'coordinates':mol_data.atcoords.tolist(),
            'nulcear_charges':mol_data.atnums.tolist(),
            'molecular_charge':int(mol_data.charge),
            'multiplicty':multiplicty,
        },
        'meta':{    # Info that is not existential but may be helpful
            'surface_type':'iso_density',
            'density_source':[fchk_file],
            'grid_spacing': float(grid_spacing),
            'iso_density_value': float(iso_dens_val),
            'num_vertices':len(verts),
            'num_faces':len(faces),
            'info_comment':'Vertices are the points of the surface and faces define the connection between them (as triangles of their indices)'
        },
    }
    file_name=drop_file(file_name, data)
    return file_name


def drop_file(file_name, the_data):
    if isinstance(file_name, type(None)):
        file_name='dummy_surface.json'
    the_drop_file=file_name.replace('.json','')+'.json'
    with open(the_drop_file, 'w') as wr:
        json.dump(the_data, wr)
    return the_drop_file

def do_marching_cubes(rho, grid_mesh, dims, isod, grid_dens):

    the_shape=grid_mesh[0].shape
    x_len=the_shape[1]
    z_len=the_shape[0]
    y_len=the_shape[2]
    
    rho_mesh=np.array(rho).reshape(grid_mesh[0].shape)
    verts,faces, = marching_cubes(rho_mesh, isod)
    origin=dims[0]
    stretch=dims[1]-dims[0]
    #weight=params['grid_space']**3
    #raise Exception(dims, verts[0],len(grid_mesh[0]), grid_mesh[0].shape, grid_mesh[1].shape, grid_mesh[2].shape )
    correction_vector=np.array(rho_mesh.shape)-np.ones(3)
    verts_coor=verts/correction_vector #(np.array(grid_mesh[0].shape[:3]-np.ones(3)))
    print(min(verts_coor[:,0]), max(verts_coor[:,0]), dims)
    print(min(verts_coor[:,1]), max(verts_coor[:,1]), dims)
    print(min(verts_coor[:,2]), max(verts_coor[:,2]), dims)
    verts_coor=origin+verts_coor*stretch
    print('AFTER', min(verts_coor[:,0]), max(verts_coor[:,0]), dims)
    print('AFTER', min(verts_coor[:,1]), max(verts_coor[:,1]), dims)
    print('AFTER', min(verts_coor[:,2]), max(verts_coor[:,2]), dims)

    #Check if any vertice is close to a box
    if len(verts_coor)==0:
        raise Exception(f"No surface produced, likely the box is too small")
    else:
        for dim in dims:
            box_dist=verts_coor-dim
            box_dist=np.min( np.abs(box_dist)  )
            if box_dist<2*grid_dens:
                raise Exception(f"Point to close to box limits ({dims}): {box_dist}")
    return verts_coor, faces


def make_file_name(fchk_file, grid_dens, isod):
    """ Make name for output file. This routine should be accessible to my scripts """
    grid_dens_key=str(grid_dens).replace('.','p')
    isod_key=str(isod).replace('.','p')
    output_name_gen=os.path.basename(fchk_file).split('.')[0]+f"_gs{grid_dens_key}-isod{isod_key}-surf" 
    return output_name_gen
@validate_call
def drop_data(results, output_name, mol_data, real_verts_coor, faces, grid_dens, isod, fchk_file,
    convention:str='qcobject'):
    if convention=='qcobject':
        try:
            from qc_objects.objects.grids import molecular_isodensity_grid
            grid=molecular_isodensity_grid(input_file=None, output_file=None, vertices=real_verts_coor, faces=faces, length_units='BOHR',
                                    iso_density_value=isod)
        except Exception as ex:
            raise Exception(f"Could not populate {molecular_isodensity_grid.__name__}: {ex}")
        data=grid.model_dump()
    else:
        raise Exception(f"Convention not defined: {convention}")
        output_name_gen=drop_surface(mol_data, real_verts_coor, faces, grid_dens, isod, fchk_file=fchk_file, file_name=output_name_gen)
    output_name_gen=drop_file(output_name,data)
    results['files']['grids'].update({isod:os.path.realpath(output_name_gen)})
    return results

@validate_call
def IsoDensSurf(
    fchk_file:file, grid_spacing:my_list_float|None=None, iso_dens:my_list_float|None=[0.001], do_plot=False, faces=None, drop=True, output_name=None, test=False
):
    start=time.time()
    def process_grid_spacings(grid_spacing, iso_dens):
        if isinstance(grid_spacing, type(None)):
            grid_dens_def={
                1:0.1,
                0.001: 0.2,
                0.0001: 0.3,
                0.00001: 0.5,
            }
            grid_spacing=[min([grid_spac for the_isod, grid_spac in grid_dens_def.items() if the_isod<=isod])  for isod in iso_dens]
        else:
            assert len(grid_spacing)==len(iso_dens), f"Expected same number of grid_spacing as iso density values: {grid_spacing} {iso_dens}"
        return grid_spacing
    def make_grid_di(grid_spacing, iso_dens):
        grid_di={
        }
        for grid_dens, isod in zip(grid_spacing, iso_dens):
            if not grid_dens in grid_di.keys():
                grid_di.update({grid_dens:[]})
            grid_di[grid_dens].append(isod)
        # Sort dict
        grid_di=dict(  sorted(list(grid_di.items()), key=lambda x:x[0], reverse=True)  )
        print_info=True
        if print_info:
            print(f"Will compute following iso_density grids with corresponding iso density values:")
            for gs, isdens in grid_di.items():
                print(f"    {gs} : "+ ' , '.join([f"{x}" for x in isdens]))
        return grid_di
    def get_margin(iso_densities):
        margin_di={
            1:4,
            0.002:5,
            0.0005:6,
            0.0002:7,
            0.0001:8,
        }
        margin_size=max([marg for the_isod, marg in margin_di.items() if marg>=min(iso_densities)])
        return margin_size
    
    print(f"All units are in au")
    results={
        'files':{'grids':{}},
        'isodensities':[],
        'spacings':[],
    }


    # Molecule data
    #fchk_file=m_util.process_file(fchk_file) # in case symlink etc.
    from qc_density_operations.util.environment import temporary_file
    tmp_fchk=temporary_file(fchk_file)

    try:
        mol_data = load_one(tmp_fchk.file)
        coordinates = mol_data.atcoords
        atnums = mol_data.atnums

        # Check that length of gridspacings and isodenstiy is identical
        grid_spacing=process_grid_spacings(grid_spacing, iso_dens)
        
        # Make dictionary assigning grid spaces and iso-densities (avoid repeating expensive grid calculations)
        grid_di=make_grid_di(grid_spacing, iso_dens)

        
        for grid_dens, iso_densities in grid_di.items():

            # Make box size iso_dens dependant
            margin_size=get_margin(iso_densities)

            ### Make the grid according to the given spacing        
            start=time.time()
            grid, grid_mesh,dims =generate_grid(coordinates=coordinates, grid_space=grid_dens, margin_size=margin_size)
            print(f"Grid gen (grid_dens={grid_dens}): {time.time()-start} (length={len(grid)})")
            ### Evaluate density
            start=time.time()
            slice_size=5e+4
            rho=evaluate_density(mol_data, grid, slice_size=slice_size)
            print(f"Eval dens (grid_dens={grid_dens}): {time.time()-start}")

            ### Marching cubes for the given density
            for isod in iso_densities:
                results['isodensities'].append(isod)
                results['spacings'].append(grid_dens)

                start=time.time()
                real_verts_coor, faces=do_marching_cubes(rho,grid_mesh, dims, isod, grid_dens)


                print(f"Marching cubes (grid_dens={grid_dens}, iso_dens={isod}): {time.time()-start}")

                # Grid_mesh to grid
                #real_verts_coor=np.array([ dims[0]+(dims[1]-dims[0])*x for x in abstrcat_verts_coor ])

                if do_plot:
                    import matplotlib.pyplot as plt
                    from mpl_toolkits.mplot3d.art3d import Poly3DCollection
                    fig = plt.figure(figsize=(10, 10))
                    ax = fig.add_subplot(111, projection='3d')

                    lims=np.array(dims).T
                    ax.set_xlim(*lims[0])  # a = 6 (times two for 2nd ellipsoid)
                    ax.set_ylim(*lims[1])  # b = 10
                    ax.set_zlim(*lims[2])  # c = 16

                    mesh = Poly3DCollection(real_verts_coor[faces])
                    mesh.set_edgecolor('k')
                    ax.add_collection3d(mesh)

                    #plt.tight_layout()
                    plt.show()
                
                if drop:
                    if isinstance(output_name,type(None)):
                        output_name_gen= make_file_name(fchk_file, grid_dens, isod)
                    else:
                        output_name_gen=output_name
                    results=drop_data(results, output_name, mol_data, real_verts_coor, faces, grid_dens, isod, fchk_file)
        with open('results.json','w') as wr:        
            json.dump(results, wr)
        tmp_fchk.remove_tmp()
        print(f"Took {time.time()-start} seconds")

        return real_verts_coor, faces
    except Exception as ex:
        print(f"Catched extension, deleting temporary_file")
        tmp_fchk.remove_tmp()
        raise Exception(f"Error: {ex}")



