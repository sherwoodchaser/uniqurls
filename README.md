# 🔗 uniqurls

![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Tool](https://img.shields.io/badge/tool-URL%20Deduplicator-orange)

**uniqurls** is a high-performance Python CLI tool to **deduplicate and filter large URL lists**.  
It was built for bug bounty hunters, security researchers, and recon engineers who need to reduce noisy URL lists into **unique, actionable targets** quickly.

---

## 🔥 What it does (short)
- Removes duplicate URLs while **ignoring query parameter values** (keeps unique parameter *names*).
- Optionally collapses *similar* endpoints (`-s`) — replaces numeric IDs, file-extensions and can collapse deep path segments to a configurable depth.
- Optionally outputs **only** URLs that have query parameters (`-op`).
- Multi-core processing for scale (`-w`).
- Interactive ASCII banner (printed to `stderr` so it **won’t break pipes**).

---

## 📦 Requirements & Installation

- Requires **Python 3.9+** (stdlib only for the core tool).

Install (basic):
```bash
git clone https://github.com/sherwoodchaser/uniqurl.git
cd uniqurls
python3 uniqurls.py -h
```

🧭 Usage (examples)

Read from stdin:

```bash
cat urls.txt | python uniqurls.py
```

Read from file:

```bash
python uniqurls.py -l urls.txt
```

Deduplicate similar paths (IDs, file extensions, collapse deep paths):

```bash
cat urls.txt | python uniqurls.py -s
```

Keep only URLs that have query parameters:

```bash
cat urls.txt | python uniqurls.py -op
```

Set path collapse depth to 3 segments (when using -s):

```bash
cat urls.txt | python uniqurls.py -s --depth 3
```

Use 8 workers for speed:

```bash
python uniqurls.py -l urls.txt -w 8
```

Save deduped output to a file:

```bash
python uniqurls.py -l urls.txt -o uniq.txt
```

Combine flags (example typical recon flow):

```bash
httpx -status -l targets.txt | python uniqurls.py -s --depth 2 -op | tee uniq_params.txt
```


### 🔬 Examples & behavior

Given the input:

```bash
https://example.com
https://example.com/home?qs=1
https://example.com/home?qs=2
https://example.com/api/users/123
https://example.com/api/users/456
https://example.com/electronics/item/a
https://example.com/electronics/item/b
```

After running uniqurl :

### Basic deduplication
```bash
https://example.com
https://example.com/home?qs=1
https://example.com/api/users/123
https://example.com/electronics/item/a
```

### With -s (similar) and --depth 2
```bash
https://example.com
https://example.com/home?qs=1
https://example.com/api/users/123
https://example.com/electronics/item/*
```

### With -op (only parameters)
```bash
https://example.com/home?qs=1
```


python uniqurls.py → will keep one of the /home?qs= lines (unique param names), keep one /api/users endpoint (based on normalization), and one electronics path (if -s is used it collapses).

`python uniqurls.py -s --depth 1` → all /electronics/... URLs collapse to one /electronics/* representative.

`python uniqurls.py -op` → will only output the home?qs=... URL(s) that have query parameters.



### Implementation notes (brief)

Normalization ignores query values and uses sorted parameter names for dedupe keys.

Similar-mode normalization:

Replaces numeric path segments with a token ({id}).

Collapses file extensions to .*.

Collapses the path after the configured --depth into /*.

Banner prints to stderr and only when in interactive TTY mode, so it will never corrupt stdout which is used for piping results into other tools.

Uses Python's ProcessPoolExecutor to parallelize normalization routine for higher throughput on multi-core systems.



### 🛠 Flags Summary

| Flag | Description |
|------|-------------|
| `-l, --list <file>` | Input file containing URLs (one per line). If omitted, `uniqurls.py` reads from **stdin**. Useful for piping workflows. |
| `-s, --similar` | Deduplicate **similar endpoints & deep paths**: replaces numeric IDs in URLs, collapses file extensions (e.g., `photo.jpg` → `photo.*`), and collapses deep paths to a representative form depending on `--depth`. |
| `--depth <N>` | Number of path segments to keep when collapsing in `-s` mode (default: 2). Example: `/a/b/c/d` → `/a/b/*`. Use `--depth 1` to collapse to top-level only (e.g., `/electronics/*`). |
| `-w, --workers <num>` | Number of parallel worker processes (default: 4). Speeds up deduplication on multi-core machines. |
| `-o, --output <file>` | Save deduplicated URLs to a file instead of stdout. |
| `-op, --only-params` | Only show URLs that contain query parameters. Useful for parameterized endpoints or injection points. |
| `-h, --help` | Show the help message and exit. |
