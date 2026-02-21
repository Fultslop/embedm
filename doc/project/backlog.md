# Embedm backlog

## High level overview 

* Review, check if we can/need to move functionality from table transformer to other file. 
  * Opportunity to have transformer chaining ?
  * Note that table_transformer contains hard coded strings again.
  * Magic consts again:
      if ext == "csv":
        return _parse_delimited(content, ","), None
      if ext == "tsv":
        return _parse_delimited(content, "\t"), None
      if ext == "json":
        return _parse_json(content)
  => turn into a function map
  * Comments should capture intention. Guess it's hard to determine when it's needed and not
    eg. _parse_delimited
    * Error handlig is not using the status pattern established elsewhere
      eg: def _parse_json(content: str) -> tuple[list[Row], str | None]:
      try:
          data: Any = json.loads(content)
      except json.JSONDecodeError as exc:
          return [], _render_error(str_resources.err_table_invalid_json.format(exc=exc))
    * Avoid using unicode chars, prefer '->' over '→' in docs

* --silent --dry-run --verify
* Add progress indicator

