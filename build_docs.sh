#!/usr/bin/env bash
# Builds the book locally and serves it. The published version is built by the
# deploy-book GitHub Actions workflow, this script is for previewing changes.
#
# Usage:
#   ./build_docs.sh              build, stopping at the first task that errors
#   ./build_docs.sh --tolerant   build everything, putting tracebacks on the
#                                pages of tasks that fail
#
# Use --tolerant when your machine is missing some of the nuclear data, for
# example the depletion chain file or the WMP library. Without it quarto stops
# at the first failing task, and because it empties the output directory before
# it starts you are left with a mostly empty _build/html.
set -e

if ! command -v quarto > /dev/null; then
  echo "quarto is not on your PATH." >&2
  echo >&2
  echo "Install it with:" >&2
  echo "    pip install quarto-cli" >&2
  echo >&2
  echo "Note the -cli suffix. The package called just 'quarto' on PyPI is an" >&2
  echo "unrelated project and does not provide the quarto command." >&2
  echo "The standalone installers at https://quarto.org/docs/get-started/ work too." >&2
  exit 1
fi

render_args=()
if [ "${1:-}" = "--tolerant" ]; then
  # CI leaves this off so that a task which stops working fails the build
  render_args+=(-M error:true)
  shift
fi

# Executes any task whose source has changed since the last build and reuses the
# cached results in _freeze for the rest. Do not add --no-execute, it drops every
# plot and table from the pages.
quarto render "${render_args[@]}" "$@"

echo
echo "Book built in _build/html, open _build/html/index.html to view it."
echo "Use 'quarto preview' for a live reloading version."
