# Elucidator

Extremely simple static site generator script written in Python, mostly for use on my personal website. Because of this, features are limited strictly to ones that I require.

Named after a sword from the anime Sword Art Online, just because.

Tested on Ubuntu/WSL, should also work on Windows.

## Features
- basically just fills html teplate file with content for each .md file, with special case for top level index file
- extremely simple templating using [Mustache](https://mustache.github.io/)

## Usage

```python elucidator.py {ROOT_DIR}```

## Future features
- properly rewrite everything so that it handles paths and files properly
- automatic check for required files and config values
- automatic menu blob generation
- automatic index file for subfolder generation

## Used tech
- uses Py-Markdown for parsing Markdown with code highlighting and few other extensions(tables, TOC)
- Mustache (Chevron) for templating

## Dependencies
- Python 3.6
- chevron
- pyyaml
- py-markdown

## Generation progress
- load config yaml file
- start copying and filling pages
- tada, done!