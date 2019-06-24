# Data-Quality-Checker
I'll put notes here. Feel free to give feedback

Be sure to change directory to where the script is located using **_cd "pathname_"**

Examples of pathname
* Full pathname: "C:/Users/name/.../filename.extension"
* Local pathname: "files/filename.extension"
* For going back a folder: "../files/filename.extension"

EXCEL DIFF: **_python diff.py "oldFile" "newFile"_**

Format Check:
* Setup: **_python setup.py "sampleFile"_**
* Check File: **_python formatcheck.py "pathname"_**

[More Details](https://docs.google.com/document/d/1fem53kzp4PkXbNiEpmJCJsC1mjv_ELOK9bDdLi_UksA/edit?ts=5cffd8a1)

## Progress so far
[6/24]
* Mics cols: Ready?
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
