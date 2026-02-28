# The gate in a pipeline

Two jobs, and they answer different questions.

## 1. the repository agrees with itself

Runs on every push and merge request. Cheap, no network, no secrets.

    - run: promptlock verify
    - run: promptlock check
    - run: promptlock fmt --check

This catches an edited prompt with a stale pin, a declaration that no
longer matches the text, and a file whose whitespace disagrees with its
own hash. It does *not* catch anything about production, because it only
ever looked at the checkout.

## 2. production agrees with the repository

Runs after a deploy, and on a schedule, because the interesting drift
happens between deploys.

    - promptlock verify --format json > verify.json

with `PROMPTLOCK_DB` in the job's variables, masked. With a database
source this is the check that matters: a prompt edited through an
admin page and the text under test is no longer the text running. In a
file-only setup there is nothing to compare against at runtime and job
1 is all there is, which is worth knowing before concluding the gate
covers production.

## the whole thing, as it stands in my repositories

    prompts:
      image: python:3.12
      script:
        - pipx install ./vendor/promptlock-1.0.0-py3-none-any.whl
        - promptlock verify
        - promptlock check
        - promptlock fmt --check

    prompts-nightly:
      image: python:3.12
      rules:
        - if: $CI_PIPELINE_SOURCE == "schedule"
      script:
        - pipx install ./vendor/promptlock-1.0.0-py3-none-any.whl
        - promptlock verify
        - promptlock eval check

The wheel is vendored into each repository that gates on this. Not
elegant, and the alternative is a gate that depends on my instance
being up, which is a worse property for the thing whose job is to be
boringly reliable.

## eval check in CI, carefully

`promptlock eval check` exits 1 for a stale binding, and a stale
binding is the *normal* state for about a day after any prompt edit.
On the merge-request job that means every prompt change is red until
the evals have been re-run, which trained me to merge red inside a
week.

On a schedule it is a useful nag. On a merge request it is a tax. Run
it nightly, let it fail, and treat the failure as a queue of evals to
re-run rather than a broken build.

## pre-commit

    - repo: local
      hooks:
        - id: promptlock
          name: promptlock verify
          entry: promptlock verify
          language: system
          pass_filenames: false
          files: ^(prompts/|promptlock\.(toml|lock))

Scoped to the prompt directory and the registry so it does not run on
every unrelated commit. The hook is a convenience, not the gate: a hook
can be skipped and CI cannot.
