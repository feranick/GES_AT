# GridEdge Autotesting
Fully automated control software for acquisition of near-certification performance data for solar photovoltaic devices. It works in combination with the GridEdge Autotesting system developed at MIT. 

## Installation:
The software can be run "offline", meaning without being connected to the hardware, for example to load data, etc. The dependencies needed for running the "online" version (i.e. to be able to control the acquisition hardware) are listed as such below. These are not needed for running the "offline" version. If you are planning to use this software for "offline" use on your computer, do not install the "online" dependencies. The software automatically recognizes the presence (or lack thereof) of the required dependencies for online/offline use.

### Dependencies
GridEdge Autotesting is written in [Python 3.x](<http://www.python.org/>) and relies on the following libraries:
- [Python v.3.5/3.6](<http://www.python.org/>)
- [Qt5](<http://qt.io>)
- [PyQt version 5](<http://www.riverbankcomputing.co.uk/>)
- [Numpy >1.5](http://www.numpy.org/)
- [Scipy >0.9](<http://www.scipy.org/>)
- [Matplotlib >0.9](<http://matplotlib.org/>)
- [Pandas](<https://pandas.pydata.org/>)
- [OpenCV >3.2](<http://opencv.org/>)
- [Pillow (for .tif, .png, .jpg)](https://python-pillow.github.io/>)
- [PyVisa](<https://pyvisa.readthedocs.io/en/stable/index.html>)
- [ThorlabsPM100-PyPi](<https://pypi.python.org/pypi/ThorlabsPM100>) - [ThorlbsPM100-official](<https://www.thorlabs.com/software_pages/viewsoftwarepage.cfm?code=PM100x>) The drivers for Windows as well as the Python library are needed
- [FTDI drivers](<http://www.ftdichip.com/Drivers/D2XX.htm>) - This is to control the shutter via TTL using a [TTL-232R-5V](<http://www.ftdichip.com/Support/Documents/DataSheets/Cables/DS_TTL-232R_CABLES.pdf>) USB cable.

### Installing dependencies on Mac OSX
All required packages can be obtained through [MacPorts](<http://www.macports.org/>). After installing macports, individual libraries are installed with the following:

    sudo port install python3.6 +readline
    sudo port install py36-numpy, py36-scipy, py36-matplotlib, py36-pillow, py36-pandas
    sudo port install opencv +python36
    sudo port install qt5 py3.6-pyqt5
    (optional) sudo port install qt5-qtcreator
        
### Installing dependencies on Ubuntu Linux
    sudo apt-get update; sudo apt-get upgrade
    sudo apt-get install python3 python3-numpy python3-scipy
    sudo apt-get install python3-matplotlib python3-pil python3-pandas
    sudo apt-get install qt5-default python3-pyqt5
    sudo apt-get install qtcreator
    (optional) sudo apt-get install opencv-data
    
### Installing dependencies on Microsoft Windows
The simplest way to get all the required python packages at once is to install the Python 3 distribution from [python.org](<http://www.python.org/>) (recommended) or from [Anaconda](<https://www.continuum.io/downloads/>). You will use ```pip``` for installing most of the dependencies.

    pip install numpy scipy matplotlib pillow pandas
    pip install pyqt5 opencv-python

Install Qt5 from the [qt.io](https://www.qt.io/download/) directly.

### "Online" dependencies for hardware control:
    pip install pyvisa ThorlabsPM100 requests ftd2xx pywin32
    
### Creating a wheel package for redistribution
In order to satisfy all dependency and at the same time have a seamless experience, assuming ```python 3```, ```pip``` and ```wheel``` are installed, one can create a wheel package that can be used for seamless installation. To create the wheel package:

    cd /UI
    python3 setup.py bdist_wheel
    
A wheel package is created inside a new folder ```dist```. On UNIX-systems the package can be installed simply as user by:

    pip3 install --upgrade --user <package.whl>
    
or system-wide:

    sudo pip3 install --upgrade <package.whl>
    
On MS Windows:

    pip install --upgrade <package.whl>

## Run
After downloading the zip-file extract its content to a directory. If you have already installed the dependencies, you are ready to go.

### Linux/Mac OSX
From the terminal, run: ```python3 gridedge_AT_run.py```
    
### Windows
From the terminal, run: ```python gridedge_AT_run.py```
Alternatively, launch by double clicking the file ```gridedge_AT_windows.bat```

## User Manual
It can be found in the User Manual folder within the repo or [online as a google doc](https://docs.google.com/document/d/13y0wFV21d75kd37jS3CpJvZL-_ImOJHvAZBCXCPn-OQ/edit?usp=sharing>).

## Features
- Pressing ALT while starting the acquisition will temporarily enable saving acquisition data locally
- After acquisition, right click on a device in the table in Results allows for saving locally the corresponding data.
- A substrate in the substrate panel can be exluded from the acquisition through a right click. The corresponding cell when disables appears with a red background.
- Double click on a device in the table in Results will open the default browser in the Data Management page with the corresponding substrate info.
- Devices can be removed form the sample list by selecting "Remove..." from the right click menu on the result table.

## Release History
Pre-release, beta and stable releases are available in [github](https://github.com/feranick/GES_AT/releases).

