# Check Filtering

[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)
[![GitHub release](https://img.shields.io/github/release/hatamiarash7/CheckFiltering.svg)](https://GitHub.com/hatamiarash7/CheckFiltering/releases/)
[![Release](https://github.com/hatamiarash7/CheckFiltering/actions/workflows/release.yml/badge.svg)](https://github.com/hatamiarash7/CheckFiltering/actions/workflows/release.yml)
[![codecov](https://codecov.io/gh/hatamiarash7/CheckFiltering/branch/master/graph/badge.svg)](https://codecov.io/gh/hatamiarash7/CheckFiltering)
![GitHub](https://img.shields.io/github/license/hatamiarash7/CheckFiltering)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/check-filter?label=Supported%20versions)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Checked with mypy](https://www.mypy-lang.org/static/mypy_badge.svg)](https://mypy-lang.org/)

A command-line tool to check if domains are filtered (blocked) in Iran by analyzing DNS responses.

## 🔍 How It Works

This tool checks if a domain is blocked by Iranian ISPs by:

1. Resolving the domain's A record using DNS
2. Comparing the resolved IP addresses against known blocking IPs used by Iranian ISPs
3. Reporting whether the domain is blocked or accessible

**Note:** This tool can only detect DNS-based blocking and does not have the power to detect other types of filtering or network disorders.

## ✨ Features

- 🚀 **Fast async DNS resolution** - Check multiple domains concurrently
- 📋 **Multiple input methods** - Single domain, comma-separated list, or file
- 🎨 **Beautiful CLI output** - Rich formatted tables with live updates
- 🔧 **Configurable** - Custom DNS servers and timeout settings

## 📋 Requirements

- Python 3.10+

## 📦 Installation

### From PyPI

```bash
pip install check-filter
```

### From Source

```bash
git clone https://github.com/hatamiarash7/CheckFiltering.git
cd CheckFiltering
poetry install
```

You can also download the wheel package from the [release](https://github.com/hatamiarash7/CheckFiltering/releases/latest) page.

## 🚀 Usage

### Command Line Interface

#### Check a Single Domain

```bash
check-filter domain github.com
```

![single](.github/single.png)

#### Check Multiple Domains

```bash
check-filter domains github.com,google.com,twitter.com
```

![multiple](.github/multiple.png)

#### Check Domains from File

Create a file with domain names (one per line). Lines starting with `#` are treated as comments:

```text
# Social media
github.com
twitter.com
facebook.com

# Development
gitlab.com
stackoverflow.com
```

Then run:

```bash
check-filter file domains.txt
```

![file](.github/file.png)

#### Show Version

```bash
check-filter --version
# or
check-filter -v
```

#### Show Help

```bash
check-filter --help
check-filter domain --help
check-filter domains --help
check-filter file --help
```

### As a Python Library

```python
import asyncio
from check_filter import DomainChecker, FilterStatus

async def main():
    checker = DomainChecker()
    
    # Check a single domain
    result = await checker.acheck("google.com")
    print(f"{result.domain}: {result.status.value}")
    print(f"Blocked: {result.is_blocked}")
    print(f"IPs: {result.ips}")
    
    # Check multiple domains concurrently
    results = await checker.acheck_many([
        "google.com",
        "twitter.com",
        "github.com",
    ])
    
    for result in results:
        status = "🚫 Blocked" if result.is_blocked else "✅ Free"
        print(f"{result.domain}: {status}")

asyncio.run(main())
```

#### Custom Configuration

```python
from check_filter import DomainChecker

# Use custom blocked IPs and DNS servers
checker = DomainChecker(
    blocked_ips={"10.10.34.34", "10.10.34.35"},
    nameservers=["8.8.8.8", "8.8.4.4"],
    timeout=10.0,
)
```

#### Using CheckResult

```python
from check_filter import CheckResult, FilterStatus

# CheckResult is a dataclass with useful properties
result = await checker.acheck("example.com")

# Access properties
print(result.domain)      # "example.com"
print(result.status)      # FilterStatus.FREE
print(result.is_free)     # True
print(result.is_blocked)  # False
print(result.ips)         # frozenset({'93.184.216.34'})
print(result.error)       # None (or error message if failed)

# Backward compatible tuple unpacking
domain, is_free = result
```

## 🛠️ Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/hatamiarash7/CheckFiltering.git
cd CheckFiltering

# Install dependencies with dev tools
make install-dev
```

### Available Commands

```bash
make help           # Show all available commands
make test           # Run tests
make test-cov       # Run tests with coverage report
make lint           # Run all linters
make lint-fix       # Run linters with auto-fix
make format         # Format code with black and isort
make type-check     # Run type checking with mypy
make check          # Run all checks (format, lint, type-check, test)
make build          # Build package
make clean          # Clean build artifacts
```

### Running Tests

```bash
# Run all tests
make test

# Run tests with coverage
make test-cov

# Run fast tests (exclude slow/integration tests)
make test-fast
```

## 📄 API Reference

### `DomainChecker`

Main class for checking domain filtering status.

```python
DomainChecker(
    blocked_ips: Set[str] | None = None,  # Custom blocked IPs
    nameservers: list[str] | None = None,  # DNS servers to use
    timeout: float = 5.0,                  # DNS query timeout
)
```

**Methods:**

- `acheck(domain: str) -> CheckResult` - Check a single domain
- `acheck_many(domains: list[str]) -> list[CheckResult]` - Check multiple domains

### `CheckResult`

Dataclass containing the result of a domain check.

**Attributes:**

- `domain: str` - The checked domain
- `status: FilterStatus` - The filtering status
- `ips: frozenset[str]` - Resolved IP addresses
- `error: str | None` - Error message if check failed

**Properties:**

- `is_blocked: bool` - True if domain is blocked
- `is_free: bool` - True if domain is not blocked

### `FilterStatus`

Enum with possible filtering statuses:

- `FREE` - Domain is accessible
- `BLOCKED` - Domain is blocked
- `ERROR` - Check failed (timeout, etc.)
- `UNKNOWN` - Domain doesn't exist (NXDOMAIN)

---

## 💛 Support

[![Donate with Bitcoin](https://img.shields.io/badge/Bitcoin-bc1qmmh6vt366yzjt3grjxjjqynrrxs3frun8gnxrz-orange)](https://donatebadges.ir/donate/Bitcoin/bc1qmmh6vt366yzjt3grjxjjqynrrxs3frun8gnxrz)
[![Donate with Ethereum](https://img.shields.io/badge/Ethereum-0x0831bD72Ea8904B38Be9D6185Da2f930d6078094-blueviolet)](https://donatebadges.ir/donate/Ethereum/0x0831bD72Ea8904B38Be9D6185Da2f930d6078094)

<div><a href="https://payping.ir/@hatamiarash7"><img src="https://cdn.payping.ir/statics/Payping-logo/Trust/blue.svg" height="128" width="128"></a></div>

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch: `git checkout -b feature/my-new-feature`
3. Install development dependencies: `make install-dev`
4. Make your changes and add tests
5. Run checks: `make check`
6. Commit your changes: `git commit -am 'Add some feature'`
7. Push to the branch: `git push origin feature/my-new-feature`
8. Submit a pull request

## 🐛 Issues

Found a bug or have a suggestion? Please [open an issue](https://github.com/hatamiarash7/CheckFiltering/issues).

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
