# PARUS Application Programming Interface (API)

The API reference for **Parus** is automatically generated from Google-style docstrings using 
[**Sphinx**](https://www.sphinx-doc.org/) with the
[**PyData Sphinx Theme**](https://pydata-sphinx-theme.readthedocs.io/).

Users can download the `api.zip` archive from this directory for offline access.
The archive is refreshed with each release to reflect the latest documentation.

After unzipping, open:

```
[unzipped folder]/index.html
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
| `make publish`  | Package `build/html` into `api.zip` for distribution               |

After a successful build, the entry page is at:

```
build/html/index.html
```

Open with any web browser.
