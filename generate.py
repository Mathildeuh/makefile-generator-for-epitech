#!/usr/bin/env python3

import sys
import os
from datetime import datetime
from colorama import init, Fore, Style

# Initialize colorama
init(autoreset=True)

# =============================================================================
# Constants
# =============================================================================

MAKEFILE_HEADER = """\
##
## EPITECH PROJECT, {year}
## {project_name}
## File description:
## Makefile
##"""

DEFAULT_CC = "clang-20"
DEFAULT_CFLAGS = "-Werror -Wextra"
CRITERION_FLAGS = "-lcriterion --coverage"

# =============================================================================
# Helper Functions
# =============================================================================

def print_colored(message: str, color: str = Fore.WHITE, style: str = Style.NORMAL) -> None:
    """Print a colored message."""
    print(f"{style}{color}{message}{Style.RESET_ALL}")

def generate_makefile_header(project_name: str) -> str:
    """Generate Makefile header."""
    return MAKEFILE_HEADER.format(
        year=datetime.now().year,
        project_name=project_name
    )

def generate_makefile(
    project_name: str,
    binary_name: str,
    src_files: list[str],
    include_dirs: list[str] = ["./include"],
    extra_flags: list[str] = None,
    test_files: list[str] = None
) -> str:
    """Generate a Makefile for EPITECH with build directory and tests."""
    makefile = []
    makefile.append(generate_makefile_header(project_name))
    makefile.append("\n\n")

    # CC
    makefile.append(f"CC = {DEFAULT_CC}\n\n")

    # CFLAGS
    cflags = DEFAULT_CFLAGS
    if include_dirs:
        include_flags = " ".join(f"-I{inc}" for inc in include_dirs)
        cflags += f" {include_flags}"
    if extra_flags:
        cflags += f" {' '.join(extra_flags)}"

    makefile.append(f"CFLAGS = {cflags}\n\n")

    # SRC
    src_list = " \\\n\t\t".join(src_files) if len(src_files) > 1 else src_files[0]
    makefile.append(f"SRC = {src_list}\n\n")

    # Tests section if test_files provided
    if test_files:
        test_list = " \\\n\t\t".join(test_files) if len(test_files) > 1 else test_files[0]
        makefile.append(f"TESTS = {test_list}\n\n")

        # Filter main.c from SRC for tests (avoid multiple main functions)
        makefile.append("SRC_NO_MAIN = $(filter-out %main.c, $(SRC))\n\n")

    # NAME
    makefile.append(f"NAME = {binary_name}\n\n")

    # BUILD DIR
    makefile.append("BUILD_DIR = objects\n\n")

    # Test binary name
    if test_files:
        makefile.append(f"TEST_NAME = unit_tests\n\n")

    # OBJ - Transform src paths to build paths
    makefile.append("OBJ = $(SRC:%.c=$(BUILD_DIR)/%.o)\n\n")

    if test_files:
        makefile.append("TEST_OBJ = $(TESTS:%.c=$(BUILD_DIR)/%.o) $(SRC_NO_MAIN:%.c=$(BUILD_DIR)/%.o)\n\n")

    # Rules
    makefile.append("all: $(NAME)\n\n")

    # Binary rule
    makefile.append("$(NAME): $(OBJ)\n")
    makefile.append("\t$(CC) -o $(NAME) $(OBJ) -g $(CFLAGS)\n\n")

    # Test rule if tests exist
    if test_files:
        makefile.append("tests_run: $(TEST_OBJ)\n")
        makefile.append(f"\t$(CC) -o $(TEST_NAME) $(TEST_OBJ) -g $(CFLAGS) {CRITERION_FLAGS}\n")
        makefile.append("\t./$(TEST_NAME)\n")
        makefile.append("\tgcovr --exclude tests/\n")
        makefile.append("\tgcovr --exclude tests/ --branches\n\n")

    # Object compilation rule with directory creation
    makefile.append("$(BUILD_DIR)/%.o: %.c\n")
    makefile.append("\t@mkdir -p $(dir $@)\n")
    makefile.append("\t$(CC) $(CFLAGS) -c $< -o $@\n\n")

    # Clean rules
    makefile.append("clean:\n")
    makefile.append("\trm -rf $(BUILD_DIR)\n")
    makefile.append("\trm -Rf *.o\n")
    if test_files:
        makefile.append("\trm -rf *.gcda *.gcno\n")
    makefile.append("\n")

    makefile.append("fclean: clean\n")
    makefile.append("\trm -f $(NAME)\n")
    if test_files:
        makefile.append("\trm -f $(TEST_NAME)\n")
    makefile.append("\trm -Rf #*#\n")
    makefile.append("\trm -Rf #~\n\n")

    makefile.append("re: fclean all\n\n")

    # cs rule for coding style
    makefile.append("cs: clean fclean\n")
    makefile.append("\tcoding-style . .\n")
    makefile.append("\tcat *.log\n")
    makefile.append("\tsudo rm *.log\n\n")

    # ban rule for banned functions
    makefile.append("ban:\n")
    makefile.append("\tbanned_functions write\n\n")

    # Debug rule to show structure
    makefile.append("debug:\n")
    makefile.append("\t@echo \"CC: $(CC)\"\n")
    makefile.append("\t@echo \"CFLAGS: $(CFLAGS)\"\n")
    makefile.append("\t@echo \"SRC: $(SRC)\"\n")
    makefile.append("\t@echo \"OBJ: $(OBJ)\"\n")
    if test_files:
        makefile.append("\t@echo \"TESTS: $(TESTS)\"\n")
        makefile.append("\t@echo \"TEST_OBJ: $(TEST_OBJ)\"\n")
        makefile.append("\t@echo \"SRC_NO_MAIN: $(SRC_NO_MAIN)\"\n")
    makefile.append("\t@echo \"BUILD_DIR: $(BUILD_DIR)\"\n\n")

    # PHONY
    phony_targets = "fclean re all cs ban debug"
    if test_files:
        phony_targets += " tests_run"

    makefile.append(f".PHONY: {phony_targets}\n")

    return "".join(makefile)

def write_makefile(content: str, output_file: str = "Makefile") -> None:
    """Write the Makefile to disk."""
    with open(output_file, "w") as f:
        f.write(content)
    print_colored(f"[+] Makefile generated: {output_file}", Fore.GREEN)

# =============================================================================
# Argument parsing
# =============================================================================

def parse_arguments(args: list[str]) -> dict:
    """Parse command line arguments."""
    if len(args) < 2:
        return None

    config = {
        "project_name": None,
        "binary_name": None,
        "src_files": [],
        "test_files": [],
        "include_dirs": ["./include"],
        "extra_flags": []
    }

    i = 1
    while i < len(args):
        arg = args[i]

        if arg == "--name" or arg == "-n":
            if i + 1 < len(args):
                config["project_name"] = args[i + 1]
                i += 2
            else:
                print_colored("[!] Error: --name requires a value", Fore.RED)
                return None

        elif arg == "--binary" or arg == "-b":
            if i + 1 < len(args):
                config["binary_name"] = args[i + 1]
                i += 2
            else:
                print_colored("[!] Error: --binary requires a value", Fore.RED)
                return None

        elif arg == "--src" or arg == "-s":
            if i + 1 < len(args):
                src_arg = args[i + 1]
                if "," in src_arg:
                    config["src_files"] = [s.strip() for s in src_arg.split(",")]
                else:
                    config["src_files"].append(src_arg)
                i += 2
            else:
                print_colored("[!] Error: --src requires a value", Fore.RED)
                return None

        elif arg == "--tests" or arg == "-t":
            if i + 1 < len(args):
                test_arg = args[i + 1]
                if "," in test_arg:
                    config["test_files"] = [t.strip() for t in test_arg.split(",")]
                else:
                    config["test_files"].append(test_arg)
                i += 2
            else:
                print_colored("[!] Error: --tests requires a value", Fore.RED)
                return None

        elif arg == "--include" or arg == "-I":
            if i + 1 < len(args):
                include_arg = args[i + 1]
                if "," in include_arg:
                    config["include_dirs"] = [inc.strip() for inc in include_arg.split(",")]
                else:
                    config["include_dirs"] = [include_arg]
                i += 2
            else:
                print_colored("[!] Error: --include requires a value", Fore.RED)
                return None

        elif arg == "--flags" or arg == "-f":
            if i + 1 < len(args):
                config["extra_flags"] = args[i + 1].split()
                i += 2
            else:
                print_colored("[!] Error: --flags requires a value", Fore.RED)
                return None

        elif arg.startswith("-"):
            print_colored(f"[!] Error: Unknown option {arg}", Fore.RED)
            return None
        else:
            # If no options are specified, treat as positional args
            if not config["project_name"]:
                config["project_name"] = arg
            elif not config["binary_name"]:
                config["binary_name"] = arg
            elif arg.endswith(".c"):
                config["src_files"].append(arg)
            i += 1

    # Set defaults if not provided
    if not config["binary_name"] and config["project_name"]:
        config["binary_name"] = config["project_name"]

    return config

def print_usage() -> None:
    """Print usage instructions."""
    print_colored("Usage: python3 generate.py [options] <project_name> [binary_name] [sources...]", Fore.CYAN)
    print_colored("\nOptions:", Fore.YELLOW)
    print_colored("  -n, --name <name>        Project name", Fore.GREEN)
    print_colored("  -b, --binary <name>      Binary name (default: project name)", Fore.GREEN)
    print_colored("  -s, --src <files>        Source files (comma-separated)", Fore.GREEN)
    print_colored("  -t, --tests <files>      Test files for Criterion (comma-separated)", Fore.GREEN)
    print_colored("  -I, --include <dirs>     Include directories (default: ./include)", Fore.GREEN)
    print_colored("  -f, --flags <flags>      Additional compiler flags", Fore.GREEN)

    print_colored("\nExamples:", Fore.YELLOW)
    print_colored("  python3 generate.py my_project", Fore.MAGENTA)
    print_colored("  python3 generate.py --name my_project --binary my_prog --src src/main.c,src/utils.c", Fore.MAGENTA)
    print_colored("  python3 generate.py my_project --tests tests/test_main.c,tests/test_utils.c", Fore.MAGENTA)
    print_colored("  python3 generate.py my_project my_binary src/main.c src/file.c", Fore.MAGENTA)
    print_colored("  python3 generate.py my_project --src src/core/main.c,src/utils/helper.c --tests tests/test_core.c", Fore.MAGENTA)

    print_colored("\nFeatures:", Fore.YELLOW)
    print_colored("  - Uses clang-20 as default compiler", Fore.GREEN)
    print_colored("  - Creates build/ directory for .o files", Fore.GREEN)
    print_colored("  - Preserves source directory structure in build/", Fore.GREEN)
    print_colored("  - EPITECH coding-style compliant", Fore.GREEN)
    print_colored("  - Criterion unit tests support with coverage", Fore.GREEN)
    print_colored("  - Automatic main.c exclusion in tests", Fore.GREEN)
    sys.exit(1)

# =============================================================================
# Main
# =============================================================================

def main() -> None:
    if len(sys.argv) < 2:
        print_usage()

    config = parse_arguments(sys.argv)
    if not config:
        print_usage()

    # Validate required fields
    if not config["project_name"]:
        print_colored("[!] Error: Project name is required", Fore.RED)
        print_usage()

    if not config["binary_name"]:
        config["binary_name"] = config["project_name"]

    # Default source if none provided
    if not config["src_files"]:
        config["src_files"] = ["src/main.c"]

    # Default test files if tests requested but none specified
    if config["test_files"] and not any(config["test_files"]):
        config["test_files"] = ["tests/test_main.c"]

    # Validate source files
    for src in config["src_files"]:
        if not src.endswith(".c"):
            print_colored(f"[!] Warning: '{src}' is not a .c file", Fore.YELLOW)

    # Validate test files
    for test in config["test_files"]:
        if not test.endswith(".c"):
            print_colored(f"[!] Warning: '{test}' is not a .c test file", Fore.YELLOW)

    print_colored(f"[+] Generating Makefile for project: {config['project_name']}", Fore.GREEN)
    print_colored(f"[+] Compiler: {DEFAULT_CC}", Fore.BLUE)
    print_colored(f"[+] Binary name: {config['binary_name']}", Fore.BLUE)
    print_colored(f"[+] Source files: {', '.join(config['src_files'])}", Fore.BLUE)
    if config["test_files"]:
        print_colored(f"[+] Test files: {', '.join(config['test_files'])}", Fore.BLUE)
        print_colored(f"[+] Tests: Criterion with coverage enabled", Fore.BLUE)
    print_colored(f"[+] Include directories: {', '.join(config['include_dirs'])}", Fore.BLUE)
    print_colored(f"[+] Build directory: build/ (preserves source structure)", Fore.BLUE)

    # Generate Makefile
    makefile_content = generate_makefile(
        project_name=config["project_name"],
        binary_name=config["binary_name"],
        src_files=config["src_files"],
        include_dirs=config["include_dirs"],
        extra_flags=config["extra_flags"],
        test_files=config["test_files"] if config["test_files"] else None
    )

    # Write to disk
    write_makefile(makefile_content)

if __name__ == "__main__":
    main()
