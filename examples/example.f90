! whowasi: a tool to record source version information into binaries.
!
! Copyright (c) 2026 Institut des Géosciences de l'Environnement, Grenoble.
!
! License: BSD 3-clause "new" or "revised" license (BSD-3-Clause).
!
! This file is an example FORTRAN 90+ programme that uses whowasi.

program example

  use, intrinsic :: iso_fortran_env, only : stdout=>output_unit
  use module_whowasi, only: whowasi
  implicit none

  call whowasi(stdout)
  print'(A)', "Hello world!"

end program example
