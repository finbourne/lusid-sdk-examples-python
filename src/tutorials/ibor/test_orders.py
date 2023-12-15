import datetime
import json


import lusid
import lusid.models as models
from lusid import OrderRequest
from lusid import OrderSetRequest
from lusid import PerpetualProperty
from lusid import PropertyValue
from lusid import ResourceId
from utilities import DataUtilities

import pytest
import pytest_asyncio


@pytest.fixture(scope="class")
def default_scope(scope="class"):
    return DataUtilities.tutorials_scope


@pytest.fixture(scope="class")
def scopes():
    return {"simple-upsert": "Orders-SimpleUpsert-TestScope"}


@pytest.fixture(scope="class")
def codes():
    return ["TIF", "OrderBook", "PortfolioManager", "Account", "Strategy"]


@pytest_asyncio.fixture(scope="class")
async def load_properties(property_definitions_api, id_generator, scopes, codes):
    for scope in scopes.values():
        for code in codes:
            create_property_definition_request = models.CreatePropertyDefinitionRequest(
                domain="Order",
                scope=scope,
                code=code,
                display_name=code,
                constraint_style="Property",
                data_type_id=lusid.ResourceId(scope="system", code="string"),
            )
            try:
                await property_definitions_api.create_property_definition(
                    create_property_definition_request=create_property_definition_request  # noqa: E501
                )
            except lusid.ApiException as e:
                if json.loads(e.body)["name"] == "PropertyAlreadyExists":
                    pass  # ignore if the property definition exists
            finally:
                id_generator.add_scope_and_code(
                    "property_definition", scope, code, ["Order"]
                )


class TestOrders:
    @pytest.mark.asyncio
    async def test_upsert_simple_order(
        self,
        orders_api,
        instruments_api,
        property_definitions_api,
        instruments,
        load_properties,
        id_generator,
        scopes,
    ):
        """Makes a request for a single order."""

        # Construct order arguments
        instrument_identifiers = {DataUtilities.lusid_luid_identifier: instruments[0]}
        _, orders_scope, order_id = id_generator.generate_scope_and_code(
            "order", scope=scopes["simple-upsert"]
        )

        # Create ResourceId for order
        order_resource_id = models.ResourceId(scope=orders_scope, code=order_id)
        portfolio_id = ResourceId(scope=orders_scope, code="OrdersTestPortfolio")
        properties = {
            f"Order/{orders_scope}/TIF": PerpetualProperty(
                key=f"Order/{orders_scope}/TIF", value=PropertyValue(label_value="GTC")
            ),
            f"Order/{orders_scope}/OrderBook": PerpetualProperty(
                key=f"Order/{orders_scope}/OrderBook",
                value=PropertyValue(label_value="UK Test Orders"),
            ),
            f"Order/{orders_scope}/PortfolioManager": PerpetualProperty(
                key=f"Order/{orders_scope}/PortfolioManager",
                value=PropertyValue(label_value="F Bar"),
            ),
            f"Order/{orders_scope}/Account": PerpetualProperty(
                key=f"Order/{orders_scope}/Account",
                value=PropertyValue(label_value="J Wilson"),
            ),
            f"Order/{orders_scope}/Strategy": PerpetualProperty(
                key=f"Order/{orders_scope}/Strategy",
                value=PropertyValue(label_value="RiskArb"),
            ),
        }

        quantity = 100
        state = "New"
        type = "Limit"
        date = datetime.datetime.fromisoformat("2022-07-05T10:15:30+00:00")
        # Construct request
        order_request = OrderRequest(
            properties=properties,
            instrument_identifiers=instrument_identifiers,
            quantity=quantity,
            side="buy",
            portfolio_id=portfolio_id,
            id=order_resource_id,
            state=state,
            type=type,
            date=date,
        )

        order_set_request = OrderSetRequest(order_requests=[order_request])

        upsert_result = await orders_api.upsert_orders(
            order_set_request=order_set_request
        )

        assert len(upsert_result.values) == 1
        response = upsert_result.values[0].to_dict()
        assert response["id"]["code"] == order_id
        assert response["lusidInstrumentId"] == instruments[0]
        assert response["quantity"] == 100
        assert (
            response["properties"][f"Order/{orders_scope}/TIF"]["key"]
            == f"Order/{orders_scope}/TIF"
        )
