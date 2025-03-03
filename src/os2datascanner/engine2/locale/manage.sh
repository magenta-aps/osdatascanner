#!/bin/bash

here="$(dirname "$0")"
source_path="$here/.."
locale_path="$here"
domain="osds_engine2"

error() {
    echo "$@" 2>&1
}

die() {
    code="$1"
    shift 1
    error "$@"
    exit "$code"
}

for command in xgettext msgmerge msgfmt msginit
do
    $command --version > /dev/null || \
        die 4 "$0: command '$command' not found; have you installed gettext?"
done

makemessages() {
    case "$1" in
        --help | -h)
            cat <<END
Usage: $0 makemessages

Generates a new .pot template from the Python source code in the parent folder
and, for each folder in the locale path, uses the template to either update its
.po file or to create a new one.
END
        exit
    esac

    echo "$0: building translation template"
    pot="$locale_path/$domain.pot"
    find "$source_path/" -iname '*.py' -print0 | \
            xargs -0 -- xgettext --output "$pot"
    for language in "$locale_path"/*/
    do
        po="$language/LC_MESSAGES/$domain.po"
        mkdir -p "$(dirname "$po")"
        if [ -f "$po" ]
        then
            echo "$0: updating translation file $po"
            msgmerge --quiet --backup off --update "$po" "$pot"
        else
            echo "$0: creating translation file $po"
            msginit --no-translator -i "$pot" -o "$po"
        fi
    done
}

compilemessages() {
    case "$1" in
        --help | -h)
            cat <<END
Usage: $0 compilemessages

Compiles every .po file in the locale path into a .mo file.
END
        exit
    esac

    for po in "$locale_path/"*"/LC_MESSAGES/$domain.po"
    do
        echo "$0: compiling $po"
        msgfmt "$po" -o "${po%%.po}".mo
    done
}

translate() {
    case "$1" in
        --help | -h)
            cat <<END
Usage: $0 translate LANGUAGE_CODE [MSGID [MSGID...]]

Prints out the translation of each MSGID in the given language, if there is
one. (Remember to run the compilemessages subcommand first.)
END
        exit
    esac

    lang="$1"
    shift 1
    LANGUAGE="$lang" TEXTDOMAINDIR="$locale_path" gettext -d "$domain" -s "$@"
}

case "$1" in
    help | --help | -h)
        cat <<END
Usage: $0 SUBCOMMAND [OPTIONS]

Manages translations.

SUBCOMMAND can be any of the following:
- makemessages (aliases: make, m)
- compilemessages (aliases: compile, c)
- translate (aliases: trans, t)
END
        exit
        ;;
    makemessages | make | m)
        shift 1
        makemessages "$@"
        ;;
    compilemessages | compile | c)
        shift 1
        compilemessages "$@"
        ;;
    translate | trans | t)
        shift 1
        translate "$@"
        ;;
    "")
        die 2 "$0: no command given (try 'makemessages' or 'compilemessages')"
        ;;
    *)
        die 3 "$0: unrecognised subcommand '$1'"
esac

echo "$0: all tasks complete"
