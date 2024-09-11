TORTOISE_ORM = {
    "connections": {
        "default": "postgres://<TA6>:<12345>@<host>:<port>/<dbname>"
    },
    "apps": {
        "models": {
            "models": ["app.models", "aerich.models"],
            "default_connection": "default",
        },
    },
}