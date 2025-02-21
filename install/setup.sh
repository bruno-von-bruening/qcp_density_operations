conda_env='qcDENS'
conda_file='install/qcDENS_env.yaml'

if [ ! -f ${conda_file} ]; then
   echo "The file \'${conda_file}\' does not exist"
   exit
fi

source activate base
conda init bash 

conda remove -n ${conda_env} --all
conda env create -f ${conda_file}

conda activate ${conda_env}
if [[ $? != 0 ]]; then
   echo "Cannot activate conda environment ${conda_env}"
   exit
fi

install_pip_project() {
   dir=$1
   if [ ! -d ${dir} ]; then
      print "Provided argument ${dir} is not a directory"
      exit
   fi
   old_dir=$(pwd)
   cd ${dir}

   conda run -n ${conda_env} python -m pip install --upgrade build
   conda run -n ${conda_env} python -m build
   conda run -n ${conda_env} python -m pip install .

   cd ${old_dir}
}

install_pip_project '.'
install_pip_project "$PROPERTY_OBJECTS_HOME"

