from rest_framework.routers import SimpleRouter, Route, DynamicRoute


class SingleObjectRouter(SimpleRouter):
    """
    Router for viewsets that work on only one specific instance and has no 'list' option
    """
    routes = [
        Route(
            url=r'^{prefix}/$',
            mapping={
                'get': 'get',
                'post': 'post',
                'patch': 'patch',
                'put': 'put',
            },
            name='{basename}-detail',
            detail=True,
            initkwargs={'suffix': 'Detail'},
        ),
        DynamicRoute(
            url=r'^{prefix}/{url_path}/$',
            name='{basename}-{url_name}',
            detail=True,
            initkwargs={},
        ),
    ]


def get_bool_val(value):
    # python passes 'if value' for more than needed cases
    if value == True or str(value).lower() in ("true", "1", "ok", '"true"', "'true'"):
        return True
    return False
