# Package Cleanup Notes

## Before

The Lambda package included `node-serialize`, which allowed unsafe executable deserialization.

```json
{
  "dependencies": {
    "node-serialize": "<vulnerable-version>"
  }
}
```

## After

Remove `node-serialize` if no safe internal-only use remains.

```json
{
  "dependencies": {}
}
```

The application should parse request bodies with `JSON.parse()` and validate fields explicitly.
