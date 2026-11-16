#!/usr/bin/env bash
# Release checks for thetripnow (mochi-agent/RELEASE-CHECKS.md). Read-only; no secrets.
#   tools/release-check.sh pre    # on the PR branch, before merge
#   tools/release-check.sh post   # after the merge has deployed
set -u
SITE=https://thetripnow.com
REPO=ptk-studio/the-trip-now-www
# Files served by GitHub Pages on purpose. Anything else at the top level must be in _config.yml exclude.
PUBLIC="CNAME index.html _config.yml assets privacy"
fail=0
ok()  { printf 'PASS  %s\n' "$1"; }
bad() { printf 'FAIL  %s\n' "$1"; fail=1; }

excludes() { awk '/^exclude:/{f=1;next} f&&/^  - /{sub(/^  - /,"");print;next} f&&!/^  - /{f=0}' _config.yml; }

pre() {
  base=$(git merge-base HEAD origin/main)
  # 1. every top-level path is public or excluded
  ex=$(excludes)
  for p in $(git ls-files | cut -d/ -f1 | sort -u); do
    case " $PUBLIC " in *" $p "*) continue;; esac
    if printf '%s\n' "$ex" | grep -qx -e "$p" -e "$p/"; then continue; fi
    bad "top-level '$p' is neither public nor in _config.yml exclude"
  done
  [ $fail = 0 ] && ok "every top-level path is public or excluded"
  # 2. no secrets in the diff (key-like strings)
  if git diff "$base"...HEAD | grep -E '^\+' | grep -Eiq '(api[_-]?key|secret|token|password)\s*[:=]\s*["'"'"']?[A-Za-z0-9_\-]{12,}|sk-[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}'; then
    bad "possible secret in the diff (check the + lines)"
  else ok "no secret-like strings in the diff"; fi
  # 3. index.html still links the store and the title is intact
  grep -q 'The Trip Now' index.html && ok "index.html has the site title" || bad "index.html lost 'The Trip Now'"
  grep -q 'shop.88eggs.com/store/the-trip-now' index.html && ok "index.html links the store" || bad "index.html lost the store link"
}

post() {
  st=$(gh api repos/$REPO/pages/builds/latest --jq '.status+" "+.commit[0:7]' 2>/dev/null)
  main=$(git ls-remote "https://github.com/$REPO" refs/heads/main | cut -c1-7)
  case "$st" in "built $main") ok "Pages build: $st (main $main)";; *) bad "Pages build '$st', main is $main";; esac
  body=$(curl -s -w '\n%{http_code}' "$SITE/"); code=${body##*$'\n'}
  [ "$code" = 200 ] && printf '%s' "$body" | grep -q 'The Trip Now' && ok "$SITE/ 200 + 'The Trip Now'" || bad "$SITE/ -> $code"
  for p in $(excludes); do
    c=$(curl -s -o /dev/null -w '%{http_code}' "$SITE/${p%/}"); c2=$(curl -s -o /dev/null -w '%{http_code}' "$SITE/$p")
    [ "$c" = 404 ] && [ "$c2" = 404 ] && ok "/$p not served (404)" || bad "/$p is served ($c/$c2)"
  done
  c=$(curl -s -o /dev/null -w '%{http_code}' https://shop.88eggs.com/store/the-trip-now)
  [ "$c" = 200 ] && ok "store page 200" || bad "store page -> $c"
}

case "${1:-}" in pre) pre;; post) post;; *) echo "usage: $0 pre|post"; exit 2;; esac
exit $fail
