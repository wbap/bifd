#!/bin/bash
usage() {      #(*1)
  echo "usage:"
  echo "${0} -b bifd.owl -d dump.rdf -h header.rdf [-m] -o result.owl"
  exit 1
}

while getopts "b:d:h:mo:" opts
do
  case $opts in
    b)
      BIFD_FILE=$OPTARG
      ;;
    d)
      DUMP_MEDIAWIKI_FILE=$OPTARG
      ;;
    h)
      HEADER_FILE=$OPTARG
      ;;
    m)
      echo "Keep intermediate files."
      KEEP_INTERMEDIATE_FILES=true
      ;;
    o)
      OUTPUT_FILE=$OPTARG
      ;;
    :|\?) usage;;
  esac
done

[ -z "${BIFD_FILE}" ] && usage && exit 1
[ -z "${DUMP_MEDIAWIKI_FILE}" ] && usage && exit 1
[ -z "${HEADER_FILE}" ] && usage && exit 1
[ -z "${OUTPUT_FILE}" ] && usage && exit 1

REPO_DIR="$(dirname $0)"
python3 ${REPO_DIR}/mapping.py -i ${DUMP_MEDIAWIKI_FILE} -o s.tsv
python3 ${REPO_DIR}/mapping_predicate.py -i ${DUMP_MEDIAWIKI_FILE} -o p.tsv
python3 ${REPO_DIR}/converter.py -i ${DUMP_MEDIAWIKI_FILE} -d ${HEADER_FILE} -s s.tsv -p p.tsv -b ${BIFD_FILE} -o ${OUTPUT_FILE}
if [[ "${KEEP_INTERMEDIATE_FILES}" != true ]] ; then
  rm s.tsv p.tsv
fi
