#!/usr/bin/env python3
"""Build the 2025 DENNIS contribution-art repo (bright letters + scatter)."""
import os
import random
import subprocess
from datetime import date, timedelta

NAME = "Dennis Gavrilenko"
EMAIL = "dennisg009@gmail.com"
LETTER_LO, LETTER_HI = 20, 28
NOISE_P, NOISE_MAX = 0.16, 3
DUST_P, DUST_LO, DUST_HI = 0.04, 4, 8
MARGIN, SEED = 10, 7
FONT = {
    "D": ["####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."],
    "E": ["#####", "#....", "#....", "####.", "#....", "#....", "#####"],
    "N": ["#...#", "##..#", "##..#", "#.#.#", "#..##", "#..##", "#...#"],
    "I": ["###", ".#.", ".#.", ".#.", ".#.", ".#.", "###"],
    "S": ["#####", "#....", "#....", "#####", "....#", "....#", "#####"],
}


def first_sunday(y):
    j = date(y, 1, 1)
    return j - timedelta(days=(j.weekday() + 1) % 7)


def glyphs(word):
    rows = [""] * 7
    for i, ch in enumerate(word):
        g = FONT[ch]
        for r in range(7):
            rows[r] += g[r]
        if i != len(word) - 1:
            for r in range(7):
                rows[r] += "."
    return rows


def build_counts():
    rows = glyphs("DENNIS")
    ww = len(rows[0])
    random.seed(SEED)
    counts = {}
    for r in range(7):
        for c in range(ww):
            if rows[r][c] == "#":
                counts[(r, MARGIN + c)] = random.randint(LETTER_LO, LETTER_HI)
    for r in range(7):
        for c in range(53):
            if (r, c) in counts:
                continue
            roll = random.random()
            if roll < DUST_P:
                counts[(r, c)] = random.randint(DUST_LO, DUST_HI)
            elif roll < DUST_P + NOISE_P:
                counts[(r, c)] = random.randint(1, NOISE_MAX)
    return counts


def main():
    counts = build_counts()
    os.makedirs("github-art", exist_ok=True)
    os.chdir("github-art")
    subprocess.run(["git", "init", "-q", "-b", "main"], check=True)
    subprocess.run(["git", "config", "user.name", NAME], check=True)
    subprocess.run(["git", "config", "user.email", EMAIL], check=True)
    fs = first_sunday(2025)
    stream, mark = [], 0
    cells = []
    for (r, c), n in counts.items():
        d = fs + timedelta(weeks=c, days=r)
        if d.year == 2025:
            cells.append((d, n))
    cells.sort()
    for d, n in cells:
        unix = int((d - date(1970, 1, 1)).days) * 86400 + 12 * 3600
        msg = f"art {d}"
        for _ in range(n):
            mark += 1
            stream.append(
                f"commit refs/heads/main\nmark :{mark}\n"
                f"author {NAME} <{EMAIL}> {unix} +0000\n"
                f"committer {NAME} <{EMAIL}> {unix} +0000\n"
                f"data {len(msg.encode())}\n{msg}\n"
            )
            if mark > 1:
                stream.append(f"from :{mark - 1}\n")
    subprocess.run(["git", "fast-import", "--quiet"], input="".join(stream), text=True, check=True)
    print(f"generated {mark} commits across {len(cells)} days")


if __name__ == "__main__":
    main()
