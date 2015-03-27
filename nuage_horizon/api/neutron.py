from openstack_dashboard.api.neutron import *
import logging

LOG = logging.getLogger(__name__)


def vsd_organisation_list(request, **params):
    LOG.debug("vsd_organisation_list(): params=%s", params)
    vsd_organisations = neutronclient(request)\
        .list('vsd_organisations', '/vsd-organisations', True, **params)\
        .get('vsd_organisations')
    return [VsdOrganisation(org) for org in vsd_organisations]


def vsd_domain_list(request, **params):
    LOG.debug("vsd_domain_list(): params=%s", params)
    vsd_domains = neutronclient(request).list(
        'vsd_domains', '/vsd-domains', True, **params).get('vsd_domains')
    return [VsdDomain(domain) for domain in vsd_domains]


def vsd_zone_list(request, **params):
    LOG.debug("vsd_zone_list(): params=%s", params)
    vsd_zones = neutronclient(request).list(
        'vsd_zones', '/vsd-zones', True, **params).get('vsd_zones')
    return [VsdZone(zone) for zone in vsd_zones]


def vsd_subnet_list(request, **params):
    LOG.debug("vsd_subnet_list(): params=%s", params)
    vsd_subnets = neutronclient(request).list(
        'vsd_subnets', '/vsd-subnets', True, **params).get('vsd_subnets')
    return [VsdSubnet(subnet) for subnet in vsd_subnets]


def vsd_subnet_get(request, vsd_subnet_id, **params):
    LOG.debug("vsd_subnet_get(): id=%s, params=%s", vsd_subnet_id, params)
    vsd_subnet = neutronclient(request).get(
        '/vsd-subnets/%s' % str(vsd_subnet_id), params=params)\
        .get('vsd_subnet')
    return VsdSubnet(vsd_subnet)


class VsdOrganisation(NeutronAPIDictWrapper):
    def __init__(self, apiresource):
        super(VsdOrganisation, self).__init__(apiresource)


class VsdDomain(NeutronAPIDictWrapper):
    def __init__(self, apiresource):
        super(VsdDomain, self).__init__(apiresource)


class VsdZone(NeutronAPIDictWrapper):
    def __init__(self, apiresource):
        super(VsdZone, self).__init__(apiresource)


class VsdSubnet(NeutronAPIDictWrapper):
    def __init__(self, apiresource):
        super(VsdSubnet, self).__init__(apiresource)
