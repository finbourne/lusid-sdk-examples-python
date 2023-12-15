from datetime import datetime

import pytz


import lusid.models as models

from utilities.test_data_utilities import DataUtilities
import pytest


@pytest.fixture(scope="class")
def default_scope(scope="class"):
    return DataUtilities.tutorials_scope


class TestProperties:
    @pytest.mark.asyncio
    async def test_create_portfolio_with_label_property(
        self,
        id_generator,
        property_definitions_api,
        transaction_portfolios_api,
        portfolios_api,
    ):
        # Details of property to be created
        effective_date = datetime(year=2018, month=1, day=1, tzinfo=pytz.utc)

        _, scope, property_code, _ = id_generator.generate_scope_and_code(
            "property_definition",
            scope=DataUtilities.tutorials_scope,
            code_prefix="fund-style-",
            annotations=["Portfolio"],
        )

        label_property_definition = models.CreatePropertyDefinitionRequest(
            domain="Portfolio",
            scope=scope,
            code=property_code,
            display_name=property_code,
            life_time="Perpetual",
            value_required=False,
            data_type_id=models.resource_id.ResourceId(scope="system", code="string"),
        )

        # create property definition
        label_property_definition_request = (
            await property_definitions_api.create_property_definition(
                label_property_definition
            )
        )

        # create property values
        property_value = models.PropertyValue(label_value="Active")

        _, scope, portfolio_code = id_generator.generate_scope_and_code(
            "portfolio",
            scope=DataUtilities.tutorials_scope,
            code_prefix="portfolio-",
        )

        # Details of new portfolio to be created
        create_portfolio_request = models.CreateTransactionPortfolioRequest(
            code=portfolio_code,
            display_name=portfolio_code,
            base_currency="GBP",
            created=effective_date,
            properties={
                label_property_definition_request.key: models.PerpetualProperty(
                    key=label_property_definition_request.key, value=property_value
                )
            },
        )

        # create portfolio
        portfolio_request = await transaction_portfolios_api.create_portfolio(
            scope=DataUtilities.tutorials_scope,
            create_transaction_portfolio_request=create_portfolio_request,
        )

        # get properties for assertions
        portfolio_properties = (
            await portfolios_api.get_portfolio_properties(
                scope=DataUtilities.tutorials_scope, code=portfolio_request.id.code
            )
        ).properties

        label_property = portfolio_properties[label_property_definition_request.key]

        # Perform assertions on keys, codes and values
        assert (
            list(portfolio_properties.keys())[0]
            == label_property_definition_request.key
        )
        assert portfolio_request.id.code == create_portfolio_request.code
        assert label_property.value.label_value == property_value.label_value

    @pytest.mark.asyncio
    async def test_create_portfolio_with_metric_property(
        self,
        id_generator,
        property_definitions_api,
        transaction_portfolios_api,
        portfolios_api,
    ):
        effective_date = datetime(year=2018, month=1, day=1, tzinfo=pytz.utc)

        _, scope, property_code, _ = id_generator.generate_scope_and_code(
            "property_definition",
            scope=DataUtilities.tutorials_scope,
            code_prefix="fund-NAV-",
            annotations=["Portfolio"],
        )

        # details of property to be created
        metric_property_definition = models.CreatePropertyDefinitionRequest(
            domain="Portfolio",
            scope=scope,
            code=property_code,
            display_name="fund NAV",
            life_time="Perpetual",
            value_required=False,
            data_type_id=models.resource_id.ResourceId(
                scope="system", code="currencyAndAmount"
            ),
        )

        # create property definitions
        metric_property_definition_result = (
            await property_definitions_api.create_property_definition(
                metric_property_definition
            )
        )

        # create the property values
        metric_property_value_request = models.PropertyValue(
            metric_value=models.MetricValue(value=1100000, unit="GBP")
        )
        # metric_property_value_request = models.PropertyValue(label_value="Active")

        # Details of the new portfolio to be created,
        # created here with the minimum set of mandatory fields

        _, scope, portfolio_code = id_generator.generate_scope_and_code(
            "portfolio",
            scope=DataUtilities.tutorials_scope,
            code_prefix="portfolio-",
        )

        create_portfolio_request = models.CreateTransactionPortfolioRequest(
            code=portfolio_code,
            display_name=portfolio_code,
            base_currency="GBP",
            created=effective_date,
            properties={
                metric_property_definition_result.key: models.PerpetualProperty(
                    key=metric_property_definition_result.key,
                    value=metric_property_value_request,
                )
            },
        )

        # Create portfolio
        portfolio_result = await transaction_portfolios_api.create_portfolio(
            scope=DataUtilities.tutorials_scope,
            create_transaction_portfolio_request=create_portfolio_request,
        )
        portfolio_properties = (
            await portfolios_api.get_portfolio_properties(
                scope=DataUtilities.tutorials_scope, code=portfolio_result.id.code
            )
        ).properties
        metric_property = portfolio_properties[metric_property_definition_result.key]

        # Perform assertions on codes, keys, values and units
        assert portfolio_result.id.code == create_portfolio_request.code
        assert (
            list(portfolio_properties.keys())[0]
            == metric_property_definition_result.key
        )
        assert (
            metric_property.value.metric_value.value
            == metric_property_value_request.metric_value.value
        )
        assert (
            metric_property.value.metric_value.unit
            == metric_property_value_request.metric_value.unit
        )
