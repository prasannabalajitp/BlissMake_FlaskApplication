from datetime import datetime
from AppConstants.Constants import Constants
import logging, json

def convert_set_to_list(log_data):
    for key, value in log_data.items():
        if isinstance(value, set):
            log_data[key] = list(value)
    return log_data

def format(user_id, query, start_time, end_time, route_url, response, response_status, http_method, host, cnt_typ):
    # Determine the standard response
    if response_status == 200:
        standard_response = Constants.RESPONSE_OK
    elif response_status == 500:
        standard_response = Constants.RESPONSE_INT_SER_ERR
    elif response_status == 400:
        standard_response = Constants.RESPONSE_BAD_REQ
    elif response_status == 401:
        standard_response = Constants.RESPONSE_UNAUTHORIZED
    else:
        standard_response = Constants.RESPONSE_UNKNOWN  # Handle other statuses

    # Prepare log data
    log_data = {
        Constants.INTERCEPTION_KEY: Constants.INTERCEPTION,
        Constants.USER_ID: user_id,
        Constants.REQUEST: {
            Constants.HTTP_METHOD_KEY: http_method,
            Constants.ROUTE_URL: route_url,
            Constants.HTTP_HEADERS: {
                Constants.CONTENT_TYPE_KEY: cnt_typ,
                Constants.DATE: start_time,
                Constants.ACCEPT: [Constants.ACCEPT_TYPE],
                Constants.CONNECTION_KEY: [Constants.CONNECTION],
                Constants.HOST: [host],
                Constants.ACCEPT_LANGUAGE_KEY: [Constants.ACCEPT_LANGUAGE]
            },
            Constants.DATA: query if http_method != Constants.GET else None
        },
        Constants.RESPONSE: {
            Constants.HTTP_STATUS_CODE: response_status,
            Constants.HTTP_STATUS: standard_response,
            Constants.HEADERS: {
                Constants.CONTENT_TYPE_KEY: Constants.CONTENT_TYPE,
                Constants.DATE: end_time,
            },
            Constants.DATE: end_time,
            Constants.RESPONSE: response
        },
        Constants.START_TIME: start_time,
        Constants.END_TIME: end_time,
        Constants.RESPONSE_TIME: None
    }

    # Calculate response time
    start_time_dt = datetime.fromisoformat(start_time)
    end_time_dt = datetime.fromisoformat(end_time)
    log_data[Constants.RESPONSE_TIME] = max((end_time_dt - start_time_dt).total_seconds(), 0)

    # Convert sets to lists if necessary
    log_data = convert_set_to_list(log_data)

    return json.dumps(log_data)

def configure_and_generate_logs(user_id, query, route_url, start_time, end_time, response, response_status, http_method, host, cnt_typ):
    logging.getLogger().setLevel(logging.INFO)
    logging.basicConfig()
    json_log = format(user_id, query, start_time, end_time, route_url, response, response_status, http_method, host, cnt_typ)
    logging.info(json_log)
    return json_log