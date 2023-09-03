<!-- TOC -->
* [Installation](#installation)
  * [Snap](#snap)
  * [AppImage](#appimage)
  * [PyPI](#pypi)
    * [Additional dependencies](#additional-dependencies)
* [Builtin documentation](#builtin-documentation)
* [Modes of operation](#modes-of-operation)
  * [Recursive file discovery](#recursive-file-discovery)
* [Template syntax](#template-syntax)
  * [Tag name](#tag-name)
  * [Tag configuration arguments](#tag-configuration-arguments)
  * [Context](#context)
* [Filtering](#filtering)
  * [Template-based filtering](#template-based-filtering)
  * [Glob filtering](#glob-filtering)
  * [Regex filtering](#regex-filtering)
  * [Filter inversion](#filter-inversion)
* [Template-based sorting](#template-based-sorting)
  * [Sorting order inversion](#sorting-order-inversion)
* [Conflict resolution strategies](#conflict-resolution-strategies)
* [Ad-hoc tags](#ad-hoc-tags)
* [Tag aliases](#tag-aliases)
* [Various options](#various-options)
  * [Dry run](#dry-run)
  * [Verbosity levels](#verbosity-levels)
  * [Hidden files handling](#hidden-files-handling)
  * [Symbolic links handling](#symbolic-links-handling)
<!-- TOC -->

* * *

# Installation
## Snap
`tempren` can be found on the [snapcraft store](https://snapcraft.io/tempren).
To install it, you can use graphical package manager or  command line:
```commandline
$ snap install tempren
```
Snap packages are updated automatically by default so no additional configuration is necessary.

## AppImage
On the [releases page](https://github.com/idle-code/tempren/releases), under _Assets_ you can find .AppImage files that can be downloaded and executed as is.
To install `tempren` this way, you will need to:
```commandline
# Download the .AppImage file
$ curl -o tempren https://<link to the latest AppImage>

# Make the file executable
$ chmod +x ./tempren

# Install it in any directory that is in your $PATH
$ sudo mv ./tempren /usr/local/bin
```
Currently, AppImage release doesn't support automatic updates so if new version of the `tempren` is released, you will need to repeat this installation procedure.

## PyPI
If `pip` is installed on the target system,
`tempren` can be installed as any other Python package:
```commandline
$ pip install [--user] tempren
```

`pip` doesn't automatically update packages so to keep `tempren` up-to-date, another command have to be used each time there is new release:

```commandline
$ pip install [--user] --upgrade 'tempren[video]'
```

### Additional dependencies
Some tags (i.e. under `Video` category) may not be available if there is no [MediaInfo](https://mediaarea.net/en/MediaInfo) library installed on the system.
This dependency cannot be installed via `pip` so user is expected to deal with it manually.

Most often, a distribution-specific package manager can be used. For example:
```commandline
$ sudo apt install libmediainfo0v5
```

# Builtin documentation
`tempren` comes in with extensive build-in documentation that is the main source of knowledge about specific tags.

Short documentation for all command line arguments can always be retrieved via `--help`/`-h` flag:
```commandline
$ tempren --help
```

Options which documentation starts with `(default)` do not have to be specified explicitly on the command line.

`--help`/`-h` flag can also be used to display tag-specific documentation when a tag name is given as an argument:
```commandline
$ tempren --help [Category.]TagName
```

To find out which tags are shipped with the installation, `--list-tags`/`-l` flag can be used:
```commandline
$ tempren --list-tags
```
The output of this command will list all available tag names sorted by name and grouped by category they belong to.


# Modes of operation
Tempren have two main modes of operation: **name** and **path**.

In the **name** mode (default, represented by `--name`/`-n` flag), the template is used for filename generation only.
This mode is used most often as it doesn't alter directory structure and focuses just on the files. In this mode, if a path separator (i.e. `/`) is present in the generated path, an error will be reported.

Name mode is used mostly when operating on a single directory or files specified directly in the command-line arguments.

With **path** mode (enabled by `--path`/`-p` flag), the template generates a whole, new path (relative to the input directory) for the processed file.
This way you can sort files into dynamically generated catalogues.

The input directory is important for the path mode because all generated paths are relative to it. What is used as the input directory depends on how you pass the arguments to the `tempren`:
- For **file paths** passed directly, their input directory will be the directory they are currently in - i.e. `dirname <processed-file>`
- **Directory paths** passed directly will be considered input directories on their own

> Note: When using recursive file discovery, only the top-most directory (the one passed in the command line) is considered as input directory.

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
Tag invocation starts with `%` symbol followed by the _tag name_, _argument list_ and (optionally) its _context_.

## Tag name
A fully qualified tag name consists of a category and tag name separated by a single dot `.`.
The tag name is case-sensitive and conforms to CamelCaseNamingConvention.
The category name is case-insensitive but to keep convention consistent it is also presented in the same (CamelCase) manner.

If the tag name is unique across categories it can be used without explicit category specification (and separating dot) like this:
```
Raw text with a %UniqueTag() in it
```

When non-unique tag name is used this way, `tempren` will report an error about tag ambiguity.

## Tag configuration arguments
Some tags can or have to be configured before they can do their work.
To do so, user is expected to pass configuration arguments in the tag _argument list_.
What arguments are expected and in what order can be found by looking at built-in [tag documentation](#Builtin documentation).

Argument list follows tag name and is contained between parentheses: `()`.
Each argument value is separated by a single coma `,` (with optional space) and can be one of three types:
- `int` for integer numbers (that match `-?[0-9]+` regex)
- `str` for quoted string literals (both single `'` and double `"` quotation marks can be used)
- `bool` for boolean flags

Numbers can be accepted only in decimal (base 10) representation without fraction part: `%Count(0, 1, 4)`

String literals may contain any character except for the used quote mark - if quote mark needs to be passed,
it should be escaped (prefixed) with a single backslash character, i.e. `\'` or `\"`.

Boolean flags can accept two types of values: `True`/`true` or `False`/`false`.\
Additionally, a shortcut exist for setting the flag argument to `True` - just use flag name as an argument value (similar to explicit argument names in programming languages).
Therefore, following invocations are equivalent:
```
%Trim(-2, left=True)
%Trim(-2, true)
%Trim(-2, left)
```

Tag prototype (which can be found in tag build-in documentation) describes names and types of every argument the tag configuration expects:
```
%Trim(width: int, left: bool = False, right: bool = False){...}
```
The above prototype, indicates that this tag accepts up to 3 arguments named `width`, `left` and `right`. Two last ones being optional as they have default `False` value.

User can prefix argument value with its name and `=` symbol to explicitly specify values just for the named arguments: `%Trim(-2, right=True)`. This way arguments can be passed out of (defined in the prototype) order: `%Trim(left, width=-1)`

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
File conflict arises when a template generates the same name for two different files or generated name already exists in the filesystem.

`tempren` supports the following conflict resolution strategies:
- `stop` - Reports an error and stops program execution (default, enabled with `--conflict-stop`/`-cs` flag)
- `ignore` - Reports problem as a warning and continue renaming leaving source file name intact (enabled with `--conflict-ignore`/`-ci` flag)
- `override` - Replaces destination file with the one being processed (enabled with `--conflict-override`/`-co` flag)
- `manual` - Interactively prompts the user to select one of the above conflict resolutions (enabled with `--conflict-manual`/`-cm` flag)
# Ad-hoc tags
TODO
# Tag aliases
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
