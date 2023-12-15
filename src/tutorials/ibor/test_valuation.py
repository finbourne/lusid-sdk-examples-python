from datetime import datetime

import pytz

import lusid.models as models


from utilities import DataUtilities
import pytest


@pytest.fixture(scope="class")
def default_scope(scope="class"):
    return DataUtilities.tutorials_scope


class TestValuation:
    @pytest.mark.asyncio
    async def test_portfolio_aggregation(
        self,
        data_utilities,
        id_generator,
        instruments,
        transaction_portfolios_api,
        quotes_api,
        recipes_api,
        aggregation_api,
    ):
        effective_date = datetime(2019, 4, 15, tzinfo=pytz.utc).isoformat()

        portfolio_code = await data_utilities.create_transaction_portfolio(
            DataUtilities.tutorials_scope
        )
        id_generator.add_scope_and_code(
            "portfolio", DataUtilities.tutorials_scope, portfolio_code
        )

        transactions = [
            data_utilities.build_transaction_request(
                instrument_id=instruments[0],
                units=100,
                price=101,
                currency="GBP",
                trade_date=effective_date,
                transaction_type="StockIn",
            ),
            data_utilities.build_transaction_request(
                instrument_id=instruments[1],
                units=100,
                price=102,
                currency="GBP",
                trade_date=effective_date,
                transaction_type="StockIn",
            ),
            data_utilities.build_transaction_request(
                instrument_id=instruments[2],
                units=100,
                price=103,
                currency="GBP",
                trade_date=effective_date,
                transaction_type="StockIn",
            ),
        ]

        await transaction_portfolios_api.upsert_transactions(
            scope=DataUtilities.tutorials_scope,
            code=portfolio_code,
            transaction_request=transactions,
        )

        prices = [
            (instruments[0], 100),
            (instruments[1], 200),
            (instruments[2], 300),
        ]

        requests = [
            models.UpsertQuoteRequest(
                quote_id=models.QuoteId(
                    quote_series_id=models.QuoteSeriesId(
                        provider="DataScope",
                        instrument_id=price[0],
                        instrument_id_type="LusidInstrumentId",
                        quote_type="Price",
                        field="mid",
                    ),
                    effective_at=effective_date,
                ),
                metric_value=models.MetricValue(value=price[1], unit="GBP"),
            )
            for price in prices
        ]

        await quotes_api.upsert_quotes(
            DataUtilities.tutorials_scope,
            request_body={
                "quote" + str(request_number): requests[request_number]
                for request_number in range(len(requests))
            },
        )

        recipe_scope = "cs-tutorials"
        recipe_code = "quotes_recipe"

        id_generator.add_scope_and_code("recipe", recipe_scope, recipe_code)

        demo_recipe = models.ConfigurationRecipe(
            scope=recipe_scope,
            code=recipe_code,
            market=models.MarketContext(
                market_rules=[],
                suppliers=models.MarketContextSuppliers(equity="DataScope"),
                options=models.MarketOptions(
                    default_supplier="DataScope",
                    default_instrument_code_type="LusidInstrumentId",
                    default_scope=DataUtilities.tutorials_scope,
                ),
            ),
        )
        upsert_recipe_request = models.UpsertRecipeRequest(
            configuration_recipe=demo_recipe
        )
        await recipes_api.upsert_configuration_recipe(upsert_recipe_request)

        valuation_request = models.ValuationRequest(
            recipe_id=models.ResourceId(scope=recipe_scope, code=recipe_code),
            metrics=[
                models.AggregateSpec(key="Instrument/default/Name", op="Value"),
                models.AggregateSpec(key="Valuation/PV", op="Proportion"),
                models.AggregateSpec(key="Valuation/PV", op="Sum"),
            ],
            group_by=["Instrument/default/Name"],
            portfolio_entity_ids=[
                models.PortfolioEntityId(
                    scope=DataUtilities.tutorials_scope, code=portfolio_code
                )
            ],
            valuation_schedule=models.ValuationSchedule(effective_at=effective_date),
        )

        #   do the aggregation
        aggregation = await aggregation_api.get_valuation(
            valuation_request=valuation_request
        )

        # Asserts
        assert len(aggregation.data) == 3
        assert aggregation.data[0]["Sum(Valuation/PV)"] == 10000
        assert aggregation.data[1]["Sum(Valuation/PV)"] == 20000
        assert aggregation.data[2]["Sum(Valuation/PV)"] == 30000
