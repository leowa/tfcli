import io
import re

from setuptools import find_packages
from setuptools import setup

with io.open("README.md", "rt", encoding="utf8") as f:
    readme = f.read()

with io.open("tfcli/__init__.py", "rt", encoding="utf8") as f:
    version = re.search(r'__version__ = "(.*?)"', f.read()).group(1)

setup(
    name="tfcli",
    version=version,
    url="https://github.com/leowa/samples/tfcli/",
    license="MIT",
    author="Andy Zhang",
    author_email="leowa@outlook.com",
    description="tool to migrate and refactor terraform code and state",
    long_description=readme,
    classifiers=[
        "Intended Audience :: Developers",
        'License :: OSI Approved :: MIT License',
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    # This field adds keywords for your project which will appear on the
    # project page. What does your project relate to?
    #
    # Note that this is a string of words separated by whitespace, not a list.
    keywords='python terraform',  # Optional
    # You can just specify package directories manually here if your project is
    # simple. Or you can use find_packages().
    #
    # Alternatively, if you just want to distribute a single Python file, use
    # the `py_modules` argument instead as follows, which will expect a file
    # called `my_module.py` to exist:
    #
    #   py_modules=["my_module"],
    #
    packages=find_packages(exclude=['examples', 'docs', 'tests']),  # Required

    # Specify which Python versions you support. In contrast to the
    # 'Programming Language' classifiers above, 'pip install' will check this
    # and refuse to install the project if the version does not match. If you
    # do not support Python 2, you can simplify this to '>=3.5' or similar, see
    # https://packaging.python.org/guides/distributing-packages-using-setuptools/#python-requires
    python_requires=">=3.5",

    # if you want to use src as your package diretory
    # package_dir={"": "src"},

    # This field lists other packages that your project depends on to run.
    # Any package you put here will be installed by pip when your project is
    # installed, so they must be valid existing projects.
    #
    # For an analysis of "install_requires" vs pip's requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires=[
        "Jinja2>=2.10.1",
        "colorlog>=4.1.0",
        "click>=7.0",
        "colorama~=0.4.0",
        "boto3~=1.14.0",
    ],

    # Similar to `install_requires` above, these must be valid existing projects.
    extras_require={
        "dotenv": ["python-dotenv"],
        "dev": [
            "pytest",
            "pyenv",
            "coverage",
            "tox",
        ],
        "test": ["coverage"],
    },
    # If there are data files included in your packages that need to be
    # installed, specify them here.
    # package_data={  # Optional
    #     'sample': ['package_data.dat'],
    # },

    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # `pip` to create the appropriate form of executable for the target
    # platform.
    #
    # For example, the following would provide a command called `pytfcli` which
    # executes the function `main` from this package when invoked:
    entry_points={  # Optional
        'console_scripts': [
            'tfcli=tfcli.cli:cli',
        ],
    },
)
