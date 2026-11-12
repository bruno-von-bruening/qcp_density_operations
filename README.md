# density_operations
Operations based on density evaluations

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
