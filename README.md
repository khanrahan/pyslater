# pyslater

Python script to generate .ttg text setup files using a .csv spreadsheet of data to be used with [Autodesk Flame](http://www.autodesk.com/products/flame) software.


## Examples

Display help output
```
python pyslater.py -h
``` 

Output filenames based on column number
```
python pyslater.py -o "<5>_<6>_<4>.ttg" sample_spreadsheet.csv templates/default_template_16x9.ttg
```

Output filenames based on column name
```
python pyslater.py -o "<Spot Code>_<Duration>_<Title>.ttg" sample_spreadsheet.csv templates/default_template_16x9.ttg
```

Include only certain rows in the CSV
```
python pyslater.py --include "*1x1*" -o "<Spot Code>_<Duration>_<Title>.ttg" sample_spreadsheet.csv templates/default_template_1x1.ttg
```

## Template Setup

It is important that you do not make  any selections when creating your templates.  The generated TTGs will have errors in them.

For example, you need the `<Title>` line to be smaller from the rest of the lines.  Do not select that line and then change the size value.  Instead, use Backspace to delete the entire line, then change the Size value, then type out `<Title>` again.   


## Acknowledgements

Heavily influenced by this [Flameslate PHP script](http://github.com/ManChicken1911/flameslater)

UI Templates courtesy of [pyflame.com](http://www.pyflame.com)
