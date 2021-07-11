for /f "delims== tokens=1,2" %%G in (doc\DEPS.txt) do (
	py -m pip install %%G
)
cls
start "" pyw src/tprts.py
