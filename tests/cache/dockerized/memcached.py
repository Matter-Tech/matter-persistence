import socket

from testcontainers.core.container import DockerContainer
from testcontainers.core.waiting_utils import wait_container_is_ready


class MemcachedNotReady(Exception):
    pass


class MemcachedContainer(DockerContainer):
    def __init__(self, image="memcached:latest", port_to_expose=11211, **kwargs):
        super(MemcachedContainer, self).__init__(image, **kwargs)
        self.port_to_expose = port_to_expose
        self.with_exposed_ports(port_to_expose)
        self.with_command("memcached -vvv")

    @wait_container_is_ready(MemcachedNotReady)
    def _connect(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            host = self.get_container_host_ip()
            port = int(self.get_exposed_port(self.port_to_expose))
            s.connect((host, port))
            s.sendall(b"stats\n\r")
            data = s.recv(1024)
            if len(data) == 0:
                raise MemcachedNotReady("Memcached not ready yet")

    def start(self):
        super().start()
        self._connect()
        return self

    def get_host_and_port(self):
        return self.get_container_host_ip(), int(self.get_exposed_port(self.port_to_expose))
