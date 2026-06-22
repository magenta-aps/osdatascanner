### Connecting to the host

Sometimes it can be helpful to start a temporary server on your computer and
scan it from the Docker environment. To do that, just configure your scan to
use the IP address `172.17.0.1`: inside a Docker container, this address refers
to the host machine. (Some Windows and Mac editions of Docker also define a DNS
name for the host, `host.docker.internal`.)

Note that you might need to adjust your firewall to allow connections from the
virtual Docker networks. By default, these are all given addresses in the range
`172.*.*.*`, equivalent to `172.0.0.0/8` in CIDR notation. Using the `ufw`
command, for example, you might do something like this to allow all connections
from that range:

    ufw allow from 172.0.0.0/8 to any