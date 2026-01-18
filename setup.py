import os

import setuptools

base_dir = os.path.dirname(__file__)

with open(os.path.join(base_dir, 'README.md'), encoding='utf8') as f:
    long_description = f.read()

setuptools.setup(
    name='py-rpautom',
    version='0.0.54b0',
    author='aranseiki',
    author_email='allanoa@5t2tj5.onmicrosoft.com',
    description='Conjunto de utilitários para automação de processos.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://aranseiki.github.io/py-rpautom/',
    packages=setuptools.find_packages(),
    project_urls={
        'Py-RPAutom': 'https://github.com/aranseiki/py-rpautom/',
    },
    classifiers=[
        'Framework :: Robot Framework :: Library',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python :: 3',
        'Development Status :: 4 - Beta',
        'Topic :: Utilities',
    ],
    python_requires='>=3.9',
    install_requires=[
        'openpyxl',
        'psutil',
        'pywinauto',
        'pywin32',
        'PyMuPDF',
        'PyPDF2',
        'Pytesseract',
        'requests',
        'selenium',
        'urllib3',
        'xlrd',
        'requests_html',
        'lxml_html_clean',
    ],
)
