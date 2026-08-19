from __future__ import annotations

import datetime
import json
import secrets
import threading
from collections import defaultdict, deque
from typing import Any, ClassVar

from flask import Blueprint, Response, abort, jsonify, request, session as flask_session
from werkzeug.security import check_password_hash

from .base import BaseHandler
from ..config import Config
from ..database import (
    QualificationDecision,
    Session,
    SportType,
    SportsAuditEntry,
    SportsGroup,
    SportsMatch,
    SportsMatchStage,
    SportsMatchStatus,
    SportsParticipant,
    SportsRule,
    SportsSeason,
    SportsSeasonPhase,
    VolleyballSetScore,
)
from ..sports import (
    ALLOWED_CLASS_CODES,
    BRACKET_SLOTS,
    GROUPS,
    SCHEDULE_TIME,
    calculate_standings,
    current_school_year,
    display_season,
    ensure_season,
    get_season,
    group_participants_by_code,
    match_loser,
    match_winner,
    parse_group,
    parse_sport,
    qualification_tie,
    serialize_audit_value,
    serialize_match,
    serialize_schedule,
    serialize_season,
    validate_class_codes,
    validate_season_key,
)
from ..utils.dates import get_weekdays


class SportsHandler(BaseHandler):
    name = "sports"

    _attempts: ClassVar[dict[tuple[str, str], deque[datetime.datetime]]] = defaultdict(deque)
    _attempts_lock: ClassVar[threading.Lock] = threading.Lock()

    @classmethod
    def routes(cls, bp: Blueprint, config: Config) -> None:
        def public_response(value: dict[str, Any]) -> Response:
            response = jsonify(value)
            response.add_etag()
            response.cache_control.public = True
            response.cache_control.max_age = 60
            response.make_conditional(request)
            return response

        def payload() -> dict[str, Any]:
            value = request.get_json(silent=True)
            if not isinstance(value, dict):
                abort(400, description="Telo zahteve mora biti veljaven predmet JSON.")
            return value

        def require_revision(season: SportsSeason, data: dict[str, Any]) -> None:
            if data.get("revision") != season.revision:
                abort(
                    409, description="Podatki so bili medtem spremenjeni. Osvežite stran in poskusite znova."
                )

        def require_match_revision(match: SportsMatch, data: dict[str, Any]) -> None:
            if data.get("matchRevision") != match.revision:
                abort(409, description="Tekma je bila medtem spremenjena. Osvežite stran in poskusite znova.")

        def sports_password_hash(sport: SportType) -> str:
            return str(getattr(config.sports.passwords, sport.value))

        def require_admin(sport: SportType, *, csrf: bool = True) -> None:
            if flask_session.get("sports_admin") != sport.value:
                abort(403, description="Za urejanje tega športa niste prijavljeni.")
            expires = flask_session.get("sports_expires")
            if not isinstance(expires, str) or datetime.datetime.fromisoformat(
                expires
            ) < datetime.datetime.now(datetime.timezone.utc):
                flask_session.clear()
                abort(401, description="Seja je potekla. Prijavite se znova.")
            if csrf and not secrets.compare_digest(
                request.headers.get("X-CSRF-Token", ""), flask_session.get("sports_csrf", "")
            ):
                abort(403, description="Varnostni žeton ni veljaven. Osvežite prijavo.")

        def client_key(sport: SportType) -> tuple[str, str]:
            forwarded = request.headers.get("X-Forwarded-For", "").split(",", 1)[0].strip()
            return sport.value, forwarded or request.remote_addr or "unknown"

        def login_is_limited(sport: SportType) -> bool:
            now = datetime.datetime.now(datetime.timezone.utc)
            cutoff = now - datetime.timedelta(minutes=config.sports.loginWindowMinutes)
            key = client_key(sport)
            with cls._attempts_lock:
                attempts = cls._attempts[key]
                while attempts and attempts[0] < cutoff:
                    attempts.popleft()
                return len(attempts) >= config.sports.loginAttempts

        def record_failed_login(sport: SportType) -> None:
            with cls._attempts_lock:
                cls._attempts[client_key(sport)].append(datetime.datetime.now(datetime.timezone.utc))

        def clear_failed_logins(sport: SportType) -> None:
            with cls._attempts_lock:
                cls._attempts.pop(client_key(sport), None)

        def audit(
            season: SportsSeason,
            action: str,
            record_type: str,
            record_id: int | None,
            before: Any,
            after: Any,
        ) -> None:
            Session.add(
                SportsAuditEntry(
                    sport=season.sport,
                    school_year=season.school_year,
                    action=action,
                    record_type=record_type,
                    record_id=record_id,
                    before_json=serialize_audit_value(before),
                    after_json=serialize_audit_value(after),
                )
            )

        def commit() -> None:
            try:
                Session.commit()
            except Exception:
                Session.rollback()
                raise

        def season_or_404(sport: SportType, school_year: str) -> SportsSeason:
            try:
                validate_season_key(school_year)
            except ValueError as error:
                abort(400, description=str(error))
            season = get_season(sport, school_year)
            if not season:
                abort(404, description="Sezona še ni nastavljena.")
            return season

        def parse_date(value: Any, school_year: str) -> datetime.date:
            try:
                date = datetime.date.fromisoformat(value)
            except (TypeError, ValueError):
                abort(400, description="Datum tekme ni veljaven.")
            if date.weekday() >= 5:
                abort(400, description="Tekme je mogoče razporediti od ponedeljka do petka.")
            start_year = int(school_year[:4])
            if not datetime.date(start_year, 9, 1) <= date <= datetime.date(start_year + 1, 8, 31):
                abort(400, description="Datum tekme mora biti znotraj izbrane šolske sezone.")
            return date

        def match_snapshot(match: SportsMatch) -> dict[str, Any]:
            return serialize_match(match)

        def participant_snapshot(season: SportsSeason) -> dict[str, str]:
            return {
                participant.class_code: participant.group.value
                for participant in Session.query(SportsParticipant)
                .filter(SportsParticipant.season_id == season.id)
                .order_by(SportsParticipant.class_code)
            }

        def active_matches_on(date: datetime.date, exclude_id: int | None = None) -> list[SportsMatch]:
            query = Session.query(SportsMatch).filter(
                SportsMatch.date == date,
                SportsMatch.status != SportsMatchStatus.POSTPONED,
            )
            if exclude_id:
                query = query.filter(SportsMatch.id != exclude_id)
            return query.all()

        def scheduling_warnings(
            season: SportsSeason,
            date: datetime.date,
            home: SportsParticipant,
            away: SportsParticipant,
            exclude_id: int | None = None,
        ) -> list[str]:
            existing = active_matches_on(date, exclude_id)
            if season.sport == SportType.FOOTBALL and existing:
                abort(400, description="Na dan nogometne tekme ne sme biti druge športne tekme.")
            if any(match.season.sport == SportType.FOOTBALL for match in existing):
                abort(400, description="Na izbrani dan je že razporejena nogometna tekma.")
            if any(match.season.sport == season.sport for match in existing):
                abort(400, description="Na isti dan je lahko največ ena tekma posameznega športa.")

            requested = {home.class_code, away.class_code}
            overlap = sorted(
                requested
                & {
                    participant.class_code
                    for match in existing
                    for participant in (match.home_participant, match.away_participant)
                    if participant
                }
            )
            if overlap:
                names = ", ".join(f"{code[0]}.{code[1].lower()}" for code in overlap)
                return [f"Razred {names} ima ob 10:30 že drugo športno tekmo."]
            return []

        def clear_result(match: SportsMatch) -> None:
            match.home_score = None
            match.away_score = None
            match.home_penalties = None
            match.away_penalties = None
            match.forfeit_winner_id = None
            Session.query(VolleyballSetScore).filter(VolleyballSetScore.match_id == match.id).delete()

        def integer_score(data: dict[str, Any], key: str, maximum: int | None = None) -> int:
            value = data.get(key)
            if not isinstance(value, int) or isinstance(value, bool) or value < 0:
                abort(400, description="Rezultati morajo biti nenegativna cela števila.")
            if maximum is not None and value > maximum:
                abort(400, description=f"Rezultat ne sme biti višji od {maximum}.")
            return value

        def apply_forfeit(match: SportsMatch, data: dict[str, Any]) -> None:
            winner_code = data.get("forfeitWinner")
            participants = {
                match.home_participant.class_code if match.home_participant else None: match.home_participant,
                match.away_participant.class_code if match.away_participant else None: match.away_participant,
            }
            winner = participants.get(winner_code)
            if not winner:
                abort(400, description="Izberite ekipo, ki je zmagala zaradi predaje.")
            home_won = winner.id == match.home_participant_id
            match.forfeit_winner_id = winner.id
            if match.season.sport == SportType.FOOTBALL:
                match.home_score, match.away_score = (3, 0) if home_won else (0, 3)
            elif match.season.sport == SportType.BASKETBALL:
                match.home_score, match.away_score = (11, 0) if home_won else (0, 11)
            else:
                match.home_score, match.away_score = (2, 0) if home_won else (0, 2)

        def apply_completed_result(match: SportsMatch, data: dict[str, Any]) -> None:
            clear_result(match)
            if match.season.sport == SportType.FOOTBALL:
                match.home_score = integer_score(data, "homeScore")
                match.away_score = integer_score(data, "awayScore")
                if match.stage != SportsMatchStage.GROUP and match.home_score == match.away_score:
                    match.home_penalties = integer_score(data, "homePenalties")
                    match.away_penalties = integer_score(data, "awayPenalties")
                    if match.home_penalties == match.away_penalties:
                        abort(400, description="Kazenski streli morajo določiti zmagovalca.")
                return

            if match.season.sport == SportType.BASKETBALL:
                match.home_score = integer_score(data, "homeScore", 15)
                match.away_score = integer_score(data, "awayScore", 15)
                if match.home_score == match.away_score:
                    abort(400, description="Košarkarska tekma se mora končati z zlatim košem.")
                return

            match.home_score = integer_score(data, "homeScore", 2)
            match.away_score = integer_score(data, "awayScore", 2)
            if sorted((match.home_score, match.away_score)) not in ([0, 2], [1, 2]):
                abort(400, description="Odbojkarski rezultat mora biti 2:0 ali 2:1 v setih.")

        def apply_match_status(match: SportsMatch, data: dict[str, Any]) -> None:
            try:
                status = SportsMatchStatus(data.get("status", match.status.value))
            except ValueError:
                abort(400, description="Stanje tekme ni veljavno.")
            if status in (SportsMatchStatus.COMPLETED, SportsMatchStatus.FORFEITED) and not match.date:
                abort(400, description="Pred vnosom rezultata določite datum tekme.")
            match.status = status
            if status in (SportsMatchStatus.SCHEDULED, SportsMatchStatus.POSTPONED):
                clear_result(match)
            elif status == SportsMatchStatus.FORFEITED:
                clear_result(match)
                apply_forfeit(match, data)
            else:
                apply_completed_result(match, data)

        def downstream_slots(slot: str | None) -> list[str]:
            if slot in ("QF1", "QF2"):
                return ["SF1", "FINAL", "THIRD"]
            if slot in ("QF3", "QF4"):
                return ["SF2", "FINAL", "THIRD"]
            if slot in ("SF1", "SF2"):
                return ["FINAL", "THIRD"]
            return []

        def completed_downstream(season: SportsSeason, slot: str | None) -> bool:
            slots = downstream_slots(slot)
            if not slots:
                return False
            return (
                Session.query(SportsMatch)
                .filter(
                    SportsMatch.season_id == season.id,
                    SportsMatch.bracket_slot.in_(slots),
                    SportsMatch.status.in_([SportsMatchStatus.COMPLETED, SportsMatchStatus.FORFEITED]),
                )
                .first()
                is not None
            )

        def propagate_bracket(season: SportsSeason) -> None:
            matches = {
                match.bracket_slot: match
                for match in Session.query(SportsMatch)
                .filter(SportsMatch.season_id == season.id, SportsMatch.bracket_slot.is_not(None))
                .all()
            }
            if not all(slot in matches for slot in BRACKET_SLOTS):
                return

            assignments = {
                "SF1": (match_winner(matches["QF1"]), match_winner(matches["QF2"])),
                "SF2": (match_winner(matches["QF3"]), match_winner(matches["QF4"])),
                "FINAL": (match_winner(matches["SF1"]), match_winner(matches["SF2"])),
                "THIRD": (match_loser(matches["SF1"]), match_loser(matches["SF2"])),
            }
            for slot, (home, away) in assignments.items():
                match = matches[slot]
                match.home_participant_id = home.id if home else None
                match.away_participant_id = away.id if away else None

        @bp.route("/sports/seasons")
        def list_seasons() -> Response:
            seasons = Session.query(SportsSeason).order_by(SportsSeason.school_year.desc()).all()
            return public_response(
                {
                    "currentSeasonKey": current_school_year(),
                    "seasons": [
                        {
                            "sport": season.sport.value,
                            "seasonKey": season.school_year,
                            "seasonLabel": display_season(season.school_year),
                            "phase": season.phase.value,
                        }
                        for season in seasons
                    ],
                }
            )

        @bp.route("/sports/<sport>/seasons/<school_year>")
        def get_sports_season(sport: str, school_year: str) -> Response:
            try:
                sport_type = parse_sport(sport)
                validate_season_key(school_year)
            except ValueError as error:
                abort(400, description=str(error))
            return public_response(
                serialize_season(sport_type, school_year, get_season(sport_type, school_year))
            )

        @bp.route("/sports/schedule/week/<date:date>")
        def get_sports_schedule(date: datetime.date) -> Response:
            weekdays = get_weekdays(date)
            matches = (
                Session.query(SportsMatch)
                .filter(SportsMatch.date.in_(weekdays))
                .order_by(SportsMatch.date, SportsMatch.start_time, SportsMatch.id)
                .all()
            )
            return public_response(
                {
                    "weekStart": weekdays[0].isoformat(),
                    "days": serialize_schedule(weekdays[0], matches),
                }
            )

        @bp.route("/sports/admin/login", methods=["POST"])
        def admin_login() -> dict[str, Any]:
            data = payload()
            try:
                sport = parse_sport(str(data.get("sport", "")))
            except ValueError as error:
                abort(400, description=str(error))
            if not config.sports.secretKey or not sports_password_hash(sport):
                abort(503, description="Administratorska prijava še ni nastavljena.")
            if login_is_limited(sport):
                abort(429, description="Preveč neuspelih prijav. Poskusite znova pozneje.")
            try:
                valid = check_password_hash(sports_password_hash(sport), str(data.get("password", "")))
            except ValueError:
                valid = False
            if not valid:
                record_failed_login(sport)
                abort(401, description="Geslo ni pravilno.")

            clear_failed_logins(sport)
            csrf_token = secrets.token_urlsafe(32)
            expires = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(
                hours=config.sports.sessionHours
            )
            flask_session.clear()
            flask_session.permanent = True
            flask_session["sports_admin"] = sport.value
            flask_session["sports_csrf"] = csrf_token
            flask_session["sports_expires"] = expires.isoformat()
            season_key = current_school_year()
            season = get_season(sport, season_key)
            if not season:
                season = ensure_season(sport, season_key)
                audit(
                    season,
                    "create_season",
                    "season",
                    season.id,
                    None,
                    {"phase": season.phase.value, "schoolYear": season.school_year},
                )
                commit()
            return {
                "authenticated": True,
                "sport": sport.value,
                "csrfToken": csrf_token,
                "expires": expires.isoformat(),
                "currentSeasonKey": season_key,
            }

        @bp.route("/sports/admin/session")
        def admin_session() -> dict[str, Any]:
            sport_value = flask_session.get("sports_admin")
            if not sport_value:
                return {"authenticated": False}
            try:
                sport = parse_sport(sport_value)
                require_admin(sport, csrf=False)
            except ValueError:
                flask_session.clear()
                return {"authenticated": False}
            return {
                "authenticated": True,
                "sport": sport.value,
                "csrfToken": flask_session.get("sports_csrf"),
                "expires": flask_session.get("sports_expires"),
            }

        @bp.route("/sports/admin/logout", methods=["POST"])
        def admin_logout() -> dict[str, bool]:
            sport_value = flask_session.get("sports_admin")
            if sport_value:
                require_admin(parse_sport(sport_value))
            flask_session.clear()
            return {"authenticated": False}

        @bp.route("/sports/<sport>/seasons/<school_year>/setup", methods=["PUT"])
        def update_setup(sport: str, school_year: str) -> dict[str, Any]:
            try:
                sport_type = parse_sport(sport)
                validate_season_key(school_year)
            except ValueError as error:
                abort(400, description=str(error))
            require_admin(sport_type)
            data = payload()
            season = get_season(sport_type, school_year)
            if season:
                require_revision(season, data)
                if season.phase in (SportsSeasonPhase.KNOCKOUT, SportsSeasonPhase.COMPLETED):
                    abort(400, description="Skupine so zaklenjene.")
            elif data.get("revision") != 0:
                abort(409, description="Osvežite podatke sezone in poskusite znova.")
            else:
                season = ensure_season(sport_type, school_year)

            assignments = data.get("groups")
            if not isinstance(assignments, dict) or set(assignments) - {group.value for group in GROUPS}:
                abort(400, description="Razporeditev skupin ni veljavna.")
            if any(
                not isinstance(assignments.get(group.value, []), list)
                or len(assignments.get(group.value, [])) > 6
                for group in GROUPS
            ):
                abort(400, description="V posamezni skupini je lahko največ šest ekip.")
            try:
                all_codes = validate_class_codes(
                    code for group in GROUPS for code in assignments.get(group.value, [])
                )
            except (TypeError, ValueError) as error:
                abort(400, description=str(error))

            before = participant_snapshot(season)
            existing = group_participants_by_code(season)
            desired = {code: group for group in GROUPS for code in assignments.get(group.value, [])}
            affected = {
                participant.id
                for code, participant in existing.items()
                if code not in desired or desired[code] != participant.group
            }
            if affected and (
                Session.query(SportsMatch)
                .filter(
                    SportsMatch.season_id == season.id,
                    (
                        SportsMatch.home_participant_id.in_(affected)
                        | SportsMatch.away_participant_id.in_(affected)
                    ),
                )
                .first()
            ):
                abort(400, description="Pred premikom ekipe odstranite vse njene tekme.")

            for code, participant in list(existing.items()):
                if code not in desired:
                    Session.delete(participant)
                else:
                    participant.group = desired[code]
            for code in all_codes:
                if code not in existing:
                    Session.add(SportsParticipant(season_id=season.id, class_code=code, group=desired[code]))
            season.revision += 1
            Session.flush()
            after = participant_snapshot(season)
            audit(season, "update_setup", "season", season.id, before, after)
            commit()
            return serialize_season(sport_type, school_year, season)

        @bp.route("/sports/<sport>/seasons/<school_year>/rules", methods=["PATCH"])
        def update_rules(sport: str, school_year: str) -> dict[str, Any]:
            try:
                sport_type = parse_sport(sport)
                validate_season_key(school_year)
            except ValueError as error:
                abort(400, description=str(error))
            require_admin(sport_type)
            data = payload()
            season = get_season(sport_type, school_year)
            if not season:
                if data.get("revision") != 0:
                    abort(409, description="Osvežite podatke sezone in poskusite znova.")
                season = ensure_season(sport_type, school_year)
            else:
                require_revision(season, data)
            raw_rules = data.get("rules")
            if not isinstance(raw_rules, list) or not raw_rules or len(raw_rules) > 50:
                abort(400, description="Vnesite od 1 do 50 pravil.")
            normalized: list[dict[str, str | None]] = []
            for item in raw_rules:
                if not isinstance(item, dict) or not isinstance(item.get("text"), str):
                    abort(400, description="Besedilo pravila ni veljavno.")
                text = item["text"].strip()
                url = item.get("url")
                if not text or len(text) > 2000 or (url is not None and not isinstance(url, str)):
                    abort(400, description="Pravilo je prazno ali predolgo.")
                normalized.append({"text": text, "url": url.strip() if url else None})
            before = [
                {"text": rule.text, "url": rule.url}
                for rule in Session.query(SportsRule)
                .filter(SportsRule.season_id == season.id)
                .order_by(SportsRule.position)
            ]
            Session.query(SportsRule).filter(SportsRule.season_id == season.id).delete()
            Session.add_all(
                SportsRule(
                    season_id=season.id,
                    position=index,
                    text=item["text"],
                    url=item["url"],
                )
                for index, item in enumerate(normalized)
            )
            season.revision += 1
            audit(season, "update_rules", "season", season.id, before, normalized)
            commit()
            return serialize_season(sport_type, school_year, season)

        @bp.route("/sports/<sport>/seasons/<school_year>/matches", methods=["POST"])
        def create_match(sport: str, school_year: str) -> tuple[dict[str, Any], int] | dict[str, Any]:
            try:
                sport_type = parse_sport(sport)
            except ValueError as error:
                abort(400, description=str(error))
            require_admin(sport_type)
            data = payload()
            season = season_or_404(sport_type, school_year)
            require_revision(season, data)
            if season.phase not in (SportsSeasonPhase.SETUP, SportsSeasonPhase.GROUP_STAGE):
                abort(400, description="Skupinskega dela ni več mogoče urejati.")
            participants = group_participants_by_code(season)
            home_code = data.get("homeClass")
            away_code = data.get("awayClass")
            home = participants.get(home_code) if isinstance(home_code, str) else None
            away = participants.get(away_code) if isinstance(away_code, str) else None
            if not home or not away or home.id == away.id:
                abort(400, description="Izberite dve različni sodelujoči ekipi.")
            assert home and away
            if home.group != away.group:
                abort(400, description="Ekipi skupinske tekme morata biti v isti skupini.")
            date = parse_date(data.get("date"), school_year)
            warnings = scheduling_warnings(season, date, home, away)
            if warnings and not data.get("confirmWarnings"):
                return {"warnings": warnings, "requiresConfirmation": True}, 409

            match = SportsMatch(
                season_id=season.id,
                stage=SportsMatchStage.GROUP,
                status=SportsMatchStatus.SCHEDULED,
                group=home.group,
                date=date,
                start_time=SCHEDULE_TIME,
                home_participant_id=home.id,
                away_participant_id=away.id,
                notes=str(data.get("notes", "")).strip() or None,
            )
            Session.add(match)
            season.phase = SportsSeasonPhase.GROUP_STAGE
            season.revision += 1
            Session.flush()
            audit(season, "create_match", "match", match.id, None, match_snapshot(match))
            commit()
            return {
                "season": serialize_season(sport_type, school_year, season),
                "match": serialize_match(match),
            }

        @bp.route("/sports/<sport>/seasons/<school_year>/matches/<int:match_id>", methods=["PATCH"])
        def update_match(
            sport: str, school_year: str, match_id: int
        ) -> tuple[dict[str, Any], int] | dict[str, Any]:
            try:
                sport_type = parse_sport(sport)
            except ValueError as error:
                abort(400, description=str(error))
            require_admin(sport_type)
            data = payload()
            season = season_or_404(sport_type, school_year)
            require_revision(season, data)
            if season.phase == SportsSeasonPhase.COMPLETED:
                abort(400, description="Zaključeno sezono morate pred urejanjem ponovno odpreti.")
            match = (
                Session.query(SportsMatch)
                .filter(SportsMatch.id == match_id, SportsMatch.season_id == season.id)
                .first()
            )
            if not match:
                abort(404, description="Tekma ne obstaja.")
            require_match_revision(match, data)
            if match.stage == SportsMatchStage.GROUP and season.phase == SportsSeasonPhase.KNOCKOUT:
                abort(400, description="Skupinski del je zaklenjen.")
            if match.stage != SportsMatchStage.GROUP and (
                not match.home_participant or not match.away_participant
            ):
                abort(400, description="Ekipi te tekme še nista znani.")

            before = match_snapshot(match)
            old_winner = match_winner(match)
            if "date" in data:
                match.date = parse_date(data["date"], school_year) if data["date"] else None
            if "notes" in data:
                match.notes = str(data.get("notes", "")).strip() or None
            if match.date and data.get("status", match.status.value) != SportsMatchStatus.POSTPONED.value:
                assert match.home_participant and match.away_participant
                warnings = scheduling_warnings(
                    season,
                    match.date,
                    match.home_participant,
                    match.away_participant,
                    match.id,
                )
                if warnings and not data.get("confirmWarnings"):
                    Session.rollback()
                    return {"warnings": warnings, "requiresConfirmation": True}, 409

            apply_match_status(match, data)
            new_winner = match_winner(match)
            if (
                match.stage != SportsMatchStage.GROUP
                and old_winner
                and (not new_winner or old_winner.id != new_winner.id)
                and completed_downstream(season, match.bracket_slot)
            ):
                Session.rollback()
                abort(
                    409,
                    description="Najprej počistite rezultate odvisnih tekem v naslednjih krogih.",
                )
            match.revision += 1
            season.revision += 1
            Session.flush()
            if match.stage != SportsMatchStage.GROUP:
                propagate_bracket(season)
            Session.flush()
            audit(season, "update_match", "match", match.id, before, match_snapshot(match))
            commit()
            return {
                "season": serialize_season(sport_type, school_year, season),
                "match": serialize_match(match),
            }

        @bp.route("/sports/<sport>/seasons/<school_year>/matches/<int:match_id>", methods=["DELETE"])
        def delete_match(sport: str, school_year: str, match_id: int) -> dict[str, Any]:
            try:
                sport_type = parse_sport(sport)
            except ValueError as error:
                abort(400, description=str(error))
            require_admin(sport_type)
            data = payload()
            season = season_or_404(sport_type, school_year)
            require_revision(season, data)
            match = (
                Session.query(SportsMatch)
                .filter(SportsMatch.id == match_id, SportsMatch.season_id == season.id)
                .first()
            )
            if not match:
                abort(404, description="Tekma ne obstaja.")
            require_match_revision(match, data)
            if match.stage != SportsMatchStage.GROUP:
                abort(400, description="Tekme izločilnih bojev ni mogoče izbrisati.")
            if match.status not in (SportsMatchStatus.SCHEDULED, SportsMatchStatus.POSTPONED):
                abort(400, description="Izbrisati je mogoče samo neodigrano tekmo.")
            before = match_snapshot(match)
            audit(season, "delete_match", "match", match.id, before, None)
            Session.query(VolleyballSetScore).filter(VolleyballSetScore.match_id == match.id).delete()
            Session.delete(match)
            season.revision += 1
            commit()
            return serialize_season(sport_type, school_year, season)

        @bp.route("/sports/<sport>/seasons/<school_year>/group-stage/close", methods=["POST"])
        def close_group_stage(sport: str, school_year: str) -> dict[str, Any]:
            try:
                sport_type = parse_sport(sport)
            except ValueError as error:
                abort(400, description=str(error))
            require_admin(sport_type)
            data = payload()
            season = season_or_404(sport_type, school_year)
            require_revision(season, data)
            if season.phase not in (SportsSeasonPhase.SETUP, SportsSeasonPhase.GROUP_STAGE):
                abort(400, description="Skupinski del je že zaključen.")
            for group in GROUPS:
                count = (
                    Session.query(SportsParticipant)
                    .filter(SportsParticipant.season_id == season.id, SportsParticipant.group == group)
                    .count()
                )
                if count < 2:
                    abort(400, description=f"Skupina {group.value} mora imeti vsaj dve ekipi.")
            unfinished = (
                Session.query(SportsMatch)
                .filter(
                    SportsMatch.season_id == season.id,
                    SportsMatch.stage == SportsMatchStage.GROUP,
                    SportsMatch.status.in_([SportsMatchStatus.SCHEDULED, SportsMatchStatus.POSTPONED]),
                )
                .count()
            )
            if unfinished:
                abort(400, description="Pred zaključkom vnesite rezultate vseh ustvarjenih tekem.")

            decisions = data.get("tieDecisions", [])
            if not isinstance(decisions, list):
                abort(400, description="Odločitve o izenačenju niso veljavne.")
            for item in decisions:
                if not isinstance(item, dict):
                    abort(400, description="Odločitev o izenačenju ni veljavna.")
                try:
                    group = parse_group(str(item.get("group", "")))
                except ValueError as error:
                    abort(400, description=str(error))
                tie = qualification_tie(season, group)
                ordered = item.get("orderedClasses")
                reason = str(item.get("reason", "")).strip()
                if (
                    not tie
                    or not isinstance(ordered, list)
                    or set(ordered) != set(tie["classCodes"])
                    or len(ordered) != len(set(ordered))
                    or not reason
                ):
                    abort(400, description=f"Odločitev za skupino {group.value} ni popolna.")
                decision = (
                    Session.query(QualificationDecision)
                    .filter(
                        QualificationDecision.season_id == season.id,
                        QualificationDecision.group == group,
                    )
                    .first()
                ) or QualificationDecision(season_id=season.id, group=group)
                decision.ordered_classes_json = json.dumps(ordered)
                decision.reason = reason
                Session.add(decision)
            Session.flush()

            unresolved = [
                tie for group in GROUPS if (tie := qualification_tie(season, group)) and not tie["resolved"]
            ]
            if unresolved:
                Session.rollback()
                abort(400, description="Razrešite izenačenja, ki vplivajo na napredovanje.")

            participants = group_participants_by_code(season)
            for participant in participants.values():
                participant.qualified_rank = None
            qualifiers: list[str] = []
            for group in GROUPS:
                rows = calculate_standings(season, group)
                for rank, row in enumerate(rows[:2], start=1):
                    participants[row["classCode"]].qualified_rank = rank
                    qualifiers.append(row["classCode"])
            before = {"phase": season.phase.value}
            season.phase = SportsSeasonPhase.KNOCKOUT
            season.revision += 1
            audit(
                season,
                "close_group_stage",
                "season",
                season.id,
                before,
                {"phase": season.phase.value, "qualifiers": qualifiers},
            )
            commit()
            return serialize_season(sport_type, school_year, season)

        @bp.route("/sports/<sport>/seasons/<school_year>/group-stage/reopen", methods=["POST"])
        def reopen_group_stage(sport: str, school_year: str) -> dict[str, Any]:
            try:
                sport_type = parse_sport(sport)
            except ValueError as error:
                abort(400, description=str(error))
            require_admin(sport_type)
            data = payload()
            season = season_or_404(sport_type, school_year)
            require_revision(season, data)
            if season.phase not in (SportsSeasonPhase.KNOCKOUT, SportsSeasonPhase.COMPLETED):
                abort(400, description="Skupinski del ni zaklenjen.")
            if data.get("confirm") is not True:
                abort(400, description="Potrdite odstranitev vseh podatkov izločilnih bojev.")
            bracket_matches = (
                Session.query(SportsMatch)
                .filter(
                    SportsMatch.season_id == season.id,
                    SportsMatch.stage != SportsMatchStage.GROUP,
                )
                .all()
            )
            before = [match_snapshot(match) for match in bracket_matches]
            match_ids = [match.id for match in bracket_matches]
            if match_ids:
                Session.query(VolleyballSetScore).filter(VolleyballSetScore.match_id.in_(match_ids)).delete(
                    synchronize_session=False
                )
            for match in bracket_matches:
                Session.delete(match)
            Session.query(QualificationDecision).filter(QualificationDecision.season_id == season.id).delete()
            for participant in Session.query(SportsParticipant).filter(
                SportsParticipant.season_id == season.id
            ):
                participant.qualified_rank = None
            season.phase = SportsSeasonPhase.GROUP_STAGE
            season.revision += 1
            audit(season, "reopen_group_stage", "bracket", None, before, None)
            commit()
            return serialize_season(sport_type, school_year, season)

        @bp.route("/sports/<sport>/seasons/<school_year>/bracket/quarterfinals", methods=["PUT"])
        def assign_quarterfinals(sport: str, school_year: str) -> dict[str, Any]:
            try:
                sport_type = parse_sport(sport)
            except ValueError as error:
                abort(400, description=str(error))
            require_admin(sport_type)
            data = payload()
            season = season_or_404(sport_type, school_year)
            require_revision(season, data)
            if season.phase != SportsSeasonPhase.KNOCKOUT:
                abort(400, description="Najprej zaključite skupinski del.")
            slots = data.get("slots")
            if not isinstance(slots, dict) or set(slots) != {"QF1", "QF2", "QF3", "QF4"}:
                abort(400, description="Zapolnite vse štiri četrtfinalne pare.")
            if any(not isinstance(slots[slot], list) or len(slots[slot]) != 2 for slot in slots):
                abort(400, description="Vsak četrtfinale potrebuje dve ekipi.")
            flattened = [code for slot in ("QF1", "QF2", "QF3", "QF4") for code in slots[slot]]
            qualifiers = {
                participant.class_code: participant
                for participant in Session.query(SportsParticipant).filter(
                    SportsParticipant.season_id == season.id,
                    SportsParticipant.qualified_rank.is_not(None),
                )
            }
            if len(flattened) != 8 or len(set(flattened)) != 8 or set(flattened) != set(qualifiers):
                abort(400, description="V četrtfinale razporedite vseh osem kvalificiranih ekip.")
            existing = (
                Session.query(SportsMatch)
                .filter(
                    SportsMatch.season_id == season.id,
                    SportsMatch.stage != SportsMatchStage.GROUP,
                )
                .all()
            )
            if any(
                match.status in (SportsMatchStatus.COMPLETED, SportsMatchStatus.FORFEITED)
                for match in existing
            ):
                abort(400, description="Po vnosu rezultatov izločilnih bojev parov ni mogoče zamenjati.")
            for match in existing:
                Session.delete(match)
            Session.flush()

            for slot in ("QF1", "QF2", "QF3", "QF4"):
                home, away = slots[slot]
                Session.add(
                    SportsMatch(
                        season_id=season.id,
                        stage=SportsMatchStage.QUARTERFINAL,
                        status=SportsMatchStatus.SCHEDULED,
                        bracket_slot=slot,
                        start_time=SCHEDULE_TIME,
                        home_participant_id=qualifiers[home].id,
                        away_participant_id=qualifiers[away].id,
                    )
                )
            for slot, stage in (
                ("SF1", SportsMatchStage.SEMIFINAL),
                ("SF2", SportsMatchStage.SEMIFINAL),
                ("THIRD", SportsMatchStage.THIRD_PLACE),
                ("FINAL", SportsMatchStage.FINAL),
            ):
                Session.add(
                    SportsMatch(
                        season_id=season.id,
                        stage=stage,
                        status=SportsMatchStatus.SCHEDULED,
                        bracket_slot=slot,
                        start_time=SCHEDULE_TIME,
                    )
                )
            season.revision += 1
            Session.flush()
            audit(season, "assign_quarterfinals", "bracket", None, None, slots)
            commit()
            return serialize_season(sport_type, school_year, season)

        @bp.route("/sports/<sport>/seasons/<school_year>/complete", methods=["POST"])
        def complete_season(sport: str, school_year: str) -> dict[str, Any]:
            try:
                sport_type = parse_sport(sport)
            except ValueError as error:
                abort(400, description=str(error))
            require_admin(sport_type)
            data = payload()
            season = season_or_404(sport_type, school_year)
            require_revision(season, data)
            if season.phase != SportsSeasonPhase.KNOCKOUT:
                abort(400, description="Sezone v tem stanju ni mogoče zaključiti.")
            matches = {
                match.bracket_slot: match
                for match in Session.query(SportsMatch).filter(SportsMatch.season_id == season.id)
                if match.bracket_slot
            }
            if not all(
                slot in matches
                and matches[slot].status in (SportsMatchStatus.COMPLETED, SportsMatchStatus.FORFEITED)
                and match_winner(matches[slot])
                for slot in ("FINAL", "THIRD")
            ):
                abort(400, description="Pred zaključkom odigrajte finale in tekmo za tretje mesto.")
            season.phase = SportsSeasonPhase.COMPLETED
            season.revision += 1
            audit(season, "complete_season", "season", season.id, "knockout", "completed")
            commit()
            return serialize_season(sport_type, school_year, season)

        @bp.route("/sports/<sport>/seasons/<school_year>/reopen", methods=["POST"])
        def reopen_season(sport: str, school_year: str) -> dict[str, Any]:
            try:
                sport_type = parse_sport(sport)
            except ValueError as error:
                abort(400, description=str(error))
            require_admin(sport_type)
            data = payload()
            season = season_or_404(sport_type, school_year)
            require_revision(season, data)
            if season.phase != SportsSeasonPhase.COMPLETED:
                abort(400, description="Sezona ni zaključena.")
            season.phase = SportsSeasonPhase.KNOCKOUT
            season.revision += 1
            audit(season, "reopen_season", "season", season.id, "completed", "knockout")
            commit()
            return serialize_season(sport_type, school_year, season)
