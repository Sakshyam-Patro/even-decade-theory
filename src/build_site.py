"""Generate the data-driven sections of index.html from output/ files.

Splices the full 93-GOAT table (from goat_list.csv) into the {{GOAT_ROWS}}
placeholder so the site can never drift from the analysis outputs.
"""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent


def main() -> None:
    goats = pd.read_csv(ROOT / "output" / "goat_list.csv").sort_values("occupation")
    rows = []
    for _, r in goats.iterrows():
        parity = "even" if r.even_decade else "odd"
        cls = ' class="ev"' if r.even_decade else ""
        rows.append(
            f"<tr{cls}><td>{r.occupation.title()}</td><td>{r['name']}</td>"
            f"<td>{int(r.birthyear)}</td><td>{parity}</td></tr>")
    html_path = ROOT / "index.html"
    html = html_path.read_text()
    if "{{GOAT_ROWS}}" not in html:
        raise SystemExit("placeholder {{GOAT_ROWS}} not found in index.html")
    html_path.write_text(html.replace("{{GOAT_ROWS}}", "\n".join(rows)))
    print(f"injected {len(rows)} GOAT rows into index.html")


if __name__ == "__main__":
    main()
