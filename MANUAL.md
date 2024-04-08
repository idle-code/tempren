<!-- TOC -->
* [Installation](#installation)
  * [Snap](#snap)
  * [PyPI](#pypi)
    * [Additional dependencies](#additional-dependencies)
* [Builtin documentation](#builtin-documentation)
* [Modes of operation](#modes-of-operation)
  * [Recursive file discovery](#recursive-file-discovery)
* [Template syntax](#template-syntax)
  * [Tag name](#tag-name)
  * [Tag configuration arguments](#tag-configuration-arguments)
  * [Context](#context)
    * [Pipe list sugar](#pipe-list-sugar)
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
  * [Loading arguments from files](#loading-arguments-from-files)
<!-- TOC -->

* * *

# Installation
## Snap
`tempren` can be found on the [snapcraft store](https://snapcraft.io/tempren).
To install it, you can use graphical package manager or command:
```commandline
snap install tempren
```
Snap packages are updated automatically so no additional configuration is necessary.

<!--
## AppImage
On the [releases page](https://github.com/idle-code/tempren/releases), under _Assets_ you can find .AppImage files that can be downloaded and executed as is.
To install `tempren` this way, you will need to:
```commandline
# Download the .AppImage file
curl -o tempren https://<link to the latest AppImage>

# Make the file executable
chmod +x ./tempren

# Install it in any directory that is in your $PATH
sudo mv ./tempren /usr/local/bin
```
Currently, AppImage release doesn't support automatic updates so if new version of the `tempren` is released, you will need to repeat this installation procedure.
-->

<!--
## Docker
TODO
-->

## PyPI
If `pip` is installed on the target system,
`tempren` can be installed as any other Python package:
```commandline
pip install [--user] 'tempren[video]'
```

`pip` doesn't automatically update packages so to keep `tempren` up-to-date, another command have to be used each time new version is released:

```commandline
# Update already installed package to the latest version:
pip install [--user] --upgrade 'tempren[video]'
```

> Note: `[video]` part of the package name indicates that optional `Video` tags should be installed. If you don't plan to work with video files, you can safely omit this part.

### Additional dependencies
Some tags under `Video` category may not be available if there is no [MediaInfo](https://mediaarea.net/en/MediaInfo) library installed on the system. This library is used to extract the metadata out of various media container formats.
As this dependency cannot be installed via `pip`, user is expected to deal with it manually.

Most often, a distribution-specific package manager can be used to install version of `libmediainfo` package.
For example:
```commandline
# Install MediaInfo library on distros using `apt` package manager:
sudo apt install libmediainfo0v5
```

# Builtin documentation
To eliminate the need for accessing external resources like websites or manpages while working with this tool, `tempren` comes in with extensive build-in documentation that is the main source of knowledge about installed tags and command line options.

Short documentation for all command line arguments can always be retrieved via `--help`/`-h` flag:
```commandline
tempren --help
```
> Note: Options which description starts with a `(default)` clause, do not have to be specified explicitly on the command line.

<!--
TODO: Longer documentation (this manual) can be retrieved via `--help-manual`/`-hm` flag:
```commandline
tempren --help-manual
```
-->

`--help`/`-h` flag can also be used to display tag-specific documentation when a tag name is given as an argument:
```commandline
tempren --help [Category.]TagName
```

To find out which tags are available to use in the templates, `--list-tags`/`-l` flag can be used:
```commandline
tempren --list-tags
```
The output of this command will list all available tag names sorted by name and grouped by category they belong to.


# Modes of operation
`tempren` have two main modes of operation: **name** and **path**.

In the (default) **name** mode (represented by `--name`/`-n` flag), the template is used for filename generation only.
This mode is used most often as it doesn't alter directory structure and focuses just on the files. In this mode, if a path separator (i.e. `/`) is present in the generated path, an error will be reported.

Name mode is used mostly when operating on a single directory or files specified directly in the command-line arguments.

In the **path** mode (enabled by `--path`/`-p` flag), for each processed file, the template generates a whole, new path (relative to the input directory).
This way you can move (sort) files into dynamically generated catalogues.

The input directory is important for the path mode because all generated paths are relative to it. What is used as the input directory depends on how you pass the arguments to the `tempren`:
- For **file paths** passed directly (in the command line), their input directory will be the directory they are currently in - i.e. `dirname <processed-file>`
- **Directory paths** passed directly will be considered input directories on their own - files contained within will have them as input directory

> Note: When using recursive file discovery, only the top-most directory (the one passed in the command line) is considered as input directory.

## Recursive file discovery
By default, `tempren` will **not** descend into subdirectories of specified input directory.
To allow recursive file discovery, `--recurse`/`-r` flag have to be used.

> Note: If `--include-hidden` flag is used, hidden directories will also be scanned.

<!--
TODO: Add warning note about symlinked directories?
-->

# Template syntax
Template pattern consist of a _raw text_ interleaved with _tag invocations_:
```
Raw text with a %TagCategory.TagName() in it
```
Raw text is treated as a constant - it doesn't change across template evaluations.
Tag invocation starts with `%` symbol followed by the [_tag name_](#tag-name), [_argument list_](#tag-configuration-arguments) and (optionally) its [_context_](#context).

## Tag name
A fully qualified tag name consists of a category and tag name separated by a single dot `.`.\
The tag name is **case-sensitive** and conforms to CamelCase naming convention.\
The category name is **case-insensitive** but to keep convention consistent it is also presented in the same (CamelCase) manner.

If the tag name is unique across categories it can be used without explicit category specification (and separating dot) like this:
```
Raw text with a %UniqueTag() in it
```

When non-unique tag name (present in more than one category) is used this way, `tempren` will report an error about tag ambiguity.

## Tag configuration arguments
Some tags might or have to be configured before they can do their work.
To do so, the user must pass configuration arguments in the tag _argument list_.
What arguments are expected and in what order can be found by looking at tag signature in the built-in [tag documentation](#Builtin-documentation).

The argument list follows tag name and is contained between parentheses: `()`.
Each argument value is separated by a single coma `,` (with optional white spaces) and can be one of three types:
- `int` for integer numbers (that match `-?[0-9]+` regex)
- `str` for quoted string literals (both single `'` and double `"` quotation marks can be used)
- `bool` for boolean flags

Numbers can be accepted only in decimal (base 10) representation without fractional part: `%Count(0, 1, 4)`

String literals may contain any character except for the used quote mark - if the quote mark needs to be passed,
it should be escaped (prefixed) with a single backslash character, i.e. `\'` or `\"`.

Boolean flags can accept two types of values: `True`/`true` or `False`/`false`.\
Additionally, a shortcut exists for setting the flag argument to `True` - just use the flag name as an argument value (similar to explicit argument names in programming languages).
Therefore, the following invocations are equivalent:
```
%Trim(-2, left=True)
%Trim(-2, true)
%Trim(-2, left)
```

The tag prototype (which can be found in tag build-in documentation) describes the names and types of every argument the tag configuration expects:
```
%Trim(width: int, left: bool = False, right: bool = False){...}
```
The above prototype indicates that this tag accepts up to 3 arguments named `width`, `left` and `right`. The last two are optional as they have default `False` value.

User can prefix argument value with its name and `=` symbol to explicitly specify values just for the named arguments: `%Trim(-2, right=True)`. This way, arguments can be passed out of (defined in the prototype) order: `%Trim(left, width=-1)`

Order of arguments is important if explicit names are not used: `%Trim(-1, True)` will set `left` flag because it's second in the argument list.

## Context
Similar to arguments, some tags can (or have to) operate on the _context_ which is another way to pass the data to the tag. In contrast to the arguments,
which have to stay the same during the entire renaming operation, contexts can change between each tag invocation. They might be considered a dynamic argument.

To pass a context to the tag invocation, use curly braces `{}` with template expression embedded between.
The curly braces can be placed directly after the argument list:
```
%Trim(5, left){Long text}
```
or (if the argument list is empty) directly after the tag name:
```
%Upper{small text}
```

The most important feature of contexts is their dynamic nature - they can contain entire sub-templates.
In the following example, the `Lower` tag receives context containing the processed file extension and makes it lowercase:
```
%Lower(){%Ext()}
```

To check if the tag might operate on a context, check build-in documentation.
The symbol after the tag name indicates context requirements:
- No symbol - when prototype ends with just argument list (`(...)`) - indicates that the tag doesn't operate on contexts and passing one will result in an error.
- `{...}` symbol indicates that this tag **requires** some context to be passed
- `[{...}]` symbol denotes that the tag **can** use the context if one is passed to it

### Pipe list sugar
> Note: Currently pipe list syntax is limited as it has to be the last element of the whole (sub)template.
> This might change in the future.

Sometimes it is desirable to create a chain of context invocations such as:
```
%Lower{%Collapse{%Strip{%Name()}}}
```

To streamline such operations, _pipe list_ syntax sugar can be used.
The, following expression is equivalent to the one above:
```
%Name()|%Strip()|%Collapse()|%Lower()
```

In the pipe list, there can be no contexts (therefore no curly braces) as the context is passed directly from the previous tag - from left to right.

> Note: For pipe list syntax, an empty argument list is required to denote the end of the tag name.
> This behaviour might change in the future.

# Filtering
Filtering allows for inclusion/exclusion of specific files from the renaming operation.

There are three types of filtering expressions supported:
- `template` - tag-template evaluated Python predicate expression, e.g.: `%Size() > 10*1024`
- `glob` - globbing expression, e.g.: `*.mp3`, `IMG_????.jpg`
- `regex` - python-flavored regular expressions, e.g.: `.*\.jpe?g`

## Template-based filtering
Template-based filtering is the most powerful and allows for the inclusion/exclusion of files based on their metadata.

A filter expression can be passed with `--filter-template`/`-ft` flag.
Filter expression tag template is rendered for each file and evaluated as **Python expression**.
If the result of evaluation is [_truthy_](https://docs.python.org/3/library/stdtypes.html#truth-value-testing), the file is considered for renaming.

For example, the following filtering template will exclude files larger than 1024 bytes:
```
%Size() <= 1024
```

Standard Python boolean operators (`and`, `or`, `not`) and built-in functions can be used to chain multiple conditions.\
For example, to include only image files that are not PNGs, the following filter expression can be used:
```
%IsMime("image") and not %Ext().endswith("png")
```

> Note: Filtering templates are evaluated a bit differently from the ones used for name generation - values generated from the tags are escaped to create valid Python literals.
> Therefore, above expression could be rendered as: \
> `True and not ".png".endswith("png")`

## Glob filtering
Glob filtering allows to include/exclude files based on the [glob expression](https://en.wikipedia.org/wiki/Glob_(programming)) matching their filenames. People used to the terminal should be familiar with this kind of filtering as it's the same one used by most *nix shells.

For example, to rename only files with an `Image_` as a prefix, the following pattern can be used:
```
Image_*
```

## Regex filtering
Regular expression filtering allows to include/exclude files based on regex expression matching their filenames.

For example, to rename only files that start with a digit, following pattern can be used:
```
^\d.*
```
This feature uses [Python-flavored](https://docs.python.org/3/howto/regex.html) regular expressions.

> Note: Regular expressions are infamous for their complexity. It is always better to prefer a simpler solution if it can accomplish the same result.

## Filter inversion
Sometimes it might be easier to specify a filter for files which should **not** be included.
To negate/invert any filtering expression you can use `--filter-invert`/`-fi` flag.

# Template-based sorting
In some cases (i.e. when `Count` tag is used), files should be processed in specific order to make renaming useful.
`--sort`/`-s` flag can be used to order files based on their metadata.

Sort expression is similar to the [filter template](#Template-based-filtering) in a way that it is also used to generate a **Python expression** which, after evaluation, is used to order the files considered for renaming.

For example, to order files based on their original name, the following expression can be used:
```
%Name()
```

In contrast to filtering expressions, the sorting expression has to be evaluated into a valid [Python tuple](https://docs.python.org/3/tutorial/datastructures.html#tuples-and-sequences) literal (excluding parenthesis). So, to add another sorting criteria (for cases where the first key may repeat across files), a comma `,` should be used as a sorting criteria separator.

For example, to order files based on their extension the first and then their size, the following expression can be used:
```
%Ext(), %Size()
```

> Note: Sorting templates are evaluated a bit differently from the ones used for name generation - values generated from the tags are escaped to create valid Python literals.
> Therefore, above expression could be rendered as: \
>  `(".png", 12345)`

## Sorting order inversion
By default, the sorting expression order files in ascending order.
To change this behaviour, `--sort-invert`/`-si` flag can be used.

# Conflict resolution strategies
File conflict arises when a template generates the same path for two different files or the generated path already exists in the filesystem.

`tempren` supports the following conflict resolution strategies:
- `stop` - Reports an error and stops program execution (default, indicated by `--conflict-stop`/`-cs` flag)
- `ignore` - Reports problem as a warning and continues renaming leaving source file name intact (enabled with `--conflict-ignore`/`-ci` flag)
- `override` - Replaces destination file with the one being processed (enabled with `--conflict-override`/`-co` flag)
- `manual` - Interactively prompts the user to select one of the above conflict resolutions (enabled with `--conflict-manual`/`-cm` flag)

# Ad-hoc tags
If the built-in tag library doesn't contain the tag appropriate for the user problem, `tempren` allows importing external executables as new, ad-hoc tags.
To create an ad-hoc tag, you will need to provide an executable path as an argument to the `--ad-hoc`/`-ah` flag. After doing so, a new tag will be placed under `Adhoc` category, and you will be able to see its documentation (i.e. invocation details) with the help of `--help`/`-h` flag:

```commandline
tempren --ad-hoc awk --help awk
```

> Note: When executing the ad-hoc tags, even with `--dry-run`/`-dr` flag, `tempren` doesn't have control of the behaviour of the invoked executables.
> Care should be taken to make sure that the user-provided program doesn't create any undesirable side effects upon template execution.

There are two ways in which an executable associated with an ad-hoc tag can be invoked.
If no context is provided in the tag template, the relative path to the processed file
is appended as the last parameter to the command line.

For example, to count lines of the processed text file, an `awk` utility can be used as such:
```commandline
tempren --ad-hoc Awk=awk '%Base()_%Awk("END {print NR}")%Ext()' *.txt
```

This invocation will result in the execution of `awk 'END {print NR}' <processed-file-path>` command for each processed file.
Explicit naming (`Awk=` part in the above example) can be skipped. This will result in the base name of the executable being used as a tag name.

If the context is provided, it will be passed to the command's standard input (`stdin`) and the command will **not** receive the processed file path.

For example, `tr` utility can be used to remove some characters from the base file name by passing it to its standard input (context) as such:
```commandline
tempren --ad-hoc Tr=tr '%Tr(" _\\-.@~", "-"){%Base()}%Ext()' --help Tr
```

Regardless of how the underlying ad-hoc executable will be invoked, any data sent to the `stdout` by it will be used as a tag output
and any data sent to the `stderr` channel will be ignored.

<!-- CHECK: -->
If the invoked command returns a non-zero error code, `tempren` will report this as an error.


Program arguments can be passed in the ad-hoc tag arguments but care should be taken to
separate them correctly as spaces do not delimit the arguments like in the shell environment.
For example, to pass two parameters to the ad-hoc `Program`, the following syntax should be used:
```
%Program("--flag-parameter", "positional")
```

# Tag aliases
Tag aliases are templates that can be reused as standalone tags.
To create a new alias, `--alias`/`-a` flag can be used:
```commandline
tempren --alias 'Normalized=%Lower{%Name()}' --help Normalized
```
Tags created from the aliases cannot receive any arguments or context - they are simply placeholders where the underlying template will be inserted.


# Various options
## Dry run
To facilitate discovery-based usage learning, `tempren`'s `--dry-run`/`-dr` flag can be used to disable the actual file renaming stage of the pipeline. This way, users can test their templates without making changes to the filesystem.
> Note: While dry-run is active, side effects from filtering/sorting template expressions (which are valid Python code), ad-hoc tags
> or even tags themselves may still affect the file system.\
> Be careful not to copy-paste templates that look suspicious.

## Verbosity levels
The number of messages produced by the tool can be increased with `--verbose`/`-v` flag
and decreased by `--quiet`/`-q` flag.
Normal messages are directed to the standard output (`stdout`) while warnings and errors are sent to `stderr`.

## Hidden files handling
By default, `tempren` won't consider hidden files or directories for renaming.
To include such files in the renaming process, `--include-hidden`/`-ih` flag can be used.

> Note: `--include-hidden` in combination with `--recursive` flag, changes how file discovery is performed.
> When both flags are specified, hidden directories and any files in them **will be** considered for renaming.

<!--
TODO: How will tempren behave when encountering the symbolic link to the directory **outside** input directory?

## Symbolic links handling
`tempren` doesn't treat symbolic links differently from the files they are targeting but each tag can introduce its own behaviour.
-->

## Loading arguments from files
If the command line argument starts with a `@` symbol, `tempren` will assume that it is a file containing the desired program arguments, and it will load it (treating each line as a separate argument).
This is especially useful in the case of reusing the same pattern (or program arguments in general) over and over.
