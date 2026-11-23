#!/usr/bin/env python3
"""
scan_project.py  -  Full ERP project scanner (read-only, kisi file ko change nahi karta)

Chalane ka tareeqa (project root se):
    python scan_project.py
    python scan_project.py --root C:\\MOHSIN_VSH_NEWS.TV --include-archive

Output (AUDIT_RECORDS folder mein):
    FULL_SCAN_<timestamp>.md    -> poori report (parhne ke liye)
    FULL_SCAN_<timestamp>.json  -> machine-readable graph/data

Report mein kya hai:
    1. Summary + project tree (LOC ke saath)
    2. Module completeness matrix (domain/service/repo/UI/test/migration)
    3. Har file ka detail: classes, functions, stubs, TODO, imports, "imported by"
    4. Forms/dialogs: input fields, buttons, signal connections
    5. Connections: layer matrix, UI -> Service -> Repository -> DB table chains
    6. Problems: syntax errors, stubs, unresolved imports, circular imports,
       layer violations, orphans, backup/duplicate files, hardcoded secrets
    7. Database: migrations, tables, numbering gaps, table used/unused
    8. Dependencies vs requirements.txt
    9. Test coverage map (kis file ka test nahi hai)
   10. Git status/summary
"""
import argparse
import ast
import datetime as dt
import json
import os
import re
import subprocess
import sys
from collections import defaultdict

EXCLUDE_DIRS = {
    ".venv", "venv", "env", "__pycache__", ".git", ".pytest_cache", ".mypy_cache",
    ".ruff_cache", "node_modules", "build", "dist", ".idea", ".vscode", "site-packages",
}
ARCHIVE_DIRS = {"archive"}
TEXT_EXT = {".py", ".sql", ".md", ".txt", ".toml", ".ini", ".cfg", ".json", ".qss",
            ".ui", ".html", ".ps1", ".iss", ".spec", ".yml", ".yaml", ".css"}
SKIP_CONTENT_NAMES = {".env"}  # secrets: sirf naam list hoga, content kabhi nahi

QT_FORM_BASES = {"QDialog", "QWidget", "QMainWindow", "QFrame", "QGroupBox", "QStackedWidget",
                 "QTabWidget", "QScrollArea", "QWizard", "QMessageBox"}
INPUT_WIDGETS = {"QLineEdit", "QTextEdit", "QPlainTextEdit", "QComboBox", "QSpinBox",
                 "QDoubleSpinBox", "QDateEdit", "QDateTimeEdit", "QTimeEdit", "QCheckBox",
                 "QRadioButton", "QSlider", "QDateTimeEdit"}
BUTTON_WIDGETS = {"QPushButton", "QToolButton", "QCommandLinkButton"}
TABLE_WIDGETS = {"QTableWidget", "QTableView", "QTreeWidget", "QTreeView", "QListWidget", "QListView"}

LAYER_RULES = [
    ("ui", ("/ui/",)),
    ("service", ("/application/services/", "/services/")),
    ("application", ("/application/",)),
    ("repository", ("/repositories/", "/repository/")),
    ("domain", ("/domain/",)),
    ("infrastructure", ("/infrastructure/",)),
    ("tests", ("/tests/", "/test/")),
    ("tools", ("/tools/",)),
    ("config", ("/config/",)),
    ("build", ("/build/",)),
    ("docs", ("/docs/",)),
]
# kaun si layer kis ko import kare to theek nahi
FORBIDDEN = {
    ("ui", "repository"): "UI seedha repository use kar rahi hai (service ke through jana chahiye)",
    ("domain", "infrastructure"): "Domain, infrastructure par depend kar raha hai",
    ("domain", "ui"): "Domain, UI par depend kar raha hai",
    ("domain", "service"): "Domain, service par depend kar raha hai",
    ("service", "ui"): "Service, UI par depend kar rahi hai",
    ("repository", "ui"): "Repository, UI par depend kar rahi hai",
    ("repository", "service"): "Repository, service par depend kar rahi hai",
}
# jo modules ERP mein hone chahiye (agar kisi layer mein naam nahi mila to 'missing' dikhega)
EXPECTED_MODULES = [
    "account", "voucher", "journal", "user", "permission", "auth", "employee", "dashboard",
    "report", "audit", "company", "fiscal", "party", "bank", "budget", "payroll", "salary",
    "attendance", "leave", "inventory", "item", "stock", "backup", "settings",
]
SQL_KEYWORDS_IGNORE = {"select", "set", "values", "dual", "only", "lateral", "unnest", "generate_series",
                       "information_schema", "pg_catalog", "if", "not", "exists", "the", "a", "as"}
STUB_PATTERNS = re.compile(r"\b(TODO|FIXME|XXX|HACK|NotImplemented(?:Error)?)\b")
SECRET_PATTERN = re.compile(r"""(?i)\b(password|passwd|secret|api[_-]?key|token)\b\s*[:=]\s*['"][^'"\s]{4,}['"]""")
STDLIB = set(getattr(sys, "stdlib_module_names", set())) | {"__future__"}


# ----------------------------------------------------------------------------- helpers
def norm(p):
    return p.replace("\\", "/")


def read_text(path):
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            return f.read()
    except Exception:
        return ""


def layer_of(rel):
    r = "/" + norm(rel).lower()
    for name, pats in LAYER_RULES:
        if any(p in r for p in pats):
            return name
    if r.count("/") == 1:
        return "root"
    return "other"


def walk_project(root, include_archive):
    skip = set(EXCLUDE_DIRS) | (set() if include_archive else ARCHIVE_DIRS)
    files = []
    for dp, dn, fn in os.walk(root):
        dn[:] = sorted(d for d in dn if d.lower() not in skip)
        for f in sorted(fn):
            full = os.path.join(dp, f)
            files.append(os.path.relpath(full, root))
    return files


def module_names(rel):
    """dotted names jin se is .py file ko import kiya ja sakta hai."""
    p = norm(rel)[:-3]
    parts = p.split("/")
    if parts[-1] == "__init__":
        parts = parts[:-1]
    if not parts:
        return []
    names = [".".join(parts)]
    if parts[0] == "src" and len(parts) > 1:
        names.append(".".join(parts[1:]))
    return names


# ----------------------------------------------------------------------------- python analysis
def is_stub_body(body):
    stmts = list(body)
    if stmts and isinstance(stmts[0], ast.Expr) and isinstance(getattr(stmts[0], "value", None), ast.Constant) \
            and isinstance(stmts[0].value.value, str):
        stmts = stmts[1:]
    if not stmts:
        return True
    for s in stmts:
        if isinstance(s, ast.Pass):
            continue
        if isinstance(s, ast.Expr) and isinstance(s.value, ast.Constant) and s.value.value is Ellipsis:
            continue
        if isinstance(s, ast.Raise):
            exc = s.exc
            name = ""
            if isinstance(exc, ast.Call) and isinstance(exc.func, ast.Name):
                name = exc.func.id
            elif isinstance(exc, ast.Name):
                name = exc.id
            if name == "NotImplementedError":
                continue
        return False
    return True


def call_name(node):
    f = node.func
    if isinstance(f, ast.Name):
        return f.id
    if isinstance(f, ast.Attribute):
        return f.attr
    return ""


def analyse_py(rel, text):
    info = {
        "loc": text.count("\n") + (1 if text and not text.endswith("\n") else 0),
        "blank_or_comment": 0, "syntax_error": None, "classes": [], "functions": [],
        "stubs": [], "imports": [], "todos": [], "bare_except": 0, "secrets": 0,
        "sql_strings": [], "forms": [], "docstring_only": False,
    }
    lines = text.splitlines()
    info["blank_or_comment"] = sum(1 for l in lines if not l.strip() or l.strip().startswith("#"))
    for i, l in enumerate(lines, 1):
        if STUB_PATTERNS.search(l):
            info["todos"].append((i, l.strip()[:120]))
        if SECRET_PATTERN.search(l):
            info["secrets"] += 1
    try:
        tree = ast.parse(text)
    except SyntaxError as e:
        info["syntax_error"] = f"line {e.lineno}: {e.msg}"
        return info
    except Exception as e:  # noqa
        info["syntax_error"] = str(e)
        return info

    body = tree.body
    meaningful = [n for n in body if not (isinstance(n, ast.Expr) and isinstance(getattr(n, "value", None), ast.Constant))]
    info["docstring_only"] = (len(meaningful) == 0)

    is_pkg = norm(rel).endswith("__init__.py")
    pkg_parts = norm(rel)[:-3].split("/")
    pkg_parts = pkg_parts[:-1]  # current package (directory)
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                info["imports"].append({"module": a.name, "names": [], "level": 0, "line": node.lineno})
        elif isinstance(node, ast.ImportFrom):
            info["imports"].append({"module": node.module or "", "names": [a.name for a in node.names],
                                    "level": node.level, "line": node.lineno})
        elif isinstance(node, ast.ExceptHandler) and node.type is None:
            info["bare_except"] += 1
        elif isinstance(node, ast.Constant) and isinstance(node.value, str) and len(node.value) > 12:
            if re.search(r"\b(select|insert\s+into|update|delete\s+from|create\s+table)\b", node.value, re.I):
                info["sql_strings"].append(node.value)

    info["_pkg_parts"] = pkg_parts
    info["_is_pkg"] = is_pkg

    for node in body:
        if isinstance(node, ast.ClassDef):
            bases = []
            for b in node.bases:
                if isinstance(b, ast.Name):
                    bases.append(b.id)
                elif isinstance(b, ast.Attribute):
                    bases.append(b.attr)
            methods = [n for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
            stub_methods = [m.name for m in methods if is_stub_body(m.body)]
            info["classes"].append({"name": node.name, "bases": bases, "methods": [m.name for m in methods],
                                    "stub_methods": stub_methods, "line": node.lineno})
            for m in methods:
                if m.name in stub_methods:
                    info["stubs"].append(f"{node.name}.{m.name} (line {m.lineno})")
            if set(bases) & QT_FORM_BASES:
                widgets = defaultdict(int)
                connects = 0
                connected_buttons_text = []
                for n in ast.walk(node):
                    if isinstance(n, ast.Call):
                        cn = call_name(n)
                        if cn in INPUT_WIDGETS:
                            widgets["inputs"] += 1
                        elif cn in BUTTON_WIDGETS:
                            widgets["buttons"] += 1
                            if n.args and isinstance(n.args[0], ast.Constant) and isinstance(n.args[0].value, str):
                                connected_buttons_text.append(n.args[0].value)
                        elif cn in TABLE_WIDGETS:
                            widgets["tables"] += 1
                        elif cn == "connect":
                            connects += 1
                info["forms"].append({"class": node.name, "bases": bases, "inputs": widgets["inputs"],
                                      "buttons": widgets["buttons"], "tables": widgets["tables"],
                                      "connects": connects, "button_texts": connected_buttons_text[:12],
                                      "methods": len(methods), "stub_methods": stub_methods})
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            st = is_stub_body(node.body)
            info["functions"].append({"name": node.name, "line": node.lineno, "stub": st})
            if st:
                info["stubs"].append(f"{node.name} (line {node.lineno})")
    return info


# ----------------------------------------------------------------------------- sql analysis
def strip_sql_comments(sql):
    sql = re.sub(r"/\*.*?\*/", " ", sql, flags=re.S)
    return re.sub(r"--[^\n]*", " ", sql)


def analyse_sql(text):
    clean = strip_sql_comments(text)
    tables = re.findall(r"create\s+table\s+(?:if\s+not\s+exists\s+)?([\w\.\"]+)", clean, re.I)
    alters = re.findall(r"alter\s+table\s+(?:only\s+)?(?:if\s+exists\s+)?([\w\.\"]+)", clean, re.I)
    indexes = re.findall(r"create\s+(?:unique\s+)?index\s+(?:if\s+not\s+exists\s+)?([\w\.\"]+)", clean, re.I)
    views = re.findall(r"create\s+(?:or\s+replace\s+)?view\s+([\w\.\"]+)", clean, re.I)
    inserts = re.findall(r"insert\s+into\s+([\w\.\"]+)", clean, re.I)
    drops = re.findall(r"drop\s+table\s+(?:if\s+exists\s+)?([\w\.\"]+)", clean, re.I)
    q = lambda xs: sorted({x.strip('"').split(".")[-1].lower() for x in xs})
    return {"create_tables": q(tables), "alter_tables": q(alters), "indexes": q(indexes), "views": q(views),
            "insert_into": q(inserts), "drop_tables": q(drops),
            "loc": text.count("\n") + 1}


def tables_in_sql_strings(strings):
    found = set()
    for s in strings:
        for m in re.finditer(r"\b(?:from|join|into|update|table)\s+([a-zA-Z_][\w\.]*)", s, re.I):
            t = m.group(1).split(".")[-1].lower()
            if t not in SQL_KEYWORDS_IGNORE and not t.startswith("{"):
                found.add(t)
    return found


# ----------------------------------------------------------------------------- main scan
def main():
    ap = argparse.ArgumentParser(description="Full ERP project scanner")
    ap.add_argument("--root", default=os.getcwd(), help="project root folder")
    ap.add_argument("--out", default=None, help="output folder (default: <root>/AUDIT_RECORDS)")
    ap.add_argument("--include-archive", action="store_true", help="archive/ folder bhi scan karo")
    ap.add_argument("--no-git", action="store_true", help="git info skip karo")
    args = ap.parse_args()

    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

    root = os.path.abspath(args.root)
    out_dir = args.out or os.path.join(root, "AUDIT_RECORDS")
    os.makedirs(out_dir, exist_ok=True)
    ts = dt.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    md_path = os.path.join(out_dir, f"FULL_SCAN_{ts}.md")
    json_path = os.path.join(out_dir, f"FULL_SCAN_{ts}.json")

    print(f"[1/7] Files collect ho rahi hain: {root}")
    all_files = walk_project(root, args.include_archive)
    py_files = [f for f in all_files if f.lower().endswith(".py")]
    sql_files = [f for f in all_files if f.lower().endswith(".sql")]

    print(f"[2/7] {len(py_files)} Python files analyse ho rahi hain")
    py = {}
    for rel in py_files:
        py[norm(rel)] = analyse_py(rel, read_text(os.path.join(root, rel)))
        py[norm(rel)]["layer"] = layer_of(rel)

    # module name -> path map
    name_map = {}
    for rel in py:
        for n in module_names(rel):
            name_map.setdefault(n, rel)

    def resolve(importer, imp):
        """internal paths jin se importer connect hai."""
        info = py[importer]
        res, unresolved = set(), None
        level, mod, names = imp["level"], imp["module"], imp["names"]
        if level:
            base = list(info.get("_pkg_parts", []))
            if level > 1:
                base = base[: len(base) - (level - 1)]
            full = ".".join(base + ([mod] if mod else []))
            candidates = [full]
            for n in names:
                candidates.append(f"{full}.{n}" if full else n)
        else:
            candidates = [mod]
            for n in names:
                candidates.append(f"{mod}.{n}")
        for c in candidates:
            if c in name_map:
                res.add(name_map[c])
        if not res and not level:
            top = mod.split(".")[0]
            if top in {p.split("/")[0] for p in py} or top in {n.split(".")[0] for n in name_map if "." in n}:
                # internal jaisa lagta hai magar resolve nahi hua
                if top not in STDLIB and any(n.startswith(top + ".") or n == top for n in name_map):
                    unresolved = mod
        elif not res and level:
            unresolved = "." * level + mod
        res.discard(importer)
        return res, unresolved

    graph = defaultdict(set)
    rgraph = defaultdict(set)
    unresolved_all = []
    external = defaultdict(set)  # top-level pkg -> files
    for rel, info in py.items():
        if info["syntax_error"]:
            continue
        for imp in info["imports"]:
            res, unres = resolve(rel, imp)
            for r in res:
                graph[rel].add(r)
                rgraph[r].add(rel)
            if unres:
                unresolved_all.append((rel, imp["line"], unres))
            if not res and not imp["level"]:
                top = imp["module"].split(".")[0]
                if top and top not in STDLIB and not unres:
                    external[top].add(rel)

    # tarjan SCC for circular imports
    sys.setrecursionlimit(10000)
    index, low, onstack, stack, sccs, idx = {}, {}, set(), [], [], [0]

    def strong(v):
        index[v] = low[v] = idx[0]
        idx[0] += 1
        stack.append(v)
        onstack.add(v)
        for w in graph.get(v, ()):
            if w not in index:
                strong(w)
                low[v] = min(low[v], low[w])
            elif w in onstack:
                low[v] = min(low[v], index[w])
        if low[v] == index[v]:
            comp = []
            while True:
                w = stack.pop()
                onstack.discard(w)
                comp.append(w)
                if w == v:
                    break
            if len(comp) > 1:
                sccs.append(sorted(comp))

    for v in list(py):
        if v not in index:
            strong(v)

    print("[3/7] SQL/migrations analyse ho rahe hain")
    sql = {norm(f): analyse_sql(read_text(os.path.join(root, f))) for f in sql_files}
    migration_files = {f: d for f, d in sql.items() if "/migrations/" in "/" + f.lower()}
    defined_tables = set()
    for d in migration_files.values():
        defined_tables.update(d["create_tables"])
    sql_outside = [f for f in sql if f not in migration_files]
    outside_tables = set()
    for f in sql_outside:
        outside_tables.update(sql[f]["create_tables"])

    mig_numbers = defaultdict(list)
    for f in migration_files:
        m = re.match(r"(\d{3,4})_", os.path.basename(f))
        if m:
            mig_numbers[int(m.group(1))].append(f)
    gaps, dups = [], []
    if mig_numbers:
        for n in range(min(mig_numbers), max(mig_numbers) + 1):
            if n not in mig_numbers:
                gaps.append(n)
        dups = [(n, fs) for n, fs in mig_numbers.items() if len(fs) > 1]

    code_tables = defaultdict(set)  # table -> files
    file_tables = {}
    for rel, info in py.items():
        ts_ = tables_in_sql_strings(info["sql_strings"])
        file_tables[rel] = ts_
        for t in ts_:
            code_tables[t].add(rel)
    known_tables = defined_tables | outside_tables
    used_not_defined = {t: sorted(fs) for t, fs in code_tables.items()
                        if t not in known_tables and len(t) > 2}
    defined_not_used = sorted(t for t in defined_tables if t not in code_tables)

    print("[4/7] Layer connections aur problems nikaale ja rahe hain")
    layer_matrix = defaultdict(int)
    violations = []
    for a, targets in graph.items():
        la = py[a]["layer"]
        for b in targets:
            lb = py[b]["layer"]
            layer_matrix[(la, lb)] += 1
            if (la, lb) in FORBIDDEN and la != "tests":
                violations.append((a, b, FORBIDDEN[(la, lb)]))

    entry_names = {"main.py", "run.py", "manage.py", "bootstrap.py", "__main__.py", "setup.py", "conftest.py"}
    orphans = []
    for rel, info in py.items():
        base = os.path.basename(rel)
        if base == "__init__.py" or base in entry_names or info["layer"] in ("tests", "tools", "config", "build", "docs"):
            continue
        if not rgraph.get(rel):
            orphans.append(rel)

    suspicious_names = [f for f in all_files if re.search(r"(\.bak$|\.backup$|_backup|_old\b|_copy|\(\d+\)|\.orig$|~$|\.tmp$)",
                                                         f, re.I)]
    # empty / stub files
    empty_files, stub_heavy = [], []
    for rel, info in py.items():
        if os.path.basename(rel) == "__init__.py":
            continue
        code_lines = info["loc"] - info["blank_or_comment"]
        if code_lines <= 2 or info["docstring_only"]:
            empty_files.append(rel)
        total_fn = len(info["functions"]) + sum(len(c["methods"]) for c in info["classes"])
        if total_fn and len(info["stubs"]) / total_fn >= 0.4:
            stub_heavy.append((rel, len(info["stubs"]), total_fn))
    empty_pkgs = []
    dirs = defaultdict(list)
    for f in py:
        dirs[os.path.dirname(f)].append(os.path.basename(f))
    for d, fs in dirs.items():
        if fs and all(x == "__init__.py" for x in fs) and layer_of(d + "/x") not in ("tests",):
            sub = any(k.startswith(d + "/") and k != d for k in dirs)
            if not sub:
                empty_pkgs.append(d)

    # tests map
    tested = defaultdict(set)
    for rel in py:
        if py[rel]["layer"] == "tests":
            for t in graph.get(rel, ()):
                tested[t].add(rel)
    untested = sorted(r for r, i in py.items()
                      if i["layer"] in ("service", "repository", "domain", "ui", "application", "infrastructure")
                      and os.path.basename(r) != "__init__.py" and r not in tested)

    # module completeness
    def stem(rel):
        b = os.path.basename(rel)[:-3] if rel.endswith(".py") else os.path.basename(rel)
        for suf in ("_service", "_repository", "_repo", "_view", "_dialog", "_window", "_form", "_widget", "_page"):
            if b.endswith(suf):
                b = b[: -len(suf)]
        b = re.sub(r"^\d{3,4}_", "", b)
        return b.lower()

    def singular(w):
        return w[:-1] if w.endswith("s") and not w.endswith("ss") else w

    layers_for_matrix = ["domain", "service", "repository", "ui", "tests"]
    matrix = defaultdict(lambda: defaultdict(list))
    for rel, info in py.items():
        if os.path.basename(rel) == "__init__.py":
            continue
        lay = info["layer"]
        if lay in layers_for_matrix:
            matrix[singular(stem(rel))][lay].append(rel)
        elif lay == "infrastructure" and "/migrations/" in rel:
            pass
    for f in migration_files:
        matrix[singular(stem(f))]["migration"].append(f)
    # domain ke andar alag folder (hr/, payroll/ ...) bhi module maane jaayein
    for rel, info in py.items():
        if info["layer"] == "domain":
            parts = norm(rel).split("/")
            if "domain" in parts:
                i = parts.index("domain")
                if i + 1 < len(parts) - 1:
                    matrix[singular(parts[i + 1])]["domain_pkg"].append(rel)
    for m in EXPECTED_MODULES:
        matrix[singular(m)]  # touch

    # forms
    forms = []
    for rel, info in py.items():
        for f in info["forms"]:
            forms.append((rel, f))

    # requirements
    req_names = set()
    for rq in ("requirements.txt", "requirements.lock.txt", "pyproject.toml"):
        p = os.path.join(root, rq)
        if os.path.exists(p):
            for line in read_text(p).splitlines():
                m = re.match(r"\s*([A-Za-z0-9_.\-]+)\s*(?:[=<>!~\[]|$)", line)
                if m and not line.strip().startswith("#"):
                    req_names.add(m.group(1).lower().replace("-", "_"))
    alias = {"pyside6": "pyside6", "dotenv": "python_dotenv", "psycopg": "psycopg", "argon2": "argon2_cffi",
             "yaml": "pyyaml", "PIL": "pillow", "win32com": "pywin32", "win32api": "pywin32"}
    internal_tops = {n.split(".")[0] for n in name_map}
    missing_req = {}
    for top, files in external.items():
        if top in internal_tops or top in {"app", "src", "tools", "config", "tests"}:
            continue
        key = alias.get(top, top).lower().replace("-", "_")
        if key not in req_names and top.lower() not in req_names:
            missing_req[top] = sorted(files)

    # git
    git_info = ""
    if not args.no_git and os.path.isdir(os.path.join(root, ".git")):
        def g(cmd):
            try:
                return subprocess.run(["git"] + cmd, cwd=root, capture_output=True, text=True, timeout=30).stdout.strip()
            except Exception as e:  # noqa
                return f"(git error: {e})"
        git_info = "\n".join([
            "Branch: " + g(["rev-parse", "--abbrev-ref", "HEAD"]),
            "\nStatus (short):\n" + (g(["status", "--short"]) or "(clean)"),
            "\nLast 15 commits:\n" + g(["log", "--oneline", "-15"]),
            "\nBranches:\n" + g(["branch", "-a"]),
        ])

    print("[5/7] Report likhi ja rahi hai")
    L = []
    w = L.append
    tot_loc = sum(i["loc"] for i in py.values())
    w(f"# FULL PROJECT SCAN REPORT\n")
    w(f"- Root: `{root}`\n- Generated: {dt.datetime.now():%Y-%m-%d %H:%M:%S}\n"
      f"- Archive scanned: {'haan' if args.include_archive else 'nahi (--include-archive se on karein)'}\n")

    w("## 1. Summary\n")
    by_layer = defaultdict(lambda: [0, 0])
    for r, i in py.items():
        by_layer[i["layer"]][0] += 1
        by_layer[i["layer"]][1] += i["loc"]
    w("| Layer | Python files | LOC |\n|---|---:|---:|")
    for k, (n, l) in sorted(by_layer.items()):
        w(f"| {k} | {n} | {l} |")
    w(f"| **Total** | **{len(py)}** | **{tot_loc}** |\n")
    w(f"- SQL files: {len(sql)} (migrations: {len(migration_files)})")
    w(f"- Total classes: {sum(len(i['classes']) for i in py.values())}, "
      f"top-level functions: {sum(len(i['functions']) for i in py.values())}")
    w(f"- Forms/UI classes: {len(forms)}")
    w(f"- Syntax errors: {sum(1 for i in py.values() if i['syntax_error'])}")
    w(f"- Stub functions/methods: {sum(len(i['stubs']) for i in py.values())}")
    w(f"- TODO/FIXME/NotImplemented hits: {sum(len(i['todos']) for i in py.values())}")
    w(f"- Unresolved internal imports: {len(unresolved_all)}")
    w(f"- Circular import groups: {len(sccs)}")
    w(f"- Layer violations: {len(violations)}")
    w(f"- Orphan files (koi import nahi karta): {len(orphans)}")
    w(f"- Empty/placeholder files: {len(empty_files)}, empty packages: {len(empty_pkgs)}")
    w(f"- Backup/duplicate-jaisi files: {len(suspicious_names)}\n")

    w("## 2. Module completeness matrix\n")
    w("`Y` = file mili, `-` = nahi mili. Naam ke hisaab se match hota hai, isliye nateeja andaza hai.\n")
    w("| Module | Domain | Service | Repository | UI | Test | Migration | Verdict |\n|---|:-:|:-:|:-:|:-:|:-:|:-:|---|")
    expected_s = {singular(m) for m in EXPECTED_MODULES}
    rows = []
    for mod, d in matrix.items():
        flags = [bool(d.get("domain") or d.get("domain_pkg")), bool(d.get("service")), bool(d.get("repository")),
                 bool(d.get("ui")), bool(d.get("tests")), bool(d.get("migration"))]
        if not any(flags) and mod not in expected_s:
            continue
        score = sum(flags[:4])
        if score == 0:
            verdict = "BANA HI NAHI"
        elif score == 4:
            verdict = "Complete (4 layer)" + ("" if flags[4] else ", test baqi")
        else:
            miss = [n for n, f in zip(["domain", "service", "repo", "UI"], flags[:4]) if not f]
            verdict = "Adhura: " + ", ".join(miss) + " baqi"
        rows.append((score, mod, flags, verdict))
    for score, mod, flags, verdict in sorted(rows, key=lambda x: (-x[0], x[1])):
        c = ["Y" if f else "-" for f in flags]
        w(f"| {mod} | {c[0]} | {c[1]} | {c[2]} | {c[3]} | {c[4]} | {c[5]} | {verdict} |")
    w("")

    w("## 3. Project tree (filtered, LOC ke saath)\n")
    w("```")
    tree = defaultdict(list)
    for f in sorted(all_files, key=lambda s: norm(s).lower()):
        tree[os.path.dirname(f)].append(os.path.basename(f))
    for d in sorted(tree, key=lambda s: norm(s).lower()):
        depth = 0 if d == "" else norm(d).count("/") + 1
        if d:
            w("  " * (depth - 1) + os.path.basename(d) + "/")
        for fn in tree[d]:
            rel = os.path.join(d, fn)
            n = norm(rel)
            extra = ""
            if n in py:
                extra = f"  [{py[n]['loc']} LOC]" + ("  <-- SYNTAX ERROR" if py[n]["syntax_error"] else "")
            elif n in sql:
                extra = f"  [{sql[n]['loc']} lines, tables: {len(sql[n]['create_tables'])}]"
            w("  " * depth + fn + extra)
    w("```\n")

    w("## 4. Har Python file ka detail aur connections\n")
    for rel in sorted(py, key=str.lower):
        i = py[rel]
        w(f"### `{rel}`")
        w(f"- Layer: **{i['layer']}** | LOC: {i['loc']}" + (f" | **SYNTAX ERROR: {i['syntax_error']}**" if i["syntax_error"] else ""))
        if i["classes"]:
            w("- Classes: " + "; ".join(f"`{c['name']}`({', '.join(c['bases'])}) [{len(c['methods'])} methods]" for c in i["classes"]))
        if i["functions"]:
            w("- Functions: " + ", ".join(f"`{f['name']}`" for f in i["functions"][:25]) + (" ..." if len(i["functions"]) > 25 else ""))
        if i["stubs"]:
            w("- STUBS (khali/NotImplemented): " + ", ".join(i["stubs"][:15]))
        if i["todos"]:
            w("- TODO/FIXME: " + " | ".join(f"L{n}: {t}" for n, t in i["todos"][:5]))
        outs = sorted(graph.get(rel, ()))
        ins = sorted(rgraph.get(rel, ()))
        w("- Imports (internal): " + (", ".join(f"`{o}`" for o in outs) if outs else "none"))
        w("- Imported by: " + (", ".join(f"`{o}`" for o in ins) if ins else "**koi nahi**"))
        ext = sorted({im["module"].split(".")[0] for im in i["imports"] if not im["level"]
                      and im["module"].split(".")[0] not in STDLIB and im["module"].split(".")[0] not in internal_tops})
        if ext:
            w("- External libs: " + ", ".join(ext))
        if file_tables.get(rel):
            w("- DB tables in SQL strings: " + ", ".join(sorted(file_tables[rel])))
        w("")

    w("## 5. Forms / dialogs / windows (UI)\n")
    w("| File | Class | Inputs | Buttons | Tables | .connect() | Warning |\n|---|---|--:|--:|--:|--:|---|")
    for rel, f in sorted(forms, key=lambda x: (x[0].lower(), x[1]["class"].lower())):
        warn = []
        if f["buttons"] > f["connects"]:
            warn.append("buttons ke mukable connect kam hain")
        if f["stub_methods"]:
            warn.append("stub methods: " + ", ".join(f["stub_methods"][:3]))
        if f["inputs"] == 0 and f["tables"] == 0 and f["buttons"] == 0:
            warn.append("koi widget nahi mila")
        w(f"| `{rel}` | {f['class']} | {f['inputs']} | {f['buttons']} | {f['tables']} | {f['connects']} | {'; '.join(warn)} |")
    w("")

    w("## 6. Connections\n")
    w("### 6a. Layer-to-layer imports\n")
    layers = sorted({k for pair in layer_matrix for k in pair})
    w("| From \\ To | " + " | ".join(layers) + " |\n|---|" + "---:|" * len(layers))
    for a in layers:
        w(f"| **{a}** | " + " | ".join(str(layer_matrix.get((a, b), 0) or "") for b in layers) + " |")
    w("")
    w("### 6b. UI -> Service -> Repository -> DB table chains\n")
    for rel in sorted(py):
        if py[rel]["layer"] != "ui":
            continue
        svcs = [t for t in graph.get(rel, ()) if py[t]["layer"] in ("service", "application")]
        direct_repos = [t for t in graph.get(rel, ()) if py[t]["layer"] == "repository"]
        if not svcs and not direct_repos:
            continue
        w(f"- **{rel}**")
        for s in sorted(svcs):
            repos = sorted(t for t in graph.get(s, ()) if py[t]["layer"] == "repository")
            doms = sorted(t for t in graph.get(s, ()) if py[t]["layer"] == "domain")
            w(f"  - service `{s}`")
            if doms:
                w("    - domain: " + ", ".join(f"`{d}`" for d in doms))
            for r in repos:
                w(f"    - repo `{r}` -> tables: {', '.join(sorted(file_tables.get(r, []))) or 'detect nahi hue'}")
        for r in sorted(direct_repos):
            w(f"  - DIRECT repo `{r}` (violation)")
    w("")

    w("## 7. Problems\n")
    def section(title, items, fmt):
        w(f"### {title} ({len(items)})")
        if not items:
            w("- koi nahi\n")
            return
        for it in items:
            w("- " + fmt(it))
        w("")

    section("7.1 Syntax errors", [(r, i["syntax_error"]) for r, i in py.items() if i["syntax_error"]],
            lambda x: f"`{x[0]}`: {x[1]}")
    section("7.2 Empty packages (sirf __init__.py, koi kaam nahi)", sorted(empty_pkgs), lambda x: f"`{x}/`")
    section("7.3 Empty / placeholder files", sorted(empty_files), lambda x: f"`{x}`")
    section("7.4 Stub-heavy files (40%+ functions khali)", stub_heavy, lambda x: f"`{x[0]}`: {x[1]}/{x[2]} stubs")
    section("7.5 TODO / FIXME / NotImplemented",
            [(r, n, t) for r, i in py.items() for n, t in i["todos"]], lambda x: f"`{x[0]}` L{x[1]}: {x[2]}")
    section("7.6 Unresolved internal imports (file maujood nahi / galat path)", unresolved_all,
            lambda x: f"`{x[0]}` L{x[1]}: `{x[2]}`")
    section("7.7 Circular imports", sccs, lambda x: " <-> ".join(f"`{p}`" for p in x))
    section("7.8 Layer violations", violations, lambda x: f"`{x[0]}` -> `{x[1]}`: {x[2]}")
    section("7.9 Orphan files (koi import nahi karta)", sorted(orphans), lambda x: f"`{x}`")
    section("7.10 Backup/duplicate-jaisi files", sorted(suspicious_names), lambda x: f"`{x}`")
    section("7.11 Bare `except:`", [(r, i["bare_except"]) for r, i in py.items() if i["bare_except"]],
            lambda x: f"`{x[0]}`: {x[1]}")
    section("7.12 Hardcoded password/secret jaisi lines (value report mein nahi)",
            [(r, i["secrets"]) for r, i in py.items() if i["secrets"]], lambda x: f"`{x[0]}`: {x[1]} line(s)")
    env_files = [f for f in all_files if os.path.basename(f).lower().startswith(".env")]
    w(f"### 7.13 .env files\n- Mili: {', '.join(env_files) or 'koi nahi'} (content scan nahi kiya)\n")
    gi = read_text(os.path.join(root, ".gitignore"))
    w("- `.env` .gitignore mein: " + ("haan" if re.search(r"^\.env\s*$", gi, re.M) else "**NAHI - secret leak ka khatra**"))
    w("- `.venv` .gitignore mein: " + ("haan" if re.search(r"\.venv", gi) else "**NAHI**"))
    w("")

    w("## 8. Database\n")
    w("### 8a. Migrations\n")
    w("| File | Create tables | Alter tables | Inserts |\n|---|---|---|---|")
    for f in sorted(migration_files):
        d = migration_files[f]
        w(f"| `{f}` | {', '.join(d['create_tables'])} | {', '.join(d['alter_tables'])} | {', '.join(d['insert_into'])} |")
    w(f"\n- Numbering gaps: {gaps or 'koi nahi'}")
    w(f"- Duplicate numbers: {dups or 'koi nahi'}")
    w(f"- Migration folders ek se zyada: " + ", ".join(sorted({os.path.dirname(f) for f in migration_files})))
    w("\n### 8b. SQL files jo migrations folder ke bahar hain (apply nahi hoti)\n")
    for f in sql_outside:
        w(f"- `{f}`: tables = {', '.join(sql[f]['create_tables']) or '-'}")
    if not sql_outside:
        w("- koi nahi")
    w("\n### 8c. Code mein use hue magar kisi migration mein define nahi\n")
    if used_not_defined:
        for t, fs in sorted(used_not_defined.items()):
            w(f"- `{t}` <- " + ", ".join(f"`{x}`" for x in fs))
    else:
        w("- koi nahi")
    w("\n### 8d. Migration mein bane magar code mein kahin use nahi\n")
    w("- " + (", ".join(defined_not_used) if defined_not_used else "koi nahi"))
    w("")

    w("## 9. Dependencies\n")
    w("| External package | Used in files |\n|---|--:|")
    for t, fs in sorted(external.items()):
        if t in internal_tops:
            continue
        w(f"| {t} | {len(fs)} |")
    w("\n- requirements mein nahi mile magar code mein use hue: " + (", ".join(sorted(missing_req)) or "koi nahi"))
    w("")

    w("## 10. Test coverage map\n")
    w(f"- Test files: {sum(1 for i in py.values() if i['layer'] == 'tests')}")
    w(f"- Source files jin ko koi test import nahi karta: {len(untested)}\n")
    for u in untested:
        w(f"- `{u}`")
    w("")

    w("## 11. Non-Python files\n")
    others = [f for f in all_files if not f.lower().endswith((".py", ".pyc"))]
    for f in sorted(others, key=str.lower):
        try:
            sz = os.path.getsize(os.path.join(root, f))
        except OSError:
            sz = 0
        w(f"- `{norm(f)}` ({sz} bytes)")
    w("")

    if git_info:
        w("## 12. Git\n```\n" + git_info + "\n```\n")

    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(L))

    print("[6/7] JSON graph likha ja raha hai")
    data = {
        "root": root, "generated": ts,
        "files": {r: {k: v for k, v in i.items() if not k.startswith("_") and k not in ("sql_strings",)} for r, i in py.items()},
        "graph": {k: sorted(v) for k, v in graph.items()},
        "reverse_graph": {k: sorted(v) for k, v in rgraph.items()},
        "sql": sql, "unresolved_imports": unresolved_all, "circular": sccs,
        "layer_violations": violations, "orphans": orphans, "untested": untested,
        "tables_used_not_defined": used_not_defined, "tables_defined_not_used": defined_not_used,
    }
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False, default=list)

    print("[7/7] Complete")
    print(f"\nReport : {md_path}\nJSON   : {json_path}")
    print(f"Python files: {len(py)} | LOC: {tot_loc} | syntax errors: {sum(1 for i in py.values() if i['syntax_error'])} "
          f"| unresolved imports: {len(unresolved_all)} | circular: {len(sccs)} | orphans: {len(orphans)}")


if __name__ == "__main__":
    main()