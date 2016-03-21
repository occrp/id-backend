#!/bin/bash

PATTERN="2.*"
CURVER=$(git tag -l $PATTERN | sort --version-sort | tail -n 1)
PREVVER=$(git tag -l $PATTERN | sort --version-sort | tail -n 2 | head -n 1)

echo -e "subject: Investigative Dashboard v$CURVER\n"

cat <<EOF
Hello!

  This is to inform you that version $CURVER of Investigative Dashboard has been tagged for release.

  You don't have to take any action, but be aware that the following changes will be made live within the next hour.

  Kind regards,
    OCCRP's tech team


Summary of changes:
EOF
git log --oneline --decorate $PREVVER..$CURVER;
