from qc_global_utilities.pydantic.pydantic import file, directory, my_list
from pydantic import validate_call
validate_call=validate_call(config=dict(arbitarty_types_allowed=True))
from typing import List


import yaml