
from iodata import load_one
from gbasis.wrappers import from_iodata
from gbasis.evals.density import evaluate_density as gbasis_eval_dens

from grid.molgrid import MolGrid
from grid.becke import BeckeWeights
from grid.onedgrid import Trapezoidal
from grid.rtransform import LinearFiniteRTransform

from grid.onedgrid import GaussLegendre
from grid.rtransform import BeckeRTransform

def evaluate_density(mol_data, grid):
    ao_basis = from_iodata(mol_data)
    rdm = mol_data.one_rdms["scf"]
    rho = gbasis_eval_dens(rdm, ao_basis, grid)
    #rho_mesh=rho.reshape(tuple(shape))
    #points_mesh=grid.reshape( (*shape, 3) )
    return rho #points_mesh, rho_mesh

def make_integration_grid(mol_data):
    """ """
    n_rpoints = 200                         # Number of radial points
    oned_grid = GaussLegendre(npoints=n_rpoints)
    radial_grid = BeckeRTransform(0.0, R=1.).transform_1d_grid(oned_grid)

    #oned = Trapezoidal(n_rpoints)           # Trapezoidal grid of that size
    #rmin, R = 0.0, 0.5                      # Parameters for the Becke radial transform
    #rgrid = LinearFiniteRTransform(rmin, 10).transform_1d_grid(oned)
    aim_weights = BeckeWeights()

    atcoords = mol_data.atcoords
    atnums = mol_data.atnums

    molgrid = MolGrid.from_preset(atnums, atcoords, rgrid=radial_grid, preset="veryfine", aim_weights=BeckeWeights() )#, store=True)
    return molgrid.points, molgrid.weights