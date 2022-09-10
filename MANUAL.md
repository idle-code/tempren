[[_TOC_]]

# Installation
## Updating
# Template syntax



#### Tag configuration
#### Pipe list sugar
### Name mode
### Path mode
### Filtering
To select which files should be considered for processing one can use filtering predicate.

There are three types of a filtering expressions supported (by `-ft`, `--filter-type` option):
- `glob` (default) - filename globbing expression, eg: `*.mp3`, `IMG_????.jpg`
- `regex` - python-flavored regex, eg: `.*\.jpe?g`
- `template` - tag-template evaluated python expression, eg: `%Size() > 10*1024`

Sometimes it might be easier to specify filter for files which should **not** be included.
To negate/invert filtering expression you can use `-fi`, `--filter-invert` flag.

#### Glob filtering
#### Regex filtering
#### Template filtering
#### Case sensitiveness and filter inversion
TODO: **IMPLEMENT**

By default, `glob` and `regex` filtering expressions will match case-sensitive.
To allow case-insensitive matching use `-fc`, `--filter-case` flag.

`template` filter isn't affected by case-sensitivity flag - you will have to make use of `str.upper` or `str.lower` python methods to simulate that.

### Sorting
