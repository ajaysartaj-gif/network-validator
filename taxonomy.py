# -------------------------------
# SEMANTIC TAXONOMY v3
# -------------------------------

SEMANTIC_TAXONOMY = {

    "routing": {
        "ospf": [
            "router ospf",
            "set protocols ospf"
        ],
        "bgp": [
            "router bgp",
            "set protocols bgp"
        ]
    },

    "security": {
        "acl": [
            "access-list",
            "firewall filter"
        ],
        "aaa": [
            "aaa",
            "tacacs",
            "radius",
            "set system login"
        ],
        "ssh": [
            "transport input ssh",
            "set system services ssh"
        ],
        "telnet": [
            "transport input telnet",
            "set system services telnet"
        ]
    },

    "monitoring": {
        "snmp": [
            "snmp-server",
            "set snmp"
        ],
        "syslog": [
            "logging host",
            "set system syslog"
        ],
        "netflow": [
            "flow exporter",
            "ip flow",
            "netflow"
        ]
    },

    "layer2": {
        "vlan": [
            "vlan",
            "set vlans"
        ],
        "stp": [
            "spanning-tree",
            "rstp",
            "mstp"
        ],
        "lldp": [
            "lldp",
            "cdp"
        ]
    },

    "layer2_security": {
        "port_security": [
            "switchport port-security"
        ],
        "dhcp_snooping": [
            "ip dhcp snooping"
        ],
        "arp_inspection": [
            "ip arp inspection"
        ]
    },

    "interface": {
        "physical_interface": [
            "interface",
            "set interfaces"
        ],
        "port_channel": [
            "port-channel",
            "ae"
        ]
    },

    "services": {
        "ntp": [
            "ntp server",
            "set system ntp"
        ],
        "dhcp": [
            "ip dhcp",
            "system services dhcp"
        ],
        "dns": [
            "ip name-server",
            "system name-server"
        ]
    },

    "vpn": {
        "ipsec": [
            "crypto isakmp",
            "set security ipsec"
        ],
        "gre": [
            "interface tunnel",
            "gr-"
        ]
    },

    "qos": {
        "policy_map": [
            "policy-map",
            "class-map",
            "class-of-service"
        ]
    }
}


