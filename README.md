# Tableaux de bord pédagogiques

A warren plugin for moodle learning analytics dashboard.

## Documentation

Project documentation is available under `docs/` folder.

It is a Markdown-based documentation generated with
[`Mkdocs`](https://www.mkdocs.org/).

It is deployed automatically with [`mike`](https://pypi.org/project/mike/)
utility (in order to manage documentation of the multiple versions of the `tdbp`
plugin).

To build and run the documentation on your machine, execute the following
commands: 

```bash
# Build documentation site
make docs-build

# Run mkdocs live server for dev docs
make docs-serve
```

## License

This work is released under the MIT License (see [LICENSE](./LICENSE.md))
