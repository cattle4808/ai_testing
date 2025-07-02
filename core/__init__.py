url_map = {
    "web": {
        "host": "http://127.0.0.1:8000",
    },
    "telegram": {
        "host": "https://api.telegram.org",
        "webapp": {
            "update_time_script": "/bot/update_time_script",
            "create_script_time": "/bot/create_script_time"
        }
    }
}