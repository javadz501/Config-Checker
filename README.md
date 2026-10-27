# SUB — Free Proxy Configuration Collector

**Collect. Test. Publish.**

SUB automatically collects public proxy configurations, tests supported protocols, and publishes organized outputs through GitHub Actions.

## Features

- Automated configuration collection and updates
- Xray and sing-box testing pipelines
- Organized outputs for supported clients
- Duplicate filtering and configuration validation
- Scheduled updates through GitHub Actions
- Publicly accessible configuration files

## Configuration Subscriptions

Use the raw links below to access the generated configuration files.

| Output | Format | Link |
|---|---|---|
| Xray Tested Configurations | TXT | [Open Subscription](https://raw.githubusercontent.com/javadz501/SUB/main/configs/proxy_configs_tested.txt) |
| sing-box Tested Configurations | JSON | [Open Configurations](https://raw.githubusercontent.com/javadz501/SUB/main/configs/singbox_configs_tested.json) |
| sing-box Secure Configurations | JSON | [Open Configurations](https://raw.githubusercontent.com/javadz501/SUB/main/configs/singbox_configs_secure.json) |
| Clash Tested Configurations | YAML | [Open Configurations](https://raw.githubusercontent.com/javadz501/SUB/main/configs/clash_configs_tested.yaml) |
| Clash Secure Configurations | YAML | [Open Configurations](https://raw.githubusercontent.com/javadz501/SUB/main/configs/clash_configs_secure.yaml) |

**Note:** These links depend on the output files being present on the `main` branch. Availability and compatibility may vary between updates and clients.

## Automated Updates

SUB uses GitHub Actions to collect and process configurations automatically.

To inspect recent runs and their results, visit the [Actions page](https://github.com/javadz501/SUB/actions).

The update schedule is controlled by the repository's workflow configuration and may change over time.

## Usage

1. Choose an output format compatible with your client.
2. Copy the corresponding raw URL.
3. Import the URL if your client supports remote subscriptions, or download the file and import it manually.
4. Refresh the subscription periodically to retrieve updated configurations.

Not every client supports every format or protocol.

## Important Notice

- Configurations are collected from public sources and may stop working without notice.
- A successful test does not guarantee long-term availability, privacy, security, or suitability for sensitive traffic.
- Public proxy operators may observe traffic metadata or unencrypted traffic. Use trusted services and encrypted protocols where appropriate.
- This repository does not guarantee uptime or uninterrupted connectivity.

## License and Attribution

This repository is based on an upstream project. Original license terms and required attribution notices must be preserved. Refer to the repository's license file for applicable terms.

---

**SUB** — Automated public proxy configuration collection and testing.
