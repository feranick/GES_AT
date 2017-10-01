from setuptools import setup, find_packages

setup(
    name='GridEdgeAT',
    packages=find_packages(),
    install_requires=['numpy', 'matplotlib', 'pillow', 'PyQt5', 'ThorlabsPM100', 'pyvisa', 'opencv-python', 'pandas', 'requests'],
    entry_points={'gui_scripts' : ['gridedgeat=GridEdgeAT.__main__:main']},
    package_data={ 'GridEdgeAT': ['gridedgeat/rsrc/*.png'],},
    version='0.6.1',
    description='Automated measurements of Current/Voltage profiles for photovoltaic solar cells',
    long_description= """ Measurements of Current/Voltage profiles for photovoltaic solar cells """,
    author='Nicola Ferralis',
    author_email='ferralis@mit.edu',
    url='https://github.com/feranick/GES_AT/tree/master/GES-AT',
    download_url='https://github.com/feranick/GES_AT/archive/0.6-20170928b.zip',
    keywords=['PV', 'devices', 'testing'],
    license='GPLv2',
    platforms='any',
    classifiers=[
     'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
     'Development Status :: 5 - Production/Stable',
     'Programming Language :: Python',
     'Programming Language :: Python :: 3',
     'Programming Language :: Python :: 3.5',
     'Programming Language :: Python :: 3.6',
     'Intended Audience :: Science/Research',
     'Topic :: Scientific/Engineering :: Chemistry',
     'Topic :: Scientific/Engineering :: Physics',
     ],
     include_package_data=True,
)
