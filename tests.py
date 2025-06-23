import os, pathlib
import pytest

os.chdir( pathlib.Path.cwd() / 'src' )

pytest.main()