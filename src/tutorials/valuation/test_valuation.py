from datetime import datetime
import pytz

import lusid
import lusid.models as models
from utilities import DataUtilities
import pytest
import pytest_asyncio


@pytest_asyncio.fixture(scope="class")
async def default_scope():
    return DataUtilities.tutorials_scope


@pytest_asyncio.fixture(scope="class")
async def portfolio_code(default_scope, data_utilities, portfolios_api):
    portfolio_code = await data_utilities.create_transaction_portfolio(
        DataUtilities.tutorials_scope
    )
    yield portfolio_code
    await portfolios_api.delete_portfolio(DataUtilities.tutorials_scope, portfolio_code)


@pytest.fixture
def effective_date():
    return datetime(2019, 4, 15, tzinfo=pytz.utc).isoformat()


class TestValuation:
    @pytest_asyncio.fixture
    async def setup_portfolio(
        self,
        effective_date,
        portfolio_code,
        data_utilities,
        instruments,
        transaction_portfolios_api,
        quotes_api,
    ) -> None:
        """
        Sets up instrument, quotes and portfolio data from DataUtilities
        :param datetime effective_date: The portfolio creation date
        :param str portfolio_code: The code of the test portfolio
        :return: None
        """
        print(effective_date)

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
                        provider="Lusid",
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

    def create_configuration_recipe(
        self, recipe_scope, recipe_code
    ) -> lusid.models.ConfigurationRecipe:
        """
        Creates a configuration recipe that can be used inline or upserted
        :param str recipe_scope: The scope for the configuration recipe
        :param str recipe_code: The code of the configuration recipe
        :return: ConfigurationRecipe
        """

        return models.ConfigurationRecipe(
            scope=recipe_scope,
            code=recipe_code,
            market=models.MarketContext(
                market_rules=[],
                suppliers=models.MarketContextSuppliers(equity="Lusid"),
                options=models.MarketOptions(
                    default_supplier="Lusid",
                    default_instrument_code_type="LusidInstrumentId",
                    default_scope=DataUtilities.tutorials_scope,
                ),
            ),
        )

    async def upsert_recipe_request(self, configuration_recipe, recipes_api) -> None:
        """
        Structures a recipe request and upserts it into LUSID
        :param ConfigurationRecipe configuration_recipe: Recipe configuration
        :return: None
        """

        upsert_recipe_request = models.UpsertRecipeRequest(
            configuration_recipe=configuration_recipe
        )
        await recipes_api.upsert_configuration_recipe(upsert_recipe_request)

    @pytest.mark.asyncio
    async def test_aggregation(
        self,
        setup_portfolio,
        recipes_api,
        aggregation_api,
        effective_date,
        portfolio_code,
    ) -> None:
        """
        General valuation/aggregation test
        """
        # create recipe (provides model parameters,
        # locations to use in resolving market data etc. and push it into LUSID.
        # Only needs to happen once each time when updated, or first time run to create.
        recipe_scope, recipe_code = (
            "TestRecipes",
            "SimpleQuotes",
        )
        recipe = self.create_configuration_recipe(recipe_scope, recipe_code)
        await self.upsert_recipe_request(recipe, recipes_api)

        # Set valuation result key
        valuation_key = "Sum(Valuation/PV)"

        # create valuation request
        valuation_request = models.ValuationRequest(
            recipe_id=models.ResourceId(scope=recipe_scope, code=recipe_code),
            metrics=[
                models.AggregateSpec(key="Instrument/default/Name", op="Value"),
                models.AggregateSpec(key="Valuation/PV", op="Proportion"),
                models.AggregateSpec(key="Valuation/PV", op="Sum"),
            ],
            group_by=["Instrument/default/Name"],
            valuation_schedule=models.ValuationSchedule(effective_at=effective_date),
            portfolio_entity_ids=[
                models.PortfolioEntityId(
                    scope=DataUtilities.tutorials_scope, code=portfolio_code
                )
            ],
        )

        # Complete aggregation
        aggregation = await aggregation_api.get_valuation(
            valuation_request=valuation_request
        )

        # Asserts
        assert len(aggregation.data) == 3
        assert aggregation.data[0][valuation_key] == 10000
        assert aggregation.data[1][valuation_key] == 20000
        assert aggregation.data[2][valuation_key] == 30000
