# Data-Quality-Checker
I'll put notes here. Feel free to give feedback

Stuff I ~stole~ borrowed:
* Excel diff: https://matthewkudija.com/blog/2018/07/21/excel-diff/

Be sure to change directory to where the py script is located using **_cd "pathname_"**

Examples of pathname
* Full pathname: "C:/Users/name/.../foldername"
* Local pathname: "foldername"
* For going back a folder: ".."

EXCEL DIFF: **_python diff.py "oldFile" "newFile"_**

Format Check:
* Check File: **_python formatcheck.py "pathname"_**
* Setup: **_python setup.py "sampleFile"_**
 * Most of the setup should already be done.

[More Details](https://docs.google.com/document/d/1fem53kzp4PkXbNiEpmJCJsC1mjv_ELOK9bDdLi_UksA/edit?ts=5cffd8a1)

## Progress so far
[6/24]
* Misc. cols: Ready?
* W count: Ready?
* Numerical Fields: wip

[6/21]
* PICKLES

[6/20]
* Transferred repo from personal to ONRR
* Separated setup and format_check

[6/19]
* Reorganization of files

[6/18]
* Format check now usable in Terminal
  * Setup: **_python setup.py "sampleFile"_**
  * Check File: **_python formatcheck.py "pathname"_**
* Unit Dictionary: Done
* Other fields?: wip
* Aggregate Data: wip

[6/17]
* Unit Dictionary: Mostly done
* Column Check: Done
* Other fields: wip
* Will start working on aggregate data soon

[6/13]
* Cleaning up DIFF script
    * Should now work through Terminal
      * Prints out differences in Terminal and outputs Excel file
        * Green = New
        * Red with arrow = Changed
        * Grey = Dropped
      * How to Run: **_python diff.py "oldFile" "newFile"_**
* Will work on other scripts soon
    1. Formatting (Order, Units, etc.) [Main Priority]
    2. Aggregate Data(Standard Deviation) [Backlog]


[6/12]
* Can now create Unit Dictionary
    * Configuration file or Read sample Excel File
* Can now create Header format
    * Same as above
