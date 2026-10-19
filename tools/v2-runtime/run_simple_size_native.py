"""New loopback-only native size fixture; retained evidence is never reused as a database.

Authentication is not applicable to this synthetic local site. No real gateway,
installed configuration, credentials, external HTTP, conversion or deployment.
"""

from __future__ import annotations

import ctypes
from contextlib import contextmanager
from datetime import datetime
import argparse
import hashlib
import html
import http.cookiejar
import json
import os
import re
import signal
from pathlib import Path
import socket
import stat
import subprocess
import time
import urllib.error
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parents[2]
ORIGINAL = Path("/Users/theceo/.codex/worktrees/release-gates-20261019/DevSkyy")
BASE = (
    ORIGINAL / ".artifacts/release-gates-20261019/gate4-populated/run-1792441452292547000/wordpress"
)
THEME = ROOT / "wordpress-theme/skyyrose-flagship-2"
PHP = "/opt/homebrew/Cellar/php/8.5.6/bin/php"
WP = str(Path("/opt/homebrew/bin/wp").resolve())
MYSQL = str(Path("/opt/homebrew/bin/mariadb").resolve())
INSTALL_DB = str(Path("/opt/homebrew/bin/mariadb-install-db").resolve())
DAEMON = str(Path("/opt/homebrew/opt/mariadb/bin/mariadbd").resolve())
PLUGINS = [
    "woocommerce",
    "stripe-tax-for-woocommerce",
    "woocommerce-paypal-payments",
    "woocommerce-shipping",
    "woocommerce-gateway-stripe",
    "woocommerce-services",
    "woocommerce-payments",
]
FLOOR = 1024**3
RUN = str(time.time_ns())
PRIVATE = ROOT / ".artifacts/release-gates-20261019/simple-size-native" / ("run-" + RUN)
SITE = PRIVATE / "wordpress"
SOCKET = "/private/tmp/sr-size-" + RUN[-12:] + ".sock"
PORT = 18368
URL = "http://127.0.0.1:" + str(PORT)
CLIENT_PROFILE = (
    '(version 1)(allow default)(deny network*)(allow network-outbound (remote unix-socket (literal "'
    + SOCKET
    + '")))'
)
REPORT: dict = {
    "schema": "skyyrose.simple-size-native.v2",
    "status": "INCOMPLETE",
    "authentication": "NOT_APPLICABLE_SYNTHETIC_LOCAL",
    "run": RUN,
    "steps": [],
    "limits": [
        "Fresh synthetic WP7.1.3/Woo11.2.1/seven-plugin HPOS site; not installed-stack parity",
        "PHP8.5.6/MariaDB13 differ from installed PHP8.4.26/MariaDB11.8.9",
        "Native HTTP classic and Store API, fake gateway only; no provider/payment/deployment qualification",
        "CLI privileged controls and native REST serialization are not production authenticated executions",
    ],
}
CHILDREN: list[subprocess.Popen] = []
COMMAND_CHILDREN: list[subprocess.Popen] = []
SEQ = 0
STORAGE = "hpos"
TASK_ENV = {
    "PATH": "/opt/homebrew/bin:/usr/bin:/bin",
    "TMPDIR": str(PRIVATE / "tmp"),
    "WP_CLI_CONFIG_PATH": str(PRIVATE / "cli.yml"),
    "WP_CLI_PACKAGES_DIR": str(PRIVATE / "cli-packages"),
    "GIT_CONFIG_NOSYSTEM": "1",
    "GIT_CONFIG_GLOBAL": "/dev/null",
    "GIT_CONFIG_SYSTEM": "/dev/null",
    "LC_ALL": "C",
}


def guard(path):
    if any(value.is_symlink() for value in (path, *path.parents)):
        raise ValueError("Symlink ancestry refused")


def git(*args):
    return (
        subprocess.check_output(
            [
                "/usr/bin/git",
                "-c",
                "core.hooksPath=/dev/null",
                "-c",
                "core.fsmonitor=false",
                "-c",
                "submodule.recurse=false",
                "-C",
                str(ROOT),
                *args,
            ],
            env=TASK_ENV,
            timeout=15,
        )
        .decode()
        .strip()
    )


def group_exists(pid):
    try:
        os.killpg(pid, 0)
        return True
    except ProcessLookupError:
        return False


def stop_group(child):
    # Only groups created by our own start_new_session Popen calls are supplied.
    if group_exists(child.pid):
        os.killpg(child.pid, signal.SIGTERM)
    try:
        child.wait(timeout=10)
    except subprocess.TimeoutExpired:
        os.killpg(child.pid, signal.SIGKILL)
        child.wait(timeout=5)
    if group_exists(child.pid):
        os.killpg(child.pid, signal.SIGKILL)
        deadline = time.monotonic() + 5
        while group_exists(child.pid) and time.monotonic() < deadline:
            time.sleep(0.05)
    if group_exists(child.pid):
        raise RuntimeError("Owned process group did not stop")


def cleanup_owned():
    receipts = []
    for child in reversed(COMMAND_CHILDREN + CHILDREN):
        try:
            stop_group(child)
            for registry in (COMMAND_CHILDREN, CHILDREN):
                if child in registry:
                    registry.remove(child)
            receipts.append(
                {"pid": child.pid, "terminal": True, "group_absent": True, "exit": child.returncode}
            )
        except BaseException as error:
            receipts.append({"pid": child.pid, "error": type(error).__name__})
    return receipts


def capacity():
    value = os.statvfs(ROOT)
    free = value.f_bavail * value.f_frsize
    if free < FLOOR:
        raise RuntimeError("Shared filesystem below existing 1GiB floor")
    return free


def pin(path):
    guard(path)
    before = path.stat()
    if path.is_symlink() or not stat.S_ISREG(before.st_mode):
        raise ValueError("Regular nonsymlink input required")
    with path.open("rb") as stream:
        digest = hashlib.file_digest(stream, "sha256").hexdigest()
    after = path.stat()
    if (before.st_ino, before.st_size, before.st_mtime_ns) != (
        after.st_ino,
        after.st_size,
        after.st_mtime_ns,
    ):
        raise ValueError("Input changed while hashing")
    return {"sha256": digest, "bytes": before.st_size, "mode": stat.S_IMODE(before.st_mode)}


def write(path, value):
    guard(path)
    with path.open("w") as stream:
        json.dump(value, stream, indent=2)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())
    path.chmod(0o600)


def record(name, **fields):
    REPORT["steps"].append({"step": name, **fields})
    write(PRIVATE / "results.json", REPORT)
    print(name, flush=True)


def command(argv, data=None, timeout=120):
    global SEQ
    capacity()
    SEQ += 1
    sequence = SEQ
    log = PRIVATE / f"command-{sequence:04}.txt"
    guard(log)
    child = subprocess.Popen(
        argv,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=TASK_ENV,
        start_new_session=True,
    )
    COMMAND_CHILDREN.append(child)
    stdout = stderr = b""
    failure = None
    cleanup_error = None
    try:
        stdout, stderr = child.communicate(data, timeout=timeout)
    except BaseException as error:
        failure = type(error).__name__
    finally:
        try:
            stop_group(child)
            # Retire immediately after proved absence: a historical PID is no
            # longer an owned group and must never be signalled by finalization.
            COMMAND_CHILDREN.remove(child)
            if failure:
                stdout, stderr = child.communicate(timeout=5)
        except BaseException as error:
            cleanup_error = type(error).__name__
        log.write_bytes(stdout + stderr)
        log.chmod(0o600)
        write(
            PRIVATE / f"command-{sequence:04}.json",
            {
                "argv": list(map(str, argv)),
                "exit": child.returncode,
                "pid": child.pid,
                "group_retired": child not in COMMAND_CHILDREN,
                "failure": failure,
                "cleanup_error": cleanup_error,
                "output": pin(log),
            },
        )
    if failure or cleanup_error or child.returncode:
        raise RuntimeError(f"Command {sequence} failed; private receipt retained")
    return stdout


def wp(*args):
    return command(
        [
            "/usr/bin/sandbox-exec",
            "-p",
            CLIENT_PROFILE,
            PHP,
            "-d",
            "memory_limit=1024M",
            "-d",
            "error_reporting=24575",
            WP,
            "--path=" + str(SITE),
            *map(str, args),
        ]
    )


def native(*args):
    body = wp("eval-file", ROOT / "tools/v2-runtime/simple-size-native-controls.php", *args)
    marker = b"SS_RESULT="
    if marker not in body:
        raise RuntimeError("Missing native result marker")
    value = json.loads(body.rsplit(marker, 1)[1])
    validate_observed_orders(value)
    return value


def validate_observed_orders(value):
    if isinstance(value, dict):
        if "data_store" in value and "native_data" in value:
            expected = (
                "Automattic\\WooCommerce\\Internal\\DataStores\\Orders\\OrdersTableDataStore"
                if STORAGE == "hpos"
                else "WC_Order_Data_Store_CPT"
            )
            assert value["data_store"] == expected
            for item in value["items"]:
                typed = [
                    row["value"] for row in item["meta_data"] if row["key"] == "_ss_typed_history"
                ]
                assert len(typed) == 1 and canonical(typed[0]) == canonical(
                    {"boolean": True, "fractional": 1.0, "integer": 1}
                )
        for child in value.values():
            validate_observed_orders(child)
    elif isinstance(value, list):
        for child in value:
            validate_observed_orders(child)


def clone_tree(source, target, skip=None):
    guard(source)
    guard(target)
    lib = ctypes.CDLL("/usr/lib/libSystem.B.dylib", use_errno=True)
    lib.clonefile.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int]
    entries = {}
    for parent, dirs, files in os.walk(
        source, followlinks=False, onerror=lambda error: (_ for _ in ()).throw(error)
    ):
        relative = Path(parent).relative_to(source)
        dirs[:] = sorted(name for name in dirs if not skip or not skip(relative / name))
        destination = target / relative
        guard(destination)
        destination.mkdir(parents=True, exist_ok=True, mode=0o700)
        for name in dirs:
            if (Path(parent) / name).is_symlink():
                raise ValueError("Symlink directory input refused")
        for name in sorted(files):
            sub = relative / name
            if skip and skip(sub):
                continue
            src, dst = source / sub, target / sub
            if any(path.is_symlink() for path in [src, *src.parents, dst, *dst.parents]):
                raise ValueError("Symlink ancestry refused")
            expected = pin(src)
            if dst.exists() or lib.clonefile(os.fsencode(src), os.fsencode(dst), 0):
                raise OSError(ctypes.get_errno(), "Exclusive APFS clone failed")
            if (
                src.stat().st_ino == dst.stat().st_ino
                or pin(dst) != expected
                or pin(src) != expected
            ):
                raise ValueError("Clone binding mismatch")
            entries[str(sub)] = expected
            if len(entries) % 2000 == 0:
                capacity()
                print("COW verified", len(entries), flush=True)
    return entries


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class Client:
    def __init__(self):
        self.opener = urllib.request.build_opener(
            urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()),
            urllib.request.ProxyHandler({}),
            NoRedirect(),
        )
        self.token = None
        self.rest_nonce = None

    def request(self, path, payload=None, method=None, api=False):
        capacity()
        if not path.startswith("/") or path.startswith("//"):
            raise ValueError("Own loopback path required")
        headers = {}
        if self.rest_nonce:
            headers["X-WP-Nonce"] = self.rest_nonce
        if api and self.token:
            headers["Cart-Token"] = self.token
        if payload is not None:
            body = json.dumps(payload).encode() if api else urllib.parse.urlencode(payload).encode()
            headers["Content-Type"] = (
                "application/json" if api else "application/x-www-form-urlencoded"
            )
        else:
            body = None
        req = urllib.request.Request(URL + path, body, headers, method=method)
        try:
            response = self.opener.open(req, timeout=30)
        except urllib.error.HTTPError as error:
            response = error
        with response:
            raw = response.read(4 * 1024 * 1024 + 1)
            if len(raw) > 4 * 1024 * 1024:
                raise ValueError("HTTP body cap exceeded")
            if response.headers.get("Cart-Token"):
                self.token = response.headers["Cart-Token"]
            value = {
                "status": response.status,
                "headers": dict(response.headers),
                "body": raw.decode("utf-8", "replace"),
            }
        global SEQ
        SEQ += 1
        write(PRIVATE / f"http-{SEQ:04}.json", value)
        return value

    def control(self, name, **values):
        result = self.request("/?" + urllib.parse.urlencode({"ss_control": name, **values}))
        assert result["status"] == 200, result["status"]
        return json.loads(result["body"])

    def api(self, route, payload=None, method=None):
        result = self.request("/?rest_route=/wc/store/v1/" + route, payload, method, True)
        return result["status"], json.loads(result["body"])


def events():
    p = PRIVATE / "events.jsonl"
    return [json.loads(line) for line in p.read_text().splitlines()] if p.exists() else []


def processor_count():
    return sum(row["event"] == "processor_entered" for row in events())


def own_new_order(before):
    added = [row for row in native("orders") if row["id"] not in before]
    assert len(added) == 1
    return added[0]


def classic_checkout(client):
    nonce = client.control("inspect")["nonce"]
    fields = {
        "billing_first_name": "Synthetic",
        "billing_last_name": "Fixture",
        "billing_country": "US",
        "billing_address_1": "1 Test Way",
        "billing_city": "Oakland",
        "billing_state": "CA",
        "billing_postcode": "94612",
        "billing_email": "fixture@example.invalid",
        "billing_phone": "5105550100",
        "payment_method": "ss_offline",
        "woocommerce-process-checkout-nonce": nonce,
        "terms": "on",
    }
    return client.request("/?wc-ajax=checkout", fields)


def classic_add(client, product, size, quantity=1):
    return client.request(
        "/?add-to-cart=" + str(product),
        {"add-to-cart": product, "quantity": quantity, "skyyrose_simple_size": size},
    )


def setup():
    # Preserve the old qualified fixture and create no cold/historical DB copies.
    assert (
        git("status", "--porcelain", "--ignore-submodules=all") == ""
    ), "Commit source before native execution"
    REPORT["source_commit"] = git("rev-parse", "HEAD")

    def skip(sub):
        parts = sub.parts
        return sub.name == "wp-config.php" or (
            len(parts) > 1
            and parts[0] == "wp-content"
            and (
                parts[1] in {"themes", "mu-plugins", "uploads", "cache"}
                or (parts[1] == "plugins" and len(parts) > 2 and parts[2] not in PLUGINS)
            )
        )

    REPORT["source_census"] = clone_tree(BASE, SITE, skip)
    REPORT["theme_census"] = clone_tree(
        THEME,
        SITE / "wp-content/themes/skyyrose-flagship-2",
        lambda sub: sub.parts[0] in {"dist", "node_modules", "vendor"},
    )
    mu = SITE / "wp-content/mu-plugins"
    guard(mu)
    mu.mkdir(parents=True, exist_ok=True)
    source = ROOT / "tools/v2-runtime/simple-size-native-fixture.php"
    guard(mu / "simple-size-fixture.php")
    (mu / "simple-size-fixture.php").write_bytes(source.read_bytes())
    REPORT["fixture_source"] = pin(source)
    config = (
        "<?php\ndefine('DB_NAME','sr_simple_size_fixture');\ndefine('DB_USER','root');\ndefine('DB_PASSWORD','');\ndefine('DB_HOST',"
        + json.dumps("localhost:" + SOCKET)
        + ");\ndefine('DB_CHARSET','utf8mb4');\n$table_prefix='wp_';\ndefine('SKYYROSE_RELEASE_SYNTHETIC_FIXTURE',true);\ndefine('SR_SIMPLE_SIZE_STORAGE',"
        + json.dumps(STORAGE)
        + ");\ndefine('SR_SIMPLE_SIZE_FIXTURE_ROOT',"
        + json.dumps(str(PRIVATE))
        + ");\ndefine('DISABLE_WP_CRON',true);\ndefine('WP_HTTP_BLOCK_EXTERNAL',true);\ndefine('AUTOMATIC_UPDATER_DISABLED',true);\ndefine('WP_DEBUG',false);\ndefine('WP_HOME',"
        + json.dumps(URL)
        + ");\ndefine('WP_SITEURL',"
        + json.dumps(URL)
        + ");\ndefine('AUTH_KEY','synthetic-no-remote-authority');\ndefine('SECURE_AUTH_KEY','synthetic-no-remote-authority');\ndefine('LOGGED_IN_KEY','synthetic-no-remote-authority');\ndefine('NONCE_KEY','synthetic-no-remote-authority');\nif(!defined('ABSPATH')){define('ABSPATH',__DIR__.'/');}\nrequire_once ABSPATH.'wp-settings.php';\n"
    )
    guard(SITE / "wp-config.php")
    (SITE / "wp-config.php").write_text(config)
    (SITE / "wp-config.php").chmod(0o600)
    datadir = PRIVATE / "mysql"
    guard(datadir)
    datadir.mkdir(mode=0o700)
    command(
        [
            "/usr/bin/sandbox-exec",
            "-p",
            "(version 1)(allow default)(deny network*)",
            INSTALL_DB,
            "--no-defaults",
            "--datadir=" + str(datadir),
            "--auth-root-authentication-method=normal",
            "--skip-test-db",
            "--skip-name-resolve",
        ]
    )
    dbprofile = (
        '(version 1)(allow default)(deny network*)(allow network-bind (local unix-socket (literal "'
        + SOCKET
        + '")))(allow network-inbound (local unix-socket (literal "'
        + SOCKET
        + '")))'
    )
    guard(Path(SOCKET))
    if Path(SOCKET).exists() or (PRIVATE / "db.pid").exists():
        raise RuntimeError("Existing socket/PID collision refused")
    guard(PRIVATE / "db.log")
    with (PRIVATE / "db.log").open("wb") as log:
        db = subprocess.Popen(
            [
                "/usr/bin/sandbox-exec",
                "-p",
                dbprofile,
                DAEMON,
                "--no-defaults",
                "--datadir=" + str(datadir),
                "--socket=" + SOCKET,
                "--pid-file=" + str(PRIVATE / "db.pid"),
                "--skip-networking",
                "--event-scheduler=OFF",
                "--skip-log-bin",
                "--innodb-buffer-pool-size=64M",
            ],
            stdout=log,
            stderr=log,
            env=TASK_ENV,
            start_new_session=True,
        )
    CHILDREN.append(db)
    for _ in range(100):
        if db.poll() is not None:
            raise RuntimeError("Owned DB failed to start")
        if Path(SOCKET).exists() and (PRIVATE / "db.pid").exists():
            break
        time.sleep(0.1)
    identity = (
        command(
            [
                MYSQL,
                "--no-defaults",
                "--socket=" + SOCKET,
                "-uroot",
                "--batch",
                "--skip-column-names",
            ],
            b"SELECT @@datadir,@@socket,@@skip_networking,@@event_scheduler,VERSION();\n",
        )
        .decode()
        .strip()
        .split("\t")
    )
    assert Path(identity[0]).resolve() == datadir.resolve() and identity[1:4] == [
        SOCKET,
        "1",
        "OFF",
    ]
    assert (
        db.poll() is None
        and os.getpgid(db.pid) == db.pid
        and int((PRIVATE / "db.pid").read_text()) == db.pid
    )
    REPORT["database_identity"] = identity
    command(
        [MYSQL, "--no-defaults", "--socket=" + SOCKET, "-uroot"],
        b"CREATE DATABASE sr_simple_size_fixture CHARACTER SET utf8mb4;\n",
    )
    wp(
        "--skip-plugins",
        "--skip-themes",
        "core",
        "install",
        "--url=" + URL,
        "--title=Synthetic size fixture",
        "--admin_user=synthetic",
        "--admin_password=synthetic-local-only",
        "--admin_email=fixture@example.invalid",
    )
    wp("plugin", "activate", *PLUGINS)
    wp("theme", "activate", "skyyrose-flagship-2")
    wp(
        "option",
        "update",
        "woocommerce_custom_orders_table_enabled",
        "yes" if STORAGE == "hpos" else "no",
    )
    wp("option", "update", "woocommerce_custom_orders_table_data_sync_enabled", "no")
    seed = native("init")
    write(PRIVATE / "seed.json", seed)
    assert (
        seed["runtime"]["wp"] == "7.1.3"
        and seed["runtime"]["woo"] == "11.2.1"
        and seed["runtime"]["php"] == "8.5.6"
    )
    assert (
        len(seed["runtime"]["plugins"]) == 7
        and ("OrdersTableDataStore" if STORAGE == "hpos" else "WC_Order_Data_Store_CPT")
        in seed["legacy"]["data_store"]
    )
    profile = (
        CLIENT_PROFILE
        + '(allow network-bind (local ip "localhost:'
        + str(PORT)
        + '"))(allow network-inbound (local ip "localhost:'
        + str(PORT)
        + '"))'
    )
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", PORT))
    guard(PRIVATE / "http-server.log")
    with (PRIVATE / "http-server.log").open("wb") as log:
        server = subprocess.Popen(
            [
                "/usr/bin/sandbox-exec",
                "-p",
                profile,
                PHP,
                "-d",
                "memory_limit=1024M",
                "-d",
                "error_reporting=24575",
                "-S",
                "127.0.0.1:" + str(PORT),
                "-t",
                str(SITE),
            ],
            stdout=log,
            stderr=log,
            env=TASK_ENV,
            start_new_session=True,
        )
    CHILDREN.append(server)
    for _ in range(100):
        if server.poll() is not None:
            raise RuntimeError("Owned HTTP server failed to start")
        try:
            with socket.create_connection(("127.0.0.1", PORT), timeout=0.1):
                break
        except OSError:
            time.sleep(0.1)
    record("FRESH_CONTAINED_NATIVE_FIXTURE", runtime=seed["runtime"], capacity_bytes=capacity())
    return seed


def qualify(seed):
    products = seed["products"]
    client = Client()
    client.control("empty")
    classic_add(client, products["br-001"], "S")
    classic_add(client, products["br-001"], "M")
    classic_add(client, products["br-001"], "S")
    cart = client.control("inspect")["cart"]
    assert len(cart) == 2 and sorted(row["quantity"] for row in cart) == [1, 2]
    assert {row["size"]["size"] for row in cart} == {"S", "M"}
    classic_add(client, products["br-001"], "M", 3)
    assert sum(row["quantity"] for row in client.control("inspect")["cart"]) == 3
    record("CLASSIC_HTTP_SESSION_DISTINCT_SIZES_MERGE_AND_SHARED_PREORDER_POOL")
    for sku, size in [("kids-002", "5"), ("sg-007", "One Size")]:
        client.control("empty")
        classic_add(client, products[sku], size)
        assert client.control("inspect")["cart"][0]["size"]["size"] == size
    record("NUMERIC_STRING_AND_ONE_SIZE_SESSION_ROUNDTRIP")
    client.control("empty")
    classic_add(client, products["br-001"], "S")
    before_ids = {row["id"] for row in native("orders")}
    before = processor_count()
    classic_checkout(client)
    paired = own_new_order(before_ids)
    assert processor_count() == before + 1 and len(paired["generation"]) == 1
    assert sorted(row["meta_key"] for row in paired["raw_size_rows"]) == [
        "Size",
        "_skyyrose_simple_size_v1",
    ]
    assert len(paired["raw_generation_rows"]) == 1
    assert not native("payment-check", paired["id"])["errors"]
    record(
        "PAIRED_NORMAL_CLASSIC_PERSISTED_SELECTION_REACHES_FAKE_PROCESSOR", order_id=paired["id"]
    )
    # Actual native classic post-save negatives: remove persisted INSERTs, not caller data.
    for kind in ["selected", "generation", "both"]:
        native("option", "ss_drop_mode", kind)
        client.control("empty")
        classic_add(client, products["br-001"], "S")
        before_ids = {row["id"] for row in native("orders")}
        before = processor_count()
        event_start = len(events())
        response = classic_checkout(client)
        assert response["status"] == 200 and json.loads(response["body"])["result"] == "failure"
        order = own_new_order(before_ids)
        assert processor_count() == before and not order["paid"]
        dropped = [
            row["data"]["key"]
            for row in events()[event_start:]
            if row["event"] == "dropped_persistence"
        ]
        expected = {
            "selected": ["_skyyrose_simple_size_v1"],
            "generation": ["_skyyrose_simple_size_generation_v1"],
            "both": ["Size", "_skyyrose_simple_size_generation_v1", "_skyyrose_simple_size_v1"],
        }[kind]
        assert sorted(dropped) == sorted(expected)
        assert "saved size" in json.loads(response["body"])["messages"]
        size_keys = [row["meta_key"] for row in order["raw_size_rows"]]
        expected_survivors = {
            "selected": ["Size"],
            "generation": ["Size", "_skyyrose_simple_size_v1"],
            "both": [],
        }[kind]
        assert sorted(size_keys) == expected_survivors
        assert len(order["raw_generation_rows"]) == (1 if kind == "selected" else 0)
        assert len(order["generation"]) == (1 if kind == "selected" else 0)
        native("option", "ss_drop_mode", "")
        assert "skyyrose_simple_size_order" in native("payment-check", order["id"])["errors"]
        before = processor_count()
        pay_order(order["id"])
        assert processor_count() == before
        record(
            "CLASSIC_DROPPED_PERSISTENCE_REFUSED_" + kind.upper(),
            order_id=order["id"],
            exact_dropped_keys=dropped,
            raw_size_keys=size_keys,
            raw_generation_rows=len(order["raw_generation_rows"]),
        )
    api = Client()
    api.control("empty")
    assert api.api("cart")[0] == 200 and api.token
    for invalid in [
        None,
        {"size": 5},
        {"size": ["S"]},
        {"size": "S", "sku": "br-001"},
        {"size": "INVALID"},
    ]:
        payload = {"id": products["br-001"], "quantity": 1}
        if invalid is not None:
            payload["extensions"] = {"skyyrose-simple-size": invalid}
        assert api.api("cart/add-item", payload)[0] == 400
    assert api.api("cart")[1]["items"] == []

    def api_add(product, size):
        payload = {"id": product, "quantity": 1}
        if size is not None:
            payload["extensions"] = {"skyyrose-simple-size": {"size": size}}
        return api.api("cart/add-item", payload)

    assert api_add(products["br-001"], "S")[0] == 201
    assert api_add(products["br-001"], "M")[0] == 201
    assert api_add(products["br-001"], "S")[0] == 201
    items = api.api("cart")[1]["items"]
    assert len(items) == 2 and sorted(item["quantity"] for item in items) == [1, 2]
    record("ACTUAL_STORE_API_INGRESS_HASHING_AND_TYPED_REFUSALS")
    api.control("tamper")
    before = api.api("cart")[1]["items"]
    assert (
        api.api(
            "cart/update-item", {"key": before[0]["key"], "quantity": before[0]["quantity"] + 1}
        )[0]
        == 400
    )
    assert api_add(products["br-001"], "S")[0] == 400
    assert [(x["key"], x["quantity"]) for x in api.api("cart")[1]["items"]] == [
        (x["key"], x["quantity"]) for x in before
    ]
    record("ACTUAL_STORE_API_INVALID_SESSION_UPDATE_AND_TOPUP_NO_QUANTITY_MUTATION")
    REPORT["status"] = "PASS_BOUNDED_INITIAL_NATIVE_MATRIX_REMAINING_CASES_OPEN"
    REPORT["remaining"] = [
        "Store API checkout / GET-PATCH persisted-history mutation cases",
        "Marked-order retry, missing-both/duplicate/conflicting saved metadata with gateway count",
        "Prior allowlisted V1 native payment and preserved variable-only draft editing",
        "Native admin/email/REST size readback and actual order-again reselection",
        "Final successor build/package/preview adoption",
    ]
    return paired


def pay_order(order_id):
    label = "pay-" + str(SEQ + 1)
    event_start = len(events())
    wp(
        "eval-file",
        ROOT / "tools/v2-runtime/simple-size-native-controls.php",
        "pay",
        order_id,
        label,
    )
    path = PRIVATE / (label + ".json")
    result = json.loads(path.read_text())
    validate_observed_orders(result)
    assert result["order"]["id"] == order_id
    assert ("OrdersTableDataStore" if STORAGE == "hpos" else "WC_Order_Data_Store_CPT") in result[
        "order"
    ]["data_store"]
    result["events_from"] = event_start
    return result


def canonical(value):
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False
    )


def immutable_order(order, allow_stock_meta=False):
    value = json.loads(
        json.dumps(
            {
                key: order[key]
                for key in [
                    "id",
                    "items",
                    "generation",
                    "raw_size_rows",
                    "raw_generation_rows",
                    "total",
                    "fixture_order_meta",
                ]
            }
        )
    )
    if allow_stock_meta:
        for item in value["items"]:
            item["meta_data"] = [row for row in item["meta_data"] if row["key"] != "_reduced_stock"]
    return canonical(value)


def payment_history_preserved(before, after, event_start):
    assert immutable_order(before) == immutable_order(after)
    for field in ("stock", "stock_reduced", "paid", "paid_timestamp", "transaction_id"):
        assert canonical(before[field]) == canonical(after[field])
    changed = [
        key
        for key in set(before["native_data"]) | set(after["native_data"])
        if canonical(before["native_data"].get(key)) != canonical(after["native_data"].get(key))
    ]
    assert set(changed) <= {"payment_method", "payment_method_title", "date_modified"}
    if changed:
        observed = events()[event_start:]
        starts = [row["data"] for row in observed if row["event"] == "native_pay_started"]
        finishes = [row["data"] for row in observed if row["event"] == "native_pay_finished"]
        assert len(starts) == len(finishes) == 1
        start, finish = starts[0], finishes[0]
        assert start["id"] == finish["id"] == before["id"]
        assert start["label"] == finish["label"] and start["at"] <= finish["at"]
        saves = [
            row["data"]
            for row in observed
            if row["event"] == "native_pay_order_saved" and row["data"]["id"] == before["id"]
        ]
        assert saves
        assert all(
            save["label"] == start["label"]
            and start["at"] <= save["at"] <= finish["at"]
            and any(
                frame["class"] == "WC_Form_Handler" and frame["function"] == "pay_action"
                for frame in save["stack"]
            )
            and not any(frame["function"].startswith("skyyrose2_") for frame in save["stack"])
            for save in saves
        )
        for field in changed:
            assert canonical(after["native_data"][field]) == canonical(saves[-1]["values"][field])
        if "payment_method" in changed:
            assert after["native_data"]["payment_method"] == "ss_offline"
        if "payment_method_title" in changed:
            assert after["native_data"]["payment_method_title"] == "Synthetic offline"
        if "date_modified" in changed:
            modified = datetime.fromisoformat(after["native_data"]["date_modified"]).timestamp()
            assert start["at"] <= modified <= finish["at"]
    return sorted(changed)


def fresh_classic(seed, sizes=("S",)):
    client = Client()
    client.control("empty")
    for size in sizes:
        classic_add(client, seed["products"]["br-001"], size)
    before_ids = {row["id"] for row in native("orders")}
    before = processor_count()
    classic_checkout(client)
    order = own_new_order(before_ids)
    assert processor_count() == before + 1 and order["generation"] and not order["paid"]
    return client, order


@contextmanager
def changed_projection(kind):
    target = SITE / "wp-content/themes/skyyrose-flagship-2/data/simple-product-sizes.json"
    guard(target)
    before = target.read_bytes()
    expected = pin(target)
    preimage = PRIVATE / ("projection-preimage-" + kind + ".json")
    guard(preimage)
    with preimage.open("xb") as stream:
        stream.write(before)
    try:
        if kind == "missing":
            target.unlink()
        else:
            value = json.loads(before)
            if kind == "stale":
                value["product_registry_sha256"] = "0" * 64
            elif kind == "removed-size":
                value["products"]["br-001"]["sizes"].remove("S")
                value["products_sha256"] = hashlib.sha256(
                    json.dumps(
                        value["products"], separators=(",", ":"), ensure_ascii=False
                    ).encode()
                ).hexdigest()
            else:
                raise ValueError("Unknown projection control")
            target.write_text(json.dumps(value, indent=2) + "\n")
        yield
    finally:
        guard(target)
        target.write_bytes(before)
        target.chmod(expected["mode"])
        assert pin(target) == expected


def qualify_saved_orders(seed, paired):
    # Pre-save classic guards cannot prove these persisted-history paths.
    client, order = fresh_classic(seed)
    before = native("order", order["id"])
    entries = processor_count()
    response = classic_checkout(client)
    assert json.loads(response["body"])["result"] == "failure" and processor_count() == entries
    assert "saved order is unchanged" in json.loads(response["body"])["messages"]
    assert canonical(native("order", order["id"])) == canonical(before)
    ids = {row["id"] for row in native("orders")}
    classic_checkout(client)
    distinct = own_new_order(ids)
    assert distinct["id"] != order["id"] and processor_count() == entries + 1
    assert canonical(native("order", order["id"])) == canonical(before)
    record(
        "CLASSIC_RESUME_REFUSES_BEFORE_DELETE_THEN_CREATES_DISTINCT_ORDER",
        prior_id=order["id"],
        successor_id=distinct["id"],
    )
    for kind in ["both", "duplicate", "conflict", "quantity"]:
        _, order = fresh_classic(seed)
        native("mutate", order["id"], kind)
        before = native("order", order["id"])
        assert "skyyrose_simple_size_order" in native("payment-check", order["id"])["errors"]
        entries = processor_count()
        payment = pay_order(order["id"])
        after = native("order", order["id"])
        assert processor_count() == entries
        changes = payment_history_preserved(before, after, payment["events_from"])
        record(
            "FRESH_PERSISTED_METADATA_REFUSAL_" + kind.upper(),
            order_id=order["id"],
            permitted_native_changes=changes,
        )
    native("option", "ss_payment_outcome", "failure")
    for kind in ["missing", "stale", "removed-size"]:
        with changed_projection(kind):
            api = Client()
            api.control("empty")
            assert api.api("cart")[0] == 200
            status, body = api.api(
                "cart/add-item",
                {
                    "id": seed["products"]["br-001"],
                    "quantity": 1,
                    "extensions": {"skyyrose-simple-size": {"size": "S"}},
                },
            )
            assert status == 400 and body["code"] == "skyyrose_simple_size_input"
            before = native("order", paired["id"])
            entries = processor_count()
            pay_order(paired["id"])
            assert processor_count() == entries + 1 and immutable_order(
                native("order", paired["id"])
            ) == immutable_order(before)
        record("NEW_PURCHASE_REFUSED_SAVED_SELECTION_PAYABLE_PROJECTION_" + kind.upper())
    history = native("history", "remove")
    try:
        api = Client()
        api.control("empty")
        assert api.api("cart")[0] == 200
        assert (
            api.api(
                "cart/add-item",
                {
                    "id": seed["products"]["br-001"],
                    "quantity": 1,
                    "extensions": {"skyyrose-simple-size": {"size": "S"}},
                },
            )[0]
            == 400
        )
        entries = processor_count()
        assert "skyyrose_simple_size_order" in native("payment-check", paired["id"])["errors"]
        pay_order(paired["id"])
        assert processor_count() == entries
    finally:
        restored = native("history", "restore")
        assert restored["preimage_sha256"] == history["preimage_sha256"]
    record("MISSING_TRUSTED_HISTORY_REFUSES_AND_EXACT_PREIMAGE_RESTORED")
    _, order = fresh_classic(seed, ("S", "M"))
    native("pool", "1")
    try:
        entries = processor_count()
        before = native("order", order["id"])
        outcome = pay_order(order["id"])
        assert processor_count() == entries and outcome["notices"]["error"]
        assert native("order", order["id"])["stock"] == before["stock"]
    finally:
        native("pool", "5")
    record("TWO_SIZE_SAVED_ORDER_REFUSES_EXHAUSTED_SHARED_PREORDER_POOL")
    before = native("order", order["id"])
    entries = processor_count()
    pay_order(order["id"])
    failed_payment = native("order", order["id"])
    assert processor_count() == entries + 1 and not failed_payment["paid"]
    assert (
        failed_payment["stock"] == before["stock"]
        and failed_payment["stock_reduced"] == before["stock_reduced"]
    )
    assert immutable_order(failed_payment) == immutable_order(before)
    before = failed_payment
    native("option", "ss_payment_outcome", "success")
    entries = processor_count()
    pay_order(order["id"])
    paid = native("order", order["id"])
    parent = str(seed["products"]["br-001"])
    assert processor_count() == entries + 1 and paid["paid"] and paid["stock_reduced"]
    assert paid["status"] == "processing" and paid["transaction_id"] == "synthetic-size-" + str(
        paid["id"]
    )
    assert paid["stock"][parent] == before["stock"][parent] - 2
    assert paid["total"] == "160.00" and immutable_order(paid, True) == immutable_order(
        before, True
    )
    for item in paid["items"]:
        reductions = [row["value"] for row in item["meta_data"] if row["key"] == "_reduced_stock"]
        assert len(reductions) == 1 and int(reductions[0]) == item["quantity"]
    entries = processor_count()
    pay_order(order["id"])
    retry = native("order", order["id"])
    assert processor_count() == entries and canonical(retry) == canonical(paid)
    record(
        "TWO_SIZE_SHARED_PARENT_STOCK_ONCE_AND_PAID_RETRY_IMMUTABLE",
        order_id=paid["id"],
        parent_stock_before=before["stock"][parent],
        parent_stock_after=paid["stock"][parent],
    )
    legacy_id = seed["legacy"]["id"]
    before = native("order", legacy_id)
    entries = processor_count()
    pay_order(legacy_id)
    after = native("order", legacy_id)
    assert (
        processor_count() == entries + 1
        and after["paid"]
        and after["generation"] == []
        and after["raw_size_rows"] == []
    )
    assert immutable_order(after, True) == immutable_order(before, True)
    assert after["stock"][parent] == before["stock"][parent] - 1
    record(
        "SYNTHETIC_PRIOR_NATIVE_ORDER_EXPLICIT_FINGERPRINT_PAYABLE_SIZE_UNKNOWN",
        order_id=legacy_id,
        scope="Native order created before enabling history; hand-built V1-shaped promise, not historical producer execution",
    )
    native("option", "ss_payment_outcome", "failure")
    return paid


def api_add(client, product_id, size=None):
    payload = {"id": product_id, "quantity": 1}
    if size is not None:
        payload["extensions"] = {"skyyrose-simple-size": {"size": size}}
    return client.api("cart/add-item", payload)


def api_checkout(client):
    address = {
        "first_name": "Synthetic",
        "last_name": "Fixture",
        "address_1": "1 Test Way",
        "address_2": "",
        "city": "Oakland",
        "state": "CA",
        "postcode": "94612",
        "country": "US",
    }
    return client.api(
        "checkout",
        {
            "billing_address": {
                **address,
                "email": "fixture@example.invalid",
                "phone": "5105550100",
            },
            "shipping_address": address,
            "payment_method": "ss_offline",
            "payment_data": [],
            "customer_note": "",
        },
    )


def fresh_api(seed, mixed=False, variable_only=False):
    client = Client()
    client.control("empty")
    assert client.api("cart")[0] == 200
    if not variable_only:
        assert api_add(client, seed["products"]["br-001"], "S")[0] == 201
        assert {"key": "Size", "value": "S"} in client.api("cart")[1]["items"][0]["item_data"]
    if mixed or variable_only:
        assert api_add(client, seed["products"]["variation-A"])[0] == 201
    ids = {row["id"] for row in native("orders")}
    count = processor_count()
    status, body = api_checkout(client)
    assert status == 400 and body["payment_result"]["payment_status"] == "failure"
    order = own_new_order(ids)
    assert processor_count() == count + 1 and bool(order["generation"]) == (not variable_only)
    assert body["order_id"] == order["id"]
    assert not order["paid"]
    return client, order


def qualify_store_checkout(seed):
    client, order = fresh_api(seed)
    assert len(order["raw_size_rows"]) == 2 and len(order["generation"]) == 1
    before = native("order", order["id"])
    assert client.api("checkout")[0] == 200
    assert (
        client.api("checkout", {"customer_note": "Synthetic unchanged-cart draft update"}, "PATCH")[
            0
        ]
        == 200
    )
    assert immutable_order(native("order", order["id"])) == immutable_order(before)
    count = processor_count()
    status, result = api_checkout(client)
    assert (
        status == 400
        and result["payment_result"]["payment_status"] == "failure"
        and result["order_id"] == order["id"]
    )
    assert processor_count() == count + 1 and immutable_order(
        native("order", order["id"])
    ) == immutable_order(before)
    record(
        "ACTUAL_STORE_API_CHECKOUT_PERSISTENCE_SAME_CART_GET_PATCH_AND_RETRY", order_id=order["id"]
    )
    for method in ["GET", "PATCH"]:
        client, order = fresh_api(seed)
        native("mutate", order["id"], "draft")
        native("mutate", order["id"], "both")
        before = native("order", order["id"])
        count = processor_count()
        status, body = client.api(
            "checkout", None if method == "GET" else {"customer_note": "must refuse"}, method
        )
        assert status == 409 and body["code"] == "skyyrose_simple_size_saved_order"
        assert processor_count() == count and canonical(native("order", order["id"])) == canonical(
            before
        )
        record(
            "ACTUAL_STORE_API_MISSING_BOTH_DRAFT_" + method + "_REFUSES_BEFORE_DELETE",
            order_id=order["id"],
        )
    client, order = fresh_api(seed)
    native("mutate", order["id"], "draft")
    before = native("order", order["id"])
    # Actual cart synchronization reaches the same pre-delete barrier.
    count = processor_count()
    status, body = api_add(client, seed["products"]["br-001"], "M")
    assert status == 409 and body["code"] == "skyyrose_simple_size_saved_order"
    assert processor_count() == count and canonical(native("order", order["id"])) == canonical(
        before
    )
    assert client.control("inspect")["draft"] == 0
    # Core may already hold a draft object in the refused request; only a subsequent
    # request creates the distinct order after the session pointer is detached.
    ids = {row["id"] for row in native("orders")}
    count = processor_count()
    status, result = api_checkout(client)
    after = own_new_order(ids)
    assert (
        status == 400
        and result["payment_result"]["payment_status"] == "failure"
        and result["order_id"] == after["id"]
        and processor_count() == count + 1
    )
    assert after["id"] != order["id"] and immutable_order(
        native("order", order["id"])
    ) == immutable_order(before)
    record(
        "ACTUAL_STORE_API_CHANGED_CHECKOUT_DRAFT_PRESERVED_AND_DETACHED",
        prior_id=order["id"],
        successor_id=after["id"],
    )
    client, order = fresh_api(seed)
    before = native("order", order["id"])
    assert api_add(client, seed["products"]["br-001"], "M")[0] == 201
    ids = {row["id"] for row in native("orders")}
    count = processor_count()
    status, result = api_checkout(client)
    after = own_new_order(ids)
    assert (
        status == 400
        and result["payment_result"]["payment_status"] == "failure"
        and result["order_id"] == after["id"]
        and processor_count() == count + 1
    )
    assert after["id"] != order["id"] and immutable_order(
        native("order", order["id"])
    ) == immutable_order(before)
    record("ACTUAL_STORE_API_CHANGED_PENDING_ORDER_USES_NATIVE_NEW_ORDER")
    client, variable = fresh_api(seed, variable_only=True)
    native("mutate", variable["id"], "draft")
    items = client.api("cart")[1]["items"]
    assert client.api("cart/update-item", {"key": items[0]["key"], "quantity": 2})[0] == 200
    assert client.api("checkout")[0] == 200
    assert (
        client.api("checkout", {"customer_note": "Native variable-only draft"}, "PATCH")[0] == 200
    )
    changed = native("order", variable["id"])
    assert changed["generation"] == [] and changed["items"][0]["quantity"] == 2
    record("ACTUAL_STORE_API_VARIABLE_ONLY_DRAFT_EDIT_REMAINS_NATIVE", order_id=variable["id"])
    for kind in ["variable-remove", "variable-alter"]:
        _, mixed = fresh_api(seed, mixed=True)
        assert len(mixed["items"]) == 2
        native("mutate", mixed["id"], kind)
        before = native("order", mixed["id"])
        assert "skyyrose_simple_size_order" in native("payment-check", mixed["id"])["errors"]
        count = processor_count()
        payment = pay_order(mixed["id"])
        assert processor_count() == count
        payment_history_preserved(before, native("order", mixed["id"]), payment["events_from"])
        record("MIXED_ORDER_COMPLETE_MEMBERSHIP_REFUSAL_" + kind.upper(), order_id=mixed["id"])


def text_content(body):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]*>", " ", body)))


def qualify_readback(seed, paid):
    readback = native("readback", paid["id"])
    assert sorted(re.findall(r"Size\s*:\s*(S|M)\b", text_content(readback["admin_html"]))) == [
        "M",
        "S",
    ]
    assert sorted(re.findall(r"Size\s*:\s*(S|M)\b", text_content(readback["email_html"]))) == [
        "M",
        "S",
    ]
    assert readback["rest_status"] == 200
    record(
        "NATIVE_EMAIL_AND_CLI_META_FORMATTER_AND_PRIVILEGED_REST_SERIALIZATION",
        order_id=paid["id"],
        limits="CLI formatter is not an authenticated admin screen",
    )
    admin = Client()
    admin.control("login")
    identity = admin.control("inspect")
    assert identity["user_id"] == 1 and "administrator" in identity["roles"]
    screen_path = (
        "/wp-admin/admin.php?page=wc-orders&action=edit&id="
        if STORAGE == "hpos"
        else "/wp-admin/post.php?action=edit&post="
    ) + str(paid["id"])
    screen = admin.request(screen_path)
    assert screen["status"] == 200
    items = admin.request(
        "/wp-admin/admin-ajax.php",
        {
            "action": "woocommerce_load_order_items",
            "order_id": paid["id"],
            "security": identity["order_item_nonce"],
        },
    )
    assert items["status"] == 200 and sorted(
        re.findall(r"Size\s*:\s*(S|M)\b", text_content(items["body"]))
    ) == ["M", "S"]
    admin.rest_nonce = identity["rest_nonce"]
    response = admin.request("/?rest_route=/wc/v3/orders/" + str(paid["id"]))
    assert response["status"] == 200
    order = json.loads(response["body"])
    assert len(order["line_items"]) == 2
    assert sorted(
        next(row["value"] for row in item["meta_data"] if row["key"] == "Size")
        for item in order["line_items"]
    ) == ["M", "S"]
    assert all(
        any(row["key"] == "_skyyrose_simple_size_v1" for row in item["meta_data"])
        for item in order["line_items"]
    )
    record(
        "AUTHENTICATED_SYNTHETIC_ADMIN_SCREEN_AJAX_AND_V3_REST_READBACK",
        site=URL,
        native_user_id=1,
        native_roles=identity["roles"],
        real_account_authentication="NOT_APPLICABLE_SYNTHETIC_SIGNED_COOKIE_ONLY",
    )
    native("mutate", seed["legacy"]["id"], "completed")
    admin.control("empty")
    nonce = admin.control("again-url")["nonce"]
    response = admin.request(
        "/?"
        + urllib.parse.urlencode(
            {"ss_control": "inspect", "order_again": seed["legacy"]["id"], "_wpnonce": nonce}
        )
    )
    assert response["status"] == 302
    destination = urllib.parse.urlparse(response["headers"]["Location"])
    assert destination.scheme == "http" and destination.netloc == "127.0.0.1:" + str(PORT)
    assert response["headers"]["Location"] == admin.control("again-url")["cart_url"]
    state = admin.control("inspect")
    assert state["cart"] == []
    assert any(
        "Choose a size again" in row["notice"]
        and "Choose size" in row["notice"]
        and "href=" in row["notice"]
        for row in state["notices"].get("notice", [])
    )
    record("ACTUAL_NATIVE_ORDER_AGAIN_REQUIRES_FRESH_SELECTION_WITH_PDP_LINK")


def main():
    global STORAGE
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--storage", choices=("hpos", "cpt"), default="hpos")
    STORAGE = parser.parse_args().storage
    REPORT["storage"] = STORAGE
    REPORT["limits"][0] = (
        "Fresh synthetic WP7.1.3/Woo11.2.1/seven-plugin "
        + STORAGE.upper()
        + " site; not installed-stack parity or synchronized-storage qualification"
    )
    if not __debug__:
        raise RuntimeError("Assertions required")
    os.umask(0o077)
    for target in [Path(__file__).absolute(), ROOT, BASE, THEME, PRIVATE]:
        guard(target)
    REPORT["preflight_free_bytes"] = capacity()
    PRIVATE.mkdir(parents=True, mode=0o700)
    for name in ["tmp", "cli-packages"]:
        guard(PRIVATE / name)
        (PRIVATE / name).mkdir(mode=0o700)
    guard(PRIVATE / "cli.yml")
    (PRIVATE / "cli.yml").write_text("{}\n")
    sources = [
        Path(__file__),
        ROOT / "tools/v2-runtime/simple-size-native-fixture.php",
        ROOT / "tools/v2-runtime/simple-size-native-controls.php",
        THEME / "inc/simple-product-sizes.php",
        THEME / "functions.php",
        THEME / "data/simple-product-sizes.json",
        THEME / "data/product-presentation-registry.json",
        ROOT / "wordpress-theme/skyyrose-flagship/data/logo-registry.json",
    ]
    binaries = [
        Path(value).resolve()
        for value in [
            PHP,
            WP,
            "/usr/bin/git",
            "/usr/bin/sandbox-exec",
            MYSQL,
            INSTALL_DB,
            DAEMON,
        ]
    ]
    inputs = {str(path): pin(path) for path in sources + binaries}
    REPORT["execution_inputs"] = inputs
    write(PRIVATE / "results.json", REPORT)
    try:
        seed = setup()
        paired = qualify(seed)
        paid = qualify_saved_orders(seed, paired)
        qualify_store_checkout(seed)
        qualify_readback(seed, paid)
        REPORT["status"] = "PASS_NATIVE_SIMPLE_SIZE_" + STORAGE.upper() + "_MATRIX"
        REPORT["remaining"] = [
            "Final successor build/package/preview/adoption",
            "Installed plugin/configuration/exact runtime gaps and full installed-stack qualification remain open",
            "Other storage mode and synchronized-storage claims require their separate actual evidence",
        ]
    except BaseException as error:
        REPORT["status"] = "FAIL"
        REPORT["error"] = {"type": type(error).__name__, "message": str(error)}
        raise
    finally:
        failed = False
        service_count = len(CHILDREN)
        cleanup = cleanup_owned()
        failed = any("error" in row for row in cleanup)
        if service_count:
            socket_absent = not Path(SOCKET).exists()
            cleanup.append({"owned_socket_absent": socket_absent})
            failed = failed or not socket_absent
        if service_count > 1:
            try:
                with socket.create_connection(("127.0.0.1", PORT), timeout=0.2):
                    listener_absent = False
            except OSError:
                listener_absent = True
            cleanup.append({"owned_listener_absent": listener_absent})
            failed = failed or not listener_absent
        REPORT["cleanup"] = cleanup
        try:
            assert inputs == {str(path): pin(path) for path in sources + binaries}
            if "source_commit" in REPORT:
                assert git("rev-parse", "HEAD") == REPORT["source_commit"] and not git(
                    "status", "--porcelain", "--ignore-submodules=all"
                )
            for folder, census in [
                (BASE, REPORT.get("source_census", {})),
                (THEME, REPORT.get("theme_census", {})),
            ]:
                for sub, expected in census.items():
                    assert pin(folder / sub) == expected
            REPORT["preservation"] = "PASS_EXECUTION_INPUTS_ORIGINAL_CODE_THEME_HEAD_AND_INDEX"
        except BaseException as error:
            failed = True
            REPORT["preservation"] = "FAIL_" + type(error).__name__
        if failed:
            REPORT["status"] = "FAIL_CLEANUP_OR_PRESERVATION"
        write(PRIVATE / "results.json", REPORT)
        print(str(PRIVATE / "results.json"), flush=True)
        if failed:
            raise RuntimeError("Owned cleanup or input preservation failed; receipt retained")


if __name__ == "__main__":
    main()
