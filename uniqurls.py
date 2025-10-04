#!/usr/bin/python3
import argparse
import sys
import re
from urllib.parse import urlparse, parse_qs, urlunparse
from concurrent.futures import ProcessPoolExecutor, as_completed

BANNER = r"""
               _                  __    
  __  ______  (_)___ ___  _______/ /____
 / / / / __ \/ / __ `/ / / / ___/ / ___/
/ /_/ / / / / / /_/ / /_/ / /  / (__  ) 
\__,_/_/ /_/_/\__, /\__,_/_/  /_/____/  
                /_/                     
        uniqurls - URL Deduplicato 🎯
        Made By Sherwood Chaser ❤️
"""

def print_banner_if_interactive():
    if sys.stdout.isatty():
        print(BANNER, file=sys.stderr)

def normalize_url(url: str, ignore_values=True) -> str:
    try:
        parsed = urlparse(url.strip())
        qs = parse_qs(parsed.query, keep_blank_values=True)

        if ignore_values:
            qs_keys = sorted(qs.keys())
            query = "&".join(f"{k}=" for k in qs_keys)
        else:
            query = "&".join(f"{k}={','.join(v)}" for k, v in sorted(qs.items()))

        normalized = urlunparse((parsed.scheme, parsed.netloc, parsed.path, "", query, ""))
        return normalized
    except Exception:
        return url.strip()


def normalize_for_similarity(url: str, collapse_paths=True) -> str:
    u = url.strip()
    parsed = urlparse(u)
    path = parsed.path
    path = re.sub(r"/\d+", "/{id}", path)
    path = re.sub(r"\.[a-zA-Z0-9]+$", ".*", path)

    if collapse_paths:
        parts = [p for p in path.split("/") if p]
        if len(parts) > 1:
            path = "/" + parts[0] + "/" + parts[1] + "/*"
        elif len(parts) == 1:
            path = "/" + parts[0] + "/*"

    return f"{parsed.scheme}://{parsed.netloc}{path}"


def dedupe_urls(urls, similar=False, workers=4):
    seen = set()
    results = []

    with ProcessPoolExecutor(max_workers=workers) as executor:
        futures = {}
        for url in urls:
            url = url.strip()
            if not url:
                continue

            if similar:
                futures[executor.submit(normalize_for_similarity, url)] = url
            else:
                futures[executor.submit(normalize_url, url)] = url

        for future in as_completed(futures):
            key = future.result()
            original_url = futures[future]
            if key not in seen:
                seen.add(key)
                results.append(original_url)

    return results


def main():
    print_banner_if_interactive()

    parser = argparse.ArgumentParser(description="Deduplicate URLs efficiently with parallel processing.")
    parser.add_argument("-l", "--list", help="File containing list of URLs", type=str)
    parser.add_argument("-s", "--similar", help="Deduplicate similar endpoints & deep paths", action="store_true")
    parser.add_argument("-w", "--workers", help="Number of parallel workers (default: 4)", type=int, default=4)
    parser.add_argument("-o", "--output", help="Save results to file instead of stdout", type=str)
    parser.add_argument("-op", "--only-params", help="Only show URLs that have query parameters", action="store_true")
    parser.add_argument("--depth", help="(optional) number of path segments to keep when collapsing (default=2)", type=int, default=2)
    args = parser.parse_args()

    if args.list:
        with open(args.list, "r", encoding="utf-8") as f:
            urls = f.readlines()
    else:
        urls = sys.stdin.readlines()
    results = dedupe_urls(urls, similar=args.similar, workers=args.workers)

    if args.only_params:
        results = [u for u in results if urlparse(u).query]

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            for url in results:
                f.write(url.strip() + "\n")
    else:
        for url in results:
            print(url)


if __name__ == "__main__":
    main()

