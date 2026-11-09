import numpy as np



# Computer science constants

infinity = np.inf
infty = infinity
NaN = np.nan
not_a_number = NaN


## Exactly defined constants

π = np.pi
pi = π

speed_of_light = 299792458  # Speed of light
c = speed_of_light

elementary_charge = 1.602176634e-19  # Elementary charge
e = elementary_charge

boltzmann_constant = 1.380649e-23  # Blotzmann constant
kB = boltzmann_constant

planck_constant = 6.62607015e-34  # Planck constant
h = planck_constant

reduced_planck_constant = planck_constant / (2*π)  # Reduced Planck constant
hbar = reduced_planck_constant



# More constants

fine_structure_constant = 1/137.036  # Fine structure constant
fine_structure = fine_structure_constant
α = fine_structure

vacuum_dielectric_permittivity = elementary_charge**2 / (2 * fine_structure_constant * planck_constant * speed_of_light)
Ɛ0 = vacuum_dielectric_permittivity

vacuum_magnetic_permittivity = 1/(c*c*Ɛ0)
µ0 = vacuum_magnetic_permittivity  # Magnetic permeability of vacuum



# hBN-related

hBN_relative_dielectric_permittivity = 3.4
Ɛr_hBN = hBN_relative_dielectric_permittivity

hBN_HPhP_I_frequency = 1e-3 * (e/hbar) * 101 # 101 meV
ΩI = hBN_HPhP_I_frequency



# Graphene-related

graphene_fermi_velocity = 1e6  # Fermi velocity in graphene
vF = graphene_fermi_velocity

grapehene_encapsulated_effective_fine_structure_constant = fine_structure_constant * speed_of_light / graphene_fermi_velocity / Ɛr_hBN
αg = grapehene_encapsulated_effective_fine_structure_constant