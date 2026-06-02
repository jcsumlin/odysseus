import json

from routes.note_routes import render_webhook_template, _parse_json_obj


def test_render_substitutes_all_placeholders():
    out = render_webhook_template(
        "{{title}} | {{message}} | {{note_id}}",
        {"title": "Hi", "message": "Body", "note_id": "n-1"},
        json_escape=False,
    )
    assert out == "Hi | Body | n-1"


def test_render_json_escape_keeps_body_valid():
    # A message with quotes + newlines must NOT break the surrounding JSON.
    tmpl = '{"chat_id":"123","text":"{{message}}"}'
    nasty = 'He said "hi"\nand left\tnow'
    out = render_webhook_template(
        tmpl, {"title": "", "message": nasty, "note_id": ""}, json_escape=True
    )
    parsed = json.loads(out)  # must not raise
    assert parsed["text"] == nasty
    assert parsed["chat_id"] == "123"


def test_render_raw_mode_does_not_escape():
    out = render_webhook_template(
        "{{message}}", {"message": 'a"b'}, json_escape=False
    )
    assert out == 'a"b'


def test_render_handles_none_and_missing_values():
    out = render_webhook_template(
        "{{title}}-{{message}}", {"title": None, "message": "x"}, json_escape=False
    )
    assert out == "-x"


def test_default_body_template_renders_to_valid_json():
    from src.settings import DEFAULT_SETTINGS

    tmpl = DEFAULT_SETTINGS["reminder_webhook_body"]
    out = render_webhook_template(
        tmpl,
        {"title": 'a "quote"', "message": "line1\nline2", "note_id": "n"},
        json_escape=True,
    )
    parsed = json.loads(out)
    assert parsed["title"] == 'a "quote"'
    assert parsed["message"] == "line1\nline2"


def test_parse_json_obj_fallbacks():
    fallback = {"Content-Type": "application/json"}
    assert _parse_json_obj('{"X-A":"1"}', fallback) == {"X-A": "1"}
    assert _parse_json_obj("", fallback) == fallback
    assert _parse_json_obj("not json", fallback) == fallback
    assert _parse_json_obj("[1,2]", fallback) == fallback  # array is not an object
    assert _parse_json_obj({"already": "dict"}, fallback) == {"already": "dict"}
