# PARUS Application Programming Interface (API)

The API reference for **Parus** is automatically generated from Google-style docstrings using 
[**Sphinx**](https://www.sphinx-doc.org/) with the
[**PyData Sphinx Theme**](https://pydata-sphinx-theme.readthedocs.io/).

Users can download the `api.tar.gz` archive from this directory for offline access.
The archive is refreshed with each release to reflect the latest documentation.

`*.tar.gz` is produced by archiving files with **Tape Archive (`tar`)** then compressing with **GNU Zip (`gzip`)**.  
This format is widely supported across POSIX systems (Unix/Linux/macOS), and modern versions of Windows (10 and later).

To extract the archive, run the following command, replacing `[api_doc_dir]` with the target directory.

```bash
mkdir [api_doc_dir]
tar -xf api.tar.gz -C [api_doc_dir]
```

After unarchiving, open the `index.html` with web browser:

```
[api_doc_dir]/index.html
```

---

## Building Locally

A `Makefile` is provided so the documentation can be regenerated on demand.
The build works on **Windows** (via `MinGW-make`) and **Unix-like systems**.

Required Python packages (install into your environment):

```
pip install sphinx sphinx-autodoc-typehints sphinx-design pydata-sphinx-theme
```

Common targets:

| Target          | Purpose                                                            |
|-----------------|--------------------------------------------------------------------|
| `make generate` | Regenerate the `source/_api` stubs from the `parus` package        |
| `make html`     | Build the HTML documentation into `build/html`                     |
| `make strict`   | Same as `html`, but treats all warnings as errors (CI mode)        |
| `make rebuild`  | `clean` + `generate` + `html` -> the typical full refresh          |
| `make clean`    | Remove the generated `_api` stubs and the entire `build` directory |
| `make publish`  | Package `build/html` into `api.tar.gz` for distribution            |

After a successful build, the entry page is at:

```
build/html/index.html
```

Open with any web browser.
