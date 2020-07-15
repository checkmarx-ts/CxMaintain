from setuptools import setup

_version = '0.0.1'

install_requires=[
    'PyInquirer',
    'requests',
    'docopt',
    'pyyaml',
    'pyjwt',
    'python-dateutil'
]

tests_require=[
    'pytest',
    'mock'
]

setup(
    name='cxmaintain',
    version=_version,
    description='Checkmarx CxSAST 9.0 Retention Helper',
    url='https://github.com/checkmarx-ts/CxDir',
    author='Checkmarx TS-APAC',
    author_email='TS-APAC-PS@checkmarx.com',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: System Administrators',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: GPL-3.0-only',
        'Programming Language :: Python :: 3.8',
    ],
    keywords='Checkmarx Maintenance helper',
    packages=['cxmaintain', 'cxmaintain.auth', 'cxmaintain.utils', 'cxmaintain.retention'],
    python_requires='>=3.7',
    install_requires=install_requires,
    extras_require={
        'tests': install_requires + tests_require,
    },
    package_data={'cxdir': ['templates/*']},
    entry_points={'console_scripts': ['cxmaintain=cxmaintain.cxmaintain:main']}
)
