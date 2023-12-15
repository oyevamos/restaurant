import os
os.system("sphinx-apidoc -o docs/ main")
os.system("sphinx-build -b html docs/ docs/_build/html")
