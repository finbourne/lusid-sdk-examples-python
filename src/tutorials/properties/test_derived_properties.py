import json
import logging

import lusid
import lusid.models as models
from utilities import DataUtilities
import pytest


@pytest.fixture(scope="class")
def default_scope(scope="class"):
    return DataUtilities.tutorials_scope


class TestDerivedProperties:
    async def create_ratings_property(
        self, property_definitions_api, id_generator, *ratings
    ):
        ratings = [*ratings]
        global scope
        scope = "Derived"

        for rating in ratings:
            property_definition = models.CreatePropertyDefinitionRequest(
                domain="Instrument",
                scope=scope,
                code=f"{rating}Rating",
                display_name=f"{rating}Rating",
                data_type_id=lusid.ResourceId(scope="system", code="number"),
            )

            try:
                # create property definition
                await property_definitions_api.create_property_definition(
                    create_property_definition_request=property_definition
                )
            except lusid.ApiException as e:
                if json.loads(e.body)["name"] == "PropertyAlreadyExists":
                    logging.info(
                        f"Property {property_definition.domain}/\
                        {property_definition.scope}/\
                        {property_definition.display_name} already exists"
                    )
            finally:
                id_generator.add_scope_and_code(
                    "property_definition",
                    property_definition.scope,
                    property_definition.code,
                    ["Instrument"],
                )

    async def upsert_ratings_property(
        self, instruments_api, figi, fitch_value=None, moodys_value=None
    ):
        properties = {
            f"Instrument/{scope}/FitchRating": fitch_value,
            f"Instrument/{scope}/MoodysRating": moodys_value,
        }

        # upsert property definition
        for key in properties:
            if properties[key] is not None:
                property_request = [
                    models.UpsertInstrumentPropertyRequest(
                        identifier_type="Figi",
                        identifier=figi,
                        properties=[
                            models.ModelProperty(
                                key=key,
                                value=models.PropertyValue(
                                    metric_value=models.MetricValue(
                                        value=properties[key]
                                    )
                                ),
                            )
                        ],
                    )
                ]

                await instruments_api.upsert_instruments_properties(
                    upsert_instrument_property_request=property_request
                )

    async def get_instruments_with_derived_prop(self, instruments_api, figi):
        response = await instruments_api.get_instruments(
            identifier_type="Figi",
            request_body=[figi],
            property_keys=[f"Instrument/{scope}/DerivedRating"],
        )

        return response.values[figi].properties[0].value.metric_value.value

    @pytest.mark.asyncio
    async def test_derived_property(
        self, property_definitions_api, id_generator, instruments_api, instruments
    ):
        await self.create_ratings_property(
            property_definitions_api, id_generator, "Fitch", "Moodys"
        )

        # create instrument property edge cases and upsert
        # (using arbitrary numeric ratings)
        await self.upsert_ratings_property(
            instruments_api, "BBG00KTDTF73", fitch_value=10, moodys_value=5
        )
        await self.upsert_ratings_property(instruments_api, "BBG00Y271826")
        await self.upsert_ratings_property(
            instruments_api, "BBG00L7XVNP1", moodys_value=5
        )
        await self.upsert_ratings_property(
            instruments_api, "BBG005D5KGM0", fitch_value=10
        )

        # create derived property using the 'Coalesce' derivation formula
        code = "DerivedRating"
        derivation_formula = f"Coalesce(Properties[Instrument/{scope}/MoodysRating], \
                            Properties[Instrument/{scope}/FitchRating],\
                            0)"

        # create derived property request
        derived_prop_definition_req = models.CreateDerivedPropertyDefinitionRequest(
            domain="Instrument",
            scope=scope,
            code=code,
            display_name=code,
            data_type_id=lusid.ResourceId(scope="system", code="number"),
            derivation_formula=derivation_formula,
        )

        try:
            # create property definition
            await property_definitions_api.create_derived_property_definition(
                derived_prop_definition_req
            )
        except lusid.ApiException as e:
            if json.loads(e.body)["name"] == "PropertyAlreadyExists":
                logging.info(
                    f"Property {derived_prop_definition_req.domain}\
                    {derived_prop_definition_req.scope}/\
                    {derived_prop_definition_req.display_name} already exists"
                )
        finally:
            id_generator.add_scope_and_code(
                "property_definition",
                derived_prop_definition_req.scope,
                derived_prop_definition_req.code,
                ["Instrument"],
            )

        # test case for derived property with both ratings
        moodys_then_fitch = await self.get_instruments_with_derived_prop(
            instruments_api, "BBG00KTDTF73"
        )
        assert moodys_then_fitch == 5.0

        # test case for derived property with no ratings
        no_ratings = await self.get_instruments_with_derived_prop(
            instruments_api, "BBG00Y271826"
        )
        assert no_ratings == 0.0

        # # test case for derived property with fitch only
        fitch_only = await self.get_instruments_with_derived_prop(
            instruments_api, "BBG005D5KGM0"
        )
        assert fitch_only == 10.0

        # test case for derived property with moodys only
        moodys_only = await self.get_instruments_with_derived_prop(
            instruments_api, "BBG00L7XVNP1"
        )
        assert moodys_only == 5.0
