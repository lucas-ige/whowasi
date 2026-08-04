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

> [!IMPORTANT]
> `whowasi` currently ignores files and directories listed in `.gitignore` files.

> [!CAUTION]
> Make sure to delete `whowasi` temporary files at compile time to avoid spurious exponential `diff`s (use an appropriate rule in the makefile, as in the example above).

# More information

Use `python -m whowasi --help` for documentation about all available options.
