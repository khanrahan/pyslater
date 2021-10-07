# pyslater

Python script to generate .ttg text setup files using a .csv spreadsheet of data to be used with [Autodesk Flame](https://www.autodesk.com/products/flame) software.

Influenced by this [Flameslate PHP script](https://github.com/ManChicken1911/flameslater).

## Examples

Display help output
```
python pyslater.py -h
``` 

Output filenames based on column number
```
python pyslater.py -o "{5}_{6}_{4}.ttg" sample_spreadsheet.csv default_template_16x9.ttg
```

Output filenames based on column name
```
python pyslater.py -o "{Spot Code}_{Duration}_{Title}.ttg" sample_spreadsheet.csv default_template_16x9.ttg
```

Include only certain rows in the CSV
```
python pyslater.py --include "*1x1*" -o "{Spot Code}_{Duration}_{Title}.ttg" sample_spreadsheet.csv default_template_1x1.ttg
Influenced by this [Flameslate PHP script](https://github.com/ManChicken1911/flameslater).
