"""Allow running abacus_lsp as a module: python -m abacus_lsp."""
from __future__ import annotations

import sys

from .cli import agent_main, fmt_main, lint_main, lsp_main, test_main


def main() -> int:
    args = sys.argv[1:]

    agent_commands = {
        "query-diagnostics", "explain-diagnostic", "apply-fix",
        "export-context", "backend",
    }
    test_commands = {"static", "smoke", "regression"}
    test_prefix = {"test"}

    if args and args[0] in agent_commands:
        return agent_main(args)
    elif args and args[0] in test_commands:
        return test_main(args)
    elif args and args[0] in test_prefix:
        return test_main(args[1:])
    elif args and args[0] == "lint":
        return lint_main(args[1:])
    elif args and args[0] == "fmt":
        return fmt_main(args[1:])
    elif args and args[0] == "--stdio":
        return lsp_main(args)
    else:
        return agent_main(args)


if __name__ == "__main__":
    sys.exit(main())
