from openstack_dashboard.api.neutron import *
import logging

LOG = logging.getLogger(__name__)


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


class VsdSubnet(NeutronAPIDictWrapper):
    def __init__(self, apiresource):
        super(VsdSubnet, self).__init__(apiresource)