Contributing
============

Creating Issues

We use issues to keep track of bugs, enhancements, or other requests;
see GitLab issues.

To create an issue, you will:

* on GitLab, goto the Issues tab of the [Ingestum source
repository](https://gitlab.com/sorcero/community/ingestum/-/issues);
* Scan the existing issues to see if there is a relevant open issue
to your issue;
* If so, open that issue and add any relevant new information to it;
* If not, open a new issue;
* Make sure that the relevant labels are applied to the issue;
* During the weekly triage process, milestones and assignees will be set.

Creating Merge Requests

We use the merge-request model, see [GitLab's help on
pull-request](https://docs.gitlab.com/ee/user/project/merge_requests/).

In brief, you will:

* on GitLab, fork the [Ingestum source
repository](https://gitlab.com/sorcero/community/ingestum);
* on your computer, clone your fork repository,
* commit your changes in a new branch;
* push your branch and submit a merge-request for it; and
* go through the review process until your merge-request is merged.

Please do include relevant URLs, screen shots, browser console logs,
etc. when appropriate.

Checklist - everyone

* [ ] make a clone of the repository;

* [ ] check if what you want to change is available already in any other
branches or forks;

* [ ] make and test your changes;

* [ ] make a pytest test and/or test script for your changes;

* [ ] run qa.sh on your code to find any errors.

* [ ] if your changes add a new feature or will affect users; update
the appropriate files in the [docs
directory](https://gitlab.com/sorcero/community/ingestum/-/tree/master/docs);

* [ ] make a branch, one or more commits, and a merge request as per
the Workflow below.

Workflow
--------

### Forking

You should first fork the [Ingestum
repository](https://gitlab.com/sorcero/community/ingestum) on
GitLab. This step is needed only once. See [GitLab's help on
fork](https://docs.gitlab.com/ee/gitlab-basics/fork-project.html).

### Cloning

You should make a local clone of your fork.
This step is needed only once.

```
git@gitlab.com:sorcero/integrations/ingestum.git
cd ingestum
git remote add upstream https://gitlab.com/sorcero/community/ingestum.git
git fetch upstream
```

### Branching

Create a branch per set of changes; e.g. to fix a problem or add a feature;

```
git checkout -b BRANCH-NAME
```

Your BRANCH-NAME can be anything, other than master. The scope is your
forked repository. The branch name will be shown on pull-requests.

### Making commits

Change files, and commit. Commit messages are kept by git, and are
used later when problems are being solved. When writing a commit
message:

1. Start with a one-line summary of the change;
2. Leave a blank line after the summary;
3. Explain the problem that is solved, unless the summary makes it obvious;
4. When the problem was introduced by a previous commit, mention the hash;
5. When the problem is in an issue or ticket, add "Fixes #1234";
6. Avoid mentioning Gitlab or other pull-requests, as these are not kept in
the git history;
7. Use imperative mood, like "add foo", or "port to bar"; (if English
is not your first language, see [imperative
mood](https://en.wikipedia.org/wiki/Imperative_mood), [git
documentation](https://git.kernel.org/pub/scm/git/git.git/tree/Documentation/SubmittingPatches#n133)
and [blog post by Dan Clarke](https://www.danclarke.com/git-tense)).

Make one or more commits and push the branch to your repository;

```
git push origin BRANCH-NAME
```

### Sending a merge-request

Send a merge-request for your branch.

Navigate to your repository page in GitLab, switch to the branch you
made, and then press the **Merge Request** button.

When writing a merge-request message:

1. If there is only one commit, begin with the GitLab default of the commit
message, otherwise write a summary of the series of commits; and
2. Link to any relevant merge-requests, issues, or tickets.

A review will happen in the merge-request, and a reviewer will either;

1. Merge, squash, or rebase your commits;
2. Merge your commits with their own changes;
3. Ask you to make changes; or
4. Close and reject your merge-request giving reasons.

When they ask you for changes, you may have to change both files,
commits or commit messages.

When squashing commits to different files, use interactive rebase.

```
git rebase -i master
```

After resolving any conflicts, push the changes to the same branch;

```
git push --force origin
```

Then respond on the merge-request.

### Keep your merge-request up to date

When there have been upstream commits while your merge-request was open, you should rebase your merge-request;

```
git pull --rebase upstream
```

Then push the changes to the same branch;

```
git push --force origin
```

The pull-request will be updated.

### Keep your fork up to date

When there have been upstream commits since your fork was made, you
should bring these into your fork:

```
git checkout master
git pull upstream
git checkout BRANCH-NAME
```

### Close Issue

Once your merge-request is merged, you should close any issue or
ticket.  GitLab issues named as "Fixes" in a commit message may be
automatically closed.

Be sure to thank everyone who helped you out along the way.

Frequently Asked Questions
--------------------------

### I've used the GitLab editor, how can I rebase or amend commits?

Make a local clone of your GitLab repository, use `git commit --amend`
or the other advanced CLI features, then `git push` back to GitLab.

### Error 403 on `git push`

Most likely you have cloned someone else's repository, and you should
instead fork their repository, clone your own repository, make your
changes, then push.  See [Getting error 403 while submitting
PR](http://lists.sugarlabs.org/archive/sugar-devel/2017-March/053926.html)
and [D. Joe's
reply](http://lists.sugarlabs.org/archive/sugar-devel/2017-March/053929.html).
