from setuptools import setup


setup(
    name='pyslibtesseract',
    version='0.0.1',
    packages=['pyslibtesseract'],
    package_dir={'pyslibtesseract': 'src'},
    package_data={'pyslibtesseract': ['cppcode/*.so']},
)
