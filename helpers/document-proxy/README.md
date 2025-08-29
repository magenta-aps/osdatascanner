# `document_proxy`

## What is this?

`document_proxy` is a middleman that can retrieve documents and metadata from
systems that don't speak a standard protocol like HTTP.

In particular, `document_proxy` understands how to open connections to the
metadata and document storage databases used by [SBSYS](https://sbsys.dk/), an
issue management system widely used in the Danish public sector.

## How do I set this up?

`document_proxy` is designed to be used as a Docker image, so its configuration
is driven by a few simple environment variables:

| Variable | Meaning |
| -------- | ------- |
| `DP_TOKEN_LIFETIME` | The duration (in seconds) for which an authentication token should be valid |

Define those in your deployment environment (or, if you just want to try it out
locally, in `docker-compose.yml`) before starting the system up.

## How do I try this out?

You'll need a environment that `document_proxy` can actually talk to. (The
OSdatascanner development environment starts a small SBSYS-compatible database
up when you use its `sbsys` profile.)

`document_proxy` expects you to use the OAuth 2.0 client credentials flow, but
`document_proxy` itself doesn't have any secrets you need to know -- instead,
the flow is used to communicate login details for the external system. (The
resulting token is an encrypted and timestamped representation of these
details; the encryption key is randomly generated when `document_proxy` starts
up.)

### SBSYS

#### `POST /sbsys.document/token`

To get started with SBSYS documents, make a `POST` request to the endpoint
 with the following parameters:

* for `grant_type`, specify `client_credentials`;
* for `client_id`, specify a string of the form `user@host:port/database` (or
  just `user@host/database` to use the default port); and
* for `client_secret`, specify the password for the named account.

The result is a JSON-formatted message; the bearer token required to use the
other endpoints is returned in its `access_token` field.

(As is customary for the client credentials flow, there's no refresh token;
once the bearer token expires, just make another request to this endpoint.)

#### `POST /sbsys.document/test_token`

Making a `POST` request to the `/sbsys.document/test_token` endpoint will give
you a HTTP `200 OK` response if the authentication token is present and valid,
and a `401 Unauthorized` response if it's not.

#### `HEAD /sbsys.document/<id:int>`

Making an authorised `HEAD` request to the `/sbsys.document/<int:pk>` endpoint,
where `pk` is the primary key of a SBSYS `Dokument` object that hasn't been
deleted, will give you a HTTP `200 OK` response with the following headers set:

* `Content-Type`, for the MIME type of the stored document;
* `Content-Disposition`, for its filename (returned in the `filename=`
  directive); and
* `Content-Length`, for its size.

If the `Dokument` object exists but its content has been deleted, the response
will be a HTTP `401 Gone`; if the `Dokument` object doesn't exist then the
response will be a `404 Not Found`.

#### `GET /sbsys.document/<id:int>`

Making an authorised `GET` request to the `/sbsys.document/<int:pk>` endpoint
behaves in every way like the `HEAD` request, except that the content of the
underlying document will also be returned if it's available.

## Who's behind this?

`document_proxy` is brought to you by [Magenta ApS](https://www.magenta.dk/),
the largest pure-play open source developer in Scandinavia. We have offices in
Copenhagen, Aarhus, and Nuuk, and we have customers -- colossal, tiny, and
everything in between -- from the public and private sector across all of
Denmark and Greenland.

Since we started in 1999, we've released all of our products under open source
and free software licences, and it'll stay that way! You deserve to know what
the programs you depend on are doing, and to be able to change them if you want
them to do something else.

`document_proxy` has been developed for use alongside
[OSdatascanner](https://os2datascanner.magenta.dk/), the advanced GDPR
compliance and data scanning tool we maintain and develop.

If you'd like to talk to us about any of our products, our plans for them, or
even about financing the development of a feature you need, you can always get
in touch with us at info@magenta.dk.

----

`document_proxy` is copyright © Magenta ApS 2024-2025, and its use is subject
to the terms of the Mozilla Public License, v. 2.0. See the `LICENSE` file for
more details.

Based in part on `fp_proxy`, copyright © Magenta ApS 2022, also released
subject to the terms of the Mozilla Public License, v. 2.0.
