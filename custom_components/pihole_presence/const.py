DOMAIN = "pihole_presence"

CONF_AWAY_TIME = "away_time"
CONF_HOST = "host"
CONF_SCAN_INTERVAL = "scan_interval"

DEFAULT_HOST = "http://pi.hole"
DEFAULT_SCAN_INTERVAL = 30  # seconds
DEFAULT_AWAY_TIME = 900     # seconds → 15 min

ATTR_INTERFACE = "interface"
ATTR_FIRST_SEEN = "first_seen"
ATTR_LAST_QUERY = "last_query"
ATTR_NUM_QUERIES = "num_queries"
ATTR_MAC_VENDOR = "mac_vendor"
ATTR_IPS = "ips"
ATTR_NAME = "name"
ATTR_DHCP_EXPIRES = "dhcp_expires"

LEASES_ENDPOINT = "/api/dhcp/leases"
DEVICES_ENDPOINT = "/api/network/devices?max_devices=999&max_addresses=24"
