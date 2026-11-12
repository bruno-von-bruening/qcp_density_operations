from pydantic import BeforeValidator
from typing import Annotated, List
from . import *

import subprocess as sp
from qcp_global_utils.environment.file_handling import temporary_file

def check_dir(string):
    assert os.path.isdir(string),f"Not a valid directory: {string}"
    return string
def check_file(string):
    assert os.path.isfile(string) or os.path.islink(string),f"Not a valid file or link: {string}"
    return string
def check_float_list(input):
    if isinstance(input, float):
        the_return=[ input ]
    elif isinstance(input, (list)):
        assert all([isinstance(x, float) for x in input]), f"Not a list of floats: {input}"
        the_return=input
    elif isinstance(input, np.ndarray):
        assert len(input.shape)==1, f"Not a one dimensional array: {input}"
        assert isinstance(input[0],float), f"Not a list of floats: {input.dtype}"
        the_return=input.tolist()
    assert isinstance(the_return, list),f"{check_float_list} is badly coded."
    return the_return

my_list_float=Annotated[ List[float], BeforeValidator(check_float_list)]
if False: # I should get that from qcp_global_utils
    pass 
    # directory=Annotated[str, BeforeValidator(check_dir)]
    # file=Annotated[str, BeforeValidator(check_file)]
else:
    from qcp_global_utils.pydantic.pydantic import pdtc_file, pdtc_directory

def run_shell_command(cmd):
    p=sp.Popen(cmd, shell=True, stdout=sp.PIPE, stderr=sp.PIPE)
    stdout, stderr= [x.decode('utf-8') for x in p.communicate()  ]
    if p.returncode!=0:
        raise Exception(f"Finished with error ({cmd}): stderr={stderr}")
    return stdout, stderr


# class temporary_file_base(BaseModel):
#     source: file
#     tmp_file: file | None
#     which:  str='tmp'
#     @property
#     def file(self):
#         which=self.which
#         if which in ['tmp', 'temporary']:
#             assert self.tmp_file is not None, f"Excepected to use temporary file but none has been define"
#             return self.tmp_file
#         elif which in ['orig','original','source']:
#             return self.source
#     def check(self):
#         assert os.path.isfile(self.source), f"Source file corrupted ({self.source} is not a file): quiting for safety"
#         assert os.path.realpath(self.source)!=os.path.realpath(self.tmp_file), f"error in this class tmp_file is source file, dangerous since source could be destroyed"
#         return True

# class temporary_file(temporary_file_base):
#     def __init__(self, fi):
#         # In case its a symlink copy to local dir
#         source=fi
#         tmp_file=None
#         info=self.handle_source(source)
#         super().__init__(**info)
# 
#     def handle_source(self,source):
#         # If its a link unlink first
#         tmp_file=source
#         if os.path.islink(tmp_file):
#             old_file=tmp_file
#             tmp_file='tmp.'+os.path.basename(tmp_file)
#             run_shell_command(f"cp {os.path.realpath(old_file)} {tmp_file}")
#             assert os.path.isfile(tmp_file), f"Expected but does not exist: {tmp_file} (pwd: {os.getcwd()})"
#             which='tmp'            
# 
#         ## Unpack 
#         if tmp_file.endswith('.gz'):
#             fi_zipped=tmp_file
#             p=sp.Popen(f"gunzip {fi_zipped}", shell=True)
#             p.communicate()
#             tmp_file=fi_zipped.replace('.gz','')
#             assert os.path.isfile(tmp_file), f"Not a file: {tmp_file}"
#         if tmp_file.endswith('.xz'):
#             fi_zipped=tmp_file
#             p=sp.Popen(f"xz -d {fi_zipped}", shell=True)
#             p.communicate()
#             tmp_file=fi_zipped.replace('.xz','')
#             assert os.path.isfile(tmp_file), f"Not a file: {tmp_file}"
# 
#         # If the tmp file is the same as source, then there is no tmp_file
#         if os.path.realpath(tmp_file)==os.path.realpath(source):
#             tmp_file=None
#             which='source'
#         # Assert the file lies in this directory and it exists
#         if tmp_file is not None:
#             assert os.path.relpath(os.path.dirname(os.path.realpath(tmp_file)),os.getcwd())=='.', f"Tmp_file should be dropped in this directory, tmp_file={tmp_file}"
#             assert os.path.isfile(tmp_file)
# 
#         return dict(
#             source=source,
#             tmp_file=tmp_file,
#             which=which
#         )
# 
#     def remove_tmp(self, verbose=True):
#         if self.tmp_file is not None:
#             self.check()
#             cmd=f"rm {self.tmp_file}"
#             run_shell_command(cmd)
#             if verbose: print(f"Deleted temporary file {self.tmp_file}")
        


# @validate_call
# def process_file(fi:file):
#     """ Generate local temporary file, that is:
#         - if symlink: copied to local directory
#         - if gzipped: unzipped
#     """
    
