import os
from uuid import uuid4


def evidence_upload_path(instance, filename):
    ext = filename.split(".")[-1]
    new_filename = f"{uuid4().hex}.{ext}"
    return os.path.join("evidence", str(instance.dispute.id), new_filename)


def validate_set_scores(set_scores):
    if not isinstance(set_scores, list):
        return False, "Set scores must be a list"

    if len(set_scores) < 2 or len(set_scores) > 5:
        return False, "Match must have between 2 and 5 sets"

    for i, set_score in enumerate(set_scores, 1):
        if not isinstance(set_score, dict):
            return False, f"Set {i} must be a dictionary"

        if "player1" not in set_score or "player2" not in set_score:
            return False, f"Set {i} must have 'player1' and 'player2' scores"

        p1 = set_score["player1"]
        p2 = set_score["player2"]

        if not isinstance(p1, int) or not isinstance(p2, int):
            return False, f"Set {i} scores must be integers"

        if p1 < 0 or p2 < 0:
            return False, f"Set {i} scores cannot be negative"

        if max(p1, p2) < 6:
            return False, f"Set {i}: Winner must have at least 6 games"

        if p1 == p2:
            return False, f"Set {i}: Scores cannot be equal"

        winner_score = max(p1, p2)
        loser_score = min(p1, p2)

        if winner_score == 6 and loser_score > 4:
            return (
                False,
                f"Set {i}: Invalid score - 6 games requires opponent to have 4 or fewer",
            )

        if winner_score == 7:
            if loser_score not in (5, 6):
                return False, f"Set {i}: 7 games requires opponent to have 5 or 6"

    return True, None


def determine_match_winner(set_scores):
    player1_sets = 0
    player2_sets = 0

    for set_score in set_scores:
        if set_score["player1"] > set_score["player2"]:
            player1_sets += 1
        else:
            player2_sets += 1

    sets_to_win = 2 if len(set_scores) <= 3 else 3

    if player1_sets >= sets_to_win:
        return "player1"
    elif player2_sets >= sets_to_win:
        return "player2"

    return None
