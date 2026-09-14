#!/usr/bin/env python3
"""
Kaukoputki ASCOM Alpaca Telescope Driver Service
Entry point for running the driver on Linux or Windows.
"""
import argparse
import logging
import sys
import uvicorn

from app.config import load_config, save_config

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("kaukoputki")


def main():
    parser = argparse.ArgumentParser(description="Kaukoputki Jetter Nano-B ASCOM Alpaca Driver")
    parser.add_argument("--port", type=str, default=None, help="Serial port (e.g. /dev/ttyUSB0 or COM1)")
    parser.add_argument("--baud", type=int, default=None, help="Baud rate (default: 9600)")
    parser.add_argument("--mock", action="store_true", help="Run in mock/simulation mode without physical hardware")
    parser.add_argument("--alpaca-port", type=int, default=None, help="Alpaca HTTP port (default: 11111)")
    parser.add_argument("--no-discovery", action="store_true", help="Disable Alpaca UDP auto-discovery")
    args = parser.parse_args()

    config = load_config()

    if args.port:
        config.serial.port = args.port
    if args.baud:
        config.serial.baudrate = args.baud
    if args.mock:
        config.serial.mock_mode = True
    if args.alpaca_port:
        config.alpaca_port = args.alpaca_port
    if args.no_discovery:
        config.enable_discovery = False

    save_config(config)

    logger.info("=" * 60)
    logger.info(" Kaukoputki ASCOM Alpaca Telescope Driver Service")
    logger.info(f" Serial Port: {config.serial.port} (Mock: {config.serial.mock_mode})")
    logger.info(f" Alpaca Port: {config.alpaca_port}")
    logger.info(f" Auto-Discovery (UDP 32227): {config.enable_discovery}")
    logger.info(f" Observatory: {config.observatory.name} ({config.observatory.latitude_deg:.4f}N, {config.observatory.longitude_deg:.4f}E)")
    logger.info("=" * 60)

    from app.alpaca_server import app
    uvicorn.run(app, host="0.0.0.0", port=config.alpaca_port, log_level="info")


if __name__ == "__main__":
    main()
