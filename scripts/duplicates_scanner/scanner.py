import argparse
import json

from db_models import DbColumn
from logger import LOGGER


def main():
    LOGGER.info("========== Scanner started ==========")

    # Getting arguments from input
    parser = argparse.ArgumentParser(description='Scan Database column on duplicates')
    parser.add_argument(
        '-t', '--table-name', required=True, metavar="", type=str, help='Table name in Database'
    )
    parser.add_argument(
        '-c', '--column-name', required=True, metavar="", type=str, help='Column name to scan'
    )
    parser.add_argument(
        '-o',
        '--output-format',
        default='json',
        choices=['json', 'md'],
        help='If values in column are case-sensetive',
    )
    parser.add_argument(
        '--case-sensetive', action='store_true', help='If values in column are case-sensetive'
    )
    args = parser.parse_args()

    # Scan column
    db_column = DbColumn(args.table_name, args.column_name, args.case_sensetive)
    db_column.find_duplicates()

    if args.output_format == "md":
        log_value_dups = db_column.duplicates.to_markdown(index=False)
    else:
        log_value_dups = json.dumps(db_column.duplicates.to_dict('records'))

    LOGGER.info(
        "(%s.%s) Duplicates found (total %s): %s",
        db_column.table,
        db_column.column,
        db_column.duplicates.shape[0],
        log_value_dups,
    )
    db_column.find_trailing_spaces()

    if args.output_format == "md":
        log_value_spaces = db_column.trailing_spaces.to_markdown(index=False)
    else:
        log_value_spaces = json.dumps(db_column.trailing_spaces.to_dict('records'))

    LOGGER.info(
        "(%s.%s) Trailing spaces found (total %s): %s",
        db_column.table,
        db_column.column,
        db_column.trailing_spaces.shape[0],
        log_value_spaces,
    )
    db_column.find_relations()

    if args.output_format == "md":
        LOGGER.info(
            "Relations found:\n%s",
            db_column.relations.to_markdown(index=False),
        )
    else:
        for _, row in db_column.relations.iterrows():
            row = row.dropna()
            LOGGER.info(
                "Relations found:\n%s\n",
                row.to_json(),
            )

    LOGGER.info("========== Scanner finished ==========\n")


if __name__ == "__main__":
    main()
