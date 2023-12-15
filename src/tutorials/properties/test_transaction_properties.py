# import general python packages
import json
from datetime import datetime
import pytz

# import lusid specific packages
import lusid
import lusid.models as models
from utilities import DataUtilities
import pytest_asyncio
import pytest


@pytest_asyncio.fixture(scope="class")
async def default_scope():
    return DataUtilities.tutorials_scope


@pytest.fixture(scope="class")
def scope():
    return "TransactionProperty"


@pytest.fixture(scope="class")
def code():
    return "TransactionTaxDetail"


class TestTransactionProperties:
    async def create_transaction_property(
        self, property_definitions_api, id_generator, scope, code
    ):
        # Details of the property
        property_definition = models.CreatePropertyDefinitionRequest(
            domain="Transaction",
            scope=scope,
            code=code,
            display_name=code,
            data_type_id=lusid.ResourceId(scope="system", code="string"),
        )

        # create property definition
        try:
            await property_definitions_api.create_property_definition(
                create_property_definition_request=property_definition
            )
        except lusid.ApiException as e:
            if json.loads(e.body)["name"] == "PropertyAlreadyExists":
                self.root_logger.info(
                    f"Property {property_definition.domain}/\
                    {property_definition.scope}/\
                    {property_definition.code} already exists"
                )
        finally:
            id_generator.add_scope_and_code(
                "property_definition",
                property_definition.scope,
                property_definition.code,
                ["Transaction"],
            )

    async def create_portfolio(
        self, transaction_portfolios_api, id_generator, scope, code
    ):
        # Details of new portfolio to be created
        effective_date = datetime(2020, 12, 1, 0, 0, tzinfo=pytz.utc)
        create_portfolio_request = models.CreateTransactionPortfolioRequest(
            code=code,
            display_name=code,
            base_currency="GBP",
            created=effective_date,
        )

        # create portfolio
        try:
            await transaction_portfolios_api.create_portfolio(
                scope=scope,
                create_transaction_portfolio_request=create_portfolio_request,
            )
        except lusid.ApiException as e:
            if json.loads(e.body)["name"] == "PortfolioWithIdAlreadyExists":
                self.root_logger.info(
                    f"Portfolio {create_portfolio_request.code} already exists"
                )
        finally:
            id_generator.add_scope_and_code("portfolio", scope, code)

    async def create_txn_with_property(
        self, transaction_portfolios_api, instrument_id, property_value, scope, code
    ):
        # setup the transaction
        effective_date = datetime(2020, 12, 1, 0, 0, tzinfo=pytz.utc).isoformat()
        txn = models.TransactionRequest(
            transaction_id="TXN001",
            type="Buy",
            instrument_identifiers={"Instrument/default/Figi": instrument_id},
            transaction_date=effective_date,
            settlement_date=effective_date,
            units=1000,
            transaction_price=models.TransactionPrice(price=100, type="Price"),
            total_consideration=models.CurrencyAndAmount(amount=1, currency="GBP"),
            exchange_rate=1,
            transaction_currency="GBP",
            properties={
                f"Transaction/{scope}/{code}": lusid.PerpetualProperty(
                    key=f"Transaction/{scope}/{code}",
                    value=lusid.PropertyValue(label_value=property_value),
                )
            },
        )

        return await transaction_portfolios_api.upsert_transactions(
            scope=scope, code=code, transaction_request=[txn]
        )

    async def get_transaction(self, transaction_portfolios_api, scope, code):
        return await transaction_portfolios_api.get_transactions(scope=scope, code=code)

    @pytest.mark.asyncio
    async def test_transaction_property(
        self,
        property_definitions_api,
        id_generator,
        transaction_portfolios_api,
        scope,
        code,
    ):
        # Value for our property
        transaction_tax_data = {"Tax": 1.0, "Rate": 0.01, "Schedule": "A"}
        # Convert property to string representation
        transaction_tax_string = json.dumps(transaction_tax_data)

        # Setup property and portfolio
        await self.create_transaction_property(
            property_definitions_api, id_generator, scope, code
        )
        await self.create_portfolio(
            transaction_portfolios_api, id_generator, scope, code
        )

        # Setup transaction with txn tax details as the property value
        response = await self.create_txn_with_property(
            transaction_portfolios_api,
            "BBG00KTDTF73",
            transaction_tax_string,
            scope,
            code,
        )
        assert response is not None

        # Get transaction with property
        txn_response = await self.get_transaction(
            transaction_portfolios_api, scope=scope, code=code
        )
        assert txn_response is not None

        # Parse property value from transaction and
        # assert is equal to original string object
        queried_property_string = (
            txn_response.values[0]
            .properties[f"Transaction/{scope}/{code}"]
            .value.label_value
        )
        assert queried_property_string is not None
        assert queried_property_string == transaction_tax_string

        # Test individual key-value pairs against original data
        queried_property_dict = json.loads(queried_property_string)
        assert transaction_tax_data["Tax"] == queried_property_dict["Tax"]
        assert transaction_tax_data["Rate"] == queried_property_dict["Rate"]
        assert transaction_tax_data["Schedule"] == queried_property_dict["Schedule"]
