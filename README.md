# density_operations
Operations based on density evaluations

# Installations

```bash
conda enc create -f qcDENS_env.yaml
python3 -m pip install --upgrade build
python3 -m build; python3 -m pip install .

python -m pip install qc-gbasis
python -m pip install qc-iodata
```
When running the python code with fortran interfacing:
```bash
cd lib/
bash compile.sh
```
This should generate an dynamic library (file with '.so' extension).
Create an environment variable to allow the python installation to access it
```
# 
export DENSITY_OPERATIONS_LIB=<path-to-lib/>
```
Consider that this environment variable may need to be loaded.

# Tests
Run
```bash
    pytest
```

There will be a warning from the `qc-grid` package in `atomgrid` about negative weights, but this has not caused a
problem yet. As I remember this occurs for large angular grids.


# TODO
- [ ] Compile and install the fortran library independently. (Just ask AI how to do that)
