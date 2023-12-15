import uuid
from datetime import datetime

import pytz


import lusid.models as models
from utilities import DataUtilities
import pytest


@pytest.fixture(scope="class")
def default_scope(scope="class"):
    return DataUtilities.tutorials_scope


class TestTransactions:
    @pytest.mark.asyncio
    async def test_load_listed_instrument_transaction(
        self, data_utilities, id_generator, instruments, transaction_portfolios_api
    ):
        # create the portfolio
        portfolio_code = await data_utilities.create_transaction_portfolio(
            DataUtilities.tutorials_scope
        )
        id_generator.add_scope_and_code(
            "portfolio", DataUtilities.tutorials_scope, portfolio_code
        )

        trade_date = datetime(2018, 1, 1, tzinfo=pytz.utc).isoformat()

        #   details of the transaction to be added
        transaction = models.TransactionRequest(
            # unique transaction id
            transaction_id=str(uuid.uuid4()),
            # transaction type, configured during system setup
            type="Buy",
            instrument_identifiers={
                DataUtilities.lusid_luid_identifier: instruments[0]
            },
            transaction_date=trade_date,
            settlement_date=trade_date,
            units=100,
            transaction_price=models.TransactionPrice(price=12.3),
            total_consideration=models.CurrencyAndAmount(amount=1230, currency="GBP"),
            source="Client",
        )

        # add the transaction
        await transaction_portfolios_api.upsert_transactions(
            scope=DataUtilities.tutorials_scope,
            code=portfolio_code,
            transaction_request=[transaction],
        )

        # get the transaction
        transactions = await transaction_portfolios_api.get_transactions(
            scope=DataUtilities.tutorials_scope, code=portfolio_code
        )

        assert len(transactions.values) == 1
        assert transactions.values[0].transaction_id == transaction.transaction_id

    @pytest.mark.asyncio
    async def test_load_cash_transaction(
        self, data_utilities, id_generator, transaction_portfolios_api
    ):
        # create the portfolio
        portfolio_code = await data_utilities.create_transaction_portfolio(
            DataUtilities.tutorials_scope
        )
        id_generator.add_scope_and_code(
            "portfolio", DataUtilities.tutorials_scope, portfolio_code
        )

        trade_date = datetime(2018, 1, 1, tzinfo=pytz.utc).isoformat()

        #   details of the transaction to be added
        transaction = models.TransactionRequest(
            # unique transaction id
            transaction_id=str(uuid.uuid4()),
            # transaction type, configured during system setup
            type="FundsIn",
            # Cash instruments are identified
            # using CCY_ followed by the ISO currency codes.
            # Cash instruments do not need to be created before use
            instrument_identifiers={DataUtilities.lusid_cash_identifier: "GBP"},
            transaction_date=trade_date,
            settlement_date=trade_date,
            transaction_price=models.TransactionPrice(price=0.0),
            units=0,
            total_consideration=models.CurrencyAndAmount(amount=0, currency="GBP"),
            source="Client",
        )

        # add the transaction
        await transaction_portfolios_api.upsert_transactions(
            scope=DataUtilities.tutorials_scope,
            code=portfolio_code,
            transaction_request=[transaction],
        )

        # get the transaction
        transactions = await transaction_portfolios_api.get_transactions(
            scope=DataUtilities.tutorials_scope, code=portfolio_code
        )

        assert len(transactions.values) == 1
        assert transactions.values[0].transaction_id == transaction.transaction_id

    @pytest.mark.asyncio
    async def test_cancel_transactions(
        self, data_utilities, id_generator, instruments, transaction_portfolios_api
    ):
        # set effective date
        effective_date = datetime(2018, 1, 1, tzinfo=pytz.utc).isoformat()

        # create portfolio code
        portfolio_code = await data_utilities.create_transaction_portfolio(
            DataUtilities.tutorials_scope
        )
        id_generator.add_scope_and_code(
            "portfolio", DataUtilities.tutorials_scope, portfolio_code
        )

        # Upsert transactions
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

        # get transactions
        transaction_ids = []
        existing_transactions = await transaction_portfolios_api.get_transactions(
            scope=DataUtilities.tutorials_scope, code=portfolio_code
        )

        for i in range(len(existing_transactions.values)):
            transaction_ids.append(existing_transactions.values[i].transaction_id)

        # cancel transactions
        await transaction_portfolios_api.cancel_transactions(
            scope=DataUtilities.tutorials_scope,
            code=portfolio_code,
            transaction_ids=transaction_ids,
        )

        # verify portfolio is now empty
        new_transactions = await transaction_portfolios_api.get_transactions(
            scope=DataUtilities.tutorials_scope, code=portfolio_code
        )
        assert len(new_transactions.values) == 0
