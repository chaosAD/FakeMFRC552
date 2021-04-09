#!/usr/bin/python #!/usr/bin/env python
#
# Fake MFRC522 setup
#
'''
## License

The MIT License (MIT)

Fake MFRC522 for fast software development and testing 
Copyright (C) 2017  Dexter Industries

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
'''

try:
	with open('package_description.rst', 'r') as file_description:
		description = file_description.read()

except IOError:
	description = "Please seek help from a human"

import setuptools

setuptools.setup(
    name = "mfrc522",
    version = "0.0.2",

    description = "Simple fake MFRC522 library for rapid software development and testing",
    long_description = description,

    author = "Poh Tze Ven",
    author_email = "frasker@hotmail.com",

    license = 'MIT',
    classifiers = [
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Developers',
    'Intended Audience :: Education',
    'License :: OSI Approved :: MIT License',
    'Operating System :: POSIX :: Linux',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 3',
    'Topic :: Software Development :: Embedded Systems',
    'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    url = "https://github.com/chaosAD/FakeMfrc522",

    keywords = ['rfid', 'nfc', 'mifare', 'contactless card', 'testing', 'prototyping'],
    py_modules = ['mfrc522'],
    packages=setuptools.find_packages(),
    python_requires=">=3.6",    
) 

