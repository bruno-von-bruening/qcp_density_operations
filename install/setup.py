#!/usr/bin/env
import os, yaml
import subprocess as sp

home=os.path.realpath('..')

def setup_env_vars():
    env={'DENSITY_OPERATIONS_HOME':home}
    return env

def  env_setup_instructions(env):
    instructions=[
        f"export {k}=\"{v}\""
        for k, v in env.items()
    ]
    with open('add_to_shell_init.txt','w') as wr:
        wr.write('\n'+'\n'.join(['# paths for Densityb Operations pip module']+instructions)+'\n\n')

    indent=4*' '
    instructions='\n'.join([f"Add the following commands to your shell initialization:"]+[ indent +x for x in instructions])

    # COuld also be done by just runnig cat and appending to right script
    print(instructions)

def compile_f90():
    origin=os.getcwd()
    lib_path=os.path.join(home, 'lib')
    os.chdir(lib_path)

    script='compile.sh'
    cmd=f"bash compile.sh"
    p=sp.Popen( cmd, shell=True, stdout=sp.PIPE, stderr=sp.PIPE)
    stdout, stderr= [ x.decode() for x in p.communicate() ]
    
    if p.returncode!=0:
        raise Exception(f"Error in executing {cmd} (pwd={os.getcwd()}):\n {stderr}")
    print(f"Compiled F90 files")

    os.chdir(origin)
    return lib_path

def setup():
    lib_path=compile_f90()

    env=setup_env_vars()
    env.update({'DENSITY_OPERATIONS_LIB':lib_path})
    env_setup_instructions(env)

if __name__=='__main__':
    setup()