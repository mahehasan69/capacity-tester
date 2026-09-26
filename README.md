# Capacity Tester V1.2

A controlled HTTP capacity-testing platform for infrastructure you own or are explicitly authorized to test.

## Safety model

- Targets are allowlisted with `ALLOWED_TARGET_HOST`.
- Telegram commands require `TELEGRAM_ADMIN_IDS`.
- A hard maximum RPS and duration are enforced server-side.
- `/stop` cancels the active test.
- This project intentionally does not implement WAF/anti-bot bypass, IP spoofing, proxy rotation, CAPTCHA bypass, or arbitrary-target scanning.
- Start with a staging endpoint and low load.

## Architecture

Telegram -> Controller -> Load Worker -> Authorized Target
                       \-> Metrics -> Telegram

GitHub Actions can run the worker as a short-lived second generator. The worker polls the controller for its assigned rate.

## Local setup

Python 3.11+ recommended.

```bash
python -m venv .venv
# Linux/macOS:
source .venv/bin/activate
# Windows PowerShell:
# .\.venv\Scripts\Activate.ps1

pip install -r requirements.txt
copy .env.example .env   # Windows
# cp .env.example .env   # Linux/macOS
```

Fill `.env`:

- TELEGRAM_BOT_TOKEN: token from BotFather
- TELEGRAM_ADMIN_IDS: comma-separated numeric Telegram user IDs
- ALLOWED_TARGET_HOST: your authorized hostname, e.g. staging.example.com
- MAX_RPS: hard ceiling (default 100)
- MAX_DURATION_SECONDS: hard ceiling (default 300)
- WORKER_SHARED_SECRET: random secret shared by controller and workers

Run:

```bash
python app.py
```

Then send `/start` to your bot.

## Commands

- `/setdomain https://staging.example.com` -> configure the authorized target
- `/domain` -> show the configured target
- `/cleardomain` -> remove the configured target
- `/status`
- `/start_test 10 60` -> start at 10 RPS for 60 seconds
- `/setrps 25`
- `/pause`
- `/resume`
- `/stop`
- `/results`

The controller clamps requested RPS/duration to configured limits.

## GitHub Actions

The workflow is manually dispatched and requires the same target/secret configuration. It is intentionally a bounded worker, not an unlimited traffic generator.

Required GitHub repository secrets:

- CONTROLLER_URL
- WORKER_SHARED_SECRET

The controller URL should be HTTPS and restricted to your own deployment.

## Production deployment

Put the controller behind HTTPS and a firewall. Do not expose the controller's admin API publicly without authentication. Use a dedicated staging environment first.

## Metrics

The worker reports request count, error count, achieved RPS and latency percentiles. The controller combines worker reports and returns a compact Telegram summary.


## Worker

On the Oracle VM, after setting `CONTROLLER_URL`, `WORKER_SHARED_SECRET`, and `WORKER_ID`:

```bash
python -m loadtest.worker
```

For GitHub Actions, manually dispatch the workflow and provide your HTTPS controller URL.

> The example default is intentionally conservative. Increase limits only after you have verified the target, controller, monitoring, and emergency stop behavior on staging.


## V1.1 target configuration

The target can now be set from Telegram with `/setdomain`. Only admin users can change it. Targets must use HTTPS and a public hostname. Localhost, private IPs, loopback, link-local, and reserved addresses are rejected. A target cannot be changed while a test is running.

For production, add your own domain-registration/allowlist policy if the controller will be used by multiple operators.

## Target state

V1.1 stores the configured target in the shared controller state, so `/setdomain` and `/domain` use the same live value. Restarting the process clears runtime state; persistent storage can be added later.

## V1.2
The controller automatically launches a local worker on `/start_test`. `/status` reports configured RPS versus achieved RPS, and `/workers` reports worker heartbeat and counters.
