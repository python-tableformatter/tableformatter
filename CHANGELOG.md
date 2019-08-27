## 0.2.0 (TBD)
* Breaking Changes
    * Internal structure of tableformatter was changed as part of the 0.2 re-architecture effort. Notably, 
      tableformatter components have been separated into separate modules placed in a package matching the original
      module name. The package has been configured to import components such that most existing code will still function
      with these changes.
    * all of the options keys that were in TableFormatter (ROW_OPT_*, COL_OPT_*, TABLE_OPT_*) have been moved to .model.Options

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
