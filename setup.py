from setuptools.command.install import install as InstallCommand
from setuptools import setup


class MyInstall(InstallCommand):
    def run(self):
        # Compile C code at src/cppcode
        from subprocess import Popen, PIPE
        import os

        my_path = os.path.dirname(os.path.realpath(__file__))

        print('Runing cmake at', my_path + '/src/cppcode/')
        p = Popen(['cmake', '.'], stdout=PIPE, cwd=my_path + '/src/cppcode/')
        print(p.stdout.read())
        assert(p.wait() == 0)

        if not os.path.exists(my_path + '/src/cppcode/Makefile'):
            raise RuntimeError('Makefile was not generated!')

        print('Runing make', my_path + '/src/cppcode/')
        p = Popen(['make'], stdout=PIPE, cwd=my_path + '/src/cppcode/')
        print(p.stdout.read())
        assert(p.wait() == 0)

        if not os.path.exists(my_path + '/src/cppcode/libpyslibtesseract.so'):
            raise RuntimeError('pyslibtesseract.so was not generated!')

        # Run install default
        return InstallCommand.run(self)

# Python setup
setup(
    name='pyslibtesseract',
    version='0.0.15',
    author='Bruno Macabeus',
    description=('Integration of Tesseract for Python using a shared library'),
    keywords='python-tesseract OCR Python',
    url='https://github.com/brunomacabeusbr/pyslibtesseract',
    packages=['pyslibtesseract'],
    package_dir={'pyslibtesseract': 'src'},
    cmdclass={
        'install': MyInstall
    },
    package_data={'pyslibtesseract': ['cppcode/main.cpp', 'cppcode/CMakeLists.txt', 'cppcode/libpyslibtesseract.so']},
)
