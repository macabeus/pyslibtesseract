from setuptools import setup


setup(
    name='pyslibtesseract',
    version='0.0.7',
    author='Bruno Macabeus',
    description=('Integration of Tesseract for Python using a shared library'),
    keywords='python-tesseract OCR Python',
    url='https://github.com/brunomacabeusbr/pyslibtesseract',
    packages=['pyslibtesseract'],
    package_dir={'pyslibtesseract': 'src'},
    package_data={'pyslibtesseract': ['cppcode/*.so']},
)
