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


def nuage_gateway_list(request, **params):
    LOG.debug("nuage_gateway_list(): params=%s", params)
    gws = neutronclient(request).list_nuage_gateways(**params)\
        .get('nuage_gateways')
    return [NuageGateway(gw) for gw in gws]


def nuage_gateway_get(request, gateway_id, **params):
    LOG.debug("nuage_gateway_get(): id=%s params=%s", gateway_id, params)
    gw = neutronclient(request).show_nuage_gateway(gateway_id, **params)\
        .get('nuage_gateway')
    return NuageGateway(gw)


def nuage_gateway_port_list(request, gateway_id=None, **params):
    LOG.debug("nuage_gateway_port_list(): gateway_id=%s params=%s",
              gateway_id, params)
    gw_ports = neutronclient(request).list_nuage_gateway_ports(
        gateway_id, **params).get('nuage_gateway_ports')
    return [NuageGatewayPort(gw_port) for gw_port in gw_ports]


def nuage_gateway_port_get(request, gw_port_id, **params):
    LOG.debug("show_nuage_gateway_port(): id=%s params=%s", gw_port_id, params)
    gw_port = neutronclient(request)\
        .show_nuage_gateway_port(gw_port_id, **params).get('nuage_gateway_port')
    return NuageGatewayPort(gw_port)


def nuage_gateway_port_vlan_create(request, **kwargs):
    LOG.debug("nuage_gateway_port_vlan_create(): kwargs=%s", kwargs)
    vlan_body = {'nuage_gateway_port_vlan': {
        'gatewayport': kwargs['gw_port_id'],
        'value': kwargs['vlan']
    }}
    gw_vlan = neutronclient(request).create_nuage_gateway_port_vlan(vlan_body)\
        .get('nuage_gateway_port_vlan')
    return NuageGatewayPortVlan(gw_vlan)


def nuage_gateway_port_vlan_assign(request, gw_port_vlan_id, **kwargs):
    LOG.debug("nuage_gateway_port_vlan_assign(): id=%s kwargs=%s",
              gw_port_vlan_id, kwargs)
    vlan_body = {'nuage_gateway_port_vlan': {
        'action': 'assign',
        'tenant': kwargs['tenant_id']
    }}
    gw_vlan = neutronclient(request).assign_nuage_gateway_port_vlan(
        gw_port_vlan_id, body=vlan_body)
    return NuageGatewayPortVlan(gw_vlan)


def nuage_gateway_port_vlan_unassign(request, gw_port_vlan_id, **kwargs):
    LOG.debug("nuage_gateway_port_vlan_unassign(): id=%s kwargs=%s",
              gw_port_vlan_id, kwargs)
    vlan_body = {'nuage_gateway_port_vlan': {
        'action': 'unassign',
        'tenant': kwargs['tenant_id']
    }}
    gw_vlan = neutronclient(request).unassign_nuage_gateway_port_vlan(
        gw_port_vlan_id, body=vlan_body)
    return NuageGatewayPortVlan(gw_vlan)


def nuage_gateway_port_vlan_list(request, gw_port_id=None, **params):
    LOG.debug("nuage_gateway_port_vlan_list(): gw_port_id=%s params=%s",
              gw_port_id, params)
    gw_port_vlans = neutronclient(request).list_nuage_gateway_port_vlans(
        gw_port_id, **params).get('nuage_gateway_port_vlans')
    return [NuageGatewayPortVlan(gw_port_vlan) for gw_port_vlan in gw_port_vlans]


def nuage_gateway_port_vlan_get(request, gw_port_vlan_id, **params):
    LOG.debug("nuage_gateway_port_vlan_get(): id=%s params=%s",
              gw_port_vlan_id, params)
    gw_port_vlan = neutronclient(request).show_nuage_gateway_port_vlan(
        gw_port_vlan_id, **params).get('nuage_gateway_port_vlan')
    return NuageGatewayPortVlan(gw_port_vlan)


def nuage_gateway_port_vlan_delete(request, gw_port_vlan_id):
    LOG.debug("nuage_gateway_port_vlan_delete(): gw_port_vlan_id=%s",
              gw_port_vlan_id)
    neutronclient(request).delete_nuage_gateway_port_vlan(gw_port_vlan_id)


def nuage_gateway_vport_get(request, gw_vport_id, **params):
    LOG.debug("nuage_gateway_vport_get(): id=%s params=%s",
              gw_vport_id, params)
    gw_vport = neutronclient(request).show_nuage_gateway_vport(
        gw_vport_id, **params).get('nuage_gateway_vport')
    return NuageGatewayVport(gw_vport)


def nuage_gateway_vport_create(request, **kwargs):
    LOG.debug("nuage_gateway_vport_create(): kwargs=%s", kwargs)
    vport_body = {'nuage_gateway_vport': {
        'gatewayvlan': kwargs['gw_port_vlan_id'],
        'tenant': kwargs['tenant_id']
    }}
    if kwargs.get('subnet_id'):
        vport_body['nuage_gateway_vport']['subnet'] = kwargs['subnet_id']
    if kwargs.get('port_id'):
        vport_body['nuage_gateway_vport']['port'] = kwargs['port_id']
    gw_vport = neutronclient(request).create_nuage_gateway_vport(vport_body)\
        .get('nuage_gateway_vport')
    return NuageGatewayVport(gw_vport)


def nuage_gateway_vport_delete(request, gw_vport_id):
    LOG.debug("nuage_gateway_vport_delete(): id=%s", gw_vport_id)
    return neutronclient(request).delete_nuage_gateway_vport(gw_vport_id)


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


class NuageGateway(NeutronAPIDictWrapper):
    def __init__(self, apiresource):
        super(NuageGateway, self).__init__(apiresource)


class NuageGatewayPort(NeutronAPIDictWrapper):
    def __init__(self, apiresource):
        super(NuageGatewayPort, self).__init__(apiresource)


class NuageGatewayPortVlan(NeutronAPIDictWrapper):
    def __init__(self, apiresource):
        super(NuageGatewayPortVlan, self).__init__(apiresource)


class NuageGatewayVport(NeutronAPIDictWrapper):
    def __init__(self, apiresource):
        super(NuageGatewayVport, self).__init__(apiresource)