from datetime import datetime

import pytz


import lusid.models as models
from utilities import DataUtilities
import pytest


@pytest.fixture(scope="class")
def default_scope(scope="class"):
    return DataUtilities.tutorials_scope


class TestReferencePortfolio:
    @pytest.mark.asyncio
    async def test_create_reference_portfolio(
        self, id_generator, reference_portfolio_api
    ):
        _, _, portfolio_code = id_generator.generate_scope_and_code("portfolio")
        f39_reference_portfolio_name = "F39p_Reference Portfolio Name"

        # Details of the new reference portfolio to be created
        request = models.CreateReferencePortfolioRequest(
            display_name=f39_reference_portfolio_name,
            code=portfolio_code,
        )

        # Create the reference portfolio in LUSID in the tutorials scope
        result = await reference_portfolio_api.create_reference_portfolio(
            scope=DataUtilities.tutorials_scope,
            create_reference_portfolio_request=request,
        )

        assert result.id.code == request.code

    @pytest.mark.asyncio
    async def test_upsert_reference_portfolio_constituents(
        self, id_generator, reference_portfolio_api, instruments
    ):
        constituent_weights = [10, 20, 30, 15, 25]
        effective_date = datetime(
            year=2021, month=3, day=29, tzinfo=pytz.UTC
        ).isoformat()

        _, _, portfolio_code = id_generator.generate_scope_and_code("portfolio")
        f40_reference_portfolio_name = "F40p_Reference Portfolio Name"

        # Create a new reference portfolio
        request = models.CreateReferencePortfolioRequest(
            display_name=f40_reference_portfolio_name,
            code=portfolio_code,
            created=effective_date,
        )

        await reference_portfolio_api.create_reference_portfolio(
            scope=DataUtilities.tutorials_scope,
            create_reference_portfolio_request=request,
        )

        # Check that all instruments were created successfully
        assert len(constituent_weights) == len(instruments)

        # Create the constituent requests
        individual_constituent_requests = [
            models.ReferencePortfolioConstituentRequest(
                instrument_identifiers={
                    DataUtilities.lusid_luid_identifier: instrument_id
                },
                weight=constituent_weight,
                currency="GBP",
            )
            for instrument_id, constituent_weight in zip(
                instruments, constituent_weights
            )
        ]

        # Create a bulk constituent upsert request
        bulk_constituent_request = models.UpsertReferencePortfolioConstituentsRequest(
            effective_from=effective_date,
            weight_type="Static",
            constituents=individual_constituent_requests,
        )

        # Make the upsert request via the reference portfolio API
        await reference_portfolio_api.upsert_reference_portfolio_constituents(
            scope=DataUtilities.tutorials_scope,
            code=portfolio_code,
            upsert_reference_portfolio_constituents_request=bulk_constituent_request,
        )

        # Get reference portfolio holdings
        constituent_holdings = (
            await reference_portfolio_api.get_reference_portfolio_constituents(
                scope=DataUtilities.tutorials_scope,
                code=portfolio_code,
            )
        )

        # Validate count of holdings
        assert len(constituent_holdings.constituents) == 5

        # Validate instruments on holdings
        for constituent, upserted_instrument in zip(
            constituent_holdings.constituents, instruments
        ):
            assert constituent.instrument_uid == upserted_instrument

        # Validate holding weights
        for constituent, weight in zip(
            constituent_holdings.constituents, constituent_weights
        ):
            assert constituent.weight == weight
