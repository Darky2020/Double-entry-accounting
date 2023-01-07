tortoise = {
    "connections": {
        "default": "postgres://dev:password@localhost:5432/database"
    },
    "apps": {
        "models": {
            "models": [
                "service.models"
            ],
            "default_connection": "default",
        }
    },
}

origins = [
    "http://localhost:3000"
]
