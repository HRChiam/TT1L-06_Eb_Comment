import sys
print(sys.path)

from . import create_app

app = create_app()
