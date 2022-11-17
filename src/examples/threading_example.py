import lusid
import os
import time


def get_lusid_version_async(application_metadata_api):
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
    async_result = application_metadata_api.get_lusid_versions(
        async_req=True,
    )
    return async_result


def get_instrument_identifier_types_async(instruments_api):
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
    async_result = instruments_api.get_instrument_identifier_types(
        async_req=True,
    )
    return async_result


def async_get_example(api_client, async_request_fn):
    """send a request asynchronously and get the result when ready.
    Args:
        api_client (Union[lusid.api.ApplicationMetadataApi, lusid.InstrumentsApi]): api object used to send request to ApplicationMetadata or Instruments endpoints
        async_request_fn (Callable[AsyncResult]): Function that requests some data from one of our APIs asynchronously
    """     
    print('Getting the result from an asynchronous request')
    try:
        async_result = async_request_fn(api_client)
        # wait for response
        # if response takes more than 2 secs
        # raise TimeoutError
        response = async_result.get(timeout=2)
        print(response)
    except TimeoutError as e:
        print(e)


def async_wait_example(api_client, async_request_fn):
    """send a request asynchronously and print "done" when the response is received

    Args:
        api_client (Union[lusid.api.ApplicationMetadataApi, lusid.InstrumentsApi]): api object used to send request to ApplicationMetadata or Instruments endpoints
        async_request_fn (Callable[AsyncResult]): Function that requests some data from one of our APIs asynchronously
    """    
    print('Waiting for asynchronous request to complete')

    try:
        
        async_result = async_request_fn(api_client)
        # wait up for response
        # throws timeout after 20 secs
        async_result.wait(timeout=20)
        print("result ready")
    except TimeoutError as e:
        print(e)


def async_ready_example(api_client, async_request_fn):
    """similar to the wait example - send a request asynchronously, polling the ready status of the AsyncResult object
    when ready, check if async function executed without error. 
    Args:
        api_client (Union[lusid.api.ApplicationMetadataApi, lusid.InstrumentsApi]): api object used to send request to ApplicationMetadata or Instruments endpoints
        async_request_fn (Callable[AsyncResult]): Function that requests some data from one of our APIs asynchronously
    """    
    print('Polling async request ready status')
    async_result = async_request_fn(api_client)
    # poll whether function has completed on other thread.
    while not async_result.ready():
        print("result not ready yet")
        time.sleep(1)
    print("result ready")
    # check if function completed without exception on other thread.
    successful = async_result.successful()
    print(
        f'async function executed {"successfully" if successful else "unsuccessfully"}'
    )


def multiple_async_requests_example(api_client, async_request_fn):
    """Send 10 requests asyncronously, wait for all to complete by polling in a while loop,
    then print results of each request.

    Args:
        api_client (Union[lusid.api.ApplicationMetadataApi, lusid.InstrumentsApi]): api object used to send request to ApplicationMetadata or Instruments endpoints
        async_request_fn (Callable[AsyncResult]): Function that requests some data from one of our APIs asynchronously
    """   
    print('sending 10 asynchronous requests')
    # send 10 requests asyncronously
    results = [async_request_fn(api_client) for i in range(10)]
    # check whether all results are ready until all results are ready
    while not all((result.ready() for result in results)):
        pass
    print('all responses in')
    # now iterate through responses and print them
    for result in results:
        print(result.get())


if __name__ == "__main__":
    secrets_path = os.environ.get("FBN_SECRETS_PATH", "secrets.json")

    # Initiate an API Factory which is the client side object for interacting with LUSID APIs
    api_factory = lusid.utilities.ApiClientFactory(
        api_secrets_filename=secrets_path,
    )

    # create our api objects
    application_metadata_api = api_factory.build(lusid.api.ApplicationMetadataApi)
    instruments_api = api_factory.build(lusid.InstrumentsApi)
    print('Trying asynchronous requests for application metadata endpoint.')

    async_get_example(application_metadata_api, get_lusid_version_async)
    print('-'*20)
    async_wait_example(application_metadata_api, get_lusid_version_async)
    print('-'*20)
    async_ready_example(application_metadata_api, get_lusid_version_async)
    print('-'*20)
    multiple_async_requests_example(application_metadata_api, get_lusid_version_async)
    print('-'*20)
    print('\n'*4)
    print('Trying asynchronous requests for instruments endpoint.')

    print('-'*20)
    async_get_example(instruments_api, get_instrument_identifier_types_async)
    print('-'*20)
    async_wait_example(instruments_api, get_instrument_identifier_types_async)
    print('-'*20)
    async_ready_example(instruments_api, get_instrument_identifier_types_async)
    print('-'*20)
    multiple_async_requests_example(
        instruments_api, get_instrument_identifier_types_async
    )
