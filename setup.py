import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.txt')) as f:
    README = f.read()
with open(os.path.join(here, 'CHANGES.txt')) as f:
    CHANGES = f.read()

requires = [
    'SQLAlchemy==1.3.18',
    'psycopg2',
    'psycopg2-binary',
    'simplejson',
    'suds',
    'requests',
    'redis',
    'zope.sqlalchemy'
]

tests_require = [
    'pytest >= 3.7.4',
    'pytest-cov',
]

setup(
    name='cronfacte',
    version='0.0',
    description='Cron para autorizacion de comprobantes',
    long_description=README + '\n\n' + CHANGES,
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Pyramid',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
    ],
    author='Manuel Japon',
    author_email='efrain.japon@gmail.com',
    url='',
    keywords='facte',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    extras_require={
        'testing': tests_require,
    },
    install_requires=requires,
)
