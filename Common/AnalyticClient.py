from datetime import datetime
from AppConstants.Constants import Constants
import logging, json

def convert_set_to_list(log_data):
    for key, value in log_data.items():
        if isinstance(value, set):
            log_data[key] = list(value)
    return log_data

def format(user_id, query, start_time, end_time, response, response_status, http_method, host):
    if response_status == 200:
        standard_response = Constants.RESPONSE_OK
    elif response_status == 500:
        standard_response = Constants.RESPONSE_INT_SER_ERR
    elif response_status == 400:
        standard_response = Constants.RESPONSE_BAD_REQ
    
    log_data = {
        Constants.INTERCEPTION_KEY: Constants.INTERCEPTION,
        Constants.USER_ID: user_id,
        Constants.REQUEST: {
            Constants.DATA: query,
            Constants.HTTP_METHOD_KEY: http_method,
            Constants.HTTP_HEADERS: {
                Constants.CONTENT_TYPE_KEY: Constants.CONTENT_TYPE,
                Constants.CONTENT_LENGTH_KEY: len(query),
                Constants.DATE: start_time,
                Constants.ACCEPT: [Constants.ACCEPT_TYPE],
                Constants.CONNECTION_KEY: [Constants.CONNECTION],
                Constants.HOST: [host],
                Constants.ACCEPT_LANGUAGE_KEY: [Constants.ACCEPT_LANGUAGE]
            }
        },
        Constants.RESPONSE: {
            Constants.HTTP_STATUS_CODE: response_status,
            Constants.HTTP_STATUS: standard_response,
            Constants.HEADERS: {
                Constants.CONTENT_TYPE_KEY: Constants.CONTENT_TYPE,
                # Constants.CONTENT_LENGTH_KEY: len(response_from_AI),
                Constants.DATE: end_time,
            },
            Constants.DATE: end_time,
            Constants.RESPONSE: response
        },
        Constants.START_TIME: start_time,
        Constants.END_TIME: end_time,
        Constants.RESPONSE_TIME: None
    }

    start_time = datetime.fromisoformat(log_data[Constants.START_TIME])
    end_time = datetime.fromisoformat(log_data[Constants.END_TIME])
    time_difference = end_time - start_time
    response_time_seconds = max(time_difference.total_seconds(), 0)
    log_data[Constants.RESPONSE_TIME] = response_time_seconds

    log_data = convert_set_to_list(log_data)

    return json.dumps(log_data)

def configure_and_generate_logs(user_id, query, start_time, end_time, response, response_status, http_method, host):
    logging.getLogger().setLevel(logging.INFO)
    logging.basicConfig()
    json_log = format(user_id, query, start_time, end_time, response, response_status, http_method, host)
    logging.info(json_log)
    return json_log