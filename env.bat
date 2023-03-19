@echo off

goto :OPTION_%1 2>nul || ( echo "%1" is not a valid option)



:: Default option
:OPTION_
	if exist venv\ (
		if "%VIRTUAL_ENV%" == "" (
			echo activating now...
			venv\Scripts\activate.bat
		) else (
			echo virtual environment already activated
		)
	) else (
		python -m venv venv
		venv\Scripts\activate.bat
		pip install -r requirements.txt
	)
	goto:eof


:OPTION_SET
	if exist venv\ (
		echo activating now...
		venv\Scripts\activate.bat
		pip freeze > requirements.txt
	) else (
		echo venv not currently setup
	)
	goto:eof


:OPTION_RESET
	rmdir /s /q venv
	pause
	python -m venv venv
	venv\Scripts\activate.bat
	pip install -r requirements.txt
	goto:eof


:OPTION_DEL
	rmdir /s /q venv
	goto:eof

