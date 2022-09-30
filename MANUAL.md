# Installation
## PyPI
If `PIP` is installed on the target system,
`tempren` can be installed as any other Python package:
```commandline
$ pip install [--user] tempren
```

PIP doesn't automatically update packages so to keep it up-to-date, another command have to be used:

```commandline
$ pip install [--user] --upgrade tempren
```

### Additional dependencies
Some tags (i.e. under `Video` category) may not be available if there is no [MediaInfo](https://mediaarea.net/en/MediaInfo) library installed on the system.
This dependency cannot be installed via PIP so user is expected to install it.
Distribution-specific package manager can often be used, for example:
```commandline
$ sudo apt install libmediainfo0v5
```

<!--
## Snaps
**TODO: Implement**
> **Note: Due to limitation of confinement policies, when this installation method is used
`tempren` will only be able to access files under user `$HOME` directory.**

```commandline
$ sudo snap install tempren
```

When installed as a snap package, `tempren` will be kept up-to-date automatically - no user action is required.
-->

# Builtin documentation
Short documentation for all command line arguments can always be retrieved via `--help`/`-h` flag:
```commandline
$ tempren --help
```

Options which documentation starts with `(default)` do not have to be specified explicitly on the command line.

`--help`/`-h` flag can also be used to display tag-specific documentation when tag name is given as an argument:
```commandline
$ tempren --help [Category.]TagName
```

To find out which tags are shipped with installation, `--list-tags`/`-l` flag can be used:
```commandline
$ tempren --list-tags
```
The output of this command will list all available tag names sorted by name and grouped by category they belong to.


# Modes of operation
Tempren have two main modes of operation: **name** and **path**.

In the **name** mode (default, enabled by `--name`/`-n` flag), the template is used for filename generation only.
It is safer mode because path separator elements in generated path will result in an error.
<!---
This is useful if you want to operate on files specified on the command line or in a single directory.
**TODO: files cannot be specified on the command line... yet**
--->

With **path** mode (enabled by `--path`/`-p` flag), the template generates a whole path (relative to the input directory).
This way you can sort files into dynamically generated catalogues.

## Recursive file discovery
By default, `tempren` will not descend into subdirectories of specified input directory.
To allow recursive file discovery, `--recurse`/`-r` flag have to be specified.

> Note: If `--include-hidden` flag is used, hidden directories will also be scanned.


# Template syntax
Template pattern consist of a _raw text_ interleaved with _tag invocations_:
```
Raw text with a %TagCategory.TagName() in it
```
Raw text is treated as constant - it doesn't change across template evaluations.
Tag invocation starts with `%` symbol followed by _tag name_, _argument list_ and (optionally) its _context_.

## Tag name
A fully qualified tag name consists of a category and tag name separated by a single dot `.`.
The tag name is case-sensitive and conforms to CamelCaseNamingConvention.
The category name is case-insensitive but to keep convention consistent it is also presented in the same (CamelCase) manner.

If the tag name is unique across categories it can be used without explicit category specification (and separating dot) like this:
```
Raw text with a %UniqueTag() in it
```

## Tag configuration arguments
Some tags can or have to be configured before they can do their work.
To do so, with every invocation user is expected to pass configuration arguments in the tags' argument list.
What arguments are expected and in what order can be found by looking at built-in [tag documentation](#Builtin documentation).

Argument list follows tag name and is contained between parentheses: `()`.
Each argument value is separated by a single coma `,` (with optional space) and can be one of three types:
- `int` for integer numbers (that match `-?[0-9]+` regex)
- `str` for quoted string literals (both single `'` and double `"` quotation marks can be used)
- `bool` for boolean flags

Numbers can be accepted only in decimal (base 10) representation without fraction part: `%Count(0, 1, 4)`

String literals may contain any character except for the used quote mark - if quote mark shall be passed,
it should be escaped (prefixed) with a single backslash character, i.e. `\'` or `\"`.

Boolean flags can accept two types of values: `True`/`true` or `False`/`false`.\
Additionally there exist shortcut for setting flag to `True` - just use flag name as an argument value (similar to explicit names).
Therefore, following invocations are equivalent:
```
%Trim(-2, left=True)
%Trim(-2, true)
%Trim(-2, left)
```

Tag prototype (which can be found in tag build-in documentation) describes names for every argument:
```
%Trim(width: int, left: bool = False, right: bool = False){...}
```
Prototype above, indicates that this tag accepts up to 3 arguments named `width`, `left` and `right` accordingly.

User can prefix argument value with its name and `=` symbol to specify values just for the named arguments: `%Trim(-2, right=True)`
If all passed argument are explicitly named, their values can be out of order: `%Trim(left, width=-1)`

Order of arguments is important if explicit names are not used: `%Trim(-1, True)` will set `left` flag because it's second in the argument list.

## Context
Contexts are parts of tag template expression passed to the tags as a kind of dynamic argument.
To pass context to the tag invocation, use curly braces `{}` with expression embedded between.

In the following example, `Upper` tag receives context containing processed file extensions and makes it uppercase:
```
%Upper(){%Ext()}
```

Context might be required, optional and forbidden.
This is indicated by `{...}` symbol at the end of tag prototype.

<!---
## Pipe list sugar
--->

# Filtering
There are three types of a filtering expressions supported:
- `template` - tag-template evaluated Python predicate expression, e.g.: `%Size() > 10*1024`
- `glob` - filename globbing expression, e.g.: `*.mp3`, `IMG_????.jpg`
- `regex` - python-flavored regex, e.g.: `.*\.jpe?g`

## Template-based filtering
Template-based filtering allows to include/exclude files based on their metadata.
Filter expression can be passed with `--filter-template`/`-ft` flag.
Filter expression tag template is rendered for each file and then, it is evaluated as Python expression.
If result of evaluation is _truthy_, the file is considered for the renaming.

For example, the following filtering template will exclude files larger than 1024 bytes:
```
%Size() <= 1024
```

Standard Python boolean operators (`and`, `or`, `not`) and build-in functions can be used to chain multiple conditions.\
For example, to include only image files that are not PNGs, following filter expression can be used:
```
%IsMime("image") and not %Ext().endswith("png")
```

## Glob filtering
Glob filtering allows to include/exclude files based on glob expression matching their filenames.

For example, to rename only files with an `Image_` prefix, following pattern can be used:
```
Image_*
```

## Regex filtering
Regular expression filtering allows to include/exclude files based on regex expression matching their filenames.

For example, to rename only files that start with a digit, following pattern can be used:
```
^\d.*
```

## Filter inversion
Sometimes it might be easier to specify filter for files which should **not** be included.
To negate/invert any filtering expression you can use `--filter-invert`/`-fi` flag.

# Template-based sorting
In some cases (i.e. when `Count` tag is used), files should be processed in specific order to make renaming useful.
`--sort`/`-s` flag can be used to order files considered for renaming based on their metadata.

Sort expression is similar to the filter expression in a way that it also should generate valid Python value.
Tag template evaluated from rendered sorting expression is used as key for the sorting.

For example, to order files based their original name, following expression can be used:
```
%Name()
```

To add another sorting criteria (for cases where first key may repeat across files), a comma `,` can be used as separator.

For example, to order files based their extension **then** their size, following expression can be used:
```
%Ext(), %Size()
```


## Sorting order inversion
By default, sorting expression order files in the ascending order.
To change this behaviour, `--sort-invert`/`-si` flag can be used.

# Conflict resolution strategies
TODO

# Various options
## Dry run
To facilitate discovery-based usage learning, `tempren`'s `--dry-run`/`-d` flag can be used to disable actual file renaming stage of utility pipeline.
> Note: While dry-run being active, side effects from filtering/sorting template expressions (which are valid Python code)
> or even tags itself may still affect the file system.\
> Be careful not to copy-paste templates that look suspicious.

## Verbosity levels
Number of messages produced by the tool can be increased with `--verbose`/`-v` flag
and decreased by `--quiet`/`-q` flag.
Normal messages are directed to the standard output (`stdout`) while warnings and errors are sent to `stderr`.

## Hidden files handling
By default, `tempren` won't consider hidden files or directories for renaming.
To consider such files for processing, `--include-hidden`/`-ih` flag can be used.

> Note: `--include-hidden` in combination with `--recursive` flag, change how file discovery is performed.
> When both flags are specified, hidden directories and any files in them **will be** considered for renaming.

## Symbolic links handling
TODO: Implement
