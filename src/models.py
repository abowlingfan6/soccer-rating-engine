# src/models.py

def defender_rating(s):
    return (
        6
        + (1.0 * s.get("Tk", 0))
        + (0.8 * s.get("INT", 0))
        + (0.5 * s.get("FW", 0))
        + (0.5 * s.get("P", 0) / 50)
        - (1.0 * s.get("RC", 0))
        - (0.5 * s.get("YC", 0))
        - (0.8 * s.get("GC", 0))
        - (0.3 * s.get("O", 0))
        + (0.5 * s.get("C", 0))
        + (0.4 * s.get("MP", 0) / 90)
    )


def midfielder_rating(s):
    return (
        6
        + (1.2 * s.get("P", 0) / 50)
        + (1.0 * s.get("C", 0))
        + (0.8 * s.get("Tk", 0))
        + (0.8 * s.get("INT", 0))
        + (0.6 * s.get("FW", 0))
        + (0.5 * s.get("A", 0))
        - (0.8 * s.get("RC", 0))
        - (0.3 * s.get("YC", 0))
        - (0.6 * s.get("O", 0))
        + (0.4 * s.get("MP", 0) / 90)
    )


def forward_rating(s):
    return (
        6
        + (2.0 * s.get("G", 0))
        + (1.2 * s.get("SOnT", 0))
        + (0.6 * s.get("SOffT", 0))
        + (1.0 * s.get("A", 0))
        + (0.8 * s.get("FW", 0))
        + (0.5 * s.get("C", 0))
        + (0.5 * s.get("P", 0) / 50)
        - (0.5 * s.get("O", 0))
        - (0.4 * s.get("RC", 0))
        - (0.2 * s.get("YC", 0))
        + (0.3 * s.get("MP", 0) / 90)
    )
