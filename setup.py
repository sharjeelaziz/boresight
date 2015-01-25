from setuptools import setup, find_packages  # Always prefer setuptools over distutils
from codecs import open  # To use a consistent encoding
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the relevant file
with open(path.join(here, 'DESCRIPTION.rst'), encoding='utf-8') as f:
    long_description = f.read()


class post_install(install):
    def run(self):
        root = getattr(self, "root", "/") or "/"
        print "Using '%s' as root" % root
        if root == "/":
            if os.getuid() != 0:
                print "ERROR: Cannot install to root '/' without root permissions"
                sys.exit(1)
            # cleanup old egg-info files
            try:
                while True:
                    p = pkg_resources.get_distribution("pysattracker")
                    for f in os.listdir(p.location):
                        if f.startswith("pysattracker") and f.endswith(".egg-info"):
                            egg_info = os.path.join(p.location, f)
                            try:
                                print "Deleting old egg-info: %s" % egg_info
                                os.unlink(egg_info)
                            except:
                                pass
                    reload(pkg_resources)
            except pkg_resources.DistributionNotFound:
                pass
        install.run(self)
        # install config file
        print ""
        cd = os.path.dirname(os.path.realpath(__file__))
        src = os.path.join(cd, "pysattracker.json")
        dest = os.path.join(root, "etc/pysattracker.json")
        dest_new = os.path.join(root, "etc/pysattracler.json.new")
        mkpath(os.path.dirname(dest))
        if os.path.isfile(dest):
            print "Warning: %s already exists. Saved new config file to %s" % (dest, dest_new)
            shutil.copyfile(src, dest_new)
        else:
            print "Installing config file to %s" % dest
            shutil.copyfile(src, dest)

setup(
    name='pysattracker',

    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/development.html#single-sourcing-the-version
    version='1.0.0a1',

    description='Satellite Antenna Tracker',
    long_description=long_description,

    # The project's main homepage.
    url='https://github.com/sharjeelaziz/pysattracker',

    # Author details
    author='Sharjeel Aziz (shaji)',
    author_email='sharjeel.aziz@gmail.com',

    # Choose your license
    license='Apache',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: End Users/Desktop',
        'Topic :: Communications :: Ham Radio',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: Apache Software License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2.7',
    ],

    # What does your project relate to?
    keywords='ham radio satellite tracker antenna',

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    packages=['pysattracker'],

    # List run-time dependencies here.  These will be installed by pip when your
    # project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    # install_requires=['peppercorn'],

    # List additional groups of dependencies here (e.g. development dependencies).
    # You can install these using the following syntax, for example:
    # $ pip install -e .[dev,test]
    # extras_require = {
    #    'dev': ['check-manifest'],
    #    'test': ['coverage'],
    # },

    # If there are data files included in your packages that need to be
    # installed, specify them here.  If using Python 2.6 or less, then these
    # have to be included in MANIFEST.in as well.
    # package_data={
    #    'sample': ['package_data.dat'],
    # },

    # Although 'package_data' is the preferred approach, in some case you may
    # need to place data files outside of your packages.
    # see http://docs.python.org/3.4/distutils/setupscript.html#installing-additional-files
    # In this case, 'data_file' will be installed into '<sys.prefix>/my_data'
    # data_files=[('my_data', ['data/data_file'])],

    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    # entry_points={
    #    'console_scripts': [
    #        'sample=sample:main',
    #    ],
    # },
    cmdclass={'install': post_install},
)
