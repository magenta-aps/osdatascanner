from typing import Iterator


def replace_regions(content: str, *regions: tuple[int, str, int]) -> Iterator[str]:
    """Given a string and a number of successive (start_offset: int,
    replacement: str, end_offset: int) tuples, yields parts of a new string in
    which the region specified by each tuple has been replaced.

    Each tuple's offsets should be relative to the original string; this
    function takes care of fixing them up as the content changes."""
    consumed = 0
    for (start, replacement, end) in regions:
        region_size = end - start

        # Map the start offset into content, taking into account that we may
        # have already emitted and consumed some characters
        adjusted_start = start - consumed
        if adjusted_start < 0:
            raise ValueError("Overlapping regions!")

        # Emit everything up to the modified start offset...
        yield content[:adjusted_start]
        # ... and update content and consumed to reflect that we've emitted a
        # block of the string
        content = content[adjusted_start:]
        consumed += adjusted_start

        yield replacement

        # After yielding the replacement region, whatever it is, we advance
        # content to skip over the rest of the original region
        content = content[region_size:]
        consumed += region_size
    yield content
