"""
Copyright 2018, Oath Inc.
Licensed under the terms of the BSD license. See LICENSE file in project root for terms.
"""

from __future__ import unicode_literals


class EasySNMPError(Exception):
    """The base Easy SNMP exception which covers all exceptions raised."""
    pass


class EasySNMPConnectionError(EasySNMPError):
    """Indicates a problem connecting to the remote host."""
    pass


class EasySNMPTimeoutError(EasySNMPConnectionError):
    """Raised when an SNMP request times out."""
    pass


class EasySNMPUnknownObjectIDError(EasySNMPError):
    """Raised when an inexisted OID is requested."""
    pass


class EasySNMPNoSuchNameError(EasySNMPError):
    """
    Raised when an OID is requested which may be an invalid object name
    or invalid instance (only applies to SNMPv1).
    """
    pass


class EasySNMPNoSuchObjectError(EasySNMPError):
    """
    Raised when an OID is requested which may have some form of existence but
    an invalid object name.
    """
    pass


class EasySNMPNoSuchInstanceError(EasySNMPError):
    """
    Raised when a particular OID index requested from Net-SNMP doesn't exist.
    """
    pass


class EasySNMPUndeterminedTypeError(EasySNMPError):
    """
    Raised when the type cannot be determine when setting the value of an OID.
    """
    pass
