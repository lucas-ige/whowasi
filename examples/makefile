# whowasi: a tool to record source version information into binaries.
#
# Copyright (c) 2026 Institut des Géosciences de l'Environnement, Grenoble.
#
# License: BSD 3-clause "new" or "revised" license (BSD-3-Clause).
#
# This makefile builds example programmes that use whowasi.

CC=gcc

C: c

c: example.c
	python -m whowasi --language c
	$(CC) -o example whowasi.c example.c
	rm whowasi.c whowasi.h
