#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <inttypes.h>

#define ALUFF_FLOW_MASK 0xFFFFFFFFFFFFFFFF
#define ALUFF_FLOW_MIRROR               (1ULL <<  0)
#define ALUFF_FLOW_PENDING_INSTALL      (1ULL <<  1)
#define ALUFF_FLOW_DHCP_OPTIONS         (1ULL <<  2)
#define ALUFF_FLOW_EVPN_FLOOD           (1ULL <<  3)
#define ALUFF_FLOW_DEFAULT              (1ULL <<  4)     /* VRF/EVPN default route */
#define ALUFF_FLOW_ECMP_ROUTE           (1ULL <<  5)
    /* Controller does not use the above */
#define ALUFF_FLOW_SPAT_NAT             (1ULL <<  7)
#define ALUFF_FLOW_ACL_FIP              (1ULL <<  8)
#define ALUFF_FLOW_SPAT                 (1ULL <<  9)       /* SPAT route */
#define ALUFF_FLOW_EXIT_DOMAIN          (1ULL << 10)
#define ALUFF_FLOW_VIF_MAPPING          (1ULL << 11)  /* NAT_T/IPSEC mappings */
#define ALUFF_FLOW_LEARNT_ARP           (1ULL << 12)
#define ALUFF_FLOW_VIP_LIST             (1ULL << 13)
#define ALUFF_FLOW_ACL_REDIRECT         (1ULL << 14)
#define ALUFF_FLOW_MCAST_RX_ENABLED     (1ULL << 15) /* enable mcast on port */
#define ALUFF_FLOW_VRF                  (1ULL << 16)       /* VRF route */
#define ALUFF_FLOW_EVPN                 (1ULL << 17)       /* EVPN route */
#define ALUFF_FLOW_LOCAL                (1ULL << 18)       /* Local route */
#define ALUFF_FLOW_REMOTE               (1ULL << 19)       /* Remote route */
#define ALUFF_FLOW_FLOOD                (1ULL << 20)       /* Flood route */
#define ALUFF_FLOW_QOS                  (1ULL << 21)       /* Qos config*/
#define ALUFF_FLOW_ACL_PRE              (1ULL << 22)
#define ALUFF_FLOW_ACL_POST             (1ULL << 23)
#define ALUFF_FLOW_STATS_COLLECTOR_INFO (1ULL << 24)
#define ALUFF_FLOW_STATIC               (1ULL << 25)
#define ALUFF_FLOW_NAT                  (1ULL << 26)      /* VRF redirect route */
#define ALUFF_FLOW_LEARNT_MAC           (1ULL << 27)
#define ALUFF_FLOW_ENABLE_LEARNING      (1ULL << 28)
#define ALUFF_FLOW_EVPN_MEMBERSHIP_ONLY (1ULL << 29)
#define ALUFF_FLOW_EVPN_REDIRECT        (1ULL << 30)
#define ALUFF_FLOW_EVPN_ARP_ROUTE       (1ULL << 31)
#define ALUFF_FLOW_ACL_FW_INGRESS       (1ULL << 32)
#define ALUFF_FLOW_ACL_FW_EGRESS        (1ULL << 33)
#define ALUFF_FLOW_HUB_ROUTABLE         (1ULL << 34) /* Revit this while revisting the NAT routes */
#define ALUFF_FLOW_BIDIR                (1ULL << 35) /* BIDIR Route */
#define ALUFF_FLOW_XPMG_NBR_MOD         (1ULL << 36)
#define ALUFF_FLOW_V6                   (1ULL << 37) /* Used in conjunction with other flags to indicate V6 flow */

#define ALUFF_FLOW_DHCP_DECLINE_ARP     (1ULL << 63)
/* Controller does not use the below */
#define ALUFF_FLOW_INDIRECT_ROUTE       (1ULL << 62)

void
vrs_aluff_flags_to_string(uint64_t flags, char *s)
{
    if (NULL == s) {
        return;
    }

    sprintf(s, "%s", "Flags_str: ");

    if (flags & ALUFF_FLOW_MIRROR) {
        strcat(s, "ALUFF_FLOW_MIRROR, ");
    }
    if (flags & ALUFF_FLOW_PENDING_INSTALL) {
        strcat(s, "ALUFF_FLOW_PENDING_INSTALL, ");
    }
    if (flags & ALUFF_FLOW_DHCP_OPTIONS) {
        strcat(s, "ALUFF_FLOW_DHCP_OPTIONS, ");
    }
    if (flags & ALUFF_FLOW_EVPN_FLOOD) {
        strcat(s, "ALUFF_FLOW_EVPN_FLOOD, ");
    }
    if (flags & ALUFF_FLOW_DEFAULT) {
        strcat(s, "ALUFF_FLOW_DEFAULT, ");
    }
    if (flags & ALUFF_FLOW_ECMP_ROUTE) {
        strcat(s, "ALUFF_FLOW_ECMP_ROUTE, ");
    }
    if (flags & ALUFF_FLOW_SPAT_NAT) {
        strcat(s, "ALUFF_FLOW_SPAT_NAT, ");
    }
    if (flags & ALUFF_FLOW_ACL_FIP) {
        strcat(s, "ALUFF_FLOW_ACL_FIP, ");
    }
    if (flags & ALUFF_FLOW_SPAT) {
        strcat(s, "ALUFF_FLOW_SPAT, ");
    }
    if (flags & ALUFF_FLOW_EXIT_DOMAIN) {
        strcat(s, "ALUFF_FLOW_EXIT_DOMAIN, ");
    }
    if (flags & ALUFF_FLOW_VIF_MAPPING) {
        strcat(s, "ALUFF_FLOW_VIF_MAPPING, ");
    }
    if (flags & ALUFF_FLOW_LEARNT_ARP) {
        strcat(s, "ALUFF_FLOW_LEARNT_ARP, ");
    }
    if (flags & ALUFF_FLOW_VIP_LIST) {
        strcat(s, "ALUFF_FLOW_VIP_LIST, ");
    }
    if (flags & ALUFF_FLOW_ACL_REDIRECT) {
        strcat(s, "ALUFF_FLOW_ACL_REDIRECT, ");
    }
    if (flags & ALUFF_FLOW_MCAST_RX_ENABLED) {
        strcat(s, "ALUFF_FLOW_MCAST_RX_ENABLED, ");
    }
    if (flags & ALUFF_FLOW_VRF) {
        strcat(s, "ALUFF_FLOW_VRF, ");
    }
    if (flags & ALUFF_FLOW_EVPN) {
        strcat(s, "ALUFF_FLOW_EVPN, ");
    }
    if (flags & ALUFF_FLOW_LOCAL) {
        strcat(s, "ALUFF_FLOW_LOCAL, ");
    }
    if (flags & ALUFF_FLOW_REMOTE) {
        strcat(s, "ALUFF_FLOW_REMOTE, ");
    }
    if (flags & ALUFF_FLOW_FLOOD) {
        strcat(s, "ALUFF_FLOW_FLOOD, ");
    }
    if (flags & ALUFF_FLOW_QOS) {
        strcat(s, "ALUFF_FLOW_QOS, ");
    }
    if (flags & ALUFF_FLOW_ACL_PRE) {
        strcat(s, "ALUFF_FLOW_ACL_PRE, ");
    }
    if (flags & ALUFF_FLOW_ACL_POST) {
        strcat(s, "ALUFF_FLOW_ACL_POST, ");
    }
    if (flags & ALUFF_FLOW_STATS_COLLECTOR_INFO) {
        strcat(s, "ALUFF_FLOW_STATS_COLLECTOR_INFO, ");
    }
    if (flags & ALUFF_FLOW_STATIC) {
        strcat(s, "ALUFF_FLOW_STATIC, ");
    }
    if (flags & ALUFF_FLOW_NAT) {
        strcat(s, "ALUFF_FLOW_NAT, ");
    }
    if (flags & ALUFF_FLOW_LEARNT_MAC) {
        strcat(s, "ALUFF_FLOW_LEARNT_MAC, ");
    }
    if (flags & ALUFF_FLOW_ENABLE_LEARNING) {
        strcat(s, "ALUFF_FLOW_ENABLE_LEARNING, ");
    }
    if (flags & ALUFF_FLOW_EVPN_MEMBERSHIP_ONLY) {
        strcat(s, "ALUFF_FLOW_EVPN_MEMBERSHIP_ONLY, ");
    }
    if (flags & ALUFF_FLOW_EVPN_REDIRECT) {
        strcat(s, "ALUFF_FLOW_EVPN_REDIRECT, ");
    }
    if (flags & ALUFF_FLOW_EVPN_ARP_ROUTE) {
        strcat(s, "ALUFF_FLOW_EVPN_ARP_ROUTE, ");
    }
    if (flags & ALUFF_FLOW_ACL_FW_INGRESS) {
        strcat(s, "ALUFF_FLOW_ACL_FW_INGRESS, ");
    }
    if (flags & ALUFF_FLOW_ACL_FW_EGRESS) {
        strcat(s, "ALUFF_FLOW_ACL_FW_EGRESS, ");
    }
    if (flags & ALUFF_FLOW_HUB_ROUTABLE) {
        strcat(s, "ALUFF_FLOW_HUB_ROUTABLE, ");
    }
    if (flags & ALUFF_FLOW_BIDIR) {
        strcat(s, "ALUFF_FLOW_BIDIR, ");
    }
    if (flags & ALUFF_FLOW_XPMG_NBR_MOD) {
        strcat(s, "ALUFF_FLOW_XPMG_NBR_MOD, ");
    }
    if (flags & ALUFF_FLOW_V6) {
        strcat(s, "ALUFF_FLOW_V6, ");
    }
    if (flags & ALUFF_FLOW_DHCP_DECLINE_ARP) {
        strcat(s, "ALUFF_FLOW_DHCP_DECLINE_ARP, ");
    }
    if (flags & ALUFF_FLOW_INDIRECT_ROUTE) {
        strcat(s, "ALUFF_FLOW_INDIRECT_ROUTE, ");
    }

    strcat(s, "\n");
}

void main(int argc, char **argv)
{
    char *str = argv[1];
    char s[500];
    uint64_t flags = strtoll(str, NULL, 16);
    printf("Flags 0x%"PRIx64, flags);
    vrs_aluff_flags_to_string(flags, s);
    printf("\n%s", s);
}
