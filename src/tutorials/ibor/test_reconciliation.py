from datetime import datetime, timedelta

import pytz


import lusid.models as models
from utilities import DataUtilities
import pytest


@pytest.fixture(scope="class")
def default_scope(scope="class"):
    return DataUtilities.tutorials_scope


class TestReconciliation:
    @pytest.mark.asyncio
    async def test_reconcile_portfolio(
        self,
        id_generator,
        data_utilities,
        instruments,
        transaction_portfolios_api,
        reconciliations_api,
    ):
        # create the portfolio
        scope = DataUtilities.tutorials_scope
        portfolio_code = await data_utilities.create_transaction_portfolio(scope)
        id_generator.add_scope_and_code("portfolio", scope, portfolio_code)

        today = datetime.now().astimezone(tz=pytz.utc)
        yesterday = today - timedelta(1)

        # create transactions for yesterday
        yesterdays_transactions = [
            data_utilities.build_transaction_request(
                instrument_id=instruments[0],
                units=1000.0,
                price=100.0,
                currency="GBP",
                trade_date=(yesterday + timedelta(hours=8)).isoformat(),
                transaction_type="StockIn",
            ),
            data_utilities.build_transaction_request(
                instrument_id=instruments[0],
                units=2300.0,
                price=101.0,
                currency="GBP",
                trade_date=(yesterday + timedelta(hours=12)).isoformat(),
                transaction_type="StockIn",
            ),
            data_utilities.build_transaction_request(
                instrument_id=instruments[1],
                units=-1000.0,
                price=102.0,
                currency="GBP",
                trade_date=(yesterday + timedelta(hours=9)).isoformat(),
                transaction_type="StockIn",
            ),
            data_utilities.build_transaction_request(
                instrument_id=instruments[2],
                units=1200.0,
                price=103.0,
                currency="GBP",
                trade_date=(yesterday + timedelta(hours=16)).isoformat(),
                transaction_type="StockIn",
            ),
            data_utilities.build_transaction_request(
                instrument_id=instruments[3],
                units=2000.0,
                price=103.0,
                currency="GBP",
                trade_date=(yesterday + timedelta(hours=9)).isoformat(),
                transaction_type="StockIn",
            ),
        ]

        # add the transactions to LUSID
        await transaction_portfolios_api.upsert_transactions(
            scope=DataUtilities.tutorials_scope,
            code=portfolio_code,
            transaction_request=yesterdays_transactions,
        )

        # transactions for today
        todays_transactions = [
            # net long 300
            data_utilities.build_transaction_request(
                instrument_id=instruments[0],
                units=-3000.0,
                price=101.78,
                currency="GBP",
                trade_date=(today + timedelta(hours=8)).isoformat(),
                transaction_type="StockIn",
            ),
            # net long 1800
            data_utilities.build_transaction_request(
                instrument_id=instruments[0],
                units=1500.0,
                price=101.78,
                currency="GBP",
                trade_date=(today + timedelta(hours=12)).isoformat(),
                transaction_type="StockIn",
            ),
            # flat
            data_utilities.build_transaction_request(
                instrument_id=instruments[1],
                units=1000.0,
                price=102.0,
                currency="GBP",
                trade_date=(today + timedelta(hours=12)).isoformat(),
                transaction_type="StockIn",
            ),
            # net long 2400
            data_utilities.build_transaction_request(
                instrument_id=instruments[2],
                units=1200.0,
                price=103.0,
                currency="GBP",
                trade_date=(today + timedelta(hours=16)).isoformat(),
                transaction_type="StockIn",
            ),
            # net long 3000
            data_utilities.build_transaction_request(
                instrument_id=instruments[3],
                units=1000.0,
                price=103.0,
                currency="GBP",
                trade_date=(today + timedelta(hours=9)).isoformat(),
                transaction_type="StockIn",
            ),
            # net long 5000
            data_utilities.build_transaction_request(
                instrument_id=instruments[3],
                units=2000.0,
                price=103.0,
                currency="GBP",
                trade_date=(today + timedelta(hours=20)).isoformat(),
                transaction_type="StockIn",
            ),
        ]

        # add the transactions to LUSID
        transactions_response = await transaction_portfolios_api.upsert_transactions(
            scope=DataUtilities.tutorials_scope,
            code=portfolio_code,
            transaction_request=todays_transactions,
        )

        # get the time of the last update
        last_as_at = transactions_response.version.as_at_date

        # We now have the portfolio with 2 days worth of transactions,
        # going to reconcile from T-1 20:00 to now,
        # this should reflect breaks for each instrument equal
        # to the transactions from yesterday till 20:00 today
        reconciliation_request = models.PortfoliosReconciliationRequest(
            left=models.PortfolioReconciliationRequest(
                portfolio_id=models.ResourceId(
                    scope=DataUtilities.tutorials_scope, code=portfolio_code
                ),
                effective_at=(yesterday + timedelta(hours=20)).isoformat(),
                as_at=last_as_at,
            ),
            right=models.PortfolioReconciliationRequest(
                portfolio_id=models.ResourceId(
                    scope=DataUtilities.tutorials_scope, code=portfolio_code
                ),
                effective_at=(today + timedelta(hours=16)).isoformat(),
                as_at=last_as_at,
            ),
            instrument_property_keys=[DataUtilities.lusid_luid_identifier],
        )

        breaks = await reconciliations_api.reconcile_holdings(
            portfolios_reconciliation_request=reconciliation_request
        )

        rec_map = {b.instrument_uid: b for b in breaks.values}

        assert -1500 == rec_map[instruments[0]].difference_units
        assert 1000 == rec_map[instruments[1]].difference_units
        assert 1200 == rec_map[instruments[2]].difference_units
        assert 1000 == rec_map[instruments[3]].difference_units
