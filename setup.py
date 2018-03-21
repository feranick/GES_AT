from setuptools import setup, find_packages

setup(
    name='GridEdgeAT',
    packages=find_packages(),
    install_requires=['numpy', 'matplotlib', 'pillow', 'PyQt5', 'scipy',
                      'pyvisa', 'opencv-contrib-python', 'pandas', 'requests', 'pymongo',
                      'ftd2xx;platform_system=="Windows"', 'pywin32;platform_system=="Windows"',
                       'ThorlabsPM100;platform_system=="Windows"'],
    entry_points={'gui_scripts' : ['gridedgeat=GridEdgeAT.__main__:main']},
    package_data={ 'GridEdgeAT': ['gridedgeat/rsrc/*',
                      'gridedgeat/modules/switchbox/*.scr','gridedgeat/modules/xystage/APT.*'],},
    include_package_data=True,
    version='0.35.0',
    description='Automated measurements of Current/Voltage profiles for photovoltaic solar cells',
    long_description= """ Control software for automated measurements of Current/Voltage profiles, device tracking for photovoltaic solar cells """,
    author='Nicola Ferralis',
    author_email='ferralis@mit.edu',
    url='https://github.com/feranick/GES_AT/tree/master/GES-AT',
    download_url='https://github.com/feranick/GES_AT/releases',
    keywords=['Photovoltaics', 'devices', 'JV', 'tracking', 'testing'],
    license='GPLv3',
    platforms='any',
    classifiers=[
     'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
     'Development Status :: 4 - Beta',
     'Programming Language :: Python :: Only',
     'Programming Language :: Python :: 3',
     'Programming Language :: Python :: 3.5',
     'Programming Language :: Python :: 3.6',
     'Intended Audience :: Science/Research',
     'Topic :: Scientific/Engineering :: Chemistry',
     'Topic :: Scientific/Engineering :: Physics',
     ],
)
