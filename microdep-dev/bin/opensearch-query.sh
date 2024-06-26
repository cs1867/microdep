#!/bin/bash
#
# Send Query string to Opensearch instance
#

URL="https://localhost:9200"
CREDS=`sed 's| |:|' /etc/perfsonar/opensearch/opensearch_login 2>/dev/null`
ACTION="GET"
IPV="-4"

function usage {
    echo "Run api command towards Opensearch server"
    echo "`basename $0` [-h] [options] api-command-path [json-input-structure]"
    echo "  -h           Help message."
    echo "  -c user:pwd  Credential to apply (defaults are fetched from /etc/perfsonar/opensearch/opensearch_login)" 
    echo "  -U url       Base url to Opensearch instance (default $URL)"
    echo "  -G           Apply GET (default)"
    echo "  -P           Apply POST and read json from stdin"
    echo "  -D           Apply DELETE"
    echo "  -v           Be verbose"
    exit 1;
}

FDATE=`date -I`
TFIELD="@timestamp"

# Parse arguments
while getopts ":U:c:hDPGv" opt; do
    case $opt in
	U)
	    URL=$OPTARG
	    ;;
	c)
	    CREDS=$OPTARG
	    ;;
	P)
	    ACTION="POST"
	    ;;
	G)
	    ACTION="GET"
	    ;;
	D)
	    echo -n "Applying DELETE. Are your sure (y/N)? "
	    read yesno
	    if [ -z $yesno ]; then exit 1; fi
	    if [ ! ${yesno:0:1} = "y" -a ! ${yesno:0:1} = "Y" ]; then
		exit 1;
	    fi
	    ACTION="DELETE"
	    ;;
	v)
	    VERBOSE="yes"
	    ;;
	h)
	    usage
	    ;;
	\?)
	    echo "Invalid option: -$OPTARG" >&2
	    exit 1
	    ;;
	:)
	    echo "Option -$OPTARG requires an argument." >&2
	    exit 1
	    ;;
    esac
done
shift $(($OPTIND - 1))  # (Shift away parsed arguments)


if [ $# -lt 1 ]; then
    usage
fi

if [ $CREDS ]; then
    # Prepare credentials as cli option
    CREDS="-u $CREDS"
fi
if [ $ACTION = "POST" ]; then
    INPUTTYPE="-H 'Content-Type: application/json'"
fi
CMD="curl -s --insecure $IPV $CREDS -X $ACTION $INPUTTYPE $URL/$1 "
if [ $VERBOSE ]; then
    echo $CMD
fi
exec $CMD
