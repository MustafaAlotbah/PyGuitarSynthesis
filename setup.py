from setuptools import setup, find_packages

setup(
    name='py_guitar_synth',
    version='0.1',
    description=
    'A Python package for synthesizing realistic guitar music from tab sheets using physical and musical modeling.',
    author='Mustafa Alotbah',
    author_email='mustafa.alotbah@gmail.com',
    url='https://github.com/MustafaAlotbah/PyGuitarSynthesis',
    packages=find_packages(),
    install_requires=[
        'numpy',
        'argparse',
        'soundfile',
    ],
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'guitar_synth = py_guitar_synth.__main__:main',
        ],
    },
    package_data={
        'py_guitar_synth': ['assets/*.wav', 'assets/*.json', 'assets/*.txt'],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Multimedia :: Sound/Audio',
    ],
    python_requires='>=3.6',
)
