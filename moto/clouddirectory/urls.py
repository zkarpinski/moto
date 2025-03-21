"""clouddirectory base URL and path."""
from .responses import CloudDirectoryResponse

url_bases = [
    r"https?://clouddirectory\.(.+)\.amazonaws\.com",
]

url_paths = {
    "{0}/amazonclouddirectory/2017-01-11/directory/create$": CloudDirectoryResponse.dispatch,
    "{0}/amazonclouddirectory/2017-01-11/directory/list$": CloudDirectoryResponse.dispatch,
    "{0}/amazonclouddirectory/2017-01-11/tags/add$": CloudDirectoryResponse.dispatch,
    "{0}/amazonclouddirectory/2017-01-11/tags/remove$": CloudDirectoryResponse.dispatch,
    "{0}/amazonclouddirectory/2017-01-11/directory$": CloudDirectoryResponse.dispatch,
    "{0}/amazonclouddirectory/2017-01-11/directory/get$": CloudDirectoryResponse.dispatch,
}
