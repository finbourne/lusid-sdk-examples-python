import pytest_asyncio
import lusid
import asyncio
import pytest
import utilities


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="class")
def data_utilities(transaction_portfolios_api):
    return utilities.test_data_utilities.DataUtilities(transaction_portfolios_api)


@pytest_asyncio.fixture(scope="class")
async def api_client_factory():
    async with lusid.extensions.ApiClientFactory() as api_client_factory:
        yield api_client_factory
        await asyncio.sleep(0.025)


@pytest_asyncio.fixture(scope="class")
async def id_generator(default_scope, api_client_factory):
    id_generator = utilities.IdGenerator(default_scope)

    yield id_generator
    await utilities.delete_entities(id_generator, api_client_factory)


@pytest_asyncio.fixture(scope="class")
async def instruments(instruments_api):
    instrument_loader = utilities.InstrumentLoader(instruments_api)
    instruments = await instrument_loader.load_instruments()
    yield instruments
    await instrument_loader.delete_instruments()


@pytest.fixture(scope="class")
def test_data_utilities(transaction_portfolios_api):
    return utilities.DataUtilities(transaction_portfolios_api)


@pytest.fixture(scope="class")
def transaction_portfolios_api(api_client_factory):
    return api_client_factory.build(lusid.TransactionPortfoliosApi)


@pytest.fixture(scope="class")
def instruments_api(api_client_factory):
    return api_client_factory.build(lusid.InstrumentsApi)


@pytest.fixture(scope="class")
def cut_label_definitions_api(api_client_factory):
    return api_client_factory.build(lusid.CutLabelDefinitionsApi)


@pytest.fixture(scope="class")
def portfolios_api(api_client_factory):
    return api_client_factory.build(lusid.PortfoliosApi)


@pytest.fixture(scope="class")
def property_definitions_api(api_client_factory):
    return api_client_factory.build(lusid.PropertyDefinitionsApi)


@pytest.fixture(scope="class")
def orders_api(api_client_factory):
    return api_client_factory.build(lusid.OrdersApi)


@pytest.fixture(scope="class")
def scopes_api(api_client_factory):
    return api_client_factory.build(lusid.ScopesApi)


@pytest.fixture(scope="class")
def reconciliations_api(api_client_factory):
    return api_client_factory.build(lusid.ReconciliationsApi)


@pytest.fixture(scope="class")
def reference_portfolio_api(api_client_factory):
    return api_client_factory.build(lusid.ReferencePortfolioApi)


@pytest.fixture(scope="class")
def aggregation_api(api_client_factory):
    return api_client_factory.build(lusid.AggregationApi)


@pytest.fixture(scope="class")
def recipes_api(api_client_factory):
    return api_client_factory.build(lusid.ConfigurationRecipeApi)


@pytest.fixture(scope="class")
def quotes_api(api_client_factory):
    return api_client_factory.build(lusid.QuotesApi)


@pytest.fixture(scope="class")
def corporate_actions_sources_api(api_client_factory):
    return api_client_factory.build(lusid.CorporateActionSourcesApi)
