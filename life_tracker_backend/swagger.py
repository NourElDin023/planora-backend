from django.urls import path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


schema_view = get_schema_view(
    openapi.Info(
        title="Planora API",
        default_version="v1",
        description="""
## Planora - Your Productivity Hub

Planora is a comprehensive productivity tool for:
- ✓ Habit building and tracking
- ✓ Task and project management
- ✓ Team collaboration
- ✓ Calendar integration

### Authentication
This API uses JWT for authentication. To authenticate:
1. Get a token using the login endpoint
2. Include the token in your requests as: `Authorization: Bearer <access_token>`

### Permissions
Most endpoints require authentication except for registration and login.
        """,
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

swagger_urlpatterns = [
    path("swagger/", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
    path("swagger.json", schema_view.without_ui(cache_timeout=0), name="schema-json"),
]