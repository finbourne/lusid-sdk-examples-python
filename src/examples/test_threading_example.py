import lusid
import time
from utilities import TestDataUtilities
import unittest
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
class AsyncExamples(unittest.TestCase):
    def setUp(self):
        # Create a configured API client
        api_client = TestDataUtilities.api_client()
        # Setup required LUSID APIs
        self.transaction_portfolios_api = lusid.TransactionPortfoliosApi(api_client)
        self.application_metadata_api = lusid.ApplicationMetadataApi(api_client)
        self.instruments_api = lusid.InstrumentsApi(api_client)

    def get_lusid_version_async(self):
        """Send request to get lusid version asyncronously

        Args:
            application_metadata_api (lusid.api.ApplicationMetadataApi): api object used to send request to ApplicationMetadata endpoints

        Returns:
            multiprocessing.pool.AsyncResult: An object with methods to monitor execution of a function in a threadpool,
            and retreive the result of the function execution
        """

        # calling with async_req = True
        # kicks off a request in a seperate thread
        # and returns a multiprocessing.pool.AsyncResult object
        # which can be used to monitor executing thread
        # and retrieve result when completed
        # https://docs.python.org/3/library/multiprocessing.html#multiprocessing.pool.AsyncResult
        async_result = self.application_metadata_api.get_lusid_versions(
            async_req=True,
        )
        return async_result

    def get_instrument_identifier_types_async(self):
        """Send request to get list of instrument identifier types asyncronously

        Args:
            instruments_api (lusid.InstrumentsApi): api object used to send request to Instruments endpoints

        Returns:
            multiprocessing.pool.AsyncResult: An object with methods to monitor execution of a function in a threadpool,
            and retreive the result of the function execution
        """

        # calling with async_req = True
        # kicks off a request in a seperate thread
        # and returns a multiprocessing.pool.AsyncResult object
        # which can be used to monitor executing thread
        # and retrieve result when completed
        # https://docs.python.org/3/library/multiprocessing.html#multiprocessing.pool.AsyncResult
        async_result = self.instruments_api.get_instrument_identifier_types(
            async_req=True,
        )
        return async_result

    def async_get_example(self, async_request_fn):
        """send a request asynchronously and get the result when ready.
        Args:
            api_client (Union[lusid.api.ApplicationMetadataApi, lusid.InstrumentsApi]): api object used to send request to ApplicationMetadata or Instruments endpoints
            async_request_fn (Callable[AsyncResult]): Function that requests some data from one of our APIs asynchronously
        Returns:
            str: Response
        """
        print("Getting the result from an asynchronous request")
        try:
            async_result = async_request_fn()
            # wait for response
            # if response takes more than 20 secs
            # raise TimeoutError
            response = async_result.get(timeout=20)
            return response
        except TimeoutError:
            logger.exception('Timed out')

    def async_wait_example(self, async_request_fn):
        """send a request asynchronously and print "done" when the response is received

        Args:
            api_client (Union[lusid.api.ApplicationMetadataApi, lusid.InstrumentsApi]): api object used to send request to ApplicationMetadata or Instruments endpoints
            async_request_fn (Callable[AsyncResult]): Function that requests some data from one of our APIs asynchronously
        """
        logger.info("Waiting for asynchronous request to complete")

        try:

            async_result = async_request_fn()
            # wait up for response
            # throws timeout after 20 secs
            async_result.wait(timeout=20)
            logger.info("result ready")
        except TimeoutError:
            logger.exception('Timed out')

    def async_ready_example(self, async_request_fn):
        """similar to the wait example - send a request asynchronously, polling the ready status of the AsyncResult object
        when ready, check if async function executed without error.
        Args:
            api_client (Union[lusid.api.ApplicationMetadataApi, lusid.InstrumentsApi]): api object used to send request to ApplicationMetadata or Instruments endpoints
            async_request_fn (Callable[AsyncResult]): Function that requests some data from one of our APIs asynchronously
        Returns:
            bool: whether the asynchronous functino completed successfully or not
        """
        logger.info("Polling async request ready status")
        async_result = async_request_fn()
        # poll whether function has completed on other thread.
        while not async_result.ready():
            logger.info("result not ready yet")
            time.sleep(1)
        logger.info("result ready")
        # check if function completed without exception on other thread.
        return async_result.successful()

    def multiple_async_requests_example(self, async_request_fn):
        """Send 10 requests asyncronously, wait for all to complete by polling in a while loop,
        then print results of each request.

        Args:
            api_client (Union[lusid.api.ApplicationMetadataApi, lusid.InstrumentsApi]): api object used to send request to ApplicationMetadata or Instruments endpoints
            async_request_fn (Callable[AsyncResult]): Function that requests some data from one of our APIs asynchronously
        Returns:
            Iterator[str]: Iterator of responses
        """
        logger.info("sending 10 asynchronous requests")
        # send 10 requests asyncronously
        results = [async_request_fn() for i in range(10)]
        # check whether all results are ready until all results are ready
        while not all((result.ready() for result in results)):
            pass
        logger.info("all responses in")
        # now iterate through response for result in results:
        return (result.get() for result in results)

    def test_async_get_example(self):
        self.assertIsNotNone(self.async_get_example(self.get_lusid_version_async))
        self.assertIsNotNone(
            self.async_get_example(self.get_instrument_identifier_types_async)
        )

    def test_async_wait_example(self):
        self.async_wait_example(self.get_lusid_version_async)
        self.async_wait_example(self.get_instrument_identifier_types_async)

    def test_async_ready_example(self):
        self.assertTrue(self.async_ready_example(self.get_lusid_version_async))
        self.assertTrue(
            self.async_ready_example(self.get_instrument_identifier_types_async)
        )

    def test_multiple_async_requests_example(self):
        self.assertIsNotNone(
            self.multiple_async_requests_example(self.get_lusid_version_async)
        )
        self.assertIsNotNone(
            self.multiple_async_requests_example(
                self.get_instrument_identifier_types_async
            )
        )
