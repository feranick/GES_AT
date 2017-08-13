# GES_AT
GridEdge Autotesting

## Dependencies
GridEdge Autotesting is written in `Python <http://www.python.org/>`_ and relies on the following libraries:
- [Python v.3.5/3.6](<http://www.python.org/>)
- [Qt5](<http://qt.io>)
- [PyQt version](<http://www.riverbankcomputing.co.uk/>) or [PySide](<https://wiki.qt.io/Category:LanguageBindings::PySide>)
- [Numpy >1.5](http://www.numpy.org/)
- [Scipy >0.9](<http://www.scipy.org/>)
- [Matplotlib >0.9] (<http://matplotlib.org/>) 

Additional libraries for images:
- [Pillow (for .tif, .png, .jpg)](https://python-pillow.github.io/>)

## Installing dependencies on Windows
The simplest way to get all the required python packages at once is to install the Python distribution [Anaconda](<https://www.continuum.io/downloads/>)

## Installing dependencies on Mac OSX
All required packages can be obtained through [MacPorts](<http://www.macports.org/>). After installing macports, individual libraries are installed with the following:

    sudo port install python3.6 +readline
    sudo port install py36-numpy, py36-scipy, py36-matplotlib, py36-pillow
    sudo port install opencv
    sudo port install qt5 py3.6-pyqt5
    sudo port install qt5-qtcreator
        
## Installing dependencies on Ubuntu Linux
    sudo apt-get update; sudo apt-get upgrade
    sudo apt-get install python3 python3-numpy python3-scipy
    sudo apt-get install python3-matplotlib python3-pil 
    sudo apt-get install qt5-default python3-pyqt5
    sudo apt-get install qtcreator
    sudo apt-get install opencv-data
    
## Installing dependencies on Microsoft Windows
Install python3 directly from [python.org](<http://www.python.org/>). You will use pip for installing most of the dependencies

    pip install numpy scipy matplotlib pillow
    pip install QtPy5 opencv-python
    
Install Qt5 from the [qt.io](https://www.qt.io/download/) directly. 
    
## Run
After downloading the zip-file extract its content to a directory. If you have already installed the dependencies, you are ready to go and can open the graphical user interface by running ``gridedge_AT_run.py``.
