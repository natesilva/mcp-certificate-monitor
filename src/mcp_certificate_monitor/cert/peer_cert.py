import datetime
import ssl

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from typing_extensions import Annotated, Literal, Union

from mcp_certificate_monitor.cert.tuple_to_x509 import (
    is_cert_tuple_pairs,
    tuple_to_rfc4514,
)


class PeerCertError(BaseModel):
    type: Literal["error"] = "error"
    error: str


class PeerCertSuccess(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    type: Literal["success"] = "success"
    subject: str
    issuer: str
    serial: str = Field(alias="serialNumber")
    not_before: datetime.datetime = Field(alias="notBefore")
    not_after: datetime.datetime = Field(alias="notAfter")
    san: list[str] = Field(alias="subjectAltName", default_factory=list)
    days_remaining: int = 0

    @model_validator(mode="after")
    def _compute_days_remaining(self) -> "PeerCertSuccess":
        """Set the days_remaining value, only if it was not in the JSON
        from which this was deserialized.
        """
        if "days_remaining" not in self.model_fields_set:
            now = datetime.datetime.now(datetime.UTC)
            self.days_remaining = max((self.not_after - now).days, 0)
        return self

    @field_validator("subject", "issuer", mode="before")
    @classmethod
    def _parse_dn(cls, v: object) -> str:
        if isinstance(v, str):
            return v

        if not is_cert_tuple_pairs(v):
            raise ValueError("Invalid DN: expected tuple of tuples")

        return tuple_to_rfc4514(v)

    @field_validator("not_before", "not_after", mode="before")
    @classmethod
    def _parse_cert_time(cls, v: object) -> datetime.datetime:
        if isinstance(v, datetime.datetime):
            return v
        assert isinstance(v, str)
        try:
            return datetime.datetime.fromisoformat(v)
        except ValueError:
            return datetime.datetime.fromtimestamp(
                ssl.cert_time_to_seconds(v), tz=datetime.timezone.utc
            )

    @field_validator("san", mode="before")
    @classmethod
    def _parse_san(cls, v: object) -> list[str]:
        if isinstance(v, list):
            return v
        return [value for kind, value in v if kind == "DNS"]  # type: ignore[misc]


PeerCert = Annotated[Union[PeerCertSuccess, PeerCertError], Field(discriminator="type")]
