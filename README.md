IDAM_charts
===========

Scripts to makes paired ameoba charts or bar charts. Renders as SVGs. You can convert .svgs to other formats with many different tools. Here is an [online converter](http://cloudconvert.org/svg-to-png).

## Use

Clone to desktop.

```
python makecharts.py [-c <config.cfg>] [-d <data.csv>] [-s <outfile>]
```

Example: ```python makecharts.py -c examples/amoeba1.cfg -d examples/maji.csv -s maji```

Data files should be csvs with 4 columns labeled magnitudebenefit, salience
benefit, magnitudecost, saliencecost.

## Config options

See [example config](http://raw.githubusercontent.com/fgassert/IDAM_charts/master/defaultconfig.cfg).

Example output:

![maji.svg](http://raw.githubusercontent.com/fgassert/IDAM_charts/master/examples/maji.svg).
