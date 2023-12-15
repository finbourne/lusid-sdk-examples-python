import uuid
from datetime import datetime

import pytz


import lusid.models as models
from utilities import DataUtilities
import pytest


@pytest.fixture(scope="class")
def default_scope(scope="class"):
    return DataUtilities.tutorials_scope


class TestPortfolios:
    @pytest.mark.asyncio
    async def test_create_portfolio(self, id_generator, transaction_portfolios_api):
        _, scope, portfolio_code = id_generator.generate_scope_and_code(
            "portfolio",
            scope=DataUtilities.tutorials_scope,
            code_prefix="portfolio-",
        )

        # details of the new portfolio to be created,
        # created here with the minimum set of mandatory fields
        request = models.CreateTransactionPortfolioRequest(
            # descriptive name for the portfolio
            display_name=portfolio_code,
            # unique portfolio code, portfolio codes must be unique across scopes
            code=portfolio_code,
            base_currency="GBP",
        )

        # create the portfolio in LUSID in the specified scope
        result = await transaction_portfolios_api.create_portfolio(
            scope=scope, create_transaction_portfolio_request=request
        )

        assert result.id.code == request.code

    @pytest.mark.asyncio
    async def test_create_portfolio_with_properties(
        self,
        id_generator,
        property_definitions_api,
        transaction_portfolios_api,
        portfolios_api,
    ):
        _, scope, property_code, _ = id_generator.generate_scope_and_code(
            "property_definition",
            scope=DataUtilities.tutorials_scope,
            code_prefix="fund-style-",
            annotations=["Portfolio"],
        )

        data_type_id = models.ResourceId(scope="system", code="string")

        #   property definition
        property_definition = models.CreatePropertyDefinitionRequest(
            domain="Portfolio",
            scope=DataUtilities.tutorials_scope,
            code=property_code,
            value_required=False,
            display_name="Fund Style",
            life_time="Perpetual",
            data_type_id=data_type_id,
        )

        #   create the property definition
        property_definition_result = (
            await property_definitions_api.create_property_definition(
                create_property_definition_request=property_definition
            )
        )

        #  property value
        property_value = "Active"
        portfolio_property = models.ModelProperty(
            key=property_definition_result.key,
            value=models.PropertyValue(label_value=property_value),
        )

        _, scope, portfolio_code = id_generator.generate_scope_and_code(
            "portfolio",
            scope=DataUtilities.tutorials_scope,
            code_prefix="portfolio-",
        )

        #  details of the portfolio to be created
        request = models.CreateTransactionPortfolioRequest(
            display_name=portfolio_code,
            code=portfolio_code,
            base_currency="GBP",
            # set the property value when creating the portfolio
            properties={property_definition_result.key: portfolio_property},
        )

        # create the portfolio
        portfolio = await transaction_portfolios_api.create_portfolio(
            scope=scope, create_transaction_portfolio_request=request
        )

        portfolio_code = portfolio.id.code
        assert portfolio_code == request.code

        portfolio_properties = await portfolios_api.get_portfolio_properties(
            DataUtilities.tutorials_scope, portfolio_code
        )

        assert len(portfolio_properties.properties) == 1
        assert (
            portfolio_properties.properties[
                property_definition_result.key
            ].value.label_value
            == property_value
        )

    @pytest.mark.asyncio
    async def test_add_transaction_to_portfolio(
        self, data_utilities, id_generator, transaction_portfolios_api, instruments
    ):
        # effective date of the portfolio
        # this is the date the portfolio was created and became live.
        # All dates/times must be supplied in UTC
        effective_date = datetime(2018, 1, 1, tzinfo=pytz.utc).isoformat()

        # create the portfolio
        portfolio_id = await data_utilities.create_transaction_portfolio(
            DataUtilities.tutorials_scope
        )
        id_generator.add_scope_and_code(
            "portfolio", DataUtilities.tutorials_scope, portfolio_id
        )

        #   details of the transaction to be added
        transaction = models.TransactionRequest(
            # unique transaction id
            transaction_id=str(uuid.uuid4()),
            # transaction type, configured during system setup
            type="Buy",
            instrument_identifiers={
                DataUtilities.lusid_luid_identifier: instruments[0]
            },
            transaction_date=effective_date,
            settlement_date=effective_date,
            units=100,
            transaction_price=models.TransactionPrice(price=12.3),
            total_consideration=models.CurrencyAndAmount(amount=1230, currency="GBP"),
            source="Client",
        )

        #   add the transaction
        await transaction_portfolios_api.upsert_transactions(
            DataUtilities.tutorials_scope,
            portfolio_id,
            transaction_request=[transaction],
        )

        #   get the trades
        trades = await transaction_portfolios_api.get_transactions(
            DataUtilities.tutorials_scope, portfolio_id
        )

        assert len(trades.values) == 1
        assert trades.values[0].transaction_id == transaction.transaction_id

    @pytest.mark.asyncio
    async def test_add_transaction_to_portfolio_with_property(
        self,
        id_generator,
        property_definitions_api,
        data_utilities,
        transaction_portfolios_api,
        instruments,
    ):
        _, scope, property_code, _ = id_generator.generate_scope_and_code(
            "property_definition",
            scope=DataUtilities.tutorials_scope,
            code_prefix="traderId-",
            annotations=["Transaction"],
        )

        #   details of the property to be created
        property_definition = models.CreatePropertyDefinitionRequest(
            # The domain the property is to be applied to
            domain="Transaction",
            # the scope the property will be created in
            scope=scope,
            life_time="Perpetual",
            # when the property value is set
            # it will be valid forever and cannot be changed.
            # properties whose values can change over time
            # should be created with LifeTimeEnum.TIMEVARIANT
            code=property_code,
            value_required=False,
            display_name="Trader Id",
            data_type_id=models.ResourceId(scope="system", code="string"),
        )

        #   create the property definition
        property_definition_result = (
            await property_definitions_api.create_property_definition(
                create_property_definition_request=property_definition
            )
        )

        # effective date for which portfolio is created
        effective_date = datetime(2018, 1, 1, tzinfo=pytz.utc).isoformat()

        # create the portfolio
        portfolio_id = await data_utilities.create_transaction_portfolio(
            DataUtilities.tutorials_scope
        )
        id_generator.add_scope_and_code(
            "portfolio", DataUtilities.tutorials_scope, portfolio_id
        )

        property_value_as_string = "A Trader"
        property_value = models.PropertyValue(label_value=property_value_as_string)

        #   details of the transaction to be added
        transaction = models.TransactionRequest(
            transaction_id=str(uuid.uuid4()),
            type="Buy",
            instrument_identifiers={
                DataUtilities.lusid_luid_identifier: instruments[0]
            },
            transaction_date=effective_date,
            settlement_date=effective_date,
            units=100,
            transaction_price=models.TransactionPrice(price=12.3),
            total_consideration=models.CurrencyAndAmount(amount=1230, currency="GBP"),
            source="Client",
            # add the property to the transaction
            properties={
                property_definition_result.key: models.PerpetualProperty(
                    key=property_definition_result.key, value=property_value
                )
            },
        )

        #   add the transaction
        await transaction_portfolios_api.upsert_transactions(
            DataUtilities.tutorials_scope,
            portfolio_id,
            transaction_request=[transaction],
        )

        #   get the trades
        trades = await transaction_portfolios_api.get_transactions(
            DataUtilities.tutorials_scope, portfolio_id
        )

        assert len(trades.values) == 1
        assert trades.values[0].transaction_id == transaction.transaction_id
        assert (
            trades.values[0]
            .properties[property_definition_result.key]
            .value.label_value
            == property_value_as_string
        )

    @pytest.mark.asyncio
    async def test_list_portfolios(self, data_utilities, id_generator, portfolios_api):
        # This defines the scope that the portfolios will be retrieved from
        scope = DataUtilities.tutorials_scope + str(uuid.uuid4())

        for i in range(10):
            code = await data_utilities.create_transaction_portfolio(scope)
            id_generator.add_scope_and_code("portfolio", scope, code)

        # Retrieve the list of portfolios
        portfolios = await portfolios_api.list_portfolios_for_scope(scope)

        assert len(portfolios.values) == 10
