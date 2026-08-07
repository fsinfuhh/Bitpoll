import re

from django.urls import URLPattern, URLResolver, get_resolver, reverse


def extract_patterns(url_patterns, args=None):
    """Yield named URL patterns and positional regex arguments recursively."""
    args = [] if args is None else list(args)
    for pattern in url_patterns:
        pattern_args = args + re.findall(r"\((?!\?P<)[^)]*\)", str(pattern.pattern))
        if isinstance(pattern, URLPattern):
            if pattern.name:
                yield pattern, pattern_args
        elif isinstance(pattern, URLResolver):
            yield from extract_patterns(pattern.url_patterns, pattern_args)


def get_module_urls(module):
    """Return ``(url_name, argument_count)`` for every named module URL."""
    resolver = get_resolver(f"bitpoll.{module}.urls")
    return [(pattern.name, len(args)) for pattern, args in extract_patterns(resolver.url_patterns)]


def get_dynamic_url(args, url_name):
    """Reverse a Bitpoll URL using positional values for its regex groups."""
    return reverse(url_name, args=args)

