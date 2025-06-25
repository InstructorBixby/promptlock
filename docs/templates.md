# Templates

`{{name}}` is a placeholder. Everything else is literal text.

| written | rendered |
|---|---|
| `{{name}}` | the value of `name` |
| `{{ name }}` | the same; inner whitespace is ignored |
| `{{{{name}}}}` | the literal text `{{name}}` |
| `{name}` | the literal text `{name}` |
| `{"a": 1}` | unchanged, which is the whole reason for double braces |

## required and optional

`variables` in the registry is the required set: `render` fails if a
call site omits one. `optional` is a placeholder a call site may omit --
which still means `render` fails, because it cannot invent a value. The
distinction exists so `check` can tell a deliberately-situational
placeholder from a drifted declaration.

There is no default-value syntax and there will not be. A default is a
second prompt hiding inside the first one, with no id and no hash.

## errors, and the one they prevent

Both directions are errors:

- a placeholder the call site did not supply
- a value the template has no placeholder for

The second is the one people argue about, and it is the one that catches
real bugs: a renamed placeholder leaves every call site passing the old
key, and under a permissive renderer the prompt simply loses that
section. The request succeeds. The model answers. Nothing says a word,
and the eval that proved the prompt safe was run against the version
that still had the section in it.

## what a placeholder must not be used for

Do not interpolate retrieved or user-controlled text through a
placeholder and then treat the result as the trusted prompt. The hash
covers the template, not the value, and nothing here yet gives you a
handle on the text the model actually saw.
