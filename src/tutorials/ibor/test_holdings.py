from datetime import datetime

import pytz

import lusid.models as models
from utilities import DataUtilities
import pytest
import pytest_asyncio


@pytest_asyncio.fixture(scope="class")
async def default_scope():
    return DataUtilities.tutorials_scope


class TestHoldings:
    @pytest.mark.asyncio
    async def test_get_holdings(
        self, test_data_utilities, id_generator, instruments, transaction_portfolios_api
    ):
        # The currency of the cash and transactions
        currency = "GBP"

        # The dates for which transactions are added to the portfolio.
        # All dates/times must be supplied in UTC
        day_t1 = datetime(2018, 1, 1, tzinfo=pytz.utc).isoformat()
        day_tplus5 = datetime(2018, 1, 5, tzinfo=pytz.utc).isoformat()
        day_tplus10 = datetime(2018, 1, 10, tzinfo=pytz.utc).isoformat()

        # Create a portfolio
        portfolio_id = await test_data_utilities.create_transaction_portfolio(
            DataUtilities.tutorials_scope
        )
        id_generator.add_scope_and_code(
            "portfolio", DataUtilities.tutorials_scope, portfolio_id
        )

        transactions = [
            # Starting cash position
            test_data_utilities.build_cash_fundsin_transaction_request(
                100000, currency, day_t1
            ),
            # Initial transaction on day_t1
            test_data_utilities.build_transaction_request(
                instruments[0], 100.0, 101.0, currency, day_t1, "Buy"
            ),
            test_data_utilities.build_transaction_request(
                instruments[1], 100.0, 102.0, currency, day_t1, "Buy"
            ),
            test_data_utilities.build_transaction_request(
                instruments[2], 100.0, 103.0, currency, day_t1, "Buy"
            ),
            # On T+5, add a transaction in another instrument
            # and another to increase the amount of instrument 1
            test_data_utilities.build_transaction_request(
                instruments[1], 100.0, 104.0, currency, day_tplus5, "Buy"
            ),
            test_data_utilities.build_transaction_request(
                instruments[3], 100.0, 105.0, currency, day_tplus5, "Buy"
            ),
        ]

        # Upload the transactions to LUSID
        await transaction_portfolios_api.upsert_transactions(
            DataUtilities.tutorials_scope,
            code=portfolio_id,
            transaction_request=transactions,
        )

        # Get the portfolio holdings on T+10
        holdings = await transaction_portfolios_api.get_holdings(
            DataUtilities.tutorials_scope, portfolio_id, effective_at=day_tplus10
        )

        # Ensure we have 5 holdings: 1 cash position
        # and a position in 4 instruments that aggregates the 5 transactions
        assert len(holdings.values) == 5, "Unexpected number of holdings"

        holdings.values.sort(key=lambda x: x.instrument_uid)

        # Check the cash balance
        assert holdings.values[0].instrument_uid == f"CCY_{currency}"

        # Validate the holdings
        assert holdings.values[0].holding_type == "B"

        assert holdings.values[1].holding_type == "P", "Incorrect holding type"
        assert (
            holdings.values[1].instrument_uid == instruments[0]
        ), "Incorrect instrument id"

        assert holdings.values[1].units == 100.0, "Incorrect units"
        assert holdings.values[1].cost.amount == 10100.0, "Incorrect amount"

        assert holdings.values[2].holding_type == "P", "Incorrect holding type"

        assert (
            holdings.values[2].instrument_uid == instruments[1]
        ), "Incorrect instrument id"
        assert holdings.values[2].units == 200.0, "Incorrect units"
        assert holdings.values[2].cost.amount == 20600.0, "Incorrect amount"

        assert holdings.values[3].holding_type == "P", "Incorrect holding type"
        assert (
            holdings.values[3].instrument_uid == instruments[2]
        ), "Incorrect instrument id"
        assert holdings.values[3].units == 100.0, "Incorrect units"
        assert holdings.values[3].cost.amount == 10300.0, "Incorrect amount"

        assert holdings.values[4].holding_type == "P", "Incorrect holding type"
        assert (
            holdings.values[4].instrument_uid == instruments[3]
        ), "Incorrect instrument id"

        assert holdings.values[4].units == 100.0, "Incorrect units"
        assert holdings.values[4].cost.amount == 10500.0, "Incorrect amount"

    @pytest.mark.asyncio
    async def test_set_target_holdings(
        self, test_data_utilities, id_generator, instruments, transaction_portfolios_api
    ):
        currency = "GBP"

        day1 = datetime(2018, 1, 1, tzinfo=pytz.utc).isoformat()
        day2 = datetime(2018, 1, 5, tzinfo=pytz.utc).isoformat()

        portfolio_code = await test_data_utilities.create_transaction_portfolio(
            DataUtilities.tutorials_scope
        )
        id_generator.add_scope_and_code(
            "portfolio", DataUtilities.tutorials_scope, portfolio_code
        )

        instrument1 = instruments[0]
        instrument2 = instruments[1]
        instrument3 = instruments[2]

        holdings_adjustments = [
            # cash balance
            models.AdjustHoldingRequest(
                instrument_identifiers={DataUtilities.lusid_cash_identifier: currency},
                tax_lots=[models.TargetTaxLotRequest(units=100000.0)],
            ),
            # instrument 1
            models.AdjustHoldingRequest(
                instrument_identifiers={
                    DataUtilities.lusid_luid_identifier: instrument1
                },
                tax_lots=[
                    models.TargetTaxLotRequest(
                        units=100.0,
                        price=101.0,
                        cost=models.CurrencyAndAmount(
                            amount=10100.0, currency=currency
                        ),
                        portfolio_cost=10100.0,
                        purchase_date=day1,
                        settlement_date=day1,
                    )
                ],
            ),
            # instrument 2
            models.AdjustHoldingRequest(
                instrument_identifiers={
                    DataUtilities.lusid_luid_identifier: instrument2
                },
                tax_lots=[
                    models.TargetTaxLotRequest(
                        units=100.0,
                        price=102.0,
                        cost=models.CurrencyAndAmount(
                            amount=10200.0, currency=currency
                        ),
                        portfolio_cost=10200.0,
                        purchase_date=day1,
                        settlement_date=day1,
                    )
                ],
            ),
        ]

        # set the initial holdings on day 1
        await transaction_portfolios_api.set_holdings(
            scope=DataUtilities.tutorials_scope,
            code=portfolio_code,
            adjust_holding_request=holdings_adjustments,
            effective_at=day1,
        )

        # add subsequent transactions on day 2
        transactions = [
            test_data_utilities.build_transaction_request(
                instrument_id=instrument1,
                units=100.0,
                price=104.0,
                currency=currency,
                trade_date=day2,
                transaction_type="Buy",
            ),
            test_data_utilities.build_transaction_request(
                instrument_id=instrument3,
                units=100.0,
                price=103.0,
                currency=currency,
                trade_date=day2,
                transaction_type="Buy",
            ),
        ]

        await transaction_portfolios_api.upsert_transactions(
            scope=DataUtilities.tutorials_scope,
            code=portfolio_code,
            transaction_request=transactions,
        )

        # get the holdings for day 2
        holdings = await transaction_portfolios_api.get_holdings(
            scope=DataUtilities.tutorials_scope,
            code=portfolio_code,
            effective_at=day2,
        )

        # sort to put the cash instrument first
        holdings.values.sort(key=lambda i: i.instrument_uid)

        # cash balance + 3 holdings
        assert len(holdings.values) == 4

        # remaining cash balance which takes
        # into account the purchase transactions on day 2

        # the call to GetHoldings returns the LUID not the identifier we created
        currency_luid = f"CCY_{currency}"

        # cash
        assert holdings.values[0].instrument_uid == currency_luid
        assert holdings.values[0].units == 79300.0

        # instrument 1 - initial holding + transaction on day 2
        assert holdings.values[1].instrument_uid == instrument1
        assert holdings.values[1].units == 200.0
        assert holdings.values[1].cost.amount == 20500.0

        # instrument 2 - initial holding
        assert holdings.values[2].instrument_uid == instrument2
        assert holdings.values[2].units == 100.0
        assert holdings.values[2].cost.amount == 10200.0

        # instrument 3 - transaction on day 2
        assert holdings.values[3].instrument_uid == instrument3
        assert holdings.values[3].units == 100.0
        assert holdings.values[3].cost.amount == 10300.0
