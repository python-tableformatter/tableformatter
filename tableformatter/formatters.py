class FormatBytes:
    """Formats a value in bytes into a human readable string"""
    KB = 1024
    MB = KB * 1024
    GB = MB * 1024
    TB = GB * 1024

    def __call__(self, byte_size: int):
        """
        Formats a value in bytes into a human readable string
        :param byte_size: size in bytes
        :return: human-readable string
        """
        if byte_size is None:
            return ''
        if not isinstance(byte_size, int):
            try:
                byte_size = int(byte_size)
            except ValueError:
                return ''

        decimal_format = '{:.02f}'
        if byte_size > FormatBytes.TB:
            out = decimal_format.format(byte_size / FormatBytes.TB) + " TB"
        elif byte_size > FormatBytes.GB:
            out = decimal_format.format(byte_size / FormatBytes.GB) + " GB"
        elif byte_size > FormatBytes.MB:
            out = decimal_format.format(byte_size / FormatBytes.MB) + " MB"
        elif byte_size > FormatBytes.KB:
            out = decimal_format.format(byte_size / FormatBytes.KB) + " KB"
        else:
            out = decimal_format.format(byte_size) + "  B"

        return out


class FormatCommas:
    """Formats a number with comma separators"""
    def __call__(self, number: Union[int, str]):
        if number is None:
            return ''
        if isinstance(number, str):
            number = int(number)
        return format(number, ',d')
