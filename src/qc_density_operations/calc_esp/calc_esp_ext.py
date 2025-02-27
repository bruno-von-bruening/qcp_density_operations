from . import *

def process_input(input):
    vertices, points, input_type =[None, None, None]
    @validate_call
    def check_file(input:file):
        if input.lower().endswith('.json'):
            input_type='surface.json'
            with open(input, 'r') as rd:
                content=json.load(rd)
            try:
                vertices=content['vertices']
                faces=content['faces']
            except Exception as ex:
                raise Exception(f"Cannot read content of file {input}: {ex}")
        else:
            raise Exception(f"File does not end with .json: {input}")
        return vertices, faces, input_type
    if isinstance(input, str):
        vertices, faces, input_type=check_file(input)
    elif isinstance(input, dict):
        assert all([x in input.keys() for x in ['vertices','faces']])
        vertices=input['vertices']
        faces=input['faces']
    elif isinstance(input, (list, type(np.array([])))):
        vertices=input
    else:
        raise Exception(f"Invalid type of vertices {type(vertices)}")
    

    return np.array(vertices), np.array(faces), input_type
@validate_call
def esp_calc(points, integration_points, integration_weights, density, engine='fortran', calc_lib: file|None=None):

    print(f"Number of points {len(points)}, number of density points {len(density)}")
    import numpy as np
    if engine=='fortran':
        import ctypes

        assert calc_lib is not None, f"For {engine} an so file is expected"
        flib= ctypes.cdll.LoadLibrary(calc_lib)

        calc_esp_f90 = flib.calculate_esp

        ar_ty=ctypes.POINTER(ctypes.c_double)
        calc_esp_f90.argtypes= [ 
            # legnth , eval_points, integration_points, integration_weights, density, esp
            ctypes.c_int, ctypes.c_int, ar_ty, ar_ty, ar_ty, ar_ty, ar_ty ]
        #calc_esp_f90.restype = ctypes.c_double

        esp=[0.0 for i in range(len(density)) ]
        array_type=ctypes.c_double * len(points)
        def nparray_to_ctypes(array):
            array=copy.deepcopy(array)
            shape=array.shape
            data_type=ctypes.c_double
            for x in list(shape)[::-1]:
                data_type=(data_type*x)
            array = (data_type)(*array)# (*(tuple(i) for i in array))
            return array
        points_c=nparray_to_ctypes(points.reshape(-1))
        integration_points_c=nparray_to_ctypes(integration_points.reshape(-1))
        integration_weights_c=nparray_to_ctypes(integration_weights.reshape(-1))
        density_c=nparray_to_ctypes(density.reshape(-1))
        esp=nparray_to_ctypes(np.array([0.0 for x in range(len(points))]))
        
        calc_esp_f90( int(len(points)), len(density), points_c, integration_points_c, integration_weights_c, density_c, esp)
        esp=np.ctypeslib.as_array(esp, shape=None)
    elif engine=='numpy':
        esp=[]
        for position in points:
            distances=integration_points-position
            distances=np.linalg.norm(distances, axis=1)
            distances=np.reciprocal(distances)
            distances[distances > 1000] = 0.
            
            elst=distances * density
            elst=np.dot(elst, integration_weights)
            esp.append(elst)
        esp=np.array(esp)
    else:
        raise Exception(f"Modus is not valid: {modus}  -> choose from {avail_modi}")




    #average.argtypes= [ ctypes.POINTER(ctypes.c_double), ctypes.c_int ]
    #average.restype= ctypes.c_double
    #values= [1., 2. ,30.]
    #array_type = ctypes.c_double * len(values)
    #values_c = array_type( * values )
    #b = average( values_c, 3)


    #values_np = np.array(values)
    #values_c = values_np.ctypes.data_as(ctypes.POINTER(ctypes.c_double))

    #b =average( values_c , 3)



    ##############
    return esp