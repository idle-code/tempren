**TODO: TOC**
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

## Snaps
**TODO: Implement**
> **Note: Due to limitation of confinement policies, when this installation method is used
`tempren` will only be able to access files under user `$HOME` directory.**

```commandline
$ sudo snap install tempren
```

When installed as a snap package, `tempren` will be kept up-to-date automatically - no user action is required.

# Builtin documentation
Short documentation for all command line arguments can always be retrieved when invoking tool with `--help`/`-h` flag:
```commandline
$ tempren --help
```

Options which documentation starts with `(default)` do not have to be specified explicitly on the command line.

`--help`/`-h` flag can also be used to display tag-specific documentation when tag name is given as an argument,
which (due to large library of tags and their variety) is only available in this form:
```commandline
$ tempren --help [Category.]TagName
```

To find out which tags are shipped with installation, `--list-tags`/`-l` flag can be used:
```commandline
$ tempren --list-tags
```
Output of this command will list all available tag names sorted by name and grouped by category they belong to.

# Template syntax
Template pattern consist of a _raw text_ interleaved with _tag invocations_:
```
Raw text with a %TagCategory.TagName() in it
```
Raw text is treated as constant - it doesn't change across template evaluations.
Tag invocation starts with `%` symbol followed by _tag name_, _argument list_ and (optionally) its _context_.

**TODO: Semantic meaning of tag invocation**
**TODO: Semantic meaning of argument list and context**
**TODO: Reference to python function invocation**

## Tag name
Fully qualified tag name consists of category and tag name itself separated by a single dot `.`.
Tag name is case-sensitive and usually conforms to CamelCaseNamingConvention.
Category name is case-insensitive but to keep convention consistent it is also presented in the same (CamelCase) manner.

If tag name is unique across categories it can be used without explicit category specification (and separating dot):
```
Raw text with a %UniqueTag() in it
```

## Tag configuration arguments

**TODO: reference to documentation types**

Argument list follows tag name and is contained in parentheses: `()`.
Each argument value is separated by a single coma `,` (with optional space) and can be one of three types:
- `int` for integer numbers (that match `-?[0-9]+` regex)
- `str` for quoted string literals (both single `'` and double `"` quotation marks can be used)
- `bool` for boolean flags

Numbers can be accepted only in decimal (base 10) representation without fraction part: `%Count(0, 1, 4)`

String literals may contain any character except for used quote mark - if quote mark is required,
it should be prefixed with a single  backslash character, i.e. `\'` or `\"`.

For boolean flags can accept two types of values: `True`/`true` or `False`/`false`.
Additionally there exist shortcut for

**TODO: explicit argument names**

## Context
## Pipe list sugar

# Modes of operation
Tempren have two main modes of operation: **name** and **path**.

In the **name** mode (default, enabled by `-n`, `--name` flag), the template is used for filename generation only.
This is useful if you want to operate on files specified on the command line or in a single directory.
**TODO: files cannot be specified on the command line... yet**

With **path** mode (enabled by `-p`, `--path` flag), the template generates a whole path (relative to the input directory).
This way you can sort files into dynamically generated catalogues.

## Recursive file discovery
By default, `tempren` will not descend into subdirectories of specified input directory.
To allow recursive file discovery, `--recurse`/`-r` flag have to be specified.

> Note: If `--include-hidden` flag is used, hidden directories will also be scanned.



# Filtering
There are three types of a filtering expressions supported:
- `template` - tag-template evaluated Python predicate expression, e.g.: `%Size() > 10*1024`
- `glob` - filename globbing expression, e.g.: `*.mp3`, `IMG_????.jpg`
- `regex` - python-flavored regex, e.g.: `.*\.jpe?g`

## Template-based filtering
## Glob filtering
## Regex filtering
## Filter inversion
Sometimes it might be easier to specify filter for files which should **not** be included.
To negate/invert filtering expression you can use `-fi`, `--filter-invert` flag.

# Template-based sorting
## Sorting order inversion

# Conflict resolution strategies

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

## Symbolic links handling
**TODO: Implement?**
