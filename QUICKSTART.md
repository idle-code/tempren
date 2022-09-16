# Quickstart
People don't have to rename massive amounts of files very often and
learning new software just to solve the problem you are facing sporadically
might be daunting.

This quickstart is meant to introduce you to the `tempren` and give you
enough information to make sure it is up to the task you are facing.
You will need around 5 minutes total to work through it.
**TODO: Measure actual time**

For more comprehensive documentation you can always refer to the [manual](MANUAL.md).

> **Note: When playing with tempren make sure to use `--dry-run` (`-d`) flag so that the actual files are not accidentally changed.**

## Installation

**Docker image**

**System installation + sample data**

To verify that you can use `tempren` run:
```commandline
tempren --help
```

## Operation modes
Tempren have two main modes of operation: **name** and **path**.

In the **name** mode (default, enabled by `-n`, `--name` flag), the template is used for filename generation only.
This is useful if you want to operate on files specified on the command line or in a single directory.
**TODO: files cannot be specified on the command line... yet**

With **path** mode (enabled by `-p`, `--path` flag), the template generates a whole path (relative to the input directory).
This way you can sort files into dynamically generated catalogues.

## Tag template syntax
The core concept of `tempren` is **tag template** or **template** for short.
To generate multiple filenames from a single prompt you need a way to distinguish parts that are different between names and tags in the template take care of that.

Template consist of _raw text_ interleaved with _tag invocations_. For example:
```
Raw text with a %TagCategory.TagName() in it
```
As you can see tag invocations really stand out - they always start with `%` symbol followed by an optional tag category and name.
At the end of tag invocation there is an empty argument list. Those familiar with programming quickly notice similarity to the function invocation.
And rightly so - each tag invocation is in fact _called_ for every file which name `tempren` attempts to change.
This is the way `tempren` introduces differences in between processed files.

Many tags don't require any arguments but some can be configured to further tweak their behaviour.
For example:
```
Image_%Count(width=4)%Ext()
```
This is our first template that could actually be used to generate new names.\
Here `Count` tag is used as a simple counter to generate 4-digit numbers for some kind of images.
`Ext` tag renders original file extension - which you often don't want to change.

> **Note: By default (when no `-s`/`--sort` flag is used) `tempren` will process files in order provided by the OS.**\
> This is different to what you usually see in the file manager and may appear random.\
> `Count` tag doesn't know order of processed files and will just provide numbers for each invocation... numbering files randomly if no sorting is specified.

### Tag configuration arguments
Tag arguments can have three types:
- `int` for decimal numbers
- `str` for quoted string literals (you can use single `'` or double `"` quotation marks)
- `bool` for boolean flags

You can see what types of arguments a tag expects by looking at its documentation, for example:
```commandline
$ tempren --help Trim

  %Trim(width: int, left: bool = False, right: bool = False){...}
        width - width of resulting trimmed context or (if negative) number of characters to trim
        left - trim characters from the left
        right - trim characters from the right

Trims context to a specified width by cropping left/right side off
```
tells you that `Trim` tag requires you to provide number of characters to trim and a side.
With this information you can invoke it like: `%Trim(width=3, right=True)` or `%Trim(3, right=true)` or even `%Trim(3, right)`.
This syntax is similar to python invocation with additional shortcut for boolean flags, which if specified are set to `True`.

### Contexts
For processor tags to be useful, there should be a way to limit their scope of operation - **tag context** is a way to do it.

When you look at the tag signature, sometimes you can notice curly braces with ellipsis within: `{...}`
This indicates that tag requires context to work on.
If this symbol is additionally enclosed in square braces - `[{...}]` - it means that context for this tag is optional.
`Trim` tag above requires context to work on. `Count` on the other hand doesn't need it and you will get an error if you try to provide it regardless.

### Escaping
`tempren`
**Escaping**
**CLI escaping considerations**
When running `tempren` from the shell you should be careful to properly escape characters in the template that may be interpreted by it.
Good way to do it is to use single quotes `'` for template arguments and double `"` for string tag arguments inside it:
```commandline
$ tempren -d
```

## Available tags
**Built-in listing and help**
```commandline
tempren -l
```

```commandline
tempren -h <TagName>
```

**Tag kinds (metadata extraction/processing)**
Most of tags falls into one of two categories: extractors or processors.

Extractor tags generate text based on some kind metadata.
`Size`, `Image.Width` and `Name` are just a few examples of such tags.
Sometimes, extracted metadata isn't ready to be used in the filename as is,
this is the time for processor tags to do their job.

Processor tags modify text passed to them in their context.
Most processor tags are versatile enough to justify they placement in `Core` and `Text` categories.
```
%AsSize('kb'){%Size()}KB
```




* * *

## Usage



### Template syntax
Tag template consists of raw text interleaved with tag invocations.
Each tag invocation starts with `%` (percent) character followed by tag name, tag configuration (argument) list (enclosed in `()` parentheses) and - optionally -
tag context (enclosed in `{}` parentheses). Consider following template:
```tempren
File_%Count(start=100).%Lower(){%Ext()}
```

Above expression can be split into:
- Raw text `File_`
- `Count` tag configured with `start` parameter set to `100`
- Raw text `.`
- `Lower` tag (with empty configuration list) operating on context rendered from:
  - `Ext` tag

**Note: You can use `--list-tags` flag to print tag names provided by your `tempren` version.**

When used withing tempren:
```console
$ tempren -d "File_%Count(start=100).%Lower(){%Ext()}" test_directory/
```
One may expect results as:

| Input name   | Output name  |
|--------------|--------------|
| test.sh      | File_100.sh  |
| img1.jpg     | File_101.jpg |
| IMG_1414.jpg | File_102.jpg |
| document.pdf | File_102.pdf |
