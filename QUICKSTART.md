# Quickstart
People don't have to rename massive amounts of files very often and
learning new software just to solve the problem you are facing sporadically
might be daunting.

This quickstart is meant to introduce you to the `tempren` and give you
enough information to make sure it is up to the task you are facing.
You will need around 5 minutes total to work through it.
**TODO: Measure actual time**

For more comprehensive documentation you can always refer to the [manual](MANUAL.md).

**Note: When playing with tempren make sure to use `--dry-run` (`-d`) flag so that the actual files are not accidentally changed.**

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

With **path** mode (enabled by `-p`, `--path` flag), the template generates a whole path (relative to the input directory).
This way you can sort files into dynamically generated catalogues.

## Tag template syntax
**Raw text**
**Tag name (and optional category)**
**Arguments + types/kinds**
**Contexts**
**Escaping**
**CLI escaping considerations**

## Available tags
**Built-in listing and help**
```commandline
tempren -l
```

```commandline
tempren -h <tag name>
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
