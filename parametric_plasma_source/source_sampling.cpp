#include <iostream>
#include "openmc/random_lcg.h"
#include "openmc/source.h"
#include "openmc/particle.h"
#include "plasma_source.hpp"
/* EU DEMO SOURCE
const double ion_density_pedistal = 1.09e20; // ions per m^3
const double ion_density_seperatrix = 3e19;
const double ion_density_origin = 1.09e20;
const double ion_temperature_pedistal = 6.09;
const double ion_temperature_seperatrix = 0.1;
const double ion_temperature_origin = 45.9;
const double pedistal_radius = 0.8; // pedistal major rad
const double ion_density_peaking_factor = 1;
const double ion_temperature_peaking_factor = 8.06; // check alpha or beta value from paper
const double minor_radius = 2.93; // metres
const double major_radius = 9.07; // metres
const double elongation = 1.590;
const double triangularity = 0.333;
const double shafranov_shift = 0.0; //metres
const std::string name = "fred";
const int number_of_bins  = 100;
const int plasma_type = 1; //0 = L mode anything else H/A mode
*/

// Spherical tokamak SOURCE 
const double ion_density_pedistal = 1.09e20; // ions per m^3
const double ion_density_seperatrix = 3e19;
const double ion_density_origin = 1.09e20;
const double ion_temperature_pedistal = 6.09;
const double ion_temperature_seperatrix = 0.1;
const double ion_temperature_origin = 25.0;
const double pedistal_radius = 0.8; // pedistal major rad
const double ion_density_peaking_factor = 1;
const double ion_temperature_peaking_factor = 2.06; // check alpha or beta value from paper
const double minor_radius = 1.118; // metres
const double major_radius = 1.9; // metres
const double elongation = 2.9;
const double triangularity = 0.55;
const double shafranov_shift = 0.0; //metres
const std::string name = "fred";
const int number_of_bins  = 100;
const int plasma_type = 1; //0 = L mode anything else H/A mode



// const double elongation = 1.558763414882943;
// const double triangularity = 0.2677975641391616;
// const double minor_radius = 2.9225806451612906; // metres
// const double major_radius = 9.06; // metres
// const double ion_density_peaking_factor = 1;
// const int plasma_type = 1; //0 = L mode anything else H/A mode
// const double shafranov_shift = 0.37043347873696075; //metres
// const double ion_density_pedistal = 1.09e20; // ions per m^3
// const double ion_density_seperatrix = 3.0e19;
// const double ion_density_origin = 1.09e20;
// const double ion_temperature_pedistal = 6.09;
// const double ion_temperature_seperatrix = 0.1;
// const double ion_temperature_origin = 45.9;
// const double pedistal_radius = 0.8; // pedistal major rad
// const double ion_temperature_peaking_factor = 8.06; // check alpha or beta value from paper
// const std::string name = "matti";
// const int number_of_bins  = 100;

plasma_source::PlasmaSource source = plasma_source::PlasmaSource(ion_density_pedistal,
       ion_density_seperatrix,
       ion_density_origin,
       ion_temperature_pedistal,
       ion_temperature_seperatrix,
       ion_temperature_origin,
       pedistal_radius,
       ion_density_peaking_factor,
       ion_temperature_peaking_factor,
       minor_radius,
       major_radius,
       elongation,
       triangularity,
       shafranov_shift,
       name,
       plasma_type,
       number_of_bins,
       0.0,
       360.0);
  
// you must have external C linkage here otherwise 
// dlopen will not find the file
extern "C" openmc::Particle::Bank sample_source() {
    openmc::Particle::Bank particle;
    // wgt
    particle.particle = openmc::Particle::Type::neutron;
    particle.wgt = 1.0;
    // position 

    std::array<double,8> randoms = {openmc::prn(),
                            openmc::prn(),
                            openmc::prn(),
                            openmc::prn(),
                            openmc::prn(),
                            openmc::prn(),
                            openmc::prn(),
                            openmc::prn()};

    double u,v,w,E;
    source.SampleSource(randoms,particle.r.x,particle.r.y,particle.r.z,
                        u,v,w,E); 

    particle.r.x *= 100.;
    particle.r.y *= 100.;
    particle.r.z *= 100.;    
   
    // particle.E = 14.08e6;
    particle.E = E*1e6; // convert from MeV -> eV

    particle.u = {u,
                  v,
                  w};

    
    particle.delayed_group = 0;
    return particle;    
}


