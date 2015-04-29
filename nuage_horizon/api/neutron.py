from openstack_dashboard.api.neutron import *
from neutronclient.common.exceptions import InternalServerError
import logging

LOG = logging.getLogger(__name__)
no_attr_changes_msg = ("Nuage API: Error in REST call to VSD: There are no "
                       "attribute changes to modify the entity.")


def catch_no_attr_changes(fn):
    def wrapped(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except InternalServerError as e:
            if no_attr_changes_msg == e.message:
                return
            raise e

    return wrapped


def vsd_organisation_list(request, **params):
    LOG.debug("vsd_organisation_list(): params=%s", params)
    vsd_organisations = neutronclient(request) \
        .list('vsd_organisations', '/vsd-organisations', True, **params) \
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
        '/vsd-subnets/%s' % str(vsd_subnet_id), params=params) \
        .get('vsd_subnet')
    return VsdSubnet(vsd_subnet)


def nuage_gateway_list(request, **params):
    LOG.debug("nuage_gateway_list(): params=%s", params)
    gws = neutronclient(request).list_nuage_gateways(**params) \
        .get('nuage_gateways')
    return [NuageGateway(gw) for gw in gws]


def nuage_gateway_get(request, gateway_id, **params):
    LOG.debug("nuage_gateway_get(): id=%s params=%s", gateway_id, params)
    gw = neutronclient(request).show_nuage_gateway(gateway_id, **params) \
        .get('nuage_gateway')
    return NuageGateway(gw)


def nuage_gateway_port_list(request, gateway_id=None, **params):
    LOG.debug("nuage_gateway_port_list(): gateway_id=%s params=%s",
              gateway_id, params)
    gw_ports = neutronclient(request).list_nuage_gateway_ports(
        gateway=gateway_id).get('nuage_gateway_ports')
    return [NuageGatewayPort(gw_port) for gw_port in gw_ports]


def nuage_gateway_port_get(request, gw_port_id, **params):
    LOG.debug("show_nuage_gateway_port(): id=%s params=%s", gw_port_id, params)
    gw_port = neutronclient(request) \
        .show_nuage_gateway_port(gw_port_id, **params).get('nuage_gateway_port')
    return NuageGatewayPort(gw_port)


def nuage_gateway_vlan_create(request, **kwargs):
    LOG.debug("nuage_gateway_vlan_create(): kwargs=%s", kwargs)
    vlan_body = {'nuage_gateway_vlan': {
        'gatewayport': kwargs['gw_port_id'],
        'value': kwargs['vlan']
    }}
    gw_vlan = neutronclient(request).create_nuage_gateway_vlan(vlan_body) \
        .get('nuage_gateway_vlan')
    return NuageGatewayVlan(gw_vlan)


def nuage_gateway_vlan_assign(request, gw_vlan_id, **kwargs):
    LOG.debug("nuage_gateway_vlan_assign(): id=%s kwargs=%s",
              gw_vlan_id, kwargs)
    vlan_body = {'nuage_gateway_vlan': {
        'action': 'assign',
        'tenant': kwargs['tenant_id']
    }}
    gw_vlan = neutronclient(request).update_nuage_gateway_vlan(
        gw_vlan_id, body=vlan_body)
    return NuageGatewayVlan(gw_vlan)


def nuage_gateway_vlan_unassign(request, gw_vlan_id, **kwargs):
    LOG.debug("nuage_gateway_vlan_unassign(): id=%s kwargs=%s",
              gw_vlan_id, kwargs)
    vlan_body = {'nuage_gateway_vlan': {
        'action': 'unassign',
        'tenant': kwargs['tenant_id']
    }}
    gw_vlan = neutronclient(request).update_nuage_gateway_vlan(
        gw_vlan_id, body=vlan_body)
    return NuageGatewayVlan(gw_vlan)


def nuage_gateway_vlan_list(request, gw_port_id=None, **params):
    LOG.debug("nuage_gateway_vlan_list(): gw_port_id=%s params=%s",
              gw_port_id, params)
    gw_vlans = neutronclient(request).list_nuage_gateway_vlans(
        gatewayport=gw_port_id, **params).get('nuage_gateway_vlans')
    return [NuageGatewayVlan(gw_vlan) for gw_vlan in gw_vlans]


def nuage_gateway_vlan_get(request, gw_vlan_id, **params):
    LOG.debug("nuage_gateway_vlan_get(): id=%s params=%s",
              gw_vlan_id, params)
    gw_vlan = neutronclient(request).show_nuage_gateway_vlan(
        gw_vlan_id, **params).get('nuage_gateway_vlan')
    return NuageGatewayVlan(gw_vlan)


def nuage_gateway_vlan_delete(request, gw_vlan_id):
    LOG.debug("nuage_gateway_vlan_delete(): gw_vlan_id=%s",
              gw_vlan_id)
    neutronclient(request).delete_nuage_gateway_vlan(gw_vlan_id)


def nuage_gateway_vport_get(request, gw_vport_id, **params):
    LOG.debug("nuage_gateway_vport_get(): id=%s params=%s",
              gw_vport_id, params)
    gw_vport = neutronclient(request).show_nuage_gateway_vport(
        gw_vport_id, **params).get('nuage_gateway_vport')
    return NuageGatewayVport(gw_vport)


def nuage_gateway_vport_create(request, **kwargs):
    LOG.debug("nuage_gateway_vport_create(): kwargs=%s", kwargs)
    vport_body = {'nuage_gateway_vport': {
        'gatewayvlan': kwargs['gw_vlan_id'],
        'tenant': kwargs['tenant_id']
    }}
    if kwargs.get('subnet_id'):
        vport_body['nuage_gateway_vport']['subnet'] = kwargs['subnet_id']
    if kwargs.get('port_id'):
        vport_body['nuage_gateway_vport']['port'] = kwargs['port_id']
    gw_vport = neutronclient(request).create_nuage_gateway_vport(vport_body) \
        .get('nuage_gateway_vport')
    return NuageGatewayVport(gw_vport)


def nuage_gateway_vport_delete(request, gw_vport_id):
    LOG.debug("nuage_gateway_vport_delete(): id=%s", gw_vport_id)
    return neutronclient(request).delete_nuage_gateway_vport(gw_vport_id)


def application_domain_list(request, **params):
    LOG.debug("application_domain_list(): params=%s", params)
    app_domains = neutronclient(request).list_application_domains(
        **params).get('application_domains')
    return [NuageApplicationDomain(app_domain) for app_domain in app_domains]


def application_domain_get(request, id, **params):
    LOG.debug("application_domain_get(): id=%s params=%s", id, params)
    app_domain = neutronclient(request).show_application_domain(
        id, **params).get('application_domain')
    return NuageApplicationDomain(app_domain)


def application_domain_create(request, **kwargs):
    LOG.debug("application_domain_create(): kwargs=%s", kwargs)
    data = {'application_domain': {}}
    data['application_domain'].update(kwargs)
    app_domain = neutronclient(request).create_application_domain(
        body=data).get('application_domain')
    return NuageApplicationDomain(app_domain)


@catch_no_attr_changes
def application_domain_update(request, id, **kwargs):
    LOG.debug("application_domain_update(): id=%s kwargs=%s", id, kwargs)
    data = {'application_domain': {}}
    data['application_domain'].update(kwargs)
    app_domain = neutronclient(request).update_application_domain(
        id, body=data).get('application_domain')
    return NuageApplicationDomain(app_domain)


def application_domain_delete(request, id):
    LOG.debug("application_domain_delete(): id=%s", id)
    neutronclient(request).delete_application_domain(id)


def application_service_list(request, **params):
    LOG.debug("application_service_list(): params=%s", params)
    app_services = neutronclient(request).list_services(
        **params).get('services')
    return [NuageApplicationService(app_service)
            for app_service in app_services]


def application_service_get(request, id, **params):
    LOG.debug("application_service_get(): params=%s", params)
    app_service = neutronclient(request).show_service(id,
                                                      **params).get('service')
    return NuageApplicationService(app_service)


def application_service_create(request, **kwargs):
    LOG.debug("application_service_create(): kwargs=%s", kwargs)
    data = {'service': {}}
    data['service'].update(kwargs)
    service = neutronclient(request).create_service(body=data).get('service')
    return NuageApplicationService(service)


@catch_no_attr_changes
def application_service_update(request, id, **kwargs):
    LOG.debug("application_service_update(): id=%s kwargs=%s", id, kwargs)
    data = {'service': {}}
    data['service'].update(kwargs)
    app_service = neutronclient(request).update_service(
        id, body=data).get('service')
    return NuageApplicationService(app_service)


def application_service_delete(request, id):
    LOG.debug("application_service_delete(): id=%s", id)
    neutronclient(request).delete_service(id)


def application_list(request, **params):
    LOG.debug("application_list(): params=%s", params)
    apps = neutronclient(request).list_applications(
        **params).get('applications')
    return [NuageApplication(app) for app in apps]


def application_get(request, application_id, **params):
    LOG.debug("application_get(): id=%s, params=%s", application_id, params)
    app = neutronclient(request).show_application(
        application_id, **params).get('application')
    return NuageApplication(app)


def application_create(request, **kwargs):
    LOG.debug("application_create(): kwargs=%s", kwargs)
    data = {'application': {}}
    data['application'].update(kwargs)
    app = neutronclient(request).create_application(
        body=data).get('application')
    return NuageApplication(app)


@catch_no_attr_changes
def application_update(request, id, **kwargs):
    LOG.debug("application_update(): id=%s kwargs=%s", id, kwargs)
    data = {'application': {}}
    data['application'].update(kwargs)
    app = neutronclient(request).update_application(
        id, body=data).get('application')
    return NuageApplication(app)


def application_delete(request, application_id):
    LOG.debug("application_delete(): id=%s", application_id)
    neutronclient(request).delete_application(application_id)


def appdport_list(request, **params):
    LOG.debug("appdport_list(): params=%s", params)
    appdports = neutronclient(request).list_appdports(
        **params).get('appdports')
    return [NuageAppdport(appdport) for appdport in appdports]


def appdport_create(request, **kwargs):
    LOG.debug("appdport_create(): kwargs=%s", kwargs)
    appdport_body = {'appdport': {
        'name': kwargs['name'],
        'tenant_id': kwargs['tenant_id'],
        'tier_id': kwargs['tier_id']
    }}
    appdport = neutronclient(request).create_appdport(appdport_body) \
        .get('appdport')
    return NuageAppdport(appdport)


def appdport_delete(request, id):
    LOG.debug("\n\n\nappdport_delete(): id=%s", id)
    neutronclient(request).delete_appdport(id)


def tier_list(request, **params):
    LOG.debug("tier_list(): params=%s", params)
    tiers = neutronclient(request).list_tiers(
        **params).get('tiers')
    return [NuageTier(tier) for tier in tiers]


def flow_list(request, **params):
    LOG.debug("flow_list(): params=%s", params)
    flows = neutronclient(request).list_flows(**params).get('flows')
    return [NuageFlow(flow) for flow in flows]


def flow_get(request, flow_id, **params):
    LOG.debug("flow_get(): params=%s", params)
    flow = neutronclient(request).show_flow(flow_id, **params).get('flow')
    return NuageFlow(flow)


def flow_create(request, **kwargs):
    LOG.debug("flow_create(): kwargs=%s", kwargs)
    data = {'flow': {}}
    data['flow'].update(kwargs)
    app = neutronclient(request).create_flow(body=data).get('flow')
    return NuageFlow(app)


@catch_no_attr_changes
def flow_update(request, id, **kwargs):
    LOG.debug("flow_update(): id=%s kwargs=%s", id, kwargs)
    data = {'flow': {}}
    data['flow'].update(kwargs)
    flow = neutronclient(request).update_flow(id, body=data).get('flow')
    return NuageFlow(flow)


def flow_delete(request, flow_id):
    LOG.debug("flow_delete(): id=%s", flow_id)
    neutronclient(request).delete_flow(flow_id)


def tier_get(request, tier_id, **params):
    LOG.debug("tier_get(): id=%s, params=%s", tier_id, params)
    tier = neutronclient(request).show_tier(tier_id, **params).get('tier')
    return NuageTier(tier)


def tier_create(request, **kwargs):
    LOG.debug("tier_create(): kwargs=%s", kwargs)
    data = {'tier': {}}
    data['tier'].update(kwargs)
    app = neutronclient(request).create_tier(body=data).get('tier')
    return app


@catch_no_attr_changes
def tier_update(request, id, **kwargs):
    LOG.debug("tier_update(): id=%s kwargs=%s", id, kwargs)
    data = {'tier': {}}
    data['tier'].update(kwargs)
    tier = neutronclient(request).update_tier(id, body=data).get('tier')
    return NuageTier(tier)


def tier_delete(request, tier_id):
    LOG.debug("tier_delete(): id=%s", tier_id)
    neutronclient(request).delete_tier(tier_id)


class NuageApplication(NeutronAPIDictWrapper):
    pass


class NuageApplicationDomain(NeutronAPIDictWrapper):
    pass


class NuageApplicationService(NeutronAPIDictWrapper):
    pass


class NuageAppdport(NeutronAPIDictWrapper):
    pass


class NuageTier(NeutronAPIDictWrapper):
    pass


class NuageFlow(NeutronAPIDictWrapper):
    pass


class VsdOrganisation(NeutronAPIDictWrapper):
    pass


class VsdDomain(NeutronAPIDictWrapper):
    pass


class VsdZone(NeutronAPIDictWrapper):
    pass


class VsdSubnet(NeutronAPIDictWrapper):
    pass


class NuageGateway(NeutronAPIDictWrapper):
    pass


class NuageGatewayPort(NeutronAPIDictWrapper):
    pass


class NuageGatewayVlan(NeutronAPIDictWrapper):
    pass


class NuageGatewayVport(NeutronAPIDictWrapper):
    pass
