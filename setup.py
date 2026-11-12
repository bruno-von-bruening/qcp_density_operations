from setuptools import setup
from setuptools.command.build_py import build_py
import subprocess
import os
import shutil
# Does not work with python <3.11
# from contextlib import chdir


class CustomBuild(build_py):
    def run(self):
        # Run Fortran compilation

        # Copy into source dir, then it will also work in editable mode!
        # Assumes that setup.py is in toplevel!
        project_dir = os.path.dirname(os.path.abspath(__file__))

        target_source = os.path.join(
                    project_dir,
                    "src",
                    "qcp_density_operations"
             )


        origin=os.getcwd()
        #with chdir('lib'):
        os.chdir('lib')
        if True:
            subprocess.run(
                ["bash", "compile.sh"],
                check=True
            )
            lib_file='libcalcesp.so'
            assert os.path.isfile(lib_file), f"No file : {lib_file}"
            lib_file=os.path.realpath(lib_file)
        os.chdir(origin)
        shutil.copy(
            lib_file,
            os.path.join(target_source, os.path.basename(lib_file))
        )

        # Build Python package
        super().run()

        # Copy compiled executable into package

        if True:
            # Also copy into build
            target_build=os.path.join(
                os.path.realpath(self.build_lib), 'qcp_density_operations'
            )
            shutil.copy(
                lib_file,
                os.path.join(target_build, os.path.basename(lib_file))
            )

setup(
    name="qcp_density_operations",
    # version="0.1.0",
    package_dir={"": "src"},
    packages=["qcp_density_operations"],
    cmdclass={"build_py": CustomBuild},
)
