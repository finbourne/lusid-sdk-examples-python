import lusid.models as models

from lusid.exceptions import ApiException
from utilities import DataUtilities
import pytest


class TestInstruments:
    async def ensure_property_definition(self, code, property_definitions_api):
        try:
            await property_definitions_api.get_property_definition(
                domain="Instrument", scope=DataUtilities.tutorials_scope, code=code
            )
        except ApiException:
            # property definition doesn't exist (returns 404), so create one
            property_definition = models.CreatePropertyDefinitionRequest(
                domain="Instrument",
                scope=DataUtilities.tutorials_scope,
                life_time="Perpetual",
                code=code,
                value_required=False,
                data_type_id=models.ResourceId("system", "string"),
            )

            # create the property
            await property_definitions_api.create_property_definition(
                definition=property_definition
            )

    @pytest.mark.asyncio
    async def test_seed_instrument_master(self, instruments_api):
        response = await instruments_api.upsert_instruments(
            request_body={
                "BBG00KTDTF73": models.InstrumentDefinition(
                    name="AT&T INC",
                    identifiers={
                        "Figi": models.InstrumentIdValue(value="BBG00KTDTF73"),
                        "ClientInternal": models.InstrumentIdValue(
                            value="internal_id_1_example"
                        ),
                    },
                ),
                "BBG00Y271826": models.InstrumentDefinition(
                    name="BYTES TECHNOLOGY GROUP PLC",
                    identifiers={
                        "Figi": models.InstrumentIdValue(value="BBG00Y271826"),
                        "ClientInternal": models.InstrumentIdValue(
                            value="internal_id_2_example"
                        ),
                    },
                ),
                "BBG00L7XVNP1": models.InstrumentDefinition(
                    name="CUSHMAN & WAKEFIELD PLC",
                    identifiers={
                        "Figi": models.InstrumentIdValue(value="BBG00L7XVNP1"),
                        "ClientInternal": models.InstrumentIdValue(
                            value="internal_id_3_example"
                        ),
                    },
                ),
                "BBG005D5KGM0": models.InstrumentDefinition(
                    name="FIRST CITRUS BANCORPORATION",
                    identifiers={
                        "Figi": models.InstrumentIdValue(value="BBG005D5KGM0"),
                        "ClientInternal": models.InstrumentIdValue(
                            value="internal_id_4_example"
                        ),
                    },
                ),
                "BBG000DPM932": models.InstrumentDefinition(
                    name="FRASERS GROUP PLC",
                    identifiers={
                        "Figi": models.InstrumentIdValue(value="BBG000DPM932"),
                        "ClientInternal": models.InstrumentIdValue(
                            value="internal_id_5_example"
                        ),
                    },
                ),
            }
        )

        assert len(response.values) == 5, response.failed

    @pytest.mark.asyncio
    async def test_lookup_instrument_by_unique_id(self, instruments_api):
        figi = "BBG00KTDTF73"

        # set up the instrument
        response = await instruments_api.upsert_instruments(
            request_body={
                figi: models.InstrumentDefinition(
                    name="AT&T INC",
                    identifiers={
                        "Figi": models.InstrumentIdValue(value=figi),
                        "ClientInternal": models.InstrumentIdValue(
                            value="internal_id_1_example"
                        ),
                    },
                )
            }
        )
        assert len(response.values) == 1, response.failed

        # look up an instrument that already exists in the instrument master by a
        # unique id, in this case an OpenFigi, and also return a list of aliases
        looked_up_instruments = await instruments_api.get_instruments(
            identifier_type="Figi",
            request_body=[figi],
            property_keys=["Instrument/default/ClientInternal"],
        )

        assert figi in looked_up_instruments.values, f"cannot find {figi}"

        instrument = looked_up_instruments.values[figi]
        assert instrument.name == "AT&T INC"

        property = next(
            filter(
                lambda i: i.key == "Instrument/default/ClientInternal",
                instrument.properties,
            ),
            None,
        )
        assert property.value.label_value == "internal_id_1_example"

    @pytest.mark.asyncio
    async def test_list_available_identifiers(self, instruments_api):
        identifiers = await instruments_api.get_instrument_identifier_types()
        assert len(identifiers.values) > 0

    @pytest.mark.asyncio
    async def test_list_all_instruments(self, instruments_api):
        page_size = 5

        # list the instruments, restricting the number that are returned
        instruments = await instruments_api.list_instruments(limit=page_size)

        assert len(instruments.values) <= page_size

    @pytest.mark.asyncio
    async def test_list_instruments_by_identifier_type(self, instruments_api):
        figis = ["BBG00KTDTF73", "BBG00Y271826", "BBG00L7XVNP1"]

        # get a set of instruments querying by FIGIs
        instruments = await instruments_api.get_instruments(
            identifier_type="Figi", request_body=figis
        )

        for figi in figis:
            assert figi in instruments.values, f"{figi} not returned"

    @pytest.mark.asyncio
    async def test_edit_instrument_property(self, instruments_api):
        property_value = models.PropertyValue(label_value="Insurance")
        property_key = f"Instrument/{DataUtilities.tutorials_scope}/CustomSector"
        identifier_type = "Figi"
        identifier = "BBG00KTDTF73"

        # update the instrument
        await instruments_api.upsert_instruments_properties(
            upsert_instrument_property_request=[
                models.UpsertInstrumentPropertyRequest(
                    identifier_type=identifier_type,
                    identifier=identifier,
                    properties=[
                        models.ModelProperty(key=property_key, value=property_value)
                    ],
                )
            ]
        )

        # get the instrument with value
        instrument = await instruments_api.get_instrument(
            identifier_type=identifier_type,
            identifier=identifier,
            property_keys=[property_key],
        )

        assert len(instrument.properties) >= 1

        prop = list(
            filter(
                lambda p: p.key == property_key
                and p.value.label_value == property_value.label_value,
                instrument.properties,
            )
        )

        assert (
            len(prop) == 1
        ), f"cannot find property key=${property_key} value={property_value}"
