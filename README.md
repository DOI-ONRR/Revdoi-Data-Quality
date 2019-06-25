# Data-Quality-Checker
I'll put notes here. Feel free to give feedback

[More Details](https://docs.google.com/document/d/1fem53kzp4PkXbNiEpmJCJsC1mjv_ELOK9bDdLi_UksA/edit?ts=5cffd8a1)

Stuff I ~stole~ borrowed:
* Excel diff: https://matthewkudija.com/blog/2018/07/21/excel-diff/

## How to Use
Suggestion: Run py scripts through Anaconda PowerShell

Be sure to change directory to where the py script is located using **_cd "pathname_"**

Examples of pathname
* Full pathname: "C:/Users/name/.../foldername"
* Local pathname: "foldername"
* For going back a folder: ".."

EXCEL DIFF: **_python diff.py "oldFile" "newFile"_**

Format Check:
* Check File: **_python formatcheck.py "pathname"_**
* Setup: **_python formatcheck.py setup "sampleFile"_**
 * Will have to redo most of the setup

## Progress so far
Unit Dictionary: Ready
Field Name Check: Ready
Non-numerical Field Check: Ready
N/A Check: wip
Numerical Field Check: wip
