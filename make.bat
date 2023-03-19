@echo off

goto :OP_%1 2>nul || (
	echo "%1" is not a valid option
)



:: Default Option
:OP_
goto :OP_BUILD
goto :eof


:OP_BUILD
python setup.py build
start build
echo Build compelte
goto :eof


:OP_DIST
python setup.py bdist_msi
start dist
echo Distribution complete
goto :eof


:OP_GRAPHS
cd symbotic
python -m pydeps .
echo Made graphs
goto :eof


:OP_COV
coverage run --source=vcs --omit=*/tests/*,*/view/*,*/control/* -m nose --traverse-namespace vcs
coverage report
coverage html
start .\htmlcov\index.html
goto :eof


:OP_OTHER
echo other
goto :eof

