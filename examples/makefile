# whowasi: a tool to record source version information into binaries.
#
# Copyright (c) 2026 Institut des Géosciences de l'Environnement, Grenoble.
#
# License: BSD 3-clause "new" or "revised" license (BSD-3-Clause).
#
# This makefile builds example programmes that use whowasi.

C: c
c: example.c
	python -m whowasi --language c
	gcc -o example_c whowasi.c example.c


F90: f90
f90: example.f90
	python -m whowasi --language f90
	gfortran -ffree-line-length-none -o example_f90 whowasi.f90 $^
