del MANIFEST
python setup.py sdist --format=zip
python setup.py sdist --format=bztar
python setup.py bdist_wininst --install-script pyffipostinstallation.py
