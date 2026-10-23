# Repository guidance

## Development and verification

- Use Poetry: `make install-dev` installs the `dev,test` groups; `poetry.toml` keeps the environment in `.venv`. Code must remain Python 3.10-compatible, although CI tests only 3.11–3.13.
- `make check` runs non-mutating format checks → Ruff and Pylint → mypy → the full test suite. `make format` writes changes; `make lint-fix` only applies Ruff fixes, not the other checks.
- For offline verification, use `make test-fast` (`poetry run pytest -m "not slow and not integration"`). `make test`, `make check`, and `make test-cov` include live DNS integration tests, which require working external DNS and can fail in restricted environments.
- Focus one test with `poetry run pytest tests/test_check.py::TestDomainChecker::test_acheck_free_domain`; append `-m "not slow and not integration"` when selecting a whole file for offline testing.
- `make test-cov` enforces 80% coverage with branch measurement enabled; ordinary `make test`/`make check` do not measure coverage.
- Pre-commit targets exist in the Makefile, but there is no checked-in `.pre-commit-config.yaml`; use the explicit checks above rather than assuming hooks are configured.

## Execution flow and compatibility

- The installed `check-filter` command invokes `check_filter.cli:app` directly, not `cli.run`; the latter's KeyboardInterrupt handler only applies when explicitly used (including `python -m check_filter.cli`). Pass CLI arguments through `poetry run check-filter ...`; `make run` invokes the bare command.
- CLI commands validate input, then use `asyncio.run(utils.print_result(...))`. `utils.print_result` schedules individual `DomainChecker.acheck` calls and returns completion-order results; it does not use `acheck_many`, which preserves input order via `asyncio.gather`.
- `CheckResult` is frozen and supports legacy `(domain, is_free)` unpacking. Preserve these behaviors and the package-root exports in `check_filter/__init__.py` when changing the library API.
- Detection is DNS A-record comparison only: NXDOMAIN becomes `UNKNOWN`, timeout/no nameservers become `ERROR`, and empty input raises `dns.resolver.NoAnswer`. Keep error/unknown results distinct from `FREE` and `BLOCKED`.

## DNS and testing gotchas

- `DomainChecker` uses `Resolver(configure=False)`, ignoring system resolver settings. Defaults are `8.8.8.8`, or `178.22.122.100` whenever `CI` exists in the environment—even `CI=false`. An explicit nonempty `nameservers` list overrides this; the CI test job sets `CI=true`.
- Unit tests mock `checker.resolver.resolve` with `AsyncMock`; successful answer records expose `.address`. CLI tests patch `check_filter.cli.utils.print_result` with `AsyncMock`. Fixtures in `tests/conftest.py` do not automatically mock DNS for all tests.

## Version and release traps

- Distribution version (`pyproject.toml`) and CLI/library version (`check_filter/__init__.py`) are separate and currently differ. `tests/test_project.py::TestVersionConsistency::test_version_matches_pyproject` actually checks a hardcoded version, not TOML. For intentional version bumps, reconcile all three; `make release-*` only changes Poetry metadata.
- `.github/workflows/release.yml` runs on published releases or manual dispatch, not pushes/PRs, and includes publishing steps. Its artifact lookup strips the first character from the Git ref and expects that version to match the built distribution (normally a `v`-prefixed release tag).
