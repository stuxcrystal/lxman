def escape_ntfs_invalid(name):
    """
    Escapes characters which are forbidden in NTFS, but are not in ext4.
    :param name: Path potentially containing forbidden NTFS characters.
    :return: Path with forbidden NTFS characters escaped.
    """
    prefix = ""
    if name[1] == ":":
        prefix = name[:2]
        name = name[2:]

    return prefix + (
        name
        .replace('*', '#002A')
        .replace('|', '#007C')
        .replace(':', '#003A')
        .replace('>', '#003E')
        .replace('<', '#003C')
        .replace('?', '#003F')
        .replace('"', '#0022')
    )
