#!/usr/bin/env python
#
# $Id: $

from setuptools import setup, Command, find_packages
import os, shutil, stat, subprocess

def get_base_path():
    """
    Use this if you need to install any non-python files found inside the
    project tree
    """
    return os.path.split(os.path.abspath(__file__))[0]

def get_python_bin_dir():
    """
    Use this if you need to install any files into the python bin dir
    """
    return os.path.join(sys.prefix, 'bin')

def shell(cmdline):
    return subprocess.Popen(cmdline, shell=True).wait()

class CreateDatabaseCommand(Command):
    """
    Sets up all database tables
    """
    description = "set up database tables"
    def initialize_options(self): pass
    def finalize_options(self): pass
    user_options = []

    def run(self):
        try:
            import sqlalchemy.exc
            from potables.db import create_all
            create_all()
        except sqlalchemy.exc.OperationalError, e:
            print "Make sure you have a database created and your db.xml configured properly."
            print "Error: {}".format(e.message)

class UnitTestCommand(Command):
    """
    Run tests with nose
    """
    description = "run tests with nose"
    def initialize_options(self): pass
    def finalize_options(self): pass
    user_options = []

    def run(self):
        shell("nosetests tests/unit --with-coverage --cover-html")

setup(name='potent-potables',
      version='0.1',
      author='Adam Ballai',
      author_email='adam@twilio.com',
      description='Potent Potables',
      packages = find_packages('src'),
      package_dir = {'': 'src'},
      include_package_data = True,
      cmdclass={'unit': UnitTestCommand, "db":CreateDatabaseCommand},
      #entry_points={
      #    'console_scripts':
      #      ['potent-processor = potent.processors.usage_triggers:main'],
      #},
)
