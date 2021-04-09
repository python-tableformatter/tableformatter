## 0.1.6 (April 9, 2021)
* Bug Fixes
    * Fixed exception when handling row objects that are iterable but are not numerically indexable sequences

## 0.1.5 (April 27, 2020)
* Bug fixes
    * Fixes issue with handling namedtuples as row ojbects
* Documentation
    * Added examples for writing terminal escape sequences to a file

## 0.1.4 (August 12, 2019)
* Bug fixes
    * Fix colors getting messed up when using the colored library
    * Fix issue wrapping text with wide-display unicode characters
* Enhancements
    * Added support for dictionaries as row objects. attrib will be used as the column key
    * Changed default colored row BG color to be 50% gray
        * So it is equally visible on black and white backgrounds

## 0.1.3 (August 18, 2018)
* Improved support for Pandas DataFrame, Numpy RecordArray, and dict tabular data types 

## 0.1.2 (June 29, 2018)
* Enabled ability to chain obj_formatter with formatter
* Improved API for specifying per-row text color in the table 

## 0.1.1 (June 25, 2018)
* Correcting incorrectly packaged 0.1.0

## 0.1.0 (June 25, 2018)
* Unit tests added with automated testing integrated
* Multiple examples added 
* Fixed some bugs related to table transpose

## 0.0.1 (June 23, 2018)
* Initial release of TableFormatter
