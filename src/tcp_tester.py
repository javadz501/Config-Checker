"""Fast TCP reachability pre-filter for proxy subscription entries."""
import argparse
import logging
import os
import socket
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Optional, Tuple

import config_parser as parser

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
DEFAULT_TIMEOUT = 2.5
DEFAULT_WORKERS = 64


def get_endpoint(config: str) -> Optional[Tuple[str, int]]:
    text = config.strip()
    low = text.lower()
    try:
        if low.startswith('vmess://'):
            data = parser.decode_vmess(text)
            host, port = (data or {}).get('add'), (data or {}).get('port')
        elif low.startswith('vless://'):
            data = parser.parse_vless(text)
            host, port = (data or {}).get('address'), (data or {}).get('port')
        elif low.startswith('trojan://'):
            data = parser.parse_trojan(text)
            host, port = (data or {}).get('address'), (data or {}).get('port')
        elif low.startswith(('hysteria2://', 'hy2://')):
            data = parser.parse_hysteria2(text)
            host, port = (data or {}).get('address'), (data or {}).get('port')
        elif low.startswith('ss://'):
            data = parser.parse_shadowsocks(text)
            host, port = (data or {}).get('address'), (data or {}).get('port')
        elif low.startswith('wireguard://'):
            data = parser.parse_wireguard(text)
            host, port = (data or {}).get('address'), (data or {}).get('port')
        elif low.startswith('tuic://'):
            data = parser.parse_tuic(text)
            host, port = (data or {}).get('address'), (data or {}).get('port')
        else:
            return None
        if not host or not port:
            return None
        port = int(port)
        if not 1 <= port <= 65535:
            return None
        return str(host).strip('[]'), port
    except (ValueError, TypeError, KeyError, AttributeError):
        return None


def tcp_reachable(config: str, timeout: float = DEFAULT_TIMEOUT) -> Optional[bool]:
    """Return True/False for TCP transports, or None when TCP is not applicable.

    QUIC/Hysteria2/TUIC/WireGuard and explicit QUIC/KCP transports are not
    rejected by a TCP-only probe; their protocol-specific URL tests decide.
    """
    text = config.strip()
    low = text.lower()
    if low.startswith(('hysteria2://', 'hy2://', 'tuic://', 'wireguard://')):
        return None
    try:
        if low.startswith('vmess://'):
            data = parser.decode_vmess(text) or {}
            if str(data.get('net', 'tcp')).lower() in {'quic', 'kcp'}:
                return None
        elif low.startswith('vless://'):
            data = parser.parse_vless(text) or {}
            if str(data.get('type', 'tcp')).lower() in {'quic', 'kcp'}:
                return None
        elif low.startswith('trojan://'):
            data = parser.parse_trojan(text) or {}
            if str(data.get('type', 'tcp')).lower() in {'quic', 'kcp'}:
                return None
    except Exception:
        return False

    endpoint = get_endpoint(text)
    if endpoint is None:
        return False
    host, port = endpoint
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except (OSError, TimeoutError):
        return False


def main() -> int:
    cli = argparse.ArgumentParser(description='Filter proxy configs by one TCP connection test.')
    cli.add_argument('input_file')
    cli.add_argument('output_file')
    cli.add_argument('--timeout', type=float, default=DEFAULT_TIMEOUT)
    cli.add_argument('--workers', type=int, default=DEFAULT_WORKERS)
    args = cli.parse_args()

    try:
        with open(args.input_file, 'r', encoding='utf-8') as stream:
            lines = stream.readlines()
    except OSError as exc:
        logger.error('Cannot read input file: %s', exc)
        return 2

    headers, configs = [], []
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith('//'):
            if not configs:
                headers.append(line.rstrip('\n'))
            continue
        configs.append(stripped)

    if not configs:
        logger.error('No configs found in %s', args.input_file)
        return 2

    logger.info('Starting one TCP reachability check for %d configs (timeout %.1fs, workers %d)',
                len(configs), args.timeout, args.workers)
    results = {}
    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as pool:
        future_map = {pool.submit(tcp_reachable, config, args.timeout): index
                      for index, config in enumerate(configs)}
        for future in as_completed(future_map):
            index = future_map[future]
            try:
                results[index] = future.result()
            except Exception as exc:
                logger.debug('TCP test error for config %d: %s', index + 1, exc)
                results[index] = False

    passed = [config for index, config in enumerate(configs) if results.get(index) is True]
    skipped = [config for index, config in enumerate(configs) if results.get(index) is None]
    failed = sum(1 for index in range(len(configs)) if results.get(index) is False)
    candidates = [config for index, config in enumerate(configs) if results.get(index) is not False]
    logger.info(
        'TCP test summary: total=%d tcp_reachable=%d tcp_unreachable=%d tcp_not_applicable=%d candidates_for_URL_test=%d',
        len(configs), len(passed), failed, len(skipped), len(candidates)
    )

    os.makedirs(os.path.dirname(args.output_file) or '.', exist_ok=True)
    with open(args.output_file, 'w', encoding='utf-8') as stream:
        for header in headers:
            stream.write(header + '\n')
        if headers and candidates:
            stream.write('\n')
        for config in candidates:
            stream.write(config + '\n\n')

    if not candidates:
        logger.error('TCP test found no reachable TCP configs or UDP configs to defer; refusing to continue with an empty candidate set')
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
