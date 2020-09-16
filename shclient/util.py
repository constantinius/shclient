from datetime import datetime

def iso8601_format(dt: datetime):
    if not dt.utcoffset():
        dt = dt.replace(tzinfo=None)
        return dt.isoformat('T') + 'Z'
    return dt.isoformat('T')
