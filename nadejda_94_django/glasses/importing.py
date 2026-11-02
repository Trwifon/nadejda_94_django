def parse_glass_kind(value):
    """Read the thickness and pane names from an Excel description."""
    thickness, description = value.strip().split(maxsplit=1)
    panes = [pane.strip() for pane in description.split('/')]
    # Excel uses both Cyrillic К and Latin K for the same coating.
    panes = ['K' if pane == 'К' else pane for pane in panes]
    first_glass = panes[0]
    second_glass = panes[1] if len(panes) > 1 else None
    third_glass = panes[2] if len(panes) > 2 else None
    return thickness, first_glass, second_glass, third_glass
