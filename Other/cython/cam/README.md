To compile:

    python3 setup.py build_ext --inplace

This will produce an cam.so library. To import it into the main python program copy it in the same folder and add:

    from . import cam

Call the definition:

    cam.check_alignment(image_data, threshold)
