# density_operations
Operations based on density evaluations. 

* Compute iso-density surfaces
* Evaluates ESP for a given surface
* Evaluate multipolar ESP for a given surface.

Using the qc-grid[^1] and qc-basis[^2] packages for density evaluations.



# Installations

```bash
conda env create -f qcp_dens_env.yml
pip install . 
```

This should automatically install the fortran library (altough this currently only works on linux).
For windows and macos users I might have to find a solution ther.
Manually this would be compiled through:
```bash
cd lib/
bash compile.sh
```
This generates an dynamic library (file with '.so' extension).

# Tests
Run
```bash
    pytest
```

There will be a warning from the `qc-grid` package in `atomgrid` about negative weights, but this has not caused a
problem yet. As I remember this occurs for large angular grids.


# TODO
- [x] Compile and install the fortran library independently. (Just ask AI how to do that)
- [ ] Make this run on Windows, MacOS!

[^1]: Tehrani, A.; Yang, X. D.; Martínez-González, M.; Pujal, L.; Hernández-Esparza, R.; Chan, M.; Vöhringer-Martinez, E.; Verstraelen, T.; Ayers, P. W.; Heidar-Zadeh, F. Grid: A Python library for molecular integration, interpolation, differentiation, and more. *The Journal of Chemical Physics* **2024**, 160 (17). https://doi.org/10.1063/5.0202240.
See github project: https://github.com/theochem/grid/

[^2]: Kim, T. D.; Pujal, L.; Richer, M.; Van Zyl, M.; Martínez-González, M.; Tehrani, A.; Chuiko, V.; Sánchez-Díaz, G.; Sanchez, W.; Adams, W.; Huang, X.; Kelly, B. D.; Vöhringer-Martinez, E.; Verstraelen, T.; Heidar-Zadeh, F.; Ayers, P. W. GBasis: A Python library for evaluating functions, functionals, and integrals expressed with Gaussian basis functions. *The Journal of Chemical Physics* **2024**, 161 (4). https://doi.org/10.1063/5.0216776.
See github project: https://github.com/theochem/gbasis

