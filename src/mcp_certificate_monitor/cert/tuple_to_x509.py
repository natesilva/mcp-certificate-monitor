import typing

from cryptography import x509
from cryptography.x509.oid import NameOID

"""Map attribute names returned in a cert to their x509 OIDs"""
ATTR_TO_OID = {
    "countryName": NameOID.COUNTRY_NAME,
    "organizationName": NameOID.ORGANIZATION_NAME,
    "organizationalUnitName": NameOID.ORGANIZATIONAL_UNIT_NAME,
    "commonName": NameOID.COMMON_NAME,
    "dnQualifier": NameOID.DN_QUALIFIER,
    "stateOrProvinceName": NameOID.STATE_OR_PROVINCE_NAME,
    "serialNumber": NameOID.SERIAL_NUMBER,
    "domainComponent": NameOID.DOMAIN_COMPONENT,
    "localityName": NameOID.LOCALITY_NAME,
    "emailAddress": NameOID.EMAIL_ADDRESS,
}

"""
A set of nested tuples representing the DN of a certificate.
Example: `((("countryName", "US"),), (("organizationName", "Example"),),
 (("commonName", "example.com"),))`
"""
type cert_tuple_pairs = tuple[tuple[tuple[str, str], ...], ...]


def is_cert_tuple_pairs(v: object) -> typing.TypeGuard[cert_tuple_pairs]:
    return isinstance(v, tuple) and all(
        isinstance(rdn, tuple)
        and all(
            isinstance(attr, tuple)
            and len(attr) == 2
            and isinstance(attr[0], str)
            and isinstance(attr[1], str)
            for attr in rdn
        )
        for rdn in v
    )


def tuple_to_x509_name(dn: cert_tuple_pairs) -> x509.Name:
    rdns = []
    for rdn in dn:
        attrs = []
        for attr, value in rdn:
            oid = ATTR_TO_OID.get(attr)
            if oid is None:
                raise KeyError(f"Unknown attribute: {attr}")
            attrs.append(x509.NameAttribute(oid, value))
        rdns.append(x509.RelativeDistinguishedName(attrs))
    return x509.Name(rdns)


def tuple_to_rfc4514(dn: cert_tuple_pairs) -> str:
    return tuple_to_x509_name(dn).rfc4514_string()
