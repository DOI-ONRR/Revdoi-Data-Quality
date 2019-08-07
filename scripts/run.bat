@echo off

call C:/programdata/anaconda3/scripts/activate.bat

:while
  echo 1. diff
  echo 2. format
  echo 3. number
  set /p ans="Type in a Number: "

  if %ans%==1 (
    goto diff
  )

  if %ans%==2 (
    goto format
  )

  if %ans%==3 (
    goto num
  )

:diff
  python diff.py
  cls
  goto while

:format
  python formatcheck.py
  cls
  goto while

:num
  python numberchecker.py
  cls
  goto while
