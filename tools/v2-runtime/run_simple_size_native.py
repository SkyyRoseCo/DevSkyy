"""New loopback-only native size fixture; retained evidence is never reused as a database.

Authentication is not applicable to this synthetic local site. No real gateway,
installed configuration, credentials, external HTTP, conversion or deployment.
"""

from __future__ import annotations

import ctypes
import hashlib
import http.cookiejar
import json
import os
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
    "schema": "skyyrose.simple-size-native.v1",
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
    return json.loads(body.rsplit(marker, 1)[1])


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

    def request(self, path, payload=None, method=None, api=False):
        if not path.startswith("/") or path.startswith("//"):
            raise ValueError("Own loopback path required")
        headers = {}
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
        + ");\ndefine('DB_CHARSET','utf8mb4');\n$table_prefix='wp_';\ndefine('SKYYROSE_RELEASE_SYNTHETIC_FIXTURE',true);\ndefine('SR_SIMPLE_SIZE_FIXTURE_ROOT',"
        + json.dumps(str(PRIVATE))
        + ");\ndefine('DISABLE_WP_CRON',true);\ndefine('WP_HTTP_BLOCK_EXTERNAL',true);\ndefine('AUTOMATIC_UPDATER_DISABLED',true);\ndefine('WP_DEBUG',false);\ndefine('WP_HOME',"
        + json.dumps(URL)
        + ");\ndefine('WP_SITEURL',"
        + json.dumps(URL)
        + ");\ndefine('AUTH_KEY','synthetic-no-remote-authority');\ndefine('SECURE_AUTH_KEY','synthetic-no-remote-authority');\ndefine('LOGGED_IN_KEY','synthetic-no-remote-authority');\ndefine('NONCE_KEY','synthetic-no-remote-authority');\ndefine('ABSPATH',__DIR__.'/');\nrequire_once ABSPATH.'wp-settings.php';\n"
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
    seed = native("init")
    write(PRIVATE / "seed.json", seed)
    assert (
        seed["runtime"]["wp"] == "7.1.3"
        and seed["runtime"]["woo"] == "11.2.1"
        and seed["runtime"]["php"] == "8.5.6"
    )
    assert (
        len(seed["runtime"]["plugins"]) == 7
        and "OrdersTableDataStore" in seed["legacy"]["data_store"]
    )
    profile = (
        CLIENT_PROFILE
        + '(allow network-bind (local ip "127.0.0.1:'
        + str(PORT)
        + '"))(allow network-inbound (local ip "127.0.0.1:'
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
        native("pay", order["id"])
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

    assert api_add(products["br-001"], "S")[0] == 200
    assert api_add(products["br-001"], "M")[0] == 200
    assert api_add(products["br-001"], "S")[0] == 200
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


def main():
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
        qualify(seed)
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
