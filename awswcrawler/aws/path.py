def map_lambda(self, method, path, lambda_function):
    path_parts = path.split("?")
    if len(path_parts) == 2:
        path_string = path_parts[0]
        query_string = path_parts[1]
    elif len(path_parts) == 1:
        path_string = path_parts[0]
        query_string = ""
    else:
        raise ValueError("Incorrect path format: %s" % path)

    query_params = self.__extract_query_params(query_string)
    path_params = self.__extract_resources(path_string)

    request_params = {}
    request_template_dict = {}

    for qsp in query_params:
        request_params['method.request.querystring.' + qsp['query_name']] = qsp['required']
        request_template_dict[qsp['name']] = "$input.params('%s')" % qsp['name']

    for psp in (p for p in path_params if p['type'] == "PATH_PARAM"):
        request_params['method.request.path.' + psp['name']] = True
        request_template_dict[psp['name']] = "$input.params('%s')" % psp['name']


def __extract_resources(self, path_string):
    path_params = []
    if path_string.startswith('/'):
        path_string = path_string[1:]
    if path_string.endswith('/'):
        path_string = path_string[:-1]

    for ps in path_string.split("/"):
        if ps.startswith("{") and ps.endswith("}"):
            path_params.append({"type": "PATH_PARAM", "name": ps[1:-1]})
        else:
            path_params.append({"type": "PATH", "name": ps})

    return path_params


def __extract_query_params(self, query_string):
    query_params = []
    for q in query_string.split("&"):
        (query_param_name, output_param) = q.split("=")

        if not output_param.startswith("{") or not output_param.endswith("}"):
            raise ValueError("Incorrect query param format expected query_name={output_name}, was %s" % q)

        output_param = output_param[1:-1]

        if output_param.startswith("!"):
            query_params.append({'query_name': query_param_name, 'name': output_param[1:], 'required': True})
        else:
            query_params.append({'query_name': query_param_name, 'name': output_param, 'required': False})

    return query_params


def split_request_string(path):
    """
    Split request path to path and query tuple 
    :param path: request path, in example: /test?test=test&q={id}
    :return: tuple of strings (path, query)
    """
    if path is None or not path.strip():
        raise ValueError("Can not process empty path")

    if ' ' in path or '\t' in path or '\r' in path or '\n' in path:
        raise ValueError("Can not process path containing whitespaces")

    pp = path.split("?")
    if len(pp) == 1:
        return trim_slashes(pp[0]), ""
    elif len(pp) == 2:
        return trim_slashes(pp[0]), pp[1]
    elif len(pp) > 2:
        raise ValueError("Path can not contain more then one '?' character")
    else:
        raise ValueError("Can not process path containing whitespaces")


def split_path_string(path):
    """
    Splits path into array of segments
    :param path: string
    :return:
        "" -> []
        "/" -> []
        "test" -> ["test"]
        "test1/test2" -> ["test1", "test2"]
    """
    segments = trim_slashes(path).split("/")

    if len(segments) == 1 and not segments[0]:
        return []

    for s in segments:
        if not s:
            raise ValueError("Path contains empty segment (TIP. check for multiple slashes like //).")

    return segments


def split_query_string(query):
    """
    Split query string into dict
    :param query: query part of request string and validate is values are provided as params
    :return: dict
        for test1={test2}&test3={!test4} will return
        {
            "test1": "{test2},
            "test3": "{!test4}
        }
    """
    segments = query.split("&")

    pairs = {}

    if len(segments) == 1 and not segments[0]:
        return pairs

    for s in segments:
        if not s:
            raise ValueError("Query contains empty segment (TIP. check for multiple ampersands like &&).")

        if "=" not in s:
            raise ValueError("Incorrect query segment %s. Expecting key={value}" % s)

        kv = s.split("=")
        if len(kv) != 2:
            raise ValueError("Incorrect query segment %s. Expecting key={value}" % s)

        if not is_param(kv[1]):
            raise ValueError("Incorrect query segment %s. Expecting key={value}" % s)

        pairs[kv[0]] = kv[1]

    return pairs


def trim_slashes(path):
    """
    Return path without slashes in front and back
    :param path: in example "/test/test/"
    :return: clean path "test/test"
    """
    path = path.strip()
    if path.startswith("/"):
        path = path[1:]
    if path.endswith("/"):
        path = path[:-1]

    return path


def is_param(param_string):
    if not param_string:
        raise ValueError("Param string is empty.")
    if ' ' in param_string or '\t' in param_string or '\r' in param_string or '\n' in param_string:
        raise ValueError("Param string can not contain whitespaces.")

    if param_string.startswith("{") and param_string.endswith("}"):
        return True
    elif param_string.startswith("{"):
        raise ValueError("Param '%s' starts with { but not ends with }" % param_string)
    elif param_string.endswith("}"):
        raise ValueError("Param '%s' ends with } but not starts with {" % param_string)
    else:
        return False


def extract_param_name(param_string):
    if is_param(param_string):
        param = param_string[1:-1]

        if param.startswith("!"):
            param = param[1:]
    else:
        param = param_string

    return param


def is_param_required(param_string):
    if is_param(param_string):
        param = param_string[1:-1]

        if param.startswith("!"):
            return True
        else:
            return False
    else:
        raise ValueError("Not a param: %s" % param_string)


def parse_path_string(path_string):
    """
    Parse path string into array of request params
    :param path_string: "/documents/{document_id}/pages"
    :return: array of dicts in format:
        {"request_string": string, "type": "PATH", "param_name": string, "required": boolean}
        {"request_string": string, "type": "PATH_PARAM", "param_name": string, "required": boolean}
    """
    request_params_array = []

    segments = split_path_string(path_string)
    for s in segments:
        if is_param(s):
            request_params_array.append(
                {"request_string": s, "type": "PATH_PARAM", "param_name": extract_param_name(s), "required": True})
        else:
            request_params_array.append({"request_string": s, "type": "PATH", "param_name": None, "required": True})

    return request_params_array


def parse_query_string(query_string):
    """
    Parse query string into array of request params
    :param query_string: Part of request string after '?' /test?a={b}&c={d} -> a={b}&c={d} 
    :return: array of dicts in format:
        {"request_string": string, "type": "QUERY_PARAM", "param_name": string, "required": boolean}
    """
    request_params_array = []

    pairs = split_query_string(query_string)
    for k, v in pairs.iteritems():
        if is_param_required(v):
            request_params_array.append(
                {"request_string": k, "type": "QUERY_PARAM", "param_name": extract_param_name(v), "required": True})
        else:
            request_params_array.append(
                {"request_string": k, "type": "QUERY_PARAM", "param_name": extract_param_name(v), "required": False})

    return request_params_array


def parse_request_string(request_string):
    (path_string, query_string) = split_request_string(request_string)
    request_path_params = parse_path_string(path_string)
    request_query_params = parse_query_string(query_string)

    return request_path_params + request_query_params


def request_params_to_aws_request_params(request_params):
    aws_request_params = {}

    for rp in request_params:
        if rp['type'] == "PATH_PARAM":
            aws_request_params['method.request.path.' + rp['param_name']] = True
        elif rp['type'] == "QUERY_PARAM":
            aws_request_params['method.request.querystring.' + rp['request_string']] = rp['required']
        # Skip other types

    return aws_request_params


def request_params_to_aws_request_template_dict(request_params):
    aws_request_template_dict = {}

    for rp in request_params:
        if rp['type'] == "PATH_PARAM":
            aws_request_template_dict[rp['param_name']] = "$input.params('%s')" % rp['param_name']
        elif rp['type'] == "QUERY_PARAM":
            aws_request_template_dict[rp['param_name']] = "$input.params('%s')" % rp['request_string']
            # Skip other types

    return aws_request_template_dict

