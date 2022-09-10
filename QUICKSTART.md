# Quickstart (5 minutes required)
People don't have to rename massive amounts of files very often and
learning new software just to solve the problem you are facing sporadically
might be daunting.

This quickstart is meant to introduce you to the `tempren` and give you
enough information to make sure it is up to the task you are facing.
You will need around 5 minutes total to work through it.

For more comprehensive documentation please refer to the [manual](MANUAL.md).

## Installation
```console
$ pip install [--user] tempren
```

## Usage

**Note: When playing with tempren make sure to use `--dry-run` (`-d`) flag so that the actual files are not accidentally changed.**

Tempren have two main modes of operation: **name** and **path**.

In the **name** mode (default, enabled by `-n`, `--name` flag), the template is used for filename generation only.
This is useful if you want to operate on files specified on the command line or in a single directory.

With **path** mode (enabled by `-p`, `--path` flag), the template generates a whole path (relative to the input directory).
This way you can sort files into dynamically generated catalogues.

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
