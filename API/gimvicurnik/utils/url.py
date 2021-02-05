def normalize_url(url, pluginfile):
    """Convert e-classroom URL from partial webservice URL to working normal URL."""
    return url.replace(pluginfile["webservice"], pluginfile["normal"]).replace("?forcedownload=1", "")


def tokenize_url(url, pluginfile, token):
    """Convert normal e-classroom URL to webservice URL and add token."""

    if pluginfile["normal"] in url:
        return url.replace(pluginfile["normal"], pluginfile["webservice"]) + "?token=" + token

    return url
