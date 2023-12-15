from datetime import datetime, timedelta

import pytz as pytz

import lusid.models as models

from utilities import DataUtilities
import pytest
import asyncio


class TestQuotes:
    @pytest.mark.asyncio
    async def test_add_quote(self, quotes_api):
        request = models.UpsertQuoteRequest(
            quote_id=models.QuoteId(
                quote_series_id=models.QuoteSeriesId(
                    provider="DataScope",
                    instrument_id="BBG000B9XRY4",
                    instrument_id_type="Figi",
                    quote_type="Price",
                    field="mid",
                ),
                effective_at=datetime(2019, 4, 15, tzinfo=pytz.utc).isoformat(),
            ),
            metric_value=models.MetricValue(value=199.23, unit="USD"),
        )

        await quotes_api.upsert_quotes(
            DataUtilities.tutorials_scope, request_body={"quote1": request}
        )

    @pytest.mark.asyncio
    async def test_get_quote_for_instrument_for_single_day(self, quotes_api):
        quote_series_id = models.QuoteSeriesId(
            provider="DataScope",
            instrument_id="BBG000B9XRY4",
            instrument_id_type="Figi",
            quote_type="Price",
            field="mid",
        )

        effective_date = datetime(2019, 4, 15, tzinfo=pytz.utc)

        # get the close quote for AAPL on 15-Apr-19
        quote_response = await quotes_api.get_quotes(
            scope=DataUtilities.tutorials_scope,
            effective_at=effective_date.isoformat(),
            request_body={"quote1": quote_series_id},
        )

        assert len(quote_response.values) == 1

        quote = quote_response.values["quote1"]

        assert 199.23 == quote.metric_value.value

    @pytest.mark.asyncio
    async def test_get_timeseries_quotes(self, quotes_api):
        start_date = datetime(2019, 4, 15, tzinfo=pytz.utc)
        date_range = [start_date + timedelta(days=x) for x in range(0, 30)]

        quote_id = models.QuoteSeriesId(
            provider="Client",
            instrument_id="BBG000B9XRY4",
            instrument_id_type="Figi",
            quote_type="Price",
            field="mid",
        )

        tasks = [
            quotes_api.get_quotes(
                scope=DataUtilities.market_data_scope,
                effective_at=d.isoformat(),
                request_body={"quote1": quote_id},
            )
            for d in date_range
        ]

        # get the quotes for each day in the date range
        quote_responses = await asyncio.gather(*tasks)

        # flatmap the quotes in the response
        assert 30 == len(
            [
                result
                for response in quote_responses
                for result in response.values.values()
            ]
        )
