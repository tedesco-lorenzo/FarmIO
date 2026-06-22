from routes.appezzamenti import register_appezzamenti_routes
from routes.auth import register_auth_routes
from routes.colture import register_colture_routes
from routes.dashboard import register_dashboard_routes
from routes.interventi import register_interventi_routes
from routes.proprieta import register_proprieta_routes
from routes.punto_vendita import register_punto_vendita_routes
from routes.risorse import register_risorse_routes
from routes.scorte import register_scorte_routes
from routes.soggetto import register_soggetto_routes


def register_routes(app):
    register_dashboard_routes(app)
    register_proprieta_routes(app)
    register_soggetto_routes(app)
    register_risorse_routes(app)
    register_punto_vendita_routes(app)
    register_scorte_routes(app)
    register_colture_routes(app)
    register_appezzamenti_routes(app)
    register_interventi_routes(app)
    register_auth_routes(app)
