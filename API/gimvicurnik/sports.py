from __future__ import annotations

import datetime
import json
import re
from collections.abc import Iterable
from functools import cmp_to_key
from typing import Any

from .database import (
    QualificationDecision,
    Session,
    SportType,
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

SPORT_NAMES = {
    SportType.FOOTBALL: "Nogomet",
    SportType.VOLLEYBALL: "Odbojka",
    SportType.BASKETBALL: "Košarka",
}

ALLOWED_CLASS_CODES = tuple(f"{year}{letter}" for year in range(1, 5) for letter in "ABCDEF")
GROUPS = tuple(SportsGroup)
SCHEDULE_TIME = datetime.time(10, 30)
SEASON_KEY_RE = re.compile(r"^(\d{4})-(\d{2})$")
BRACKET_SLOTS = ("QF1", "QF2", "QF3", "QF4", "SF1", "SF2", "THIRD", "FINAL")

DEFAULT_RULES: dict[SportType, list[tuple[str, str | None]]] = {
    SportType.FOOTBALL: [
        ("Igra se 10 + 10 minut, vmes je ena minuta odmora. Tekma se začne točno ob 10:30.", None),
        ("Menjave so leteče in neomejene.", None),
        ("V ekipi igrajo 4 + 1 igralci, na klopi so lahko največ trije rezervni igralci.", None),
        ("Prepovedanega položaja ni.", None),
        ("Avt se izvaja z nogo, igrišče pa je omejeno z oranžnimi črtami.", None),
        (
            "Če imata ekipi po skupinskem delu enako število točk, se najprej upošteva "
            "medsebojna tekma. Če se je končala neodločeno, se upošteva razlika v zadetkih.",
            None,
        ),
        ("Drseči štart ni samodejno kaznovan z rumenim kartonom.", None),
        (
            "Rdeči karton pomeni izključitev do konca tekme in prepoved igranja na naslednji "
            "tekmi. Ekipa trenutno tekmo konča s štirimi igralci, torej 3 + 1.",
            None,
        ),
        (
            "Rumeni karton pomeni dve minuti na klopi. V tem času igralca ne sme zamenjati drug igralec.",
            None,
        ),
    ],
    SportType.BASKETBALL: [
        ("Igra se 3 × 3 na en koš.", None),  # noqa: RUF001
        ("Vsaka ekipa ima lahko dve menjavi. Menjave se izvajajo ob prekinitvi.", None),
        ("Igra se do 15 točk, do rezultata 11:0 ali največ 15 minut.", None),
        (
            "Igra se po uradnih pravilih FIBA 3 × 3.",  # noqa: RUF001
            "https://youtu.be/mu_Ogwqyyic?si=wI9sRmlR7j5AGksn",
        ),
        (
            "Po košu dobi posest nasprotna ekipa. Pred metom mora žogo spraviti izven črte "
            "za tri točke z vodenjem ali podajo. Obramba jo lahko pri tem normalno ovira.",
            None,
        ),
        (
            "Po vsaki menjavi posesti je koš veljaven samo, če je ekipa žogo prej spravila "
            "izven črte za tri točke. To velja tudi po ukradeni žogi ali metu, ki se ni "
            "dotaknil obroča.",
            None,
        ),
        (
            "Igrišče je znotraj stranskih avtov, zadnje črte in črte na polovici telovadnice.",
            None,
        ),
        ("Po prekinitvi se žoga izvaja iz stranskega avta.", None),
        (
            "Prva osebna napaka pomeni izvajanje avta. Druga osebna napaka v isti posesti pomeni prosti met.",
            None,
        ),
        ("Po osebni napaki pri metu na koš se izvaja prosti met.", None),
        ("Ob izenačenju se igra na zlati koš.", None),
    ],
    SportType.VOLLEYBALL: [
        ("Prvi in drugi set se igrata do 10 točk brez zahtevane razlike.", None),
        ("Tretji set se igra do 5 točk in mora biti dobljen z razliko.", None),
        ("V vsaki ekipi je potrebna vsaj ena igralka.", None),
        ("Bonusov ni.", None),
        ("Maske pred mrežo pred servisom niso dovoljene.", None),
        ("Tekme se igrajo na polovici igrišča.", None),
        (
            "Če sodnik dogajanja ne vidi ali se ekipi glede točke ne moreta sporazumeti, se točka ponavlja.",
            None,
        ),
        (
            "Če imata ekipi po skupinskem delu enako število točk, se upošteva število dobljenih setov.",
            None,
        ),
    ],
}


def current_school_year(today: datetime.date | None = None) -> str:
    today = today or datetime.date.today()
    start = today.year if today.month >= 9 else today.year - 1
    return f"{start}-{str(start + 1)[-2:]}"


def validate_season_key(value: str) -> str:
    match = SEASON_KEY_RE.fullmatch(value)
    if not match or int(match.group(2)) != (int(match.group(1)) + 1) % 100:
        raise ValueError("Šolsko leto mora biti zapisano kot 2025-26.")
    return value


def display_season(value: str) -> str:
    return value.replace("-", "/")


def display_class(value: str) -> str:
    return f"{value[0]}.{value[1].lower()}"


def parse_sport(value: str) -> SportType:
    try:
        return SportType(value)
    except ValueError as error:
        raise ValueError("Neznan šport.") from error


def parse_group(value: str) -> SportsGroup:
    try:
        return SportsGroup(value)
    except ValueError as error:
        raise ValueError("Neznana skupina.") from error


def get_season(sport: SportType, school_year: str) -> SportsSeason | None:
    return (
        Session.query(SportsSeason)
        .filter(SportsSeason.sport == sport, SportsSeason.school_year == school_year)
        .first()
    )


def ensure_season(sport: SportType, school_year: str) -> SportsSeason:
    validate_season_key(school_year)
    existing = get_season(sport, school_year)
    if existing:
        return existing

    season = SportsSeason(sport=sport, school_year=school_year)
    Session.add(season)
    Session.flush()

    previous = (
        Session.query(SportsSeason)
        .filter(SportsSeason.sport == sport, SportsSeason.school_year < school_year)
        .order_by(SportsSeason.school_year.desc())
        .first()
    )
    if previous:
        source_rules = (
            Session.query(SportsRule)
            .filter(SportsRule.season_id == previous.id)
            .order_by(SportsRule.position)
            .all()
        )
        rules = [(rule.text, rule.url) for rule in source_rules]
    else:
        rules = DEFAULT_RULES[sport]

    Session.add_all(
        SportsRule(season_id=season.id, position=position, text=text, url=url)
        for position, (text, url) in enumerate(rules)
    )
    Session.flush()
    return season


def _base_row(sport: SportType, participant: SportsParticipant) -> dict[str, Any]:
    common: dict[str, Any] = {
        "classCode": participant.class_code,
        "className": display_class(participant.class_code),
        "played": 0,
        "won": 0,
        "lost": 0,
        "points": 0,
        "qualifiedRank": participant.qualified_rank,
    }
    if sport == SportType.FOOTBALL:
        common.update({"drawn": 0, "scored": 0, "conceded": 0, "difference": 0})
    elif sport == SportType.BASKETBALL:
        common.update({"scored": 0, "conceded": 0, "difference": 0})
    else:
        common.update({"setsWon": 0, "setsLost": 0})
    return common


def completed_group_matches(season: SportsSeason, group: SportsGroup) -> list[SportsMatch]:
    return (
        Session.query(SportsMatch)
        .filter(
            SportsMatch.season_id == season.id,
            SportsMatch.stage == SportsMatchStage.GROUP,
            SportsMatch.group == group,
            SportsMatch.status.in_([SportsMatchStatus.COMPLETED, SportsMatchStatus.FORFEITED]),
        )
        .all()
    )


def _head_to_head_points(left: str, right: str, matches: Iterable[SportsMatch]) -> tuple[int, int]:
    left_points = 0
    right_points = 0
    for match in matches:
        if not match.home_participant or not match.away_participant:
            continue
        codes = {match.home_participant.class_code, match.away_participant.class_code}
        if codes != {left, right}:
            continue
        if match.home_score is None or match.away_score is None:
            continue
        if match.home_score == match.away_score:
            left_points += 1
            right_points += 1
        else:
            winner = match.home_participant if match.home_score > match.away_score else match.away_participant
            if winner.class_code == left:
                left_points += 3
            else:
                right_points += 3
    return left_points, right_points


def _decision_order(season: SportsSeason, group: SportsGroup) -> dict[str, int]:
    decision = (
        Session.query(QualificationDecision)
        .filter(QualificationDecision.season_id == season.id, QualificationDecision.group == group)
        .first()
    )
    if not decision:
        return {}
    try:
        return {code: index for index, code in enumerate(json.loads(decision.ordered_classes_json))}
    except (TypeError, ValueError):
        return {}


def _automatic_tie_key(sport: SportType, row: dict[str, Any]) -> tuple[int, ...]:
    if sport in (SportType.FOOTBALL, SportType.BASKETBALL):
        return (row["points"], row["difference"])
    return (row["points"], row["setsWon"])


def calculate_standings(season: SportsSeason, group: SportsGroup) -> list[dict[str, Any]]:
    participants = (
        Session.query(SportsParticipant)
        .filter(SportsParticipant.season_id == season.id, SportsParticipant.group == group)
        .order_by(SportsParticipant.class_code)
        .all()
    )
    rows = {participant.id: _base_row(season.sport, participant) for participant in participants}
    matches = completed_group_matches(season, group)

    for match in matches:
        if match.home_participant_id not in rows or match.away_participant_id not in rows:
            continue
        if match.home_score is None or match.away_score is None:
            continue
        home = rows[match.home_participant_id]
        away = rows[match.away_participant_id]
        home["played"] += 1
        away["played"] += 1

        if season.sport == SportType.VOLLEYBALL:
            home["setsWon"] += match.home_score
            home["setsLost"] += match.away_score
            away["setsWon"] += match.away_score
            away["setsLost"] += match.home_score
            if match.home_score > match.away_score:
                home["won"] += 1
                away["lost"] += 1
                home["points"] += 3 if match.away_score == 0 else 2
                away["points"] += 0 if match.away_score == 0 else 1
            else:
                away["won"] += 1
                home["lost"] += 1
                away["points"] += 3 if match.home_score == 0 else 2
                home["points"] += 0 if match.home_score == 0 else 1
            continue

        home["scored"] += match.home_score
        home["conceded"] += match.away_score
        away["scored"] += match.away_score
        away["conceded"] += match.home_score
        home["difference"] = home["scored"] - home["conceded"]
        away["difference"] = away["scored"] - away["conceded"]

        if match.home_score > match.away_score:
            home["won"] += 1
            away["lost"] += 1
            home["points"] += 3 if season.sport == SportType.FOOTBALL else 2
            away["points"] += 0 if season.sport == SportType.FOOTBALL else 1
        elif match.away_score > match.home_score:
            away["won"] += 1
            home["lost"] += 1
            away["points"] += 3 if season.sport == SportType.FOOTBALL else 2
            home["points"] += 0 if season.sport == SportType.FOOTBALL else 1
        else:
            home["drawn"] += 1
            away["drawn"] += 1
            home["points"] += 1
            away["points"] += 1

    decision_order = _decision_order(season, group)
    group_rows = list(rows.values())

    def compare(left: dict[str, Any], right: dict[str, Any]) -> int:
        if left["classCode"] == right["classCode"]:
            return 0
        if left["points"] != right["points"]:
            return -1 if left["points"] > right["points"] else 1

        if season.sport == SportType.FOOTBALL:
            same_points = [row for row in group_rows if row["points"] == left["points"]]
            if len(same_points) == 2:
                left_h2h, right_h2h = _head_to_head_points(left["classCode"], right["classCode"], matches)
                if left_h2h != right_h2h:
                    return -1 if left_h2h > right_h2h else 1

        metric = "setsWon" if season.sport == SportType.VOLLEYBALL else "difference"
        if left[metric] != right[metric]:
            return -1 if left[metric] > right[metric] else 1

        left_order = decision_order.get(left["classCode"], 10_000)
        right_order = decision_order.get(right["classCode"], 10_000)
        if left_order != right_order:
            return -1 if left_order < right_order else 1
        return -1 if left["classCode"] < right["classCode"] else 1

    result = sorted(group_rows, key=cmp_to_key(compare))
    for index, row in enumerate(result, start=1):
        row["rank"] = index
    return result


def qualification_tie(season: SportsSeason, group: SportsGroup) -> dict[str, Any] | None:
    rows = calculate_standings(season, group)
    if len(rows) < 3:
        return None
    second = rows[1]
    boundary_key = _automatic_tie_key(season.sport, second)
    tied = [row["classCode"] for row in rows if _automatic_tie_key(season.sport, row) == boundary_key]
    if len(tied) < 2 or rows[2]["classCode"] not in tied:
        return None
    if season.sport == SportType.FOOTBALL:
        same_points = [row for row in rows if row["points"] == second["points"]]
        if len(same_points) == 2:
            left_points, right_points = _head_to_head_points(
                same_points[0]["classCode"],
                same_points[1]["classCode"],
                completed_group_matches(season, group),
            )
            if left_points != right_points:
                return None
    decision = _decision_order(season, group)
    resolved = all(code in decision for code in tied)
    return {
        "group": group.value,
        "classCodes": tied,
        "classNames": [display_class(code) for code in tied],
        "resolved": resolved,
    }


def match_winner(match: SportsMatch) -> SportsParticipant | None:
    if match.status == SportsMatchStatus.FORFEITED:
        return match.forfeit_winner
    if match.status != SportsMatchStatus.COMPLETED:
        return None
    if match.home_score is None or match.away_score is None:
        return None
    if match.home_score > match.away_score:
        return match.home_participant
    if match.away_score > match.home_score:
        return match.away_participant
    if match.home_penalties is not None and match.away_penalties is not None:
        return (
            match.home_participant if match.home_penalties > match.away_penalties else match.away_participant
        )
    return None


def match_loser(match: SportsMatch) -> SportsParticipant | None:
    winner = match_winner(match)
    if not winner:
        return None
    return match.away_participant if winner.id == match.home_participant_id else match.home_participant


def serialize_rule(rule: SportsRule) -> dict[str, Any]:
    return {"id": rule.id, "position": rule.position, "text": rule.text, "url": rule.url}


def serialize_match(match: SportsMatch) -> dict[str, Any]:
    sets = sorted(match.volleyball_sets, key=lambda item: item.set_number)
    return {
        "id": match.id,
        "stage": match.stage.value,
        "status": match.status.value,
        "group": match.group.value if match.group else None,
        "bracketSlot": match.bracket_slot,
        "date": match.date.isoformat() if match.date else None,
        "time": match.start_time.isoformat("minutes"),
        "homeClass": match.home_participant.class_code if match.home_participant else None,
        "homeName": display_class(match.home_participant.class_code) if match.home_participant else None,
        "awayClass": match.away_participant.class_code if match.away_participant else None,
        "awayName": display_class(match.away_participant.class_code) if match.away_participant else None,
        "homeScore": match.home_score,
        "awayScore": match.away_score,
        "homePenalties": match.home_penalties,
        "awayPenalties": match.away_penalties,
        "forfeitWinner": match.forfeit_winner.class_code if match.forfeit_winner else None,
        "notes": match.notes,
        "sets": [
            {"number": item.set_number, "homeScore": item.home_score, "awayScore": item.away_score}
            for item in sets
        ],
        "revision": match.revision,
    }


def _podium(matches: list[SportsMatch]) -> dict[str, Any] | None:
    final = next((match for match in matches if match.bracket_slot == "FINAL"), None)
    third = next((match for match in matches if match.bracket_slot == "THIRD"), None)
    if not final or not third:
        return None
    champion = match_winner(final)
    runner_up = match_loser(final)
    third_place = match_winner(third)
    if not champion or not runner_up or not third_place:
        return None
    return {
        "gold": champion.class_code,
        "silver": runner_up.class_code,
        "bronze": third_place.class_code,
    }


def serialize_season(sport: SportType, school_year: str, season: SportsSeason | None) -> dict[str, Any]:
    if not season:
        return {
            "exists": False,
            "sport": sport.value,
            "sportName": SPORT_NAMES[sport],
            "seasonKey": school_year,
            "seasonLabel": display_season(school_year),
            "phase": SportsSeasonPhase.SETUP.value,
            "revision": 0,
            "availableClasses": list(ALLOWED_CLASS_CODES),
            "rules": [
                {"id": None, "position": index, "text": text, "url": url}
                for index, (text, url) in enumerate(DEFAULT_RULES[sport])
            ],
            "groups": [
                {"name": group.value, "participants": [], "standings": [], "matches": []} for group in GROUPS
            ],
            "qualificationTies": [],
            "qualificationDecisions": [],
            "bracket": [],
            "podium": None,
        }

    participants = (
        Session.query(SportsParticipant)
        .filter(SportsParticipant.season_id == season.id)
        .order_by(SportsParticipant.class_code)
        .all()
    )
    matches = (
        Session.query(SportsMatch)
        .filter(SportsMatch.season_id == season.id)
        .order_by(SportsMatch.date, SportsMatch.id)
        .all()
    )
    group_payload = []
    for group in GROUPS:
        group_participants = [participant for participant in participants if participant.group == group]
        group_matches = [
            match for match in matches if match.stage == SportsMatchStage.GROUP and match.group == group
        ]
        group_payload.append(
            {
                "name": group.value,
                "participants": [
                    {
                        "classCode": participant.class_code,
                        "className": display_class(participant.class_code),
                        "qualifiedRank": participant.qualified_rank,
                    }
                    for participant in group_participants
                ],
                "standings": calculate_standings(season, group),
                "matches": [serialize_match(match) for match in group_matches],
            }
        )

    rules = (
        Session.query(SportsRule)
        .filter(SportsRule.season_id == season.id)
        .order_by(SportsRule.position)
        .all()
    )
    ties = [tie for group in GROUPS if (tie := qualification_tie(season, group))]
    decisions = (
        Session.query(QualificationDecision)
        .filter(QualificationDecision.season_id == season.id)
        .order_by(QualificationDecision.group)
        .all()
    )
    return {
        "exists": True,
        "sport": sport.value,
        "sportName": SPORT_NAMES[sport],
        "seasonKey": school_year,
        "seasonLabel": display_season(school_year),
        "phase": season.phase.value,
        "revision": season.revision,
        "availableClasses": list(ALLOWED_CLASS_CODES),
        "rules": [serialize_rule(rule) for rule in rules],
        "groups": group_payload,
        "qualificationTies": ties,
        "qualificationDecisions": [
            {
                "group": decision.group.value,
                "orderedClasses": json.loads(decision.ordered_classes_json),
                "reason": decision.reason,
            }
            for decision in decisions
        ],
        "bracket": [serialize_match(match) for match in matches if match.stage != SportsMatchStage.GROUP],
        "podium": _podium(matches),
    }


def serialize_schedule(start: datetime.date, matches: list[SportsMatch]) -> list[list[dict[str, Any]]]:
    days: dict[datetime.date, list[dict[str, Any]]] = {
        start + datetime.timedelta(days=offset): [] for offset in range(5)
    }
    for match in matches:
        if not match.date or match.date not in days:
            continue
        payload = serialize_match(match)
        payload.update(
            {
                "sport": match.season.sport.value,
                "sportName": SPORT_NAMES[match.season.sport],
                "seasonKey": match.season.school_year,
            }
        )
        days[match.date].append(payload)
    return [days[day] for day in sorted(days)]


def serialize_audit_value(value: Any) -> str | None:
    if value is None:
        return None
    return json.dumps(value, ensure_ascii=False, sort_keys=True, default=str)


def group_participants_by_code(season: SportsSeason) -> dict[str, SportsParticipant]:
    participants = Session.query(SportsParticipant).filter(SportsParticipant.season_id == season.id).all()
    return {participant.class_code: participant for participant in participants}


def validate_class_codes(values: Iterable[str]) -> list[str]:
    result = list(values)
    if len(result) != len(set(result)):
        raise ValueError("Razred je lahko v tekmovanju izbran samo enkrat.")
    invalid = sorted(set(result) - set(ALLOWED_CLASS_CODES))
    if invalid:
        raise ValueError(f"Neveljavni razredi: {', '.join(invalid)}.")
    return result
