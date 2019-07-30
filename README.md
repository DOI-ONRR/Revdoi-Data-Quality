# Data-Quality-Checker
I'll put notes here. Feel free to give feedback

[More Details](https://github.com/ONRR/Revdoi-Data-Quality/wiki)

Stuff I ~stole~ borrowed:
* Excel diff: https://matthewkudija.com/blog/2018/07/21/excel-diff/

## How to Use
Be sure to change directory to where the py script is located using ```cd pathname```

**Path change example:**
```
cd Documents/GitHub/Data-Quality-Checker/scripts
```

**EXCEL DIFF:** ```python diff.py oldFile.xlsx newFile.xlsx```
```
python diff.py ../files/monthly_production_05-2019 ../files/monthly_production_06-2019
```

**Format Check:**
* Check File: ```python formatcheck.py file.xlsx```
```
python formatcheck.py ../files/monthly_revenue_05-2019
```
* Export Changes to File: ```python formatcheck.py export file.xlsx```
```
python formatcheck.py export ../files/monthly_revenue_05-2019
```
* Setup (Only need to run once per configuration): ```python formatcheck.py setup file.xlsx```
```
python formatcheck.py setup ../files/monthly_production_05-2019
```

**Number Check:**
* Check File: ```python numberchecker.py file.xlsx```
```
python numberchecker.py ../files/monthly_revenue_05-2019
```
* Setup (Only need to run once per configuration): ```python numberchecker.py setup file.xlsx```
```
python numberchecker.py setup ../files/monthly_production_05-2019
```
* Update (If changing column groups via json): ```python numberchecker.py update file.xlsx```
```
python numberchecker.py update ../files/monthly_production_05-2019
```
