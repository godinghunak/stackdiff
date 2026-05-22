# stackdiff

Compare two Docker Compose files and summarize service-level changes.

---

## Installation

```bash
pip install stackdiff
```

Or install from source:

```bash
git clone https://github.com/yourname/stackdiff.git && cd stackdiff && pip install .
```

---

## Usage

```bash
stackdiff old-compose.yml new-compose.yml
```

**Example output:**

```
~ web       image changed (nginx:1.23 → nginx:1.25)
+ worker    new service added
- cache     service removed
= db        no changes
```

You can also use it as a Python library:

```python
from stackdiff import compare

changes = compare("docker-compose.v1.yml", "docker-compose.v2.yml")
for change in changes:
    print(change)
```

---

## Options

| Flag | Description |
|------|-------------|
| `--format json` | Output changes as JSON |
| `--quiet` | Only show added/removed/changed services |
| `--version` | Show the current version |

---

## Requirements

- Python 3.8+
- PyYAML

---

## Contributing

Pull requests are welcome. Please open an issue first to discuss any significant changes.

---

## License

[MIT](LICENSE)