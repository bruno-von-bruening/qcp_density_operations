conda_env='qcDENS'
conda_file='install/qcDENS_env.yaml'
dependencies=("PROPERTY_OBJECTS_HOME" "QC_GLOBAL_UTILITIES")

if [ ! -f ${conda_file} ]; then
   echo "The file \'${conda_file}\' does not exist"
   exit
fi

source install/setup_ext.sh

paths="$(get_paths_for_dependencies ${dependencies[@]})"
if [[ $? != 0 ]]; then
   echo "Error processing dependencies (${dependencies[@]}): ${paths}"
   exit
fi
paths=( ${paths} ) 
echo You gave the Dependencies: ${dependencies[@]}
echo Following paths were found for them: ${paths[@]}

source activate base
conda init bash 

conda remove -n ${conda_env} --all
conda env create -f ${conda_file}

conda activate ${conda_env}
if [[ $? != 0 ]]; then
   echo "Cannot activate conda environment ${conda_env}"
   exit
fi


install_pip_projects '.' ${paths[@]}
if [[ $? != 0 ]]; then
   echo "Error in installing pip dependencies"
   exit
fi

