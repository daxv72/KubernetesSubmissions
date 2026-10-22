"""Hourly reminder — exercise 2.9.

Wikipedia answers Special:Random with a redirect. The Location header
is the article. This process stores one todo: Read <that url>.
"""

import os
import urllib.error
import urllib.parse
import urllib.request


def required(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise SystemExit(f"Missing environment variable {name}")
    return value


WIKIPEDIA_RANDOM_URL = required("WIKIPEDIA_RANDOM_URL")
TODO_BACKEND_URL = required("TODO_BACKEND_URL")
TODO_FIELD = required("TODO_FIELD")
TODO_PREFIX = required("TODO_PREFIX")
USER_AGENT = required("USER_AGENT")
MAX_LENGTH = int(required("MAX_LENGTH"))


class NoRedirect(urllib.request.HTTPRedirectHandler):
    """Leave redirects alone so the Location header stays readable."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def random_article() -> str:
    request = urllib.request.Request(
        WIKIPEDIA_RANDOM_URL,
        headers={"User-Agent": USER_AGENT},
    )
    opener = urllib.request.build_opener(NoRedirect)
    try:
        response = opener.open(request, timeout=20)
    except urllib.error.HTTPError as error:
        if error.code not in (301, 302, 303, 307, 308):
            raise SystemExit(f"Wikipedia returned {error.code}") from error
        location = error.headers.get("Location")
        if not location:
            raise SystemExit(f"Wikipedia returned {error.code} without a Location header")
        article = urllib.parse.urljoin(WIKIPEDIA_RANDOM_URL, location)
        print(f"Random article: {article}", flush=True)
        return article
    article = response.geturl()
    response.close()
    print(f"Random article: {article}", flush=True)
    return article


def create_todo(article: str) -> None:
    text = f"{TODO_PREFIX} {article}"
    if len(text) > MAX_LENGTH:
        raise SystemExit(f"Todo is {len(text)} characters, limit is {MAX_LENGTH}")
    body = urllib.parse.urlencode({TODO_FIELD: text}).encode()
    request = urllib.request.Request(
        TODO_BACKEND_URL,
        data=body,
        method="POST",
        headers={
            "User-Agent": USER_AGENT,
            "Content-Type": "application/x-www-form-urlencoded",
        },
    )
    opener = urllib.request.build_opener(NoRedirect)
    try:
        response = opener.open(request, timeout=20)
    except urllib.error.HTTPError as error:
        # The backend answers 303 after a successful insert.
        if error.code == 303:
            print(f"Todo stored: {text}", flush=True)
            return
        detail = error.read().decode(errors="replace").strip()
        raise SystemExit(f"Backend returned {error.code}: {detail}") from error
    print(f"Backend responded {response.status}: {text}", flush=True)
    response.close()


def main() -> None:
    create_todo(random_article())


if __name__ == "__main__":
    main()
