"""
Copyright 2018, Oath Inc.
Licensed under the terms of the BSD license. See LICENSE file in project root for terms.
"""

import platform
from typing import List, Union, Dict, Any
import pytest
from yahoo_panoptes_snmp.exceptions import (
    EasySNMPError, EasySNMPUnknownObjectIDError, EasySNMPNoSuchObjectError,
    EasySNMPNoSuchInstanceError, EasySNMPNoSuchNameError
)
from yahoo_panoptes_snmp.easy import (
    snmp_get, snmp_set, snmp_set_multiple, snmp_get_next, snmp_get_bulk,
    snmp_walk
)
from .fixtures import sess_v2_args
from .helpers import snmp_set_via_cli


@pytest.fixture(autouse=True)
def reset_values():
    snmp_set_via_cli('sysLocation.0', 'my original location', 's')
    snmp_set_via_cli('nsCacheTimeout.1.3.6.1.2.1.2.2', '0', 'i')
    yield


def test_snmp_get_regular(sess_v2_args):
    # snmpget -v2c -c public localhost:11161 sysDescr.0
    res = snmp_get('sysDescr.0', **sess_v2_args)

    assert platform.version() in res.value
    assert res.oid == 'sysDescr'
    assert res.oid_index == '0'
    assert res.snmp_type == 'OCTETSTR'


def test_snmp_get_tuple(sess_v2_args):
    # snmpget -v2c -c public localhost:11161 sysDescr.0
    res = snmp_get(('sysDescr', '0'), **sess_v2_args)

    assert platform.version() in res.value
    assert res.oid == 'sysDescr'
    assert res.oid_index == '0'
    assert res.snmp_type == 'OCTETSTR'


def test_snmp_get_fully_qualified(sess_v2_args):
    # snmpget -v2c -c public localhost:11161 .iso.org.dod.internet.mgmt.mib-2.system.sysDescr.0
    res = snmp_get(
        '.iso.org.dod.internet.mgmt.mib-2.system.sysDescr.0', **sess_v2_args
    )

    assert platform.version() in res.value
    assert res.oid == 'sysDescr'
    assert res.oid_index == '0'
    assert res.snmp_type == 'OCTETSTR'


def test_snmp_get_fully_qualified_tuple(sess_v2_args):
    # snmpget -v2c -c public localhost:11161 .iso.org.dod.internet.mgmt.mib-2.system.sysDescr.0
    res = snmp_get(
        ('.iso.org.dod.internet.mgmt.mib-2.system.sysDescr', '0'), **sess_v2_args
    )

    assert platform.version() in res.value
    assert res.oid == 'sysDescr'
    assert res.oid_index == '0'
    assert res.snmp_type == 'OCTETSTR'


def test_snmp_get_numeric(sess_v2_args):
    # snmpget -v2c -c public localhost:11161 .1.3.6.1.2.1.1.1.0
    res = snmp_get('.1.3.6.1.2.1.1.1.0', **sess_v2_args)

    assert platform.version() in res.value
    assert res.oid == 'sysDescr'
    assert res.oid_index == '0'
    assert res.snmp_type == 'OCTETSTR'


def test_snmp_get_numeric_no_leading_dot(sess_v2_args):
    # snmpget -v2c -c public localhost:11161 1.3.6.1.2.1.1.1.0
    res = snmp_get('1.3.6.1.2.1.1.1.0', **sess_v2_args)

    assert platform.version() in res.value
    assert res.oid == 'sysDescr'
    assert res.oid_index == '0'
    assert res.snmp_type == 'OCTETSTR'


def test_snmp_get_numeric_tuple(sess_v2_args):
    # snmpget -v2c -c public localhost:11161 .1.3.6.1.2.1.1.1.0
    res = snmp_get(('.1.3.6.1.2.1.1.1', '0'), **sess_v2_args)

    assert platform.version() in res.value
    assert res.oid == 'sysDescr'
    assert res.oid_index == '0'
    assert res.snmp_type == 'OCTETSTR'


def test_snmp_get_unknown(sess_v2_args):
    # snmpget -v2c -c public localhost:11161 sysDescripto.0
    with pytest.raises(EasySNMPUnknownObjectIDError):
        snmp_get('sysDescripto.0', **sess_v2_args)


def test_snmp_get_invalid_instance(sess_v2_args):
    # Sadly, SNMP v1 doesn't distinguish between an invalid instance and an
    # invalid object ID, instead it excepts with noSuchName
    # snmpget -v2c -c public localhost:11161 sysContact.1
    res = snmp_get('sysContact.1', **sess_v2_args)
    assert res.snmp_type == 'NOSUCHINSTANCE'


def test_snmp_get_invalid_instance_with_abort_enabled(sess_v2_args):
    # Sadly, SNMP v1 doesn't distinguish between an invalid instance and an
    # invalid object ID, so it raises the same exception for both
    with pytest.raises(EasySNMPNoSuchInstanceError):
        snmp_get('sysContact.1', abort_on_nonexistent=True, **sess_v2_args)


def test_snmp_get_invalid_object(sess_v2_args):
    # snmpget -v2c -c public localhost:11161 iso
    if sess_v2_args['version'] == 1:
        with pytest.raises(EasySNMPNoSuchNameError):
            snmp_get('iso', **sess_v2_args)
    else:
        res = snmp_get('iso', **sess_v2_args)
        assert res.snmp_type == 'NOSUCHOBJECT'


def test_snmp_get_invalid_object_with_abort_enabled(sess_v2_args):
    # snmpget -v2c -c public localhost:11161 iso
    if sess_v2_args['version'] == 1:
        with pytest.raises(EasySNMPNoSuchNameError):
            snmp_get('iso', abort_on_nonexistent=True, **sess_v2_args)
    else:
        with pytest.raises(EasySNMPNoSuchObjectError):
            snmp_get('iso', abort_on_nonexistent=True, **sess_v2_args)


def test_snmp_get_next(sess_v2_args):
    # doesn't appear to return on Jammy
    # snmpget -v2c -c public localhost:11161 nsCacheTimeout
    res = snmp_get_next('nsCacheEntry', **sess_v2_args)

    assert res.oid == 'nsCacheTimeout'
    assert res.oid_index == '1.3.6.1.2.1.2.2'
    assert int(res.value) >= 0
    assert res.snmp_type == 'INTEGER'


def test_snmp_get_next_numeric(sess_v2_args):
    # Doesn't appear to work on Jammy
    # snmpget -v2c -c public localhost:11161 .1.3.6.1.4.1.8072.3.2.10
    res = snmp_get_next(('.1.3.6.1.2.1.1.1', '0'), **sess_v2_args)

    assert res.oid == 'sysObjectID'
    assert res.oid_index == '0'
    assert res.value == '.1.3.6.1.4.1.8072.3.2.10'
    assert res.snmp_type == 'OBJECTID'


def test_snmp_get_next_end_of_mib_view(sess_v2_args):
    if sess_v2_args['version'] == 1:
        with pytest.raises(EasySNMPNoSuchNameError):
            snmp_get_next(['iso.9', 'sysDescr', 'iso.9'], **sess_v2_args)
    else:
        res = snmp_get_next(['iso.9', 'sysDescr', 'iso.9'], **sess_v2_args)

        assert res[0]
        assert res[0].value == 'ENDOFMIBVIEW'
        assert res[0].oid == 'iso.9'
        assert res[0].snmp_type == 'ENDOFMIBVIEW'

        assert res[1]
        assert platform.version() in res[1].value
        assert res[1].oid == 'sysDescr'
        assert res[1].oid_index == '0'
        assert res[1].snmp_type == 'OCTETSTR'

        assert res[2]
        assert res[2].value == 'ENDOFMIBVIEW'
        assert res[2].oid == 'iso.9'
        assert res[2].snmp_type == 'ENDOFMIBVIEW'


def test_snmp_get_next_unknown(sess_v2_args):
    # snmpget -v2c -c public localhost:11161 sysDescripto.0
    with pytest.raises(EasySNMPUnknownObjectIDError):
        snmp_get_next('sysDescripto.0', **sess_v2_args)


def test_snmp_set_string(sess_v2_args):
    # snmpget -v2c -c public localhost:11161 sysLocation.0
    res = snmp_get(('sysLocation', '0'), **sess_v2_args)
    assert res.oid == 'sysLocation'
    assert res.oid_index == '0'
    assert res.value != 'my newer location'
    assert res.snmp_type == 'OCTETSTR'

    success = snmp_set(('sysLocation', '0'), 'my newer location', **sess_v2_args)
    assert success

    res = snmp_get(('sysLocation', '0'), **sess_v2_args)
    assert res.oid == 'sysLocation'
    assert res.oid_index == '0'
    assert res.value == 'my newer location'
    assert res.snmp_type == 'OCTETSTR'


def test_snmp_set_string_long_type(sess_v2_args):
    # snmpget -v2c -c public localhost:11161 sysLocation.0
    res = snmp_get(('sysLocation', '0'), **sess_v2_args)
    assert res.oid == 'sysLocation'
    assert res.oid_index == '0'
    assert res.value != 'my newer location'
    assert res.snmp_type == 'OCTETSTR'

    success = snmp_set(('sysLocation', '0'), 'my newer location', 'OCTETSTR', **sess_v2_args)
    assert success

    res = snmp_get(('sysLocation', '0'), **sess_v2_args)
    assert res.oid == 'sysLocation'
    assert res.oid_index == '0'
    assert res.value == 'my newer location'
    assert res.snmp_type == 'OCTETSTR'


def test_snmp_set_string_short_type(sess_v2_args):
    # snmpget -v2c -c public localhost:11161 sysLocation.0
    res = snmp_get(('sysLocation', '0'), **sess_v2_args)
    assert res.oid == 'sysLocation'
    assert res.oid_index == '0'
    assert res.value != 'my newer location'
    assert res.snmp_type == 'OCTETSTR'

    success = snmp_set(('sysLocation', '0'), 'my newer location', 's', **sess_v2_args)
    assert success

    res = snmp_get(('sysLocation', '0'), **sess_v2_args)
    assert res.oid == 'sysLocation'
    assert res.oid_index == '0'
    assert res.value == 'my newer location'
    assert res.snmp_type == 'OCTETSTR'


def test_snmp_set_integer(sess_v2_args):
    success = snmp_set(('nsCacheTimeout', '.1.3.6.1.2.1.2.2'), 65, **sess_v2_args)
    assert success

    res = snmp_get(('nsCacheTimeout', '.1.3.6.1.2.1.2.2'), **sess_v2_args)
    assert res.oid == 'nsCacheTimeout'
    assert res.oid_index == '1.3.6.1.2.1.2.2'
    assert res.value == '65'
    assert res.snmp_type == 'INTEGER'


def test_snmp_set_integer_long_type(sess_v2_args):
    success = snmp_set(('nsCacheTimeout', '.1.3.6.1.2.1.2.2'), 65, 'INTEGER', **sess_v2_args)
    assert success

    res = snmp_get(('nsCacheTimeout', '.1.3.6.1.2.1.2.2'), **sess_v2_args)
    assert res.oid == 'nsCacheTimeout'
    assert res.oid_index == '1.3.6.1.2.1.2.2'
    assert res.value == '65'
    assert res.snmp_type == 'INTEGER'


def test_snmp_set_integer_short_type(sess_v2_args):
    success = snmp_set(('nsCacheTimeout', '.1.3.6.1.2.1.2.2'), 65, 'i', **sess_v2_args)
    assert success

    res = snmp_get(('nsCacheTimeout', '.1.3.6.1.2.1.2.2'), **sess_v2_args)
    assert res.oid == 'nsCacheTimeout'
    assert res.oid_index == '1.3.6.1.2.1.2.2'
    assert res.value == '65'
    assert res.snmp_type == 'INTEGER'


def test_snmp_set_unknown(sess_v2_args):
    with pytest.raises(EasySNMPUnknownObjectIDError):
        snmp_set('nsCacheTimeoooout', 1234, **sess_v2_args)


def test_snmp_set_multiple(sess_v2_args):
    res = snmp_get(
        ['sysLocation.0', 'nsCacheTimeout.1.3.6.1.2.1.2.2'], **sess_v2_args
    )
    assert res[0].value != 'my newer location'
    assert res[1].value != '162'

    success = snmp_set_multiple([
        ('sysLocation.0', 'my newer location'),
        (('nsCacheTimeout', '.1.3.6.1.2.1.2.2'), 162)
    ], **sess_v2_args)
    assert success

    res = snmp_get(
        ['sysLocation.0', 'nsCacheTimeout.1.3.6.1.2.1.2.2'], **sess_v2_args
    )
    assert res[0].value == 'my newer location'
    assert res[1].value == '162'


def test_snmp_get_bulk(sess_v2_args):
    if sess_v2_args['version'] == 1:
        with pytest.raises(EasySNMPError):
            snmp_get_bulk([
                'sysUpTime', 'sysORLastChange', 'sysORID', 'sysORDescr',
                'sysORUpTime'], 2, 8, **sess_v2_args
            )
    else:
        res = snmp_get_bulk([
            'sysUpTime', 'sysORLastChange', 'sysORID', 'sysORDescr',
            'sysORUpTime'], 2, 8, **sess_v2_args
        )

        assert len(res) == 26

        assert res[0].oid == 'sysUpTimeInstance'
        assert res[0].oid_index == ''
        assert int(res[0].value) > 0
        assert res[0].snmp_type == 'TICKS'

        assert res[4].oid == 'sysORUpTime'
        assert res[4].oid_index == '1'
        assert int(res[4].value) >= 0
        assert res[4].snmp_type == 'TICKS'


def test_snmp_walk(sess_v2_args):
    res = snmp_walk('system', **sess_v2_args)
    assert len(res) >= 7

    assert platform.version() in res[0].value
    assert res[3].value == 'G. S. Marzot <gmarzot@marzot.net>'
    assert res[4].value == platform.node()
    assert res[5].value == 'my original location'


def test_snmp_walk_res(sess_v2_args):
    res = snmp_walk('system', **sess_v2_args)

    assert len(res) >= 7

    assert res[0].oid == 'sysDescr'
    assert res[0].oid_index == '0'
    assert platform.version() in res[0].value
    assert res[0].snmp_type == 'OCTETSTR'

    assert res[3].oid == 'sysContact'
    assert res[3].oid_index == '0'
    assert res[3].value == 'G. S. Marzot <gmarzot@marzot.net>'
    assert res[3].snmp_type == 'OCTETSTR'

    assert res[4].oid == 'sysName'
    assert res[4].oid_index == '0'
    assert res[4].value == platform.node()
    assert res[4].snmp_type == 'OCTETSTR'

    assert res[5].oid == 'sysLocation'
    assert res[5].oid_index == '0'
    assert res[5].value == 'my original location'
    assert res[5].snmp_type == 'OCTETSTR'


def test_snmp_walk_unknown(sess_v2_args):
    with pytest.raises(EasySNMPUnknownObjectIDError):
        snmp_walk('systemo', **sess_v2_args)
