

# Install fortran lib
**Reason for fortran code:**
I have type-bound fortran code since its much faster (maybe 10 times) than python numpy for my integral evaluation (but
maybe I am also using numpy suboptimal).

**How it is installed:**
In setup.py I call a compile script in bash (this will be a problem in windows.)
This furthermore drops it automatically into the pip install location (for both editable and standard install)
It is then loaded in `src/qcp_density_operations/calc_esp/calc_esp.py:get_fortran_lib()`
*Note: setup.py code is based on AI solution.*

**TODO: Possible Fallback**
Automatically fallback to numpy integration. Maybe could make a class with fort_lib_there bool property.
