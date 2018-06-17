import pytest

from molten import App, Route, testing
from molten.contrib.settings import Settings, SettingsComponent


def index(settings: Settings) -> dict:
    return settings


app = App(
    components=[SettingsComponent("./tests/contrib/fixtures/settings.toml", "prod")],
    routes=[Route("/", index)],
)

client = testing.TestClient(app)


def test_apps_can_load_settings():
    # Given that I have an app that uses settings
    # When I make a request to that handler
    response = client.get(app.reverse_uri("index"))

    # Then I should get back a successful response
    assert response.status_code == 200
    # And the response should contain the settings for the prod environment
    assert response.json() == {
        "conn_pooling": True,
        "conn_pool_size": 32,
        "sessions": {
            "secret": "supersekrit",
        },
        "oauth_providers": [
            {"name": "Facebook", "secret": "facebook-secret"},
            {"name": "Google", "secret": "google-secret"},
        ],
    }


def test_settings_can_look_up_deeply_nested_values():
    # Given that I have a settings object
    settings = Settings.from_path("tests/contrib/fixtures/settings.toml", "dev")

    # When I call deep_get to look up a nested value that doesn't exist
    # Then I should get None back
    assert settings.deep_get("i.dont.exist") is None

    # When I call deep_get to look up a nested value
    # Then I should get that value back
    assert settings.deep_get("sessions.secret") == "supersekrit"

    # When I call deep_get with a path that leads into a string
    # Then I should get back a TypeError
    with pytest.raises(TypeError):
        settings.deep_get("sessions.secret.value")

    # When I call deep_get with a path that leads into a list with an invalid integer
    # Then I should get back a TypeError
    with pytest.raises(TypeError):
        settings.deep_get("oauth_providers.facebook")

    # When I call deep_get with a path that leads into a list with an invalid index
    # Then I should get back a TypeError
    with pytest.raises(TypeError):
        settings.deep_get("oauth_providers.5")

    # When I call deep_get with a path that leads into a list with a valid index
    # Then I should get back a value
    assert settings.deep_get("oauth_providers.0.name") == "Facebook"
