from warnings import warn

@pytest.mark.order(0)
def test_fortlib_installed():
    from qcp_density_operations.density_eval.calc_esp.calc_esp import get_fortran_lib
    try:
        lib_path=get_fortran_lib()
        assert os.path.isfile(lib_path), f"Found fort lib, but not a file: {lib_path}"
        assert lib_path.endswith('.so'), f"Expected fort lib to have \'.so\' extension, got: {lib_path}"
    except Exception as ex:
        warn(f"Fortran lib not installed, that means you need to use slow numpy engine")
