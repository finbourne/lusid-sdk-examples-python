import uuid
from datetime import date, timedelta

import lusid.models as models
from lusid import ApiException
from utilities import DataUtilities
import pytest_asyncio
import pytest
import asyncio


@pytest_asyncio.fixture(scope="class")
async def default_scope():
    return DataUtilities.tutorials_scope


class TestCutLabels:
    @pytest.mark.asyncio
    async def test_cut_labels(
        self,
        id_generator,
        cut_label_definitions_api,
        data_utilities,
        instruments,
        transaction_portfolios_api,
    ):
        def get_guid():
            return str(uuid.uuid4())[:4]

        # define function to format cut labels
        def cut_label_formatter(date, cut_label_code):
            return str(date) + "N" + cut_label_code

        # Create cut labels
        code = {}

        async def create_cut_label(
            hours, minutes, display_name, description, time_zone, code_dict
        ):
            # Create the time for the cut label
            time = models.CutLocalTime(hours=hours, minutes=minutes)

            cut_label_code = display_name + "-" + get_guid()

            id_generator.add_scope_and_code(
                "cut_label", DataUtilities.tutorials_scope, cut_label_code
            )

            # Define the parameters of the cut label in a request
            request = models.CutLabelDefinition(
                code=cut_label_code,
                description=description,
                display_name=display_name,
                cut_local_time=time,
                time_zone=time_zone,
            )

            # Add the codes of our cut labels to our dictionary
            code_dict[request.display_name] = request.code

            # Send the request to LUSID to create the cut label
            result = request
            try:
                result = await cut_label_definitions_api.create_cut_label_definition(
                    create_cut_label_definition_request=request
                )
            except ApiException as ex:
                if ex.status != 409:
                    raise

            # Check that result gives same details as input
            assert result.display_name == display_name
            assert result.description == description
            assert result.cut_local_time == time
            assert result.time_zone == time_zone

        # Create cut labels for different time zones
        tasks = [
            create_cut_label(
                hours=9,
                minutes=0,
                display_name="LondonOpen",
                description="London Opening Time, 9am in UK",
                time_zone="GB",
                code_dict=code,
            ),
            create_cut_label(
                hours=17,
                minutes=0,
                display_name="LondonClose",
                description="London Closing Time, 5pm in UK",
                time_zone="GB",
                code_dict=code,
            ),
            create_cut_label(
                hours=9,
                minutes=0,
                display_name="SingaporeOpen",
                description="",
                time_zone="Singapore",
                code_dict=code,
            ),
            create_cut_label(
                hours=17,
                minutes=0,
                display_name="SingaporeClose",
                description="",
                time_zone="Singapore",
                code_dict=code,
            ),
            create_cut_label(
                hours=9,
                minutes=0,
                display_name="NYOpen",
                description="",
                time_zone="America/New_York",
                code_dict=code,
            ),
            create_cut_label(
                hours=17,
                minutes=0,
                display_name="NYClose",
                description="",
                time_zone="America/New_York",
                code_dict=code,
            ),
        ]
        await asyncio.gather(*tasks)
        # Create portfolio
        portfolio_code = await data_utilities.create_transaction_portfolio(
            DataUtilities.tutorials_scope
        )
        id_generator.add_scope_and_code(
            "portfolio", DataUtilities.tutorials_scope, portfolio_code
        )

        # Get the instrument identifiers
        instrument1 = instruments[0]
        instrument2 = instruments[1]
        instrument3 = instruments[2]

        currency = "GBP"

        # set a currency LUID, as the call to GetHoldings
        # returns the LUID not the identifier we are about to create
        currency_luid = "CCY_{}".format(currency)

        # Set initial holdings for each instrument from LondonOpen 5 days ago
        initial_holdings_cut_label = cut_label_formatter(
            date.today() - timedelta(days=5), code["LondonOpen"]
        )
        initial_holdings = [
            # cash balance
            data_utilities.build_cash_funds_in_adjust_holdings_request(
                currency=currency, units=100000.0
            ),
            # instrument 1
            data_utilities.build_adjust_holdings_request(
                instrument_id=instrument1,
                units=100.0,
                price=101.0,
                currency=currency,
                trade_date=None,
            ),
            # instrument 2
            data_utilities.build_adjust_holdings_request(
                instrument_id=instrument2,
                units=100.0,
                price=102.0,
                currency=currency,
                trade_date=None,
            ),
            # instrument 3
            data_utilities.build_adjust_holdings_request(
                instrument_id=instrument3,
                units=100.0,
                price=99.0,
                currency=currency,
                trade_date=None,
            ),
        ]
        # add initial holdings to our portfolio from LondonOpen 5 days ago
        await transaction_portfolios_api.set_holdings(
            scope=DataUtilities.tutorials_scope,
            code=portfolio_code,
            adjust_holding_request=initial_holdings,
            effective_at=initial_holdings_cut_label,
        )

        # Check initial holdings
        # get holdings at LondonOpen today, before transactions occur
        get_holdings_cut_label = cut_label_formatter(date.today(), code["LondonOpen"])
        holdings = await transaction_portfolios_api.get_holdings(
            scope=DataUtilities.tutorials_scope,
            code=portfolio_code,
            effective_at=get_holdings_cut_label,
        )
        # check that holdings are as expected before
        # transactions occur for each instrument
        holdings.values.sort(key=lambda i: i.instrument_uid)
        assert len(holdings.values) == 4
        data_utilities.TestDataUtilities.assert_cash_holdings(
            holdings=holdings, index=0, instrument_id=currency_luid, units=100000.0
        )
        data_utilities.TestDataUtilities.assert_holdings(
            holdings=holdings,
            index=1,
            instrument_id=instrument1,
            units=100.0,
            cost_amount=10100.0,
        )
        data_utilities.TestDataUtilities.assert_holdings(
            holdings=holdings,
            index=2,
            instrument_id=instrument2,
            units=100.0,
            cost_amount=10200.0,
        )
        data_utilities.TestDataUtilities.assert_holdings(
            holdings=holdings,
            index=3,
            instrument_id=instrument3,
            units=100.0,
            cost_amount=9900.0,
        )

        # Add transactions at different times in
        # different time zones during the day with cut labels
        transaction_1_cut_label = cut_label_formatter(date.today(), code["LondonOpen"])
        transaction_2_cut_label = cut_label_formatter(
            date.today(), code["SingaporeClose"]
        )
        transaction_3_cut_label = cut_label_formatter(date.today(), code["NYOpen"])
        transaction_4_cut_label = cut_label_formatter(date.today(), code["NYClose"])
        transactions = [
            data_utilities.build_transaction_request(
                instrument_id=instrument1,
                units=100.0,
                price=100.0,
                currency=currency,
                trade_date=transaction_1_cut_label,
                transaction_type="Buy",
            ),
            data_utilities.build_transaction_request(
                instrument_id=instrument2,
                units=100.0,
                price=100.0,
                currency=currency,
                trade_date=transaction_2_cut_label,
                transaction_type="Buy",
            ),
            data_utilities.build_transaction_request(
                instrument_id=instrument3,
                units=100.0,
                price=100.0,
                currency=currency,
                trade_date=transaction_3_cut_label,
                transaction_type="Buy",
            ),
            data_utilities.build_transaction_request(
                instrument_id=instrument1,
                units=100.0,
                price=100.0,
                currency=currency,
                trade_date=transaction_4_cut_label,
                transaction_type="Buy",
            ),
        ]
        # Add transactions to the portfolio
        await transaction_portfolios_api.upsert_transactions(
            scope=DataUtilities.tutorials_scope,
            code=portfolio_code,
            transaction_request=transactions,
        )

        # Retrieve holdings at LondonClose today (5pm local time)
        # This will mean that the 4th transaction will not be included,
        # demonstrating how cut labels work across time zones
        get_holdings_cut_label = cut_label_formatter(date.today(), code["LondonClose"])
        holdings = await transaction_portfolios_api.get_holdings(
            scope=DataUtilities.tutorials_scope,
            code=portfolio_code,
            effective_at=get_holdings_cut_label,
        )

        # check that holdings are as expected after transactions for each instrument
        holdings.values.sort(key=lambda i: i.instrument_uid)
        assert len(holdings.values) == 4
        data_utilities.TestDataUtilities.assert_cash_holdings(
            holdings=holdings, index=0, instrument_id=currency_luid, units=70000.0
        )
        data_utilities.TestDataUtilities.assert_holdings(
            holdings=holdings,
            index=1,
            instrument_id=instrument1,
            units=200.0,
            cost_amount=20100.0,
        )
        data_utilities.TestDataUtilities.assert_holdings(
            holdings=holdings,
            index=2,
            instrument_id=instrument2,
            units=200.0,
            cost_amount=20200.0,
        )
        data_utilities.TestDataUtilities.assert_holdings(
            holdings=holdings,
            index=3,
            instrument_id=instrument3,
            units=200.0,
            cost_amount=19900.0,
        )
