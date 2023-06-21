import logging

import lusid
from lusid import ApiException


async def delete_entities(id_generator, api_client_factory):
    logging.basicConfig(
        format="%(asctime)s %(levelname)s %(message)s", level=logging.INFO
    )
    logger = logging.getLogger()

    property_definitions_api = api_client_factory.build(lusid.PropertyDefinitionsApi)
    portfolios_api = api_client_factory.build(lusid.PortfoliosApi)
    cut_labels = api_client_factory.build(lusid.CutLabelDefinitionsApi)
    orders_api = api_client_factory.build(lusid.OrdersApi)
    recipes_api = api_client_factory.build(lusid.ConfigurationRecipeApi)
    corporate_action_sources_api = api_client_factory.build(
        lusid.CorporateActionSourcesApi
    )

    for item in id_generator.pop_scope_and_codes():
        entity = item[0]
        scope = item[1]
        code = item[2]

        log_str = " ".join(item)

        try:
            if entity == "property_definition":
                domain = item[3]
                await property_definitions_api.delete_property_definition(
                    domain, scope, code
                )
                logger.info(f"deleting property definition: {log_str}")
            elif entity == "portfolio":
                await portfolios_api.delete_portfolio(scope, code)
                logger.info(f"deleting portfolio: {log_str}")
            elif entity == "cut_label":
                await cut_labels.delete_cut_label_definition(code)
                logger.info(f"deleting cut label: {log_str}")
            elif entity == "order":
                await orders_api.delete_order(scope, code)
                logger.info(f"deleting order: {log_str}")
            elif entity == "recipe":
                await recipes_api.delete_configuration_recipe(scope, code)
                logger.info(f"deleting recipe: {log_str}")
            elif entity == "ca_source":
                await corporate_action_sources_api.delete_corporate_action_source(
                    scope, code
                )
                logger.info(f"deleting corporate action source: {log_str}")
            else:
                logging.warning(f"unknown entity: {log_str}")
        except ApiException as ex:
            logging.error(ex)
