import datetime
import uuid

from pydantic import BaseModel, ConfigDict


class BaseInputSchema(BaseModel):
    """
    Base schema for all input data schema
    """

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )


class BaseOutputSchema(BaseModel):
    """
    Base schema for all output data schema
    """

    model_config = ConfigDict(
        from_attributes=True, arbitrary_types_allowed=True, extra="ignore"
    )


class BaseModelOutput(BaseOutputSchema):
    """
    Base schema for all output database model schema
    """

    id: uuid.UUID
    created_at: datetime.datetime
    updated_at: datetime.datetime
