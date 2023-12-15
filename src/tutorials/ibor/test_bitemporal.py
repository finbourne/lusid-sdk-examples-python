from datetime import datetime
from time import sleep

import pytz

from utilities import DataUtilities
import pytest
import pytest_asyncio


@pytest_asyncio.fixture(scope="class")
async def default_scope():
    return DataUtilities.tutorials_scope


class TestBitemporal:
    @pytest.mark.asyncio
    async def test_apply_bitemporal_portfolio_change(
        self,
        test_data_utilities,
        id_generator,
        transaction_portfolios_api,
        portfolios_api,
        instruments,
    ):
        portfolio_code = await test_data_utilities.create_transaction_portfolio(
            DataUtilities.tutorials_scope
        )
        id_generator.add_scope_and_code(
            "portfolio", DataUtilities.tutorials_scope, portfolio_code
        )

        initial_transactions = [
            test_data_utilities.build_transaction_request(
                instrument_id=instruments[0],
                units=100,
                price=101,
                currency="GBP",
                trade_date=datetime(2018, 1, 1, tzinfo=pytz.utc).isoformat(),
                transaction_type="StockIn",
            ),
            test_data_utilities.build_transaction_request(
                instrument_id=instruments[1],
                units=100,
                price=102,
                currency="GBP",
                trade_date=datetime(2018, 1, 2, tzinfo=pytz.utc).isoformat(),
                transaction_type="StockIn",
            ),
            test_data_utilities.build_transaction_request(
                instrument_id=instruments[2],
                units=100,
                price=103,
                currency="GBP",
                trade_date=datetime(2018, 1, 3, tzinfo=pytz.utc).isoformat(),
                transaction_type="StockIn",
            ),
        ]

        # add the initial batch of transactions
        inital_result = await transaction_portfolios_api.upsert_transactions(
            scope=DataUtilities.tutorials_scope,
            code=portfolio_code,
            transaction_request=initial_transactions,
        )

        as_at_1 = inital_result.version.as_at_date
        sleep(0.5)

        # add another trade for 2018-1-8
        new_trade = test_data_utilities.build_transaction_request(
            instrument_id=instruments[3],
            units=100,
            price=104,
            currency="GBP",
            trade_date=datetime(2018, 1, 8, tzinfo=pytz.utc).isoformat(),
            transaction_type="StockIn",
        )
        added_result = await transaction_portfolios_api.upsert_transactions(
            scope=DataUtilities.tutorials_scope,
            code=portfolio_code,
            transaction_request=[new_trade],
        )
        as_at_2 = added_result.version.as_at_date
        sleep(0.5)

        # add back dated trade for 2018-1-5
        backdated_trade = test_data_utilities.build_transaction_request(
            instrument_id=instruments[4],
            units=100,
            price=105,
            currency="GBP",
            trade_date=datetime(2018, 1, 5, tzinfo=pytz.utc).isoformat(),
            transaction_type="StockIn",
        )

        added_result = await transaction_portfolios_api.upsert_transactions(
            scope=DataUtilities.tutorials_scope,
            code=portfolio_code,
            transaction_request=[backdated_trade],
        )

        as_at_3 = added_result.version.as_at_date
        sleep(0.5)

        # as_at_1_str = as_at_1.isoformat()

        # list transactions at initial upload
        transactions = await transaction_portfolios_api.get_transactions(
            scope=DataUtilities.tutorials_scope,
            code=portfolio_code,
            as_at=as_at_1,
        )
        assert len(transactions.values) == 3

        transactions = await transaction_portfolios_api.get_transactions(
            scope=DataUtilities.tutorials_scope,
            code=portfolio_code,
            as_at=as_at_2.isoformat(),
        )

        assert len(transactions.values) == 4

        transactions = await transaction_portfolios_api.get_transactions(
            scope=DataUtilities.tutorials_scope,
            code=portfolio_code,
            as_at=as_at_3.isoformat(),
        )

        assert len(transactions.values) == 5

        transactions = await transaction_portfolios_api.get_transactions(
            scope=DataUtilities.tutorials_scope, code=portfolio_code
        )

        assert len(transactions.values) == 5
