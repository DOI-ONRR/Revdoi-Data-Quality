# Experimental Data-Quality-Checker
## Warning! This build is volatile and subject to change at any moment

[More Details on Experimental](https://github.com/ONRR/Revdoi-Data-Quality/wiki/Experimental-Stuff)

Stuff I ~stole~ borrowed:
* Excel diff: https://matthewkudija.com/blog/2018/07/21/excel-diff/

## How to Use
Be sure to change directory to where the py script is located using **_cd pathname_**

Example Run(s):
```
cd Documents/GitHub/Data-Quality-Checker/scripts
python diff.py ../files/monthly_production_05-2019 ../files/monthly_production_06-2019
python formatcheck.py ../files/monthly_revenue_05-2019
```

EXCEL DIFF: **_python diff.py oldFile.xlsx newFile.xlsx_**

Format Check:
* Check File: **_python formatcheck.py file.xlsx_**
* (Only need to run once for format) Setup: **_python formatcheck.py setup sampleFile.xlsx_**


## Progress so far
- [x] Unit Dictionary
- [x] Field Name Check
- [x] Non-numerical Field Check
- [ ] N/A Check: Mostly Done (Bugs everywhere)
- [ ] Numerical Field Check: wip
