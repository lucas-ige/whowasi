[![Ruff](https://github.com/lucas-ige/whowasi/actions/workflows/ruff.yaml/badge.svg)](https://github.com/lucas-ige/whowasi/actions/workflows/ruff.yaml) [![Unit tests](https://github.com/lucas-ige/whowasi/actions/workflows/unit-tests-python.yaml/badge.svg)](https://github.com/lucas-ige/whowasi/actions/workflows/unit-tests-python.yaml)

# What is whowasi?

It is a tool to record source version information into binaries.

# What was the motivation to create this tool?

Geoscientists (and, as I am sure, many others) often make simulations using large C, C++, and/or FORTRAN models. To do so, they may clone the model source code, modify some things, commit some changes, modify the code further, and so on. At some point, geoscientists run production simulations to write papers. At a later date (eg. when revising the paper following peer review), they want to know what version of the code was used to run the production simulations. It may happen that they cannot quite remember whether "this last-minute change" was actually included or not in the binary used for production simulations. `whowasi` is designed to address this issue.

# How to install it?

You can install it using `pip`:

```sh
pip install whowasi@git+https://github.com/lucas-ige/whowasi.git
```

> [!NOTE]
> There is no tagged version available at this time. It is still largely a work in progress.

# How does it work (example with a C program)?

> [!NOTE]
> At the moment, `whowasi` only works for the `git` version control system and for the C and FORTRAN programming languages.

Consider the following minimalist C program:

```C
#include <stdio.h>

int main() {
    printf("Hello world\n");
}
```

and the associated makefile:

```
myprogram: myprogram.c
	gcc -o $@ $^
```

To use `whowasi`, you need to call a mysterious `whowasi` function from your program:

```C
#include <stdio.h>
#include "whowasi.h"

int main() {
    whowasi(stdout);
    printf("Hello world!\n");
}
```

The code of this function is created on the fly at compile time by modifying the makefile like so:

```
myprogram: myprogram.c
	python -m whowasi --language c
	gcc -o $@ whowasi.c $^
	rm whowasi.c whowasi.h
```

What does this function do? It will write (into a file, standard output, or standard error) the exact state of the `git` repository at the moment that `myprogram` was compiled.

After building and running this example program, standard output will look something like:

```
##############################################
#                                            #
# ?? whowasi ??                              #
#                                            #
# Commit                                     #
# ------                                     #
#                                            #
# commit commit_hash                         #
# Author: FirstName LastName <email address> #
# Date:   commit_date                        #
#                                            #
#     A nice commit message                  #
#                                            #
##############################################
Hello world!
```

The `whowasi` function printed information about the commit that was checked out when `myprogram` was compiled.

Now let use translate the program into French:

```C
#include <stdio.h>
#include "whowasi.h"

int main() {
    whowasi(stdout);
    printf("Bonjour tout le monde!\n");
}
```

We do not commit the changes, but we build and run the program again. Standard output will now look something like:

```
#################################################
#                                               #
# ?? whowasi ??                                 #
#                                               #
# Commit                                        #
# ------                                        #
#                                               #
# commit commit_hash                            #
# Author: FirstName LastName <email address>    #
# Date:   commit_date                           #
#                                               #
#     A nice commit message                     #
#                                               #
# New file: myprogram, which seems to be binary #
# --------------------------------------------- #
#                                               #
# Modified file: myprogram.c                    #
# --------------------------                    #
#                                               #
# diff --git a/myprogram.c b/myprogram.c        #
# --- a/myprogram.c                             #
# +++ b/myprogram.c                             #
# @@ -3,5 +3,5 @@                               #
#                                               #
#  int main() {                                 #
#      whowasi(stdout);                         #
# -    printf("Hello world!\n");                #
# +    printf("Bonjour tout le monde!\n");      #
#  }                                            #
#                                               #
#################################################
Bonjour tout le monde!
```

It is now hard-coded into the executable that the corresponding source file had been modified but not commited when the program was compiled. We can also note that `whowasi` detected the presence of a binary file called `mypogram`. This corresponds to the executable created during the first step of this example.

# Ignoring files

Compiling code can generate intermediate files (eg. object files `*.o`) that you generally do not need to track. In this situation, you can use the option `--ignore` (or `-i` for short) to specify one or more ignore rule(s). For example:

```
python -m whowasi --language f90 --ignore "**/*.o" "**/*.mod"
```

The syntax of the rules follows the [gitignore syntax](https://git-scm.com/docs/gitignore). However, only a subset of this syntax is currently implemented into `whowasi`:

 - "**/myscript.py" will ignore any file called `myscript.py` anywhere in the repository.
 - "**/*.py" will ignore any file with the `.py` extension anywhere in the repository.
 - "foo/bar/**" will ignore anything in directory `foo/bar`, with infinite depth.
 - "foo/**/bar/myscript.py" will ignore any file called `myscript.py` in all directories named `bar` that are subdirectories of `foo` at any depth.
 - a non-escaped "*" means any series of characters except a slash.
 - a non-escaped "?" means any one character except a slash.
 - You can escape characters with `\`.
 - You can use ranges such as "[A-z0-9]" to mean any one character in the given range. Currently supported range boundaries are the (26*2) ASCII letters (lower case and upper case) and the 10 ASCII digits.

Currently **NOT** supported (`whowasi` will not crash but it may not produce the desired result):

 - Any rule that targets a directory and not a file.
 - The `!` to negate a rule (ie. to force-include files).

Besides, and unlike gitignore rules, a rule that specifies a file name without any context (eg ".DS_Store") will ignore this file only when located at the root of the repository (use "**/.DS_Store" to ignore these pesky files anywhere in the repository).

In any case, `whowasi` ignores files and directories listed in `.gitignore` files. That's another method to ignore files.

Note that, by default, `whowasi` automatically ignores the files that it creates and the files that will likely be created by their integration into the compilation process. Use option `--no-auto-ignore` to disable this behavior. Which files are automatically ignored depends on the language, as listed in the table below (the default name "whowasi" can be adjusted with option `--name`):

| Language | Automatically ignored files                          |
| -------- | ---------------------------------------------------- |
| C        | `"**/whowasi.c"`, `"**/whowasi.h"`, `"**/whowasi.o"` |
| F90      | `"**/whowasi.f90"`, `"**/module_whowasi.mod"`        |

# More information

Use `python -m whowasi --help` for documentation about all available options.
