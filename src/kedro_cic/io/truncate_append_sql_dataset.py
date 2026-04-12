"""SQL dataset variants used by the project."""

from __future__ import annotations

import copy
from typing import Any

import pandas as pd
from kedro.io.core import DatasetError
from kedro_datasets.pandas.sql_dataset import SQLTableDataset
from sqlalchemy import MetaData, Table, text


class TruncateAppendSQLTableDataset(SQLTableDataset):
    """Persist a dataframe without dropping the target table."""

    def __init__(  # noqa: PLR0913
        self,
        *,
        table_name: str,
        credentials: dict[str, Any],
        load_args: dict[str, Any] | None = None,
        save_args: dict[str, Any] | None = None,
        truncate: bool = True,
        truncate_cascade: bool = False,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            table_name=table_name,
            credentials=credentials,
            load_args=load_args,
            save_args=save_args,
            metadata=metadata,
        )
        self._truncate = truncate
        self._truncate_cascade = truncate_cascade

        if self._save_args.get("if_exists") not in {None, "append"}:
            raise DatasetError(
                "TruncateAppendSQLTableDataset only supports "
                "save_args.if_exists='append'."
            )

        self._save_args["if_exists"] = "append"

    def _describe(self) -> dict[str, Any]:
        description = super()._describe()
        description["truncate"] = self._truncate
        description["truncate_cascade"] = self._truncate_cascade
        return description

    def _get_schema(self) -> str | None:
        return self._save_args.get("schema") or self._load_args.get("schema")

    def _get_truncate_statement(self) -> str:
        table = Table(
            self._load_args["table_name"],
            MetaData(),
            schema=self._get_schema(),
        )
        qualified_name = self.engine.dialect.identifier_preparer.format_table(table)
        cascade_clause = " CASCADE" if self._truncate_cascade else ""
        return f"TRUNCATE TABLE {qualified_name}{cascade_clause}"

    def _get_existing_column_names(self) -> list[str]:
        table = Table(
            self._load_args["table_name"],
            MetaData(),
            schema=self._get_schema(),
            autoload_with=self.engine,
        )
        return [column.name for column in table.columns]

    def save(self, data: pd.DataFrame) -> None:
        save_args = copy.deepcopy(self._save_args)
        save_args["if_exists"] = "append"

        with self.engine.begin() as connection:
            table_exists = self._exists()
            if self._truncate and table_exists:
                connection.execute(text(self._get_truncate_statement()))

            if table_exists:
                existing_columns = set(self._get_existing_column_names())
                data = data.loc[:, [col for col in data.columns if col in existing_columns]]

            data.to_sql(con=connection, **save_args)
