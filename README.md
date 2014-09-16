IDAM_charts
===========

Scripts to makes paired ameoba charts or bar charts. Renders as SVGs. You can convert .svgs to other formats with many different tools. Here is an [online converter](http://cloudconvert.org/svg-to-png).

## Use

Clone to desktop.

```
python makecharts.py [-c <config.cfg>] [-d <data.csv>] [-s <outfile>]
```

Example: ```python makecharts.py -c examples/amoeba1.cfg -d examples/maji.csv -s maji```

Data files should be csvs with 5 columns. See an [example](http://github.com/fgassert/IDAM_charts/blob/master/examples/maji.csv).

## Config options

See [example config](http://github.com/fgassert/IDAM_charts/blob/master/examples/ameoba1.cfg).

Example output:

![maji.svg](http://rawgit.com/fgassert/IDAM_charts/master/examples/maji.svg).
