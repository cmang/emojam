from setuptools import setup
#from setuptools import find_packages

with open("README.md") as f_readme:
    long_description = f_readme.read()

setup(
    name='emojam',
    version='0.1.10',
    author='Sam Foster',
    author_email='samfoster@gmail.com',
    description='A lighweight emoji picker for X-Windows',
    long_description = long_description,
    #py_modules=["PyGObject"],
    url='https://github.com/cmang/emojam',
    license='GPLv3',
    # package_dir={'': 'emojam'},
    packages=['emojam'],
    install_requires=["PyGObject"],
    include_package_data = True, 
    # package_data = ["emojis.csv"], # emoji_sets/emojis.csv
    data_files = [
        ('share/icons', ['data/emojam.png']),
        ('share/applications', ['data/emojam.desktop']),
    ],
    classifiers=[
        'Environment :: X11 Applications :: GTK',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Operating System :: POSIX',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Desktop Environment',
        'Topic :: Utilities'
        'Private :: Do Not Upload',
    ],
    entry_points={
    'console_scripts': [
        'emojam = emojam.main:main',
    ],
},
)

