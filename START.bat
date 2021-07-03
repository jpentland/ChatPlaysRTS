for /f "delims== tokens=1,2" %%G in (DEPS.txt) do (
	py -m pip install %%G
)
py tprts.py