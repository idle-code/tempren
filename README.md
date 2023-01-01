# Tempren - template-based file renaming utility

![run-tests](https://github.com/idle-code/tempren/actions/workflows/run-tests.yml/badge.svg)
[![codecov](https://codecov.io/gh/idle-code/tempren/branch/develop/graph/badge.svg?token=1CR2PX6GYB)](https://codecov.io/gh/idle-code/tempren)
[![Maintainability](https://api.codeclimate.com/v1/badges/d67f6ebe698b79d75279/maintainability)](https://codeclimate.com/github/idle-code/tempren/maintainability)
[![PyPI version](https://badge.fury.io/py/tempren.svg)](https://badge.fury.io/py/tempren)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/idle-code/tempren/develop.svg)](https://results.pre-commit.ci/latest/github/idle-code/tempren/develop)

`tempren` is a powerful file renaming utility that uses flexible template expressions to create new file paths and names.
New file paths can be based on original filename, created independently or from the underlying file's tags.
Rich library of built-in tag extraction modules helps with tagging many common file types.

## Features
- Template-based filename/path generation
- Audio/Video/Images/etc metadata extraction
- Configurable, metadata-based file selection (filtering)
- Metadata-based sorting

## Installation
Currently only PyPI installation is supported, just run following command:
```commandline
$ pip install [--user] tempren
```

## Documentation
[Manual](MANUAL.md) gives a tour of all `tempren` features and (until quickstart is created) should work as a guide.

<!--
## [Quickstart](QUICKSTART.md)
For quick, five-minute introduction to the most of `tempren` features please refer to the [quickstart](QUICKSTART.md) page.
You can also take a look on the following examples.
-->

## Examples
**Note: When experimenting on your own please use `--dry-run` flag!** \
**Tempren will not override your files by default but invalid template can mangle their names.**

<details>
<summary>Cleaning up names for sensitive (e.g. FAT32) filesystems</summary>

```commandline
$ tempren --recursive --name "%Strip(){%Base()|%Unidecode()|%Sanitize()|%Collapse()}%Ext()" ./Some\ OST/
Renamed: Disk 1/14 - 接近.flac
     to: Disk 1/14 - Jie Jin.flac
Renamed: Disk 1/02 - なつのあお.flac
     to: Disk 1/02 - natsunoao.flac
Renamed: Disk 1/11 - 灯火-re.flac
     to: Disk 1/11 - Deng Huo -re.flac
Renamed: Disk 1/05 - 記録.flac
     to: Disk 1/05 - Ji Lu.flac
Renamed: Disk 1/10 - むかしむかし、あるところに.flac
     to: Disk 1/10 - mukashimukashi, arutokoroni.flac
Renamed: Disk 1/09 - 阿良句のテーマ(ハイ).flac
     to: Disk 1/09 - A Liang Ju notema(hai).flac
...
```
</details>

<details>
<summary>Adding resolution to the image files</summary>

```commandline
$ tempren --name "%Base()_%Image.Width()x%Image.Height()%Ext()" ~/Pictures/Wallpapers
Renamed: 0sa5yfiskqr21.jpg
     to: 0sa5yfiskqr21_3728x4660.jpg
Renamed: rkgjq6883fp81.jpg
     to: rkgjq6883fp81_3024x4032.jpg
Renamed: lcrkvphf28911.jpg
     to: lcrkvphf28911_4016x4684.jpg
Renamed: y6nzcv55k3851.jpg
     to: y6nzcv55k3851_3784x5670.jpg
Renamed: 1211740803547.jpg
     to: 1211740803547_1200x1109.jpg
...
```
</details>

<details>
<summary>Sorting files into directories based on their MIME type</summary>

```commandline
$ tempren -d --path "%Capitalize(){%Mime(subtype)}/%Name()" ~/Downloads
Renamed: dotnet-install.sh
     to: X-shellscript/dotnet-install.sh
Renamed: openrgb_0.7_amd64_buster_6128731.deb
     to: Vnd.debian.binary-package/openrgb_0.7_amd64_buster_6128731.deb
Renamed: prometheus-2.26.0.linux-amd64.tar.gz
     to: Gzip/prometheus-2.26.0.linux-amd64.tar.gz
Renamed: nldb remote.zip
     to: Zip/nldb remote.zip
Renamed: artifacts.zip
     to: Zip/artifacts.zip
Renamed: 2021-06-11_12-09-34.webm
     to: X-matroska/2021-06-11_12-09-34.webm
Renamed: antlr-4.9.2-complete.jar
     to: Java-archive/antlr-4.9.2-complete.jar
...
```
</details>

<details>
<summary>Adding checksums to the names of the audio files</summary>

```commandline
$ tempren --filter-template "%IsMime('audio')" --name "%Base() [%Upper(){%Crc32()}]%Ext()" ./Roger\ Subirana\ Mata\ -\ Point\ of\ no\ return
Renamed: 10-169205-Roger Subirana Mata-Island of light.mp3
     to: 10-169205-Roger Subirana Mata-Island of light [08E46C33].mp3
Renamed: 12-169207-Roger Subirana Mata-Tales of trees.mp3
     to: 12-169207-Roger Subirana Mata-Tales of trees [33EFEC5E].mp3
Renamed: 11-169206-Roger Subirana Mata-Requiem.mp3
     to: 11-169206-Roger Subirana Mata-Requiem [5E48759B].mp3
Renamed: 05-168950-Roger Subirana Mata-The mask.mp3
     to: 05-168950-Roger Subirana Mata-The mask [045DBC19].mp3
Renamed: 03-168948-Roger Subirana Mata-Thryst.mp3
     to: 03-168948-Roger Subirana Mata-Thryst [5D23E43B].mp3
...
```
</details>


## Contributing
If you noticed a bug or have an idea for a new tag please open an issue with appropriate tags.
If you would like to contribute to the development you can visit [contributing page](CONTRIBUTING.md) designed specially for that.
