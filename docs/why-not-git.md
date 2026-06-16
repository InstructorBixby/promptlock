# "Can't I just use git for this?"

Mostly yes, and the honest answer is that for prompts that are files
in a reviewed repository, git already gives most of this. What it does
not give is these five things, and each one is why a piece of this
tool exists.

**1. A canonical hash.** `git log -p prompts/` tells you a file
changed. It cannot tell you whether the change mattered. A reflowed
paragraph and a reversed instruction are the same size diff. The
canonical form plus the whitespace-only classification in
`promptlock diff` is the difference between "something changed" and
"something changed that a model will notice".

**2. A name a result can be attached to.** A commit sha names a whole
tree. An eval result is about one string. Binding a number to a commit
means the number silently covers every unrelated change in that commit,
and re-running it after an unrelated change looks like a regression.

**3. Anything that is not a file.** A prompt in a database row edited
through an admin page has no commit, no review and no diff. That is the
case that most needs a gate and it is the one git cannot reach.

**4. A statement about production.** `git status` is clean on a machine
that has not deployed in three weeks. `promptlock verify --deployed`
asks the running process what it has loaded. These are different
questions and only one of them is interesting.

**5. A declaration to check against.** git has no opinion about whether
a prompt's variables match its call sites. `promptlock check` does, and
that catches a class of silent-empty-string bug that no amount of
version control touches.

## what git does better

Blame, history, review, branching, and the fact that it is already
there. Nothing in here replaces any of that. The lockfile is a file in
git; the store is directories in git; the gate runs in the pipeline
git already triggers. If a future version of this ever needs a server
of its own, it has gone wrong.
