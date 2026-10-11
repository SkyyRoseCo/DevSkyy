# Coolify + OpenHands Install Runbook
**Target:** Ubuntu 24.04 home server · 2+ cores · ≥2GB RAM · ≥30GB disk · LAN access only
**Outcome:** Coolify dashboard on `http://<server-ip>:8000` + OpenHands GUI on `http://<server-ip>:3000` · both auto-restart on reboot
**Time:** ~15–25 minutes (mostly Docker pulls)
**Mode:** Paste each block into your SSH session sequentially. Read the **Verify** line after each phase before moving on.

> **Convention used below:** `$` = run as your regular user, `#` = run as root (or with `sudo`). Replace `<server-ip>` with the LAN IP of your server (e.g. `192.168.1.50`) wherever you see it.

---

## Phase 0 — Pre-flight (2 min)

### 0.1 SSH in + sanity check the box

```bash
$ ssh <user>@<server-ip>
$ lsb_release -a              # confirm Ubuntu 24.04
$ free -h                     # confirm ≥2GB total RAM
$ df -h /                     # confirm ≥30GB free on /
$ nproc                       # confirm ≥2 cores
$ uname -m                    # confirm amd64 (x86_64) or aarch64 (arm64)
```

**Verify:** All five must return sane values. If RAM < 2GB or disk < 30GB, stop — Coolify + OpenHands will fail under memory pressure.

### 0.2 Update package index + base tools

```bash
$ sudo apt update && sudo apt upgrade -y
$ sudo apt install -y curl wget git ufw htop ca-certificates
```

### 0.3 Firewall (LAN-only access)

Detect your LAN subnet (most home routers use `192.168.0.0/16` or `192.168.1.0/24`):

```bash
$ ip -o -f inet addr show | awk '/scope global/ {print $4}'
# Example output: 192.168.1.50/24 → your LAN subnet is 192.168.1.0/24
```

Apply firewall:

```bash
$ sudo ufw default deny incoming
$ sudo ufw default allow outgoing
$ sudo ufw allow from 192.168.0.0/16 to any port 22 proto tcp comment 'SSH from LAN'
$ sudo ufw allow from 192.168.0.0/16 to any port 8000 proto tcp comment 'Coolify dashboard from LAN'
$ sudo ufw allow from 192.168.0.0/16 to any port 6001 proto tcp comment 'Coolify realtime from LAN'
$ sudo ufw allow from 192.168.0.0/16 to any port 6002 proto tcp comment 'Coolify terminal from LAN'
$ sudo ufw allow from 192.168.0.0/16 to any port 3000 proto tcp comment 'OpenHands GUI from LAN'
$ sudo ufw allow from 192.168.0.0/16 to any port 80 proto tcp comment 'Coolify HTTP proxy from LAN'
$ sudo ufw allow from 192.168.0.0/16 to any port 443 proto tcp comment 'Coolify HTTPS proxy from LAN'
$ sudo ufw enable
$ sudo ufw status numbered
```

**Verify:** `ufw status` shows all 7 rules ACTIVE. No public exposure — confirm your router doesn't port-forward these ports from WAN.

---

## Phase 1 — Coolify Install (5–10 min)

Coolify auto-installs Docker + Docker Compose + dependencies. You do NOT need to install Docker first.

### 1.1 Run the official installer

```bash
$ sudo curl -fsSL https://cdn.coollabs.io/coolify/install.sh | sudo bash
```

If you want to pre-create the admin account (so nobody else can claim it):

```bash
$ sudo env ROOT_USERNAME=admin ROOT_USER_EMAIL=you@example.com ROOT_USER_PASSWORD='CHANGE_ME_STRONG_PASSWORD' bash -c 'curl -fsSL https://cdn.coollabs.io/coolify/install.sh | bash'
```

The installer will:
1. Install Docker + Docker Compose (idempotent — skips if already present)
2. Pull Coolify images (~500MB)
3. Generate SSH keys + secrets in `/data/coolify/`
4. Start Coolify via Docker Compose
5. Print the dashboard URL when done

**Verify:**
```bash
$ sudo docker ps --format 'table {{.Names}}\t{{.Status}}'
# Expect rows for: coolify, coolify-proxy, coolify-db, coolify-redis, coolify-realtime — all "Up"
```

### 1.2 First-login security gate

Open `http://<server-ip>:8000` in your browser **immediately**. Whoever loads it first becomes root admin.

- If you set `ROOT_USERNAME` env var in 1.1 → log in with those credentials
- Otherwise → register the admin account now

After login:
1. **Settings → Instance Settings** → set the instance name
2. **Settings → Instance Settings → "Instance URL"** → set to `http://<server-ip>:8000` (skip the SSL/domain prompts — you're LAN-only)
3. **Server → localhost** → already configured pointing at the local Docker. Verify it shows "Reachable"

### 1.3 Disable auto-update prompts (optional, LAN box)

If you don't want Coolify nagging about updates on a home box:
**Settings → Update** → toggle "Auto-update" OFF. Run updates manually when you're ready.

**Verify Phase 1 complete:**
```bash
$ curl -sI http://localhost:8000 | head -1
# Expect: HTTP/1.1 200 OK or HTTP/1.1 302 Found
```

---

## Phase 2 — OpenHands Install (5 min)

Coolify already installed Docker. We'll run OpenHands as a sibling container, not inside Coolify (simpler, easier to debug).

### 2.1 Pre-pull the runtime image (separate so progress is visible)

```bash
$ sudo docker pull ghcr.io/openhands/agent-server:1.19.1-python
$ sudo docker pull docker.openhands.dev/openhands/openhands:1.7
```

These are ~2GB combined. Wait for both to finish before continuing.

### 2.2 Create the persistent state directory

```bash
$ mkdir -p ~/.openhands
```

OpenHands writes session history, agent state, and credentials here. Bind-mounted into the container so it survives restarts.

### 2.3 Launch OpenHands as a long-running service

For a one-shot test (foreground, Ctrl-C to stop):

```bash
$ sudo docker run -it --rm --pull=always \
    -e AGENT_SERVER_IMAGE_REPOSITORY=ghcr.io/openhands/agent-server \
    -e AGENT_SERVER_IMAGE_TAG=1.19.1-python \
    -e LOG_ALL_EVENTS=true \
    -v /var/run/docker.sock:/var/run/docker.sock \
    -v ~/.openhands:/.openhands \
    -p 3000:3000 \
    --add-host host.docker.internal:host-gateway \
    --name openhands-app \
    docker.openhands.dev/openhands/openhands:1.7
```

For a **persistent service** (auto-restart on reboot — recommended):

```bash
$ sudo docker run -d --restart=unless-stopped --pull=always \
    -e AGENT_SERVER_IMAGE_REPOSITORY=ghcr.io/openhands/agent-server \
    -e AGENT_SERVER_IMAGE_TAG=1.19.1-python \
    -e LOG_ALL_EVENTS=true \
    -v /var/run/docker.sock:/var/run/docker.sock \
    -v ~/.openhands:/.openhands \
    -p 3000:3000 \
    --add-host host.docker.internal:host-gateway \
    --name openhands-app \
    docker.openhands.dev/openhands/openhands:1.7
```

**Verify:**
```bash
$ sudo docker ps --filter name=openhands-app --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'
# Expect: openhands-app | Up <N> seconds | 0.0.0.0:3000->3000/tcp
$ curl -sI http://localhost:3000 | head -1
# Expect: HTTP/1.1 200 OK
```

### 2.4 Configure Anthropic Claude on first login

Open `http://<server-ip>:3000` in your browser.

On the welcome screen:
1. **LLM Provider** → select `Anthropic`
2. **LLM Model** → `anthropic/claude-sonnet-4-6` (best coding agent model as of 2026-05)
   - Alternatives: `anthropic/claude-opus-4-7` (deepest reasoning, ~5x cost), `anthropic/claude-haiku-4-5-20251001` (cheapest, faster but weaker agent)
3. **API Key** → paste your Anthropic API key (starts `sk-ant-...`)
4. **Save** → the page reloads with the agent ready

If you want the API key baked into the container instead of entering via UI, add these env vars to the `docker run` (then UI lock-in is removed but agent still picks them up):

```bash
    -e LLM_API_KEY='sk-ant-...' \
    -e LLM_MODEL='anthropic/claude-sonnet-4-6' \
```

### 2.5 First agent run (smoke test)

In the OpenHands UI:
1. Click **New Conversation**
2. Type: `Create a file hello.txt in the workspace containing "openhands works"`
3. Watch the agent's tool calls in the right pane
4. After "Agent finished" → check `~/.openhands/workspace/hello.txt` on the server:

```bash
$ cat ~/.openhands/workspace/hello.txt
# Expect: openhands works
```

---

## Phase 3 — Coordinate the two (2 min)

### 3.1 Port usage map

| Service | Port | Purpose |
|---------|------|---------|
| Coolify dashboard | 8000 | Web UI |
| Coolify realtime | 6001 | WebSocket events |
| Coolify terminal | 6002 | In-browser SSH |
| Coolify proxy | 80, 443 | App routing (only matters if you host apps via Coolify) |
| OpenHands GUI | 3000 | Web UI + WebSocket |

No port collisions. Both can run side-by-side indefinitely.

### 3.2 Optional — register OpenHands as a Coolify-managed app

If you want Coolify's dashboard to show OpenHands status / logs / restart button:

1. Coolify dashboard → **Projects** → **+ New Project** → name it "OpenHands"
2. **+ New Resource** → **Docker Compose**
3. Paste this compose YAML:

```yaml
services:
  openhands:
    image: docker.openhands.dev/openhands/openhands:1.7
    container_name: openhands-app
    restart: unless-stopped
    pull_policy: always
    environment:
      AGENT_SERVER_IMAGE_REPOSITORY: ghcr.io/openhands/agent-server
      AGENT_SERVER_IMAGE_TAG: 1.19.1-python
      LOG_ALL_EVENTS: 'true'
      LLM_MODEL: anthropic/claude-sonnet-4-6
      # LLM_API_KEY: set via Coolify "Environment Variables" tab as a secret
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - /root/.openhands:/.openhands
    ports:
      - "3000:3000"
    extra_hosts:
      - host.docker.internal:host-gateway
```

4. **Environment Variables** tab → add `LLM_API_KEY` as a secret
5. **Deploy**

**Before deploying via Coolify, stop the standalone container first:**
```bash
$ sudo docker stop openhands-app && sudo docker rm openhands-app
```

Otherwise Coolify will fail to create the container (name collision).

### 3.3 Keep the runtime updated

OpenHands ships rapid releases. Update monthly:

```bash
$ sudo docker pull docker.openhands.dev/openhands/openhands:1.7
$ sudo docker pull ghcr.io/openhands/agent-server:1.19.1-python
$ sudo docker stop openhands-app && sudo docker rm openhands-app
# then re-run the docker run from 2.3
```

Coolify auto-pulls images on its own update cycle (Settings → Update).

---

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| Coolify install hangs at "Pulling Docker images" | Slow network or DockerHub rate limit | Wait. If >10min, `Ctrl-C`, re-run installer — it's idempotent. |
| `http://<ip>:8000` connection refused from LAN device | UFW blocking | Verify LAN subnet matches firewall rules: `sudo ufw status numbered` |
| OpenHands UI loads but "agent failed to start" | Bad API key OR wrong model name | Re-check key in Anthropic console. Model must be prefixed `anthropic/...` |
| OpenHands stuck on "starting runtime container" | Docker socket permissions | Confirm `-v /var/run/docker.sock:/var/run/docker.sock` is in the run command. The container needs Docker access to spawn sandbox. |
| Coolify dashboard says "Server unreachable" for localhost | SSH key permission issue | Coolify writes its key to `/data/coolify/ssh/keys/`. Verify owned by `coolify` user. |
| Both up but home network can't reach :3000 | Router doesn't bridge VLANs | Confirm you're on the same VLAN/SSID as the server. If isolation enabled, disable AP isolation on router. |

---

## Security Notes — Read Before Sharing the Server

1. **OpenHands has root via Docker socket.** Anyone who reaches `http://<ip>:3000` can run arbitrary code on the host as root. UFW + LAN-only is the only thing protecting it. **Never** port-forward 3000 to the public internet without putting auth (e.g. a reverse proxy with basic auth or Tailscale) in front.

2. **Coolify admin = root on server.** Whoever logs into Coolify first owns everything Coolify manages. Set strong admin password in step 1.1.

3. **API key is sensitive.** If you set `LLM_API_KEY` via env var in the docker run, it's visible via `docker inspect openhands-app`. Use the Coolify secret manager (3.2) for stronger isolation, or rely on the UI-only entry which stores it inside `~/.openhands/`.

4. **Router config.** Confirm WAN port-forwards for 3000, 6001, 6002, 8000 are NOT enabled on your router. These ports should be unreachable from outside your home network.

---

## Rollback

### Uninstall OpenHands
```bash
$ sudo docker stop openhands-app && sudo docker rm openhands-app
$ sudo docker rmi docker.openhands.dev/openhands/openhands:1.7
$ sudo docker rmi ghcr.io/openhands/agent-server:1.19.1-python
$ rm -rf ~/.openhands
```

### Uninstall Coolify
```bash
$ sudo curl -fsSL https://cdn.coollabs.io/coolify/uninstall.sh | sudo bash
# Removes containers, /data/coolify, generated SSH keys.
```

### Reset firewall
```bash
$ sudo ufw reset
$ sudo ufw disable
```
