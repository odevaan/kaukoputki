import json
import logging
import socket
import threading

logger = logging.getLogger(__name__)

DISCOVERY_PORT = 32227
DISCOVERY_MESSAGE = b"alpacadiscovery1"


class AlpacaDiscoveryServer:
    """
    ASCOM Alpaca UDP Discovery Responder.
    Listens on UDP port 32227 and responds to 'alpacadiscovery1' broadcast packets,
    enabling N.I.N.A. and Stellarium to discover the telescope on the LAN.
    """

    def __init__(self, alpaca_port: int = 11111):
        self.alpaca_port = alpaca_port
        self._sock: socket.socket = None
        self._running = False
        self._thread: threading.Thread = None

    def start(self) -> None:
        if self._running:
            return
        try:
            self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            # Bind to all interfaces on discovery port
            self._sock.bind(("", DISCOVERY_PORT))
            self._running = True
            self._thread = threading.Thread(target=self._listen_loop, daemon=True)
            self._thread.start()
            logger.info(f"ASCOM Alpaca Discovery responder running on UDP port {DISCOVERY_PORT}")
        except Exception as e:
            logger.warning(f"Could not bind Alpaca Discovery on UDP port {DISCOVERY_PORT}: {e}")

    def _listen_loop(self) -> None:
        response_payload = json.dumps({"AlpacaPort": self.alpaca_port}).encode("utf-8")
        while self._running:
            try:
                data, addr = self._sock.recvfrom(1024)
                if data and DISCOVERY_MESSAGE in data:
                    self._sock.sendto(response_payload, addr)
                    logger.debug(f"Discovered by Alpaca client at {addr[0]}:{addr[1]}")
            except Exception as e:
                if self._running:
                    logger.error(f"Error in discovery listener: {e}")

    def stop(self) -> None:
        self._running = False
        if self._sock:
            try:
                self._sock.close()
            except Exception:
                pass
        self._sock = None
        logger.info("Alpaca Discovery responder stopped.")
