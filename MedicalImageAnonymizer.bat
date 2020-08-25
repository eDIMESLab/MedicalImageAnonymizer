echo OFF

for /f %%i in ('where python') do (
  set my_python=%%i
  goto endloop
)
:endloop

%my_python% %cd%\MedicalImageAnonymizer\GUI\gui.py
