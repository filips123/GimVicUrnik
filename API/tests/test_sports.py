from __future__ import annotations

import datetime
from pathlib import Path
from typing import Any

import pytest
import yaml
from alembic import command
from alembic.config import Config as AlembicConfig
from sqlalchemy import create_engine, inspect
from sqlalchemy.pool import StaticPool
from werkzeug.security import generate_password_hash

from gimvicurnik import GimVicUrnik
from gimvicurnik.database import (
    Base,
    Session,
    SessionFactory,
    SportType,
    SportsGroup,
    SportsMatch,
    SportsMatchStage,
    SportsMatchStatus,
    SportsParticipant,
    SportsSeason,
)
from gimvicurnik.sports import calculate_standings, current_school_year


@pytest.fixture(autouse=True)
def database() -> None:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Session.remove()
    SessionFactory.configure(bind=engine)
    Base.metadata.create_all(engine)
    yield
    Session.remove()
    Base.metadata.drop_all(engine)


def create_group(sport: SportType, codes: list[str]) -> tuple[SportsSeason, dict[str, SportsParticipant]]:
    season = SportsSeason(sport=sport, school_year="2025-26")
    Session.add(season)
    Session.flush()
    participants = {
        code: SportsParticipant(season_id=season.id, class_code=code, group=SportsGroup.A) for code in codes
    }
    Session.add_all(participants.values())
    Session.flush()
    return season, participants


def add_result(
    season: SportsSeason,
    participants: dict[str, SportsParticipant],
    home: str,
    away: str,
    score: tuple[int, int],
) -> None:
    Session.add(
        SportsMatch(
            season_id=season.id,
            stage=SportsMatchStage.GROUP,
            status=SportsMatchStatus.COMPLETED,
            group=SportsGroup.A,
            date=datetime.date(2025, 10, 1),
            start_time=datetime.time(10, 30),
            home_participant_id=participants[home].id,
            away_participant_id=participants[away].id,
            home_score=score[0],
            away_score=score[1],
        )
    )
    Session.flush()


def rows_by_class(season: SportsSeason) -> dict[str, dict[str, int]]:
    return {row["classCode"]: row for row in calculate_standings(season, SportsGroup.A)}


def test_school_year_rolls_over_on_september_first() -> None:
    assert current_school_year(datetime.date(2026, 8, 31)) == "2025-26"
    assert current_school_year(datetime.date(2026, 9, 1)) == "2026-27"


def test_basketball_sample_scoring() -> None:
    season, teams = create_group(SportType.BASKETBALL, ["4E", "3B", "2B", "1E"])
    add_result(season, teams, "4E", "3B", (10, 13))
    add_result(season, teams, "1E", "2B", (3, 15))
    add_result(season, teams, "3B", "1E", (13, 15))
    add_result(season, teams, "4E", "2B", (9, 8))
    add_result(season, teams, "3B", "2B", (13, 3))
    add_result(season, teams, "4E", "1E", (12, 8))

    rows = rows_by_class(season)
    assert rows["4E"]["points"] == 5
    assert rows["4E"]["scored"] == 31
    assert rows["4E"]["conceded"] == 29
    assert rows["3B"]["points"] == 5
    assert rows["2B"]["points"] == 4


def test_volleyball_points_depend_on_set_result() -> None:
    season, teams = create_group(SportType.VOLLEYBALL, ["1A", "1B", "1C"])
    add_result(season, teams, "1A", "1B", (2, 0))
    add_result(season, teams, "1A", "1C", (2, 1))
    add_result(season, teams, "1B", "1C", (1, 2))

    rows = rows_by_class(season)
    assert rows["1A"]["points"] == 5
    assert rows["1B"]["points"] == 1
    assert rows["1C"]["points"] == 3
    assert rows["1A"]["setsWon"] == 4


def test_football_two_team_tie_uses_head_to_head() -> None:
    season, teams = create_group(SportType.FOOTBALL, ["1A", "1B", "1C", "1D"])
    add_result(season, teams, "1A", "1B", (1, 0))
    add_result(season, teams, "1C", "1A", (2, 0))
    add_result(season, teams, "1B", "1C", (4, 0))
    add_result(season, teams, "1D", "1B", (1, 0))
    add_result(season, teams, "1C", "1D", (0, 0))

    rows = calculate_standings(season, SportsGroup.A)
    order = [row["classCode"] for row in rows]
    assert order.index("1A") < order.index("1B")


def test_football_three_team_tie_uses_overall_goal_difference() -> None:
    season, teams = create_group(SportType.FOOTBALL, ["1A", "1B", "1C"])
    add_result(season, teams, "1A", "1B", (3, 0))
    add_result(season, teams, "1B", "1C", (2, 0))
    add_result(season, teams, "1C", "1A", (1, 0))

    rows = calculate_standings(season, SportsGroup.A)
    assert [row["classCode"] for row in rows] == ["1A", "1B", "1C"]


def create_test_app(tmp_path: Path) -> GimVicUrnik:
    password_hash = generate_password_hash("test-password", method="scrypt")
    config = {
        "sources": {
            "timetable": {"url": "https://example.invalid/timetable"},
            "eclassroom": {
                "token": "test",
                "webserviceUrl": "https://example.invalid/ws",
                "pluginFileWebserviceUrl": "https://example.invalid/plugin-ws",
                "pluginFileNormalUrl": "https://example.invalid/plugin",
                "course": 1,
            },
            "menu": {"url": "https://example.invalid/menu"},
            "solsis": {
                "url": "https://example.invalid/solsis",
                "serverName": "example.invalid",
                "apiKey": "test",
            },
        },
        "urls": {"website": "http://localhost", "api": "http://localhost/api"},
        "database": f"sqlite:///{(tmp_path / 'api.db').as_posix()}",
        "lessonTimes": [],
        "sports": {
            "secretKey": "test-secret-that-is-long-enough-for-a-signed-session",
            "passwords": {
                "football": password_hash,
                "volleyball": password_hash,
                "basketball": password_hash,
            },
        },
    }
    config_path = tmp_path / "config.yaml"
    config_path.write_text(yaml.safe_dump(config), encoding="utf-8")
    application = GimVicUrnik(str(config_path))
    Base.metadata.create_all(application.engine)
    application.app.config["TESTING"] = True
    return application


def login(client: Any, sport: str) -> str:
    response = client.post(
        "/sports/admin/login",
        json={"sport": sport, "password": "test-password"},
    )
    assert response.status_code == 200
    return response.get_json()["csrfToken"]


def test_login_lazily_creates_current_season_with_default_rules(tmp_path: Path) -> None:
    application = create_test_app(tmp_path)
    client = application.app.test_client()
    season_key = current_school_year()

    before = client.get(f"/sports/football/seasons/{season_key}").get_json()
    assert before["exists"] is False

    login(client, "football")

    after = client.get(f"/sports/football/seasons/{season_key}").get_json()
    assert after["exists"] is True
    assert after["phase"] == "setup"
    assert after["rules"]


@pytest.mark.parametrize(
    "path",
    [
        "/sports/seasons",
        "/sports/football/seasons/2025-26",
        "/sports/schedule/week/2025-10-01",
    ],
)
def test_public_sports_reads_support_conditional_etags(tmp_path: Path, path: str) -> None:
    application = create_test_app(tmp_path)
    client = application.app.test_client()

    first = client.get(path)
    assert first.status_code == 200
    assert first.headers["ETag"]
    assert first.cache_control.public is True
    assert first.cache_control.max_age == 60

    unchanged = client.get(path, headers={"If-None-Match": first.headers["ETag"]})
    assert unchanged.status_code == 304
    assert unchanged.data == b""


def save_setup(client: Any, sport: str, csrf: str) -> None:
    season = client.get(f"/sports/{sport}/seasons/2025-26").get_json()
    response = client.put(
        f"/sports/{sport}/seasons/2025-26/setup",
        json={
            "revision": season["revision"],
            "groups": {"A": ["1A", "1B"], "B": [], "C": [], "D": []},
        },
        headers={"X-CSRF-Token": csrf},
    )
    assert response.status_code == 200


def test_admin_scope_csrf_and_schedule_conflicts(tmp_path: Path) -> None:
    application = create_test_app(tmp_path)
    client = application.app.test_client()

    basketball_csrf = login(client, "basketball")
    save_setup(client, "basketball", basketball_csrf)
    basketball = client.post(
        "/sports/basketball/seasons/2025-26/matches",
        json={
            "revision": 2,
            "homeClass": "1A",
            "awayClass": "1B",
            "date": "2025-10-01",
        },
        headers={"X-CSRF-Token": basketball_csrf},
    )
    assert basketball.status_code == 200

    volleyball_csrf = login(client, "volleyball")
    save_setup(client, "volleyball", volleyball_csrf)
    overlap = client.post(
        "/sports/volleyball/seasons/2025-26/matches",
        json={
            "revision": 2,
            "homeClass": "1A",
            "awayClass": "1B",
            "date": "2025-10-01",
        },
        headers={"X-CSRF-Token": volleyball_csrf},
    )
    assert overlap.status_code == 409
    assert overlap.get_json()["requiresConfirmation"] is True

    confirmed = client.post(
        "/sports/volleyball/seasons/2025-26/matches",
        json={
            "revision": 2,
            "homeClass": "1A",
            "awayClass": "1B",
            "date": "2025-10-01",
            "confirmWarnings": True,
        },
        headers={"X-CSRF-Token": volleyball_csrf},
    )
    assert confirmed.status_code == 200

    football_csrf = login(client, "football")
    save_setup(client, "football", football_csrf)
    football = client.post(
        "/sports/football/seasons/2025-26/matches",
        json={
            "revision": 2,
            "homeClass": "1A",
            "awayClass": "1B",
            "date": "2025-10-01",
        },
        headers={"X-CSRF-Token": football_csrf},
    )
    assert football.status_code == 400

    wrong_scope = client.put(
        "/sports/basketball/seasons/2025-26/setup",
        json={"revision": 3, "groups": {"A": [], "B": [], "C": [], "D": []}},
        headers={"X-CSRF-Token": football_csrf},
    )
    assert wrong_scope.status_code == 403

    missing_csrf = client.put(
        "/sports/football/seasons/2025-26/setup",
        json={"revision": 2, "groups": {"A": ["1A", "1B"], "B": [], "C": [], "D": []}},
    )
    assert missing_csrf.status_code == 403

    stale_revision = client.put(
        "/sports/football/seasons/2025-26/setup",
        json={"revision": 1, "groups": {"A": ["1A", "1B"], "B": [], "C": [], "D": []}},
        headers={"X-CSRF-Token": football_csrf},
    )
    assert stale_revision.status_code == 409


@pytest.mark.parametrize(
    ("sport", "expected_score", "expected_sets"),
    [
        ("football", (3, 0), []),
        ("basketball", (11, 0), []),
        ("volleyball", (2, 0), []),
    ],
)
def test_automatic_forfeit_scores(
    tmp_path: Path,
    sport: str,
    expected_score: tuple[int, int],
    expected_sets: list[tuple[int, int]],
) -> None:
    application = create_test_app(tmp_path)
    client = application.app.test_client()
    csrf = login(client, sport)
    save_setup(client, sport, csrf)
    season = client.get(f"/sports/{sport}/seasons/2025-26").get_json()

    created = client.post(
        f"/sports/{sport}/seasons/2025-26/matches",
        json={
            "revision": season["revision"],
            "homeClass": "1A",
            "awayClass": "1B",
            "date": "2025-10-01",
        },
        headers={"X-CSRF-Token": csrf},
    ).get_json()
    match = created["match"]
    response = client.patch(
        f"/sports/{sport}/seasons/2025-26/matches/{match['id']}",
        json={
            "revision": created["season"]["revision"],
            "matchRevision": match["revision"],
            "status": "forfeited",
            "forfeitWinner": "1A",
        },
        headers={"X-CSRF-Token": csrf},
    )

    assert response.status_code == 200
    completed = response.get_json()["match"]
    assert (completed["homeScore"], completed["awayScore"]) == expected_score
    assert [(item["homeScore"], item["awayScore"]) for item in completed["sets"]] == expected_sets


def test_volleyball_result_uses_only_set_count(tmp_path: Path) -> None:
    application = create_test_app(tmp_path)
    client = application.app.test_client()
    csrf = login(client, "volleyball")
    save_setup(client, "volleyball", csrf)
    season = client.get("/sports/volleyball/seasons/2025-26").get_json()

    created = client.post(
        "/sports/volleyball/seasons/2025-26/matches",
        json={
            "revision": season["revision"],
            "homeClass": "1A",
            "awayClass": "1B",
            "date": "2025-10-02",
        },
        headers={"X-CSRF-Token": csrf},
    ).get_json()
    match = created["match"]
    completed = client.patch(
        f"/sports/volleyball/seasons/2025-26/matches/{match['id']}",
        json={
            "revision": created["season"]["revision"],
            "matchRevision": match["revision"],
            "status": "completed",
            "homeScore": 2,
            "awayScore": 1,
        },
        headers={"X-CSRF-Token": csrf},
    )

    assert completed.status_code == 200
    result = completed.get_json()["match"]
    assert (result["homeScore"], result["awayScore"]) == (2, 1)
    assert result["sets"] == []


def test_group_setup_rejects_more_than_six_teams(tmp_path: Path) -> None:
    application = create_test_app(tmp_path)
    client = application.app.test_client()
    csrf = login(client, "football")
    season = client.get("/sports/football/seasons/2025-26").get_json()

    response = client.put(
        "/sports/football/seasons/2025-26/setup",
        json={
            "revision": season["revision"],
            "groups": {
                "A": ["1A", "1B", "1C", "1D", "1E", "1F", "2A"],
                "B": [],
                "C": [],
                "D": [],
            },
        },
        headers={"X-CSRF-Token": csrf},
    )

    assert response.status_code == 400


def test_sports_migration_upgrades_existing_database(tmp_path: Path) -> None:
    database_path = tmp_path / "migration.db"
    engine = create_engine(f"sqlite:///{database_path.as_posix()}")
    existing_tables = [
        table
        for name, table in Base.metadata.tables.items()
        if not name.startswith("sports_") and name != "volleyball_set_scores"
    ]
    Base.metadata.create_all(engine, tables=existing_tables)

    project_root = Path(__file__).parents[1]
    config = AlembicConfig(str(project_root / "alembic.ini"))
    config.set_main_option("script_location", str(project_root / "migrations"))
    config.set_main_option("sqlalchemy.url", f"sqlite:///{database_path.as_posix()}")
    command.upgrade(config, "head")

    tables = set(inspect(engine).get_table_names())
    assert "lessons" in tables
    assert "sports_seasons" in tables
    assert "sports_matches" in tables
    assert "volleyball_set_scores" in tables


def test_sports_migration_upgrades_empty_database(tmp_path: Path) -> None:
    database_path = tmp_path / "empty-migration.db"
    project_root = Path(__file__).parents[1]
    config = AlembicConfig(str(project_root / "alembic.ini"))
    config.set_main_option("script_location", str(project_root / "migrations"))
    config.set_main_option("sqlalchemy.url", f"sqlite:///{database_path.as_posix()}")

    command.upgrade(config, "head")

    engine = create_engine(f"sqlite:///{database_path.as_posix()}")
    tables = set(inspect(engine).get_table_names())
    assert "alembic_version" in tables
    assert "sports_seasons" in tables
    assert "sports_matches" in tables
    assert "sports_audit_entries" in tables


def test_complete_tournament_workflow_and_bracket_progression(tmp_path: Path) -> None:
    application = create_test_app(tmp_path)
    client = application.app.test_client()
    csrf = login(client, "basketball")
    setup = client.put(
        "/sports/basketball/seasons/2025-26/setup",
        json={
            "revision": client.get("/sports/basketball/seasons/2025-26").get_json()["revision"],
            "groups": {
                "A": ["1A", "1B"],
                "B": ["1C", "1D"],
                "C": ["1E", "1F"],
                "D": ["2A", "2B"],
            },
        },
        headers={"X-CSRF-Token": csrf},
    ).get_json()
    season = setup

    group_games = [
        ("1A", "1B", "2025-10-01"),
        ("1C", "1D", "2025-10-02"),
        ("1E", "1F", "2025-10-03"),
        ("2A", "2B", "2025-10-06"),
    ]
    for home, away, date in group_games:
        created = client.post(
            "/sports/basketball/seasons/2025-26/matches",
            json={
                "revision": season["revision"],
                "homeClass": home,
                "awayClass": away,
                "date": date,
            },
            headers={"X-CSRF-Token": csrf},
        ).get_json()
        season = created["season"]
        match = created["match"]
        completed = client.patch(
            f"/sports/basketball/seasons/2025-26/matches/{match['id']}",
            json={
                "revision": season["revision"],
                "matchRevision": match["revision"],
                "status": "completed",
                "homeScore": 10,
                "awayScore": 8,
            },
            headers={"X-CSRF-Token": csrf},
        )
        assert completed.status_code == 200
        season = completed.get_json()["season"]

    closed = client.post(
        "/sports/basketball/seasons/2025-26/group-stage/close",
        json={"revision": season["revision"], "tieDecisions": []},
        headers={"X-CSRF-Token": csrf},
    )
    assert closed.status_code == 200
    season = closed.get_json()
    assert season["phase"] == "knockout"

    seeded = client.put(
        "/sports/basketball/seasons/2025-26/bracket/quarterfinals",
        json={
            "revision": season["revision"],
            "slots": {
                "QF1": ["1A", "1D"],
                "QF2": ["1E", "2B"],
                "QF3": ["1C", "1F"],
                "QF4": ["2A", "1B"],
            },
        },
        headers={"X-CSRF-Token": csrf},
    )
    assert seeded.status_code == 200
    season = seeded.get_json()

    def complete_slot(slot: str, date: str) -> None:
        nonlocal season
        match = next(item for item in season["bracket"] if item["bracketSlot"] == slot)
        assert match["homeClass"] and match["awayClass"]
        response = client.patch(
            f"/sports/basketball/seasons/2025-26/matches/{match['id']}",
            json={
                "revision": season["revision"],
                "matchRevision": match["revision"],
                "date": date,
                "status": "completed",
                "homeScore": 12,
                "awayScore": 9,
            },
            headers={"X-CSRF-Token": csrf},
        )
        assert response.status_code == 200
        season = response.get_json()["season"]

    complete_slot("QF3", "2025-10-09")
    complete_slot("QF4", "2025-10-10")
    sf1 = next(item for item in season["bracket"] if item["bracketSlot"] == "SF1")
    sf2 = next(item for item in season["bracket"] if item["bracketSlot"] == "SF2")
    assert (sf1["homeClass"], sf1["awayClass"]) == (None, None)
    assert (sf2["homeClass"], sf2["awayClass"]) == ("1C", "2A")

    complete_slot("QF1", "2025-10-07")
    complete_slot("QF2", "2025-10-08")
    sf1 = next(item for item in season["bracket"] if item["bracketSlot"] == "SF1")
    assert (sf1["homeClass"], sf1["awayClass"]) == ("1A", "1E")
    complete_slot("SF1", "2025-10-13")
    complete_slot("SF2", "2025-10-14")

    qf1 = next(item for item in season["bracket"] if item["bracketSlot"] == "QF1")
    invalidating_change = client.patch(
        f"/sports/basketball/seasons/2025-26/matches/{qf1['id']}",
        json={
            "revision": season["revision"],
            "matchRevision": qf1["revision"],
            "status": "scheduled",
        },
        headers={"X-CSRF-Token": csrf},
    )
    assert invalidating_change.status_code == 409

    complete_slot("THIRD", "2025-10-15")
    complete_slot("FINAL", "2025-10-16")

    completed = client.post(
        "/sports/basketball/seasons/2025-26/complete",
        json={"revision": season["revision"]},
        headers={"X-CSRF-Token": csrf},
    )
    assert completed.status_code == 200
    season = completed.get_json()
    assert season["phase"] == "completed"
    assert season["podium"] == {"gold": "1A", "silver": "1C", "bronze": "1E"}
