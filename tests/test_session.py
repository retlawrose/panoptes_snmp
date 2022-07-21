"""
Copyright 2018, Oath Inc.
Licensed under the terms of the BSD license. See LICENSE file in project root for terms.
"""
import platform
import re

import pytest
from yahoo_panoptes_snmp.exceptions import (
    EasySNMPError, EasySNMPConnectionError, EasySNMPTimeoutError,
    EasySNMPNoSuchObjectError, EasySNMPNoSuchInstanceError,
    EasySNMPNoSuchNameError
)

from yahoo_panoptes_snmp.session import Session
from .fixtures import sess_v2, sess_v3, sess_v2_args, sess_v3_args
from .helpers import snmp_set_via_cli


@pytest.fixture
def reset_values():
    snmp_set_via_cli('sysLocation.0', 'my original location', 's')
    snmp_set_via_cli('nsCacheTimeout.1.3.6.1.2.1.2.2', '0', 'i')
    yield


def test_session_invalid_snmp_version():
    with pytest.raises(ValueError):
        Session(version=4)


@pytest.mark.parametrize('version', [2, 3])
def test_session_invalid_hostname(version):
    with pytest.raises(EasySNMPConnectionError):
        session = Session(hostname='invalid', version=version)
        session.get('sysContact.0')


@pytest.mark.parametrize('version', [2, 3])
def test_session_invalid_hostname_and_remote_port(version):
    with pytest.raises(ValueError):
        Session(hostname='localhost:162', remote_port=163, version=version)


@pytest.mark.parametrize('version', [2, 3])
def test_session_hostname_and_remote_port_split(version):
    session = Session(hostname='localhost:162', version=version)
    assert session.hostname == 'localhost'
    assert session.remote_port == 162


@pytest.mark.parametrize('version', [2, 3])
def test_session_invalid_port(version):
    with pytest.raises(EasySNMPTimeoutError):
        session = Session(
            remote_port=1234, version=version, timeout=0.2, retries=1
        )
        session.get('sysContact.0')


# TODO: Determine how to test this more than once without a problem
# @pytest.mark.parametrize('sess', [sess_v1(), sess_v2(), sess_v3()])
def test_session_set_multiple_next(sess_v2):
    success = sess_v2.set_multiple([
        ('.1.3.6.1.6.3.12.1.2.1.2.116.101.115.116', '.1.3.6.1.6.1.1'),
        ('.1.3.6.1.6.3.12.1.2.1.3.116.101.115.116', '1234'),
        ('.1.3.6.1.6.3.12.1.2.1.9.116.101.115.116', 4),
    ])
    assert success

    res = sess_v2.get_next([
        'snmpTargetAddrTDomain', 'snmpTargetAddrTAddress',
        'snmpTargetAddrRowStatus'
    ])

    assert len(res) == 3

    assert res[0].oid == 'snmpTargetAddrTDomain'
    assert res[0].oid_index == '116.101.115.116'
    assert res[0].value == '.1.3.6.1.6.1.1'
    assert res[0].snmp_type == 'OBJECTID'

    assert res[1].oid == 'snmpTargetAddrTAddress'
    assert res[1].oid_index == '116.101.115.116'
    assert res[1].value == '1234'
    assert res[1].snmp_type == 'OCTETSTR'

    assert res[2].oid == 'snmpTargetAddrRowStatus'
    assert res[2].oid_index == '116.101.115.116'
    assert res[2].value == '3'
    assert res[2].snmp_type == 'INTEGER'


def test_session_set_clear(sess_v2):
    res = sess_v2.set('.1.3.6.1.6.3.12.1.2.1.9.116.101.115.116', 6)
    assert res == 1

    res = sess_v2.get_next([
        'snmpTargetAddrTDomain', 'snmpTargetAddrTAddress',
        'snmpTargetAddrRowStatus'
    ])

    assert len(res) == 3

    assert res[0].oid == 'snmpUnavailableContexts'
    assert res[0].oid_index == '0'
    assert res[0].value == '0'
    assert res[0].snmp_type == 'COUNTER'

    assert res[1].oid == 'snmpUnavailableContexts'
    assert res[1].oid_index == '0'
    assert res[1].value == '0'
    assert res[1].snmp_type == 'COUNTER'

    assert res[2].oid == 'snmpUnavailableContexts'
    assert res[2].oid_index == '0'
    assert res[2].value == '0'
    assert res[2].snmp_type == 'COUNTER'


def test_session_get(sess_v2):
    res = sess_v2.get([
        ('sysUpTime', '0'),
        ('sysContact', '0'),
        ('sysLocation', '0')
    ])

    assert len(res) == 3

    assert res[0].oid == 'sysUpTimeInstance'
    assert res[0].oid_index == ''
    assert int(res[0].value) > 0
    assert res[0].snmp_type == 'TICKS'

    assert res[1].oid == 'sysContact'
    assert res[1].oid_index == '0'
    assert res[1].value == 'G. S. Marzot <gmarzot@marzot.net>'
    assert res[1].snmp_type == 'OCTETSTR'

    assert res[2].oid == 'sysLocation'
    assert res[2].oid_index == '0'
    assert res[2].value == 'my original location'
    assert res[2].snmp_type == 'OCTETSTR'


def test_session_get_use_numeric(sess_v2):
    sess_v2.use_numeric = True
    res = sess_v2.get('sysContact.0')

    assert res.oid == '.1.3.6.1.2.1.1.4'
    assert res.oid_index == '0'
    assert res.value == 'G. S. Marzot <gmarzot@marzot.net>'
    assert res.snmp_type == 'OCTETSTR'


def test_session_get_use_sprint_value(sess_v2):
    sess_v2.use_sprint_value = True
    res = sess_v2.get('sysUpTimeInstance')

    assert res.oid == 'sysUpTimeInstance'
    assert res.oid_index == ''
    assert re.match(r'^\d+:\d+:\d+:\d+\.\d+$', res.value)
    assert res.snmp_type == 'TICKS'


def test_session_get_use_enums(sess_v2):
    sess_v2.use_enums = True
    res = sess_v2.get('ifAdminStatus.1')

    assert res.oid == 'ifAdminStatus'
    assert res.oid_index == '1'
    assert res.value == 'up'
    assert res.snmp_type == 'INTEGER'


def test_session_get_next(sess_v2):
    res = sess_v2.get_next([
        ('sysUpTime', '0'),
        ('sysContact', '0'),
        ('sysLocation', '0')
    ])

    assert len(res) == 3

    assert res[0].oid == 'sysContact'
    assert res[0].oid_index == '0'
    assert res[0].value == 'G. S. Marzot <gmarzot@marzot.net>'
    assert res[0].snmp_type == 'OCTETSTR'

    assert res[1].oid == 'sysName'
    assert res[1].oid_index == '0'
    assert res[1].value == platform.node()
    assert res[1].snmp_type == 'OCTETSTR'

    assert res[2].oid == 'sysORLastChange'
    assert res[2].oid_index == '0'
    assert int(res[2].value) >= 0
    assert res[2].snmp_type == 'TICKS'


def test_session_set(sess_v2):
    res = sess_v2.get(('sysLocation', '0'))
    assert res.value != 'my newer location'

    success = sess_v2.set(('sysLocation', '0'), 'my newer location')
    assert success

    res = sess_v2.get(('sysLocation', '0'))
    assert res.value == 'my newer location'


def test_session_set_multiple(sess_v2):
    res = sess_v2.get(['sysLocation.0', 'nsCacheTimeout.1.3.6.1.2.1.2.2'])
    assert res[0].value != 'my newer location'
    assert res[1].value != '160'

    success = sess_v2.set_multiple([
        ('sysLocation.0', 'my newer location'),
        (('nsCacheTimeout', '.1.3.6.1.2.1.2.2'), 160),
    ])
    assert success

    res = sess_v2.get(['sysLocation.0', 'nsCacheTimeout.1.3.6.1.2.1.2.2'])
    assert res[0].value == 'my newer location'
    assert res[1].value == '160'


def test_session_get_bulk(sess_v2):  # noqa
    if sess_v2.version == 1:
        with pytest.raises(EasySNMPError):
            sess_v2.get_bulk(
                ['sysUpTime', 'sysORLastChange', 'sysORID', 'sysORDescr',
                 'sysORUpTime'], 2, 8
            )
    else:
        res = sess_v2.get_bulk(
            ['sysUpTime', 'sysORLastChange', 'sysORID', 'sysORDescr',
             'sysORUpTime'], 2, 8
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


def test_session_get_invalid_instance(sess_v2):
    # Sadly, SNMP v1 doesn't distinguish between an invalid instance and an
    # invalid object ID, instead it excepts with noSuchName
    if sess_v2.version == 1:
        with pytest.raises(EasySNMPNoSuchNameError):
            sess_v2.get('sysDescr.100')
    else:
        res = sess_v2.get('sysDescr.100')
        assert res.snmp_type == 'NOSUCHINSTANCE'


def test_session_get_invalid_instance_with_abort_enabled(sess_v2):
    # Sadly, SNMP v1 doesn't distinguish between an invalid instance and an
    # invalid object ID, instead it excepts with noSuchName
    sess_v2.abort_on_nonexistent = True
    if sess_v2.version == 1:
        with pytest.raises(EasySNMPNoSuchNameError):
            sess_v2.get('sysDescr.100')
    else:
        with pytest.raises(EasySNMPNoSuchInstanceError):
            sess_v2.get('sysDescr.100')


def test_session_get_invalid_object(sess_v2):
    if sess_v2.version == 1:
        with pytest.raises(EasySNMPNoSuchNameError):
            sess_v2.get('iso')
    else:
        res = sess_v2.get('iso')
        assert res.snmp_type == 'NOSUCHOBJECT'


def test_session_get_invalid_object_with_abort_enabled(sess_v2):
    sess_v2.abort_on_nonexistent = True
    if sess_v2.version == 1:
        with pytest.raises(EasySNMPNoSuchNameError):
            sess_v2.get('iso')
    else:
        with pytest.raises(EasySNMPNoSuchObjectError):
            sess_v2.get('iso')


def test_session_walk(sess_v2):
    res = sess_v2.walk('system')

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


def test_session_walk_all(sess_v2):
    # TODO: Determine why walking iso doesn't work for SNMP v1
    if sess_v2.version == 1:
        with pytest.raises(EasySNMPNoSuchNameError):
            sess_v2.walk('.')
    else:
        res = sess_v2.walk('.')

        assert len(res) > 0

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
