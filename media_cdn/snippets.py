#!/usr/bin/env python
#
# Copyright 2022 Google, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""This application demonstrates how to perform operations on data (content)
when using Google Cloud Media CDN.

For more information, see the README.md under /media-cdn and the documentation
at https://cloud.google.com/media-cdn/docs.
"""

# [START mediacdn_sign_url]
# [START mediacdn_sign_cookie]
# [START mediacdn_sign_token]
import base64
import datetime

# [END mediacdn_sign_cookie]
# [END mediacdn_sign_url]
import hashlib
import hmac

# [START mediacdn_sign_cookie]
# [START mediacdn_sign_url]

import cryptography.hazmat.primitives.asymmetric.ed25519 as ed25519

# [END mediacdn_sign_token]

from six.moves import urllib

# [END mediacdn_sign_cookie]
# [END mediacdn_sign_url]


# [START mediacdn_sign_url]
def sign_url(
    url: str, key_name: str, base64_key: str, expiration_time: datetime.datetime
) -> str:
    """Gets the Signed URL string for the specified URL and configuration.

    Args:
        url: URL to sign as a string.
        key_name: name of the signing key as a string.
        base64_key: signing key as a base64 encoded byte string.
        expiration_time: expiration time as a UTC datetime object.

    Returns:
        Returns the Signed URL appended with the query parameters based on the
        specified configuration.
    """
    stripped_url = url.strip()
    parsed_url = urllib.parse.urlsplit(stripped_url)
    query_params = urllib.parse.parse_qs(parsed_url.query, keep_blank_values=True)
    epoch = datetime.datetime.utcfromtimestamp(0)
    expiration_timestamp = int((expiration_time - epoch).total_seconds())
    decoded_key = base64.urlsafe_b64decode(base64_key)

    url_pattern = "{url}{separator}Expires={expires}&KeyName={key_name}"

    url_to_sign = url_pattern.format(
        url=stripped_url,
        separator="&" if query_params else "?",
        expires=expiration_timestamp,
        key_name=key_name,
    )

    digest = ed25519.Ed25519PrivateKey.from_private_bytes(decoded_key).sign(
        url_to_sign.encode("utf-8")
    )
    signature = base64.urlsafe_b64encode(digest).decode("utf-8")
    signed_url = "{url}&Signature={signature}".format(
        url=url_to_sign, signature=signature
    )

    return signed_url


# [END mediacdn_sign_url]


# [START mediacdn_sign_url_prefix]
def sign_url_prefix(
    url: str,
    url_prefix: str,
    key_name: str,
    base64_key: str,
    expiration_time: datetime.datetime,
) -> str:
    """Gets the Signed URL string for the specified URL prefix and configuration.

    Args:
        url: URL of request.
        url_prefix: URL prefix to sign as a string.
        key_name: name of the signing key as a string.
        base64_key: signing key as a base64 encoded string.
        expiration_time: expiration time as a UTC datetime object.

    Returns:
        Returns the Signed URL appended with the query parameters based on the
        specified URL prefix and configuration.
    """
    stripped_url = url.strip()
    parsed_url = urllib.parse.urlsplit(stripped_url)
    query_params = urllib.parse.parse_qs(parsed_url.query, keep_blank_values=True)
    encoded_url_prefix = base64.urlsafe_b64encode(
        url_prefix.strip().encode("utf-8")
    ).decode("utf-8")
    epoch = datetime.datetime.utcfromtimestamp(0)
    expiration_timestamp = int((expiration_time - epoch).total_seconds())
    decoded_key = base64.urlsafe_b64decode(base64_key)

    policy_pattern = (
        "URLPrefix={encoded_url_prefix}&Expires={expires}&KeyName={key_name}"
    )
    policy = policy_pattern.format(
        encoded_url_prefix=encoded_url_prefix,
        expires=expiration_timestamp,
        key_name=key_name,
    )

    digest = ed25519.Ed25519PrivateKey.from_private_bytes(decoded_key).sign(
        policy.encode("utf-8")
    )
    signature = base64.urlsafe_b64encode(digest).decode("utf-8")
    signed_url = "{url}{separator}{policy}&Signature={signature}".format(
        url=stripped_url,
        separator="&" if query_params else "?",
        policy=policy,
        signature=signature,
    )
    return signed_url


# [START mediacdn_sign_url_prefix]


# [START mediacdn_sign_cookie]
def sign_cookie(
    url_prefix: str, key_name: str, base64_key: str, expiration_time: datetime.datetime
) -> str:
    """Gets the Signed cookie value for the specified URL prefix and configuration.

    Args:
        url_prefix: URL prefix to sign as a string.
        key_name: name of the signing key as a string.
        base64_key: signing key as a base64 encoded string.
        expiration_time: expiration time as a UTC datetime object.

    Returns:
        Returns the Edge-Cache-Cookie value based on the specified configuration.
    """
    encoded_url_prefix = base64.urlsafe_b64encode(
        url_prefix.strip().encode("utf-8")
    ).decode("utf-8")
    epoch = datetime.datetime.utcfromtimestamp(0)
    expiration_timestamp = int((expiration_time - epoch).total_seconds())
    decoded_key = base64.urlsafe_b64decode(base64_key)

    policy_pattern = (
        "URLPrefix={encoded_url_prefix}:Expires={expires}:KeyName={key_name}"
    )
    policy = policy_pattern.format(
        encoded_url_prefix=encoded_url_prefix,
        expires=expiration_timestamp,
        key_name=key_name,
    )
    digest = ed25519.Ed25519PrivateKey.from_private_bytes(decoded_key).sign(
        policy.encode("utf-8")
    )
    signature = base64.urlsafe_b64encode(digest).decode("utf-8")

    signed_policy = "Edge-Cache-Cookie={policy}:Signature={signature}".format(
        policy=policy, signature=signature
    )
    return signed_policy


# [END mediacdn_sign_cookie]


# [START mediacdn_sign_token]
def sign_token(
    base64_key: bytes,
    encryption_algorithm: str,
    expiration_time: datetime.datetime = None,
    url_prefix: str = None,
    full_path: str = None,
    path_globs: str = None,
) -> bytes:
    """Gets the Signed URL Suffix string for the Media CDN' Short token URL requests.

    One of (`url_prefix`, `full_path`, `path_globs`) must be included in each input.

    Args:
        base64_key: Secret key as a base64 encoded string.
        encryption_algorithm: Algorithm can be either `SHA1` or `SHA256`.
        expiration_time: Expiration time as a UTC datetime object.

        url_prefix: the URL prefix to sign, including protocol.
                    For example: http://example.com/path/ for URLs under /path or http://example.com/path?param=1
        full_path:  A full path to sign, starting with the first '/'.
                    For example: /path/to/content.mp4
        path_globs: a set of ','- or '!'-delimited path glob strings.
                    For example: /tv/*!/film/* to sign paths starting with /tv/ or /film/ in any URL.

    Returns:
        The Signed URL appended with the query parameters based on the
        specified URL prefix and configuration.
    """

    if url_prefix is None and full_path is None and path_globs is None:
        raise ValueError(
            "User Input Missing: One of `url_prefix`, `full_path` or `path_globs` must be specified"
        )

    algo = encryption_algorithm.lower()
    if algo not in ["sha1", "sha256", "ed25519"]:
        raise ValueError(
            "Input Missing Error: `encryption_algorithm` can only be one of `sha1`, `sha256` or `ed25519`"
        )

    if full_path:
        output = "FullPath".encode("utf-8")  # Not required to include path in signature
    elif path_globs:
        path_globs = path_globs.strip()
        output = f"PathGlobs={path_globs}".encode("utf-8")
    elif url_prefix:
        output = b"URLPrefix=" + base64.urlsafe_b64encode(url_prefix.encode("utf-8"))

        # TODO(sampathm): Remove following block
    while chr(output[-1]) == "=":
        output = output[:-1]

    if not expiration_time:
        expiration_time = datetime.datetime.now() + datetime.timedelta(hours=1)
    epoch_duration = int(
        (expiration_time - datetime.datetime.utcfromtimestamp(0)).total_seconds()
    )
    output += b"~Expires=" + str(epoch_duration).encode("utf-8")

    decoded_key = base64.urlsafe_b64decode(base64_key)
    if algo == "sha1":
        signature = hmac.new(decoded_key, output, digestmod=hashlib.sha1).hexdigest()
        output += b"~hmac=" + signature.encode("utf-8")
    elif algo == "sha256":
        signature = hmac.new(decoded_key, output, digestmod=hashlib.sha256).hexdigest()
        output += b"~hmac=" + signature.encode("utf-8")
    elif algo == "ed25519":
        digest = ed25519.Ed25519PrivateKey.from_private_bytes(decoded_key).sign(output)
        signature = base64.urlsafe_b64encode(digest).decode("utf-8")
        output += b"~Signature=" + signature.encode("utf-8")
    return output.decode("utf-8")


# [END mediacdn_sign_token]
