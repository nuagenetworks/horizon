# Copyright 2018 NOKIA
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from openstack_dashboard.api.neutron import *  # noqa

LOG = logging.getLogger(__name__)


def router_add_gateway(request, router_id, network_id, enable_snat=None):
    body = {'network_id': network_id}
    if enable_snat is not None:
        body['enable_snat'] = enable_snat
    neutronclient(request).add_gateway_router(router_id, body)


def vsd_organisation_list(request, **params):
    LOG.debug("vsd_organisation_list(): params=%s", params)
    vsd_organisations = neutronclient(request).list(
        'vsd_organisations', '/vsd-organisations',
        True, **params).get('vsd_organisations')
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
        '/vsd-subnets/{}'.format(vsd_subnet_id), params=params) \
        .get('vsd_subnet')
    return VsdSubnet(vsd_subnet)


def nuage_gateway_list(request, **params):
    LOG.debug("nuage_gateway_list(): params=%s", params)
    gws = neutronclient(request).list('nuage_gateways', '/nuage-gateways',
                                      True, **params)['nuage_gateways']
    return [NuageGateway(gw) for gw in gws]


def nuage_gateway_get(request, gateway_id, **params):
    LOG.debug("nuage_gateway_get(): id=%s params=%s", gateway_id, params)
    gw = neutronclient(request).get('/nuage-gateways/{}'.format(gateway_id),
                                    params=params).get('nuage_gateway')
    return NuageGateway(gw)


def nuage_gateway_port_list(request, gateway_id=None, **params):
    LOG.debug("nuage_gateway_port_list(): gateway_id=%s params=%s",
              gateway_id, params)
    gw_ports = neutronclient(request).list('nuage_gateway_ports',
                                           '/nuage-gateway-ports', True,
                                           **params)['nuage_gateway_ports']
    return [NuageGatewayPort(gw_port) for gw_port in gw_ports]


def nuage_gateway_port_get(request, gw_port_id, **params):
    LOG.debug("show_nuage_gateway_port(): id=%s params=%s", gw_port_id, params)
    gw_port = neutronclient(request).get(
        '/nuage-gateway-ports/{}'.format(gw_port_id),
        params=params).get('nuage_gateway_port')
    return NuageGatewayPort(gw_port)


def nuage_gateway_vlan_create(request, **kwargs):
    LOG.debug("nuage_gateway_vlan_create(): kwargs=%s", kwargs)
    vlan_body = {'nuage_gateway_vlan': {
        'gatewayport': kwargs['gw_port_id'],
        'value': kwargs['vlan']
    }}
    gw_vlan = neutronclient(request).post(
        '/nuage-gateway-vlans/', vlan_body).get('nuage_gateway_vlan')
    return NuageGatewayVlan(gw_vlan)


def nuage_gateway_vlan_assign(request, gw_vlan_id, **kwargs):
    LOG.debug("nuage_gateway_vlan_assign(): id=%s kwargs=%s",
              gw_vlan_id, kwargs)
    vlan_body = {
        'action': 'assign',
        'tenant': kwargs['tenant_id']
    }
    gw_vlan = neutronclient(request).put(
        '/nuage-gateway-vlans/{}'.format(gw_vlan_id), **vlan_body)
    return NuageGatewayVlan(gw_vlan)


def nuage_gateway_vlan_unassign(request, gw_vlan_id, **kwargs):
    LOG.debug("nuage_gateway_vlan_unassign(): id=%s kwargs=%s",
              gw_vlan_id, kwargs)
    vlan_body = {
        'action': 'unassign',
        'tenant': kwargs['tenant_id']
    }
    gw_vlan = neutronclient(request).put(
        '/nuage-gateway-vlans/{}'.format(gw_vlan_id), **vlan_body)
    return NuageGatewayVlan(gw_vlan)


def nuage_gateway_vlan_list(request, gw_port_id=None, **params):
    LOG.debug("nuage_gateway_vlan_list(): gw_port_id=%s params=%s",
              gw_port_id, params)
    gw_vlans = neutronclient(request).list(
        'nuage_gateway_vlans', '/nuage-gateway-vlans/', True,
        gatewayport=gw_port_id,
        **params).get('nuage_gateway_vlans')
    return [NuageGatewayVlan(gw_vlan) for gw_vlan in gw_vlans]


def nuage_gateway_vlan_get(request, gw_vlan_id, **params):
    LOG.debug("nuage_gateway_vlan_get(): id=%s params=%s",
              gw_vlan_id, params)
    gw_vlan = neutronclient(request).get(
        '/nuage-gateway-vlans/{}'.format(gw_vlan_id),
        **params).get('nuage_gateway_vlan')
    return NuageGatewayVlan(gw_vlan)


def nuage_gateway_vlan_delete(request, gw_vlan_id):
    LOG.debug("nuage_gateway_vlan_delete(): gw_vlan_id=%s",
              gw_vlan_id)
    neutronclient(request).delete('/nuage-gateway-vlans/{}'.format(gw_vlan_id))


def nuage_gateway_vport_get(request, gw_vport_id, **params):
    LOG.debug("nuage_gateway_vport_get(): id=%s params=%s",
              gw_vport_id, params)
    gw_vport = neutronclient(request).get(
        '/nuage-gateway-vports/{}'.format(gw_vport_id),
        params=params).get('nuage_gateway_vport')
    return NuageGatewayVport(gw_vport)


def nuage_gateway_vport_create(request, **kwargs):
    LOG.debug("nuage_gateway_vport_create(): kwargs=%s", kwargs)
    vport_body = {
        'gatewayvlan': kwargs['gw_vlan_id'],
        'tenant': kwargs['tenant_id']
    }
    if kwargs.get('subnet_id'):
        vport_body['subnet'] = kwargs['subnet_id']
    if kwargs.get('port_id'):
        vport_body['port'] = kwargs['port_id']
    gw_vport = neutronclient(request).post(
        '/nuage-gateway-vports', vport_body).get('nuage_gateway_vport')
    return NuageGatewayVport(gw_vport)


def nuage_gateway_vport_delete(request, gw_vport_id):
    LOG.debug("nuage_gateway_vport_delete(): id=%s", gw_vport_id)
    return neutronclient(request).delete(
        '/nuage-gateway-vports/{}'.format(gw_vport_id))


def nuage_security_group_create(request, params):
    LOG.debug("nuage_security_group_create(): name=%s", params['name'])
    body = {
        'security_group':
            params
    }
    sg = neutronclient(request).create_security_group(
        body=body).get('security_group')
    return NuageSecurityGroup(sg)


def nuage_security_group_update(request, sg_id, params):
    LOG.debug("nuage_security_group_update(): name=%s", params['name'])
    body = {
        'security_group':
            params
    }
    sg = neutronclient(request).update_security_group(
        sg_id, body=body).get('security_group')
    return NuageSecurityGroup(sg)


class VsdOrganisation(NeutronAPIDictWrapper):
    pass


class VsdDomain(NeutronAPIDictWrapper):
    pass


class VsdZone(NeutronAPIDictWrapper):
    pass


class VsdSubnet(NeutronAPIDictWrapper):
    pass


class NuageGateway(NeutronAPIDictWrapper):
    def __init__(self, apiresource):
        if 'description' not in apiresource.keys():
            apiresource['description'] = '-'
        super(NuageGateway, self).__init__(apiresource)


class NuageGatewayPort(NeutronAPIDictWrapper):
    def __init__(self, apiresource):
        if 'description' not in apiresource.keys():
            apiresource['description'] = '-'
        super(NuageGatewayPort, self).__init__(apiresource)


class NuageGatewayVlan(NeutronAPIDictWrapper):
    pass


class NuageGatewayVport(NeutronAPIDictWrapper):
    pass


class NuageSecurityGroup(NeutronAPIDictWrapper):
    pass
