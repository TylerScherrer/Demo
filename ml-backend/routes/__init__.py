# routes/__init__.py
from .predict import register_predict_route
from .explain_forecast import register_explain_route
from .get_stores import register_get_stores_route

def register_routes(app, context):
    register_predict_route(app, context)
    register_explain_route(app, context)
    register_get_stores_route(app, context)
