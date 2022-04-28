# -*- coding: utf-8 -*-

raw_makeself = r"""
#!/bin/sh


unset CDPATH

if test -d /usr/xpg4/bin; then
    PATH=/usr/xpg4/bin:$PATH
    export PATH
fi

# Procedures
MS_Usage()
{
    echo "Error"
    exit 1
}

# Default settings
if type gzip >/dev/null 2>&1; then
    COMPRESS=gzip
elif type compress >/dev/null 2>&1; then
    COMPRESS=compress
else
    echo "ERROR: missing commands: gzip, compress" >&2
    MS_Usage
fi


ENCRYPT=n
OPENSSL_NO_MD=n
COMPRESS_LEVEL=9
DEFAULT_THREADS=123456 # Sentinel value
THREADS=$DEFAULT_THREADS
KEEP=n
CURRENT=n
NOX11=n
NOWAIT=n
APPEND=n
TAR_QUIETLY=n
KEEP_UMASK=n
QUIET=n
NOPROGRESS=n
COPY=none
NEED_ROOT=n
TAR_ARGS=rvf
TAR_FORMAT=ustar
DU_ARGS=-ks
HEADER=`dirname "$0"`/makeself-header.sh
NOOVERWRITE=n
DATE=`LC_ALL=C date`
EXPORT_CONF=n
SHA256=n
OWNERSHIP=n
SIGN=n

LSM_CMD="echo No LSM. >> \"\$archname\""

APPEND=y
shift

archdir="$1"
archname="$2"


if test "$APPEND" = y; then
    if test $# -lt 2; then
        MS_Usage
    fi

    # Gather the info from the original archive
    OLDENV=`sh "$archname" --dumpconf`
    if test $? -ne 0; then
        echo "Unable to update archive: $archname" >&2
        exit 1
    else
        eval "$OLDENV"
        OLDSKIP=`expr $SKIP + 1`
    fi
else
    if test "$KEEP" = n -a $# = 3; then
        echo "ERROR: Making a temporary archive with no embedded command does not make sense!" >&2
        echo >&2
        MS_Usage
    fi
    # We don't want to create an absolute directory unless a target directory is defined
    if test "$CURRENT" = y; then
        archdirname="."
    elif test x"$TARGETDIR" != x; then
        archdirname="$TARGETDIR"
    else
        archdirname=`basename "$1"`
    fi

    if test $# -lt 3; then
        MS_Usage
    fi

    LABEL="$3"
    SCRIPT="$4"
    test "x$SCRIPT" = x || shift 1
    shift 3
    SCRIPTARGS="$*"
fi

if test "$KEEP" = n -a "$CURRENT" = y; then
    echo "ERROR: It is A VERY DANGEROUS IDEA to try to combine --notemp and --current." >&2
    exit 1
fi

case $COMPRESS in
gzip)
    GZIP_CMD="gzip -c$COMPRESS_LEVEL"
    GUNZIP_CMD="gzip -cd"
    ;;
compress)
    GZIP_CMD="compress -fc"
    GUNZIP_CMD="(type compress >/dev/null 2>&1 && compress -fcd || gzip -cd)"
    ;;
none)
    GZIP_CMD="cat"
    GUNZIP_CMD="cat"
    ;;
esac

tmpfile="${TMPDIR:-/tmp}/mkself$$"

if test -f "$HEADER"; then
    oldarchname="$archname"
    archname="$tmpfile"
    # Generate a fake header to count its lines
    SKIP=0
    . "$HEADER"
    SKIP=`cat "$tmpfile" |wc -l`
    # Get rid of any spaces
    SKIP=`expr $SKIP`
    rm -f "$tmpfile"
    if test "$QUIET" = "n"; then
        echo "Header is $SKIP lines long" >&2
    fi
    archname="$oldarchname"
else
    echo "Unable to open header file: $HEADER" >&2
    exit 1
fi

if test "$QUIET" = "n"; then
    echo
fi

USIZE=`du $DU_ARGS "$archdir" | awk '{print $1}'`

if test "." = "$archdirname"; then
    if test "$KEEP" = n; then
        archdirname="makeself-$$-`date +%Y%m%d%H%M%S`"
    fi
fi

test -d "$archdir" || { echo "Error: $archdir does not exist."; rm -f "$tmpfile"; exit 1; }
if test "$QUIET" = "n"; then
   echo "About to compress $USIZE KB of data..."
   echo "Adding files to archive named \"$archname\"..."
fi

# See if we have GNU tar
TAR=`exec <&- 2>&-; which gtar || command -v gtar || type gtar`
test -x "$TAR" || TAR=tar

tmparch="${TMPDIR:-/tmp}/mkself$$.tar"
(
    if test "$APPEND" = "y"; then
        tail -n "+$OLDSKIP" "$archname" | eval "$GUNZIP_CMD" > "$tmparch"
    fi
    cd "$archdir"
    find . \
        \( \
        ! -type d \
        -o \
        \( -links 2 -exec sh -c '
            is_empty () (
                cd "$1"
                set -- .[!.]* ; test -f "$1" && return 1
                set -- ..?* ; test -f "$1" && return 1
                set -- * ; test -f "$1" && return 1
                return 0
            )
            is_empty "$0"' {} \; \
        \) \
        \) -print \
        | LC_ALL=C sort \
        | sed 's/./\\&/g' \
        | xargs $TAR $TAR_EXTRA --format $TAR_FORMAT -$TAR_ARGS "$tmparch"
) || {
    echo "ERROR: failed to create temporary archive: $tmparch"
    rm -f "$tmparch" "$tmpfile"
    exit 1
}

USIZE=`du $DU_ARGS "$tmparch" | awk '{print $1}'`

eval "$GZIP_CMD" <"$tmparch" >"$tmpfile" || {
    echo "ERROR: failed to create temporary file: $tmpfile"
    rm -f "$tmparch" "$tmpfile"
    exit 1
}
rm -f "$tmparch"

if test x"$ENCRYPT" = x"openssl"; then
    echo "About to encrypt archive \"$archname\"..."
    { eval "$ENCRYPT_CMD -in $tmpfile -out ${tmpfile}.enc" && mv -f ${tmpfile}.enc $tmpfile; } || \
        { echo Aborting: could not encrypt temporary file: "$tmpfile".; rm -f "$tmpfile"; exit 1; }
fi

fsize=`cat "$tmpfile" | wc -c | tr -d " "`

# Compute the checksums

shasum=0000000000000000000000000000000000000000000000000000000000000000
md5sum=00000000000000000000000000000000
crcsum=0000000000


OLD_PATH=$PATH
PATH=${GUESS_MD5_PATH:-"$OLD_PATH:/bin:/usr/bin:/sbin:/usr/local/ssl/bin:/usr/local/bin:/opt/openssl/bin"}
MD5_ARG=""
MD5_PATH=`exec <&- 2>&-; which md5sum || command -v md5sum || type md5sum`
test -x "$MD5_PATH" || MD5_PATH=`exec <&- 2>&-; which md5 || command -v md5 || type md5`
test -x "$MD5_PATH" || MD5_PATH=`exec <&- 2>&-; which digest || command -v digest || type digest`
PATH=$OLD_PATH
if test -x "$MD5_PATH"; then
    if test `basename ${MD5_PATH}`x = digestx; then
        MD5_ARG="-a md5"
    fi
    md5sum=`eval "$MD5_PATH $MD5_ARG" < "$tmpfile" | cut -b-32`
    if test "$QUIET" = "n"; then
        echo "MD5: $md5sum"
    fi
else
    if test "$QUIET" = "n"; then
        echo "MD5: none, MD5 command not found"
    fi
fi


totalsize=0
for size in $fsize;
do
    totalsize=`expr $totalsize + $size`
done

if test "$APPEND" = y; then
    mv "$archname" "$archname".bak || exit

    # Prepare entry for new archive
    filesizes="$fsize"
    CRCsum="$crcsum"
    MD5sum="$md5sum"
    SHAsum="$shasum"
    Signature="$SIGNATURE"
    # Generate the header
    . "$HEADER"
    # Append the new data
    cat "$tmpfile" >> "$archname"

    chmod +x "$archname"
    rm -f "$archname".bak
    if test "$QUIET" = "n"; then
        echo "Self-extractable archive \"$archname\" successfully updated."
    fi
else
    filesizes="$fsize"
    CRCsum="$crcsum"
    MD5sum="$md5sum"
    SHAsum="$shasum"
    Signature="$SIGNATURE"

    # Generate the header
    . "$HEADER"

    # Append the compressed tar data after the stub
    if test "$QUIET" = "n"; then
        echo
    fi
    cat "$tmpfile" >> "$archname"
    chmod +x "$archname"
    if test "$QUIET" = "n"; then
        echo Self-extractable archive \"$archname\" successfully created.
    fi
fi
rm -f "$tmpfile"

"""




