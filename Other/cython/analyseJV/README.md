To compile:

    python3 setup.py build_ext --inplace


This will produce an analyseJV.so library. To import it into the main python program copy it in the same folder and add:

    from . import analyseJV

Call the definition:

    analyseJV.analyseJV(JV)
