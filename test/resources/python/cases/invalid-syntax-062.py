root=Path(session['workspace']['root']); gh=root/'.vis/extensions/gh.py'
print(await patch(str(gh),[{'from':'97:cfb','replace':'''_MONTHS = ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")


def _display_started(value):
    """A compact, timezone-explicit start instant for the run status detail."""
    instant = _timestamp(value)
    if instant is None:
        return None
    utc = time.gmtime(instant)
    return f"{utc.tm_mday} {_MONTHS[utc.tm_mon - 1]} {utc.tm_year}, {utc.tm_hour:02d}:{utc.tm_min:02d} UTC"


def _wall_time():''':'''ignored'''}]))