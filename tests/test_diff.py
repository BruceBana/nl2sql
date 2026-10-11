from nl2sql.diff import normalise, tags


def test_normalise_ignores_formatting():
    assert normalise("SELECT  count(*)\nFROM t WHERE a  =  1") == normalise(
        "select count( * ) from t where a=1"
    )


def test_identical_sql_is_flagged():
    assert "identical SQL (result flipped anyway)" in tags(
        "SELECT a FROM t", "select a  from t", None, None
    )


def test_structural_changes():
    found = tags(
        "SELECT name FROM singer",
        "SELECT DISTINCT T1.name FROM singer AS T1 JOIN concert AS T2 ON T1.id = T2.sid",
        None,
        None,
    )
    assert "DISTINCT added" in found
    assert "T1/T2 aliases added" in found
    assert "joins 0->1" in found


def test_runs_and_no_longer_runs():
    assert "now runs" in tags("SELECT x", "SELECT y", "OperationalError: x", None)
    assert "no longer runs" in tags("SELECT x", "SELECT y", None, "OperationalError: y")


def test_word_boundaries():
    # "distinctive" is not DISTINCT, and "t10" is a T-alias but "tt1" is not.
    assert tags(
        "SELECT distinctive FROM tt1", "SELECT distinctive FROM tt1", None, None
    ) == ["identical SQL (result flipped anyway)"]
