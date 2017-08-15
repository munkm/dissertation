############################################################################
# File  : omnibus/postprocess/integrator.py
# Author: Madicken
# Date  : Tue Mar 17 16:41:55 2015
#
# <+ This file holds all of the tools necessary for doing the post-processing
# of a .txt output file, integrating the adjoint and forward angular fluxes,
# and returning
# the adjoint scalar flux in a .silo file readable by Advantg.  +>
############################################################################
from __future__ import (division, absolute_import, print_function, )
#--------------------------------------------------------------------------#
import numpy as np
import os
import re
import h5py
from nemesis import (const_View_Field_Dbl)
from nemesis import (Silo_Mesh_Writer as SiloMeshFile)

############################################################################

class h5reader(object):
    def __init__(self, filename, adjoint=False):
        # declare all variables that this object will contain; filename is a
        # required user input and adjoint mode is False by default. A
        # True will result in a matrix rotation to ensure the omega
        # coordinates in forard and adjoint are consistent.
        self.filename = str(filename)
        self.adjoint = adjoint
        self.mesh_g = []
        self.mesh_x = []
        self.mesh_y = []
        self.mesh_z = []
        self.quadrature_weights = []
        self.angular_flux = []
        self.angles = []
        self.group_bounds = []
        pass

    def __call__(self):
        pass

    def filereader(self):
        h5file = h5py.File(self.filename,'r')

        # Read in the data from h5file
        self.angles = h5file['/denovo/angles'][:]
        angular_flux = h5file['/denovo/angular_flux'][:]
        self.mesh_g = h5file['/denovo/mesh_g'][:]
        self.mesh_x = h5file['/denovo/mesh_x'][:]
        self.mesh_y = h5file['/denovo/mesh_y'][:]
        self.mesh_z = h5file['/denovo/mesh_z'][:]
        self.group_bounds_n = h5file['/denovo/group_bounds_n'][:]
        self.quadrature_weights = h5file['/denovo/quadrature_weights'][:]

        # Set variables for the expected size of the data
        z_len = len(self.mesh_z)-1
        y_len = len(self.mesh_y)-1
        x_len = len(self.mesh_x)-1
        g_len = len(self.mesh_g)
        m_len = len(self.quadrature_weights)

        # consider putting an assertion to check the variables rather than
        # trimming it.

        # Remove padding from the angular flux matrix
        self.angular_flux = angular_flux[:g_len,:z_len,:y_len,:x_len,:m_len]

		# Resort the angular fluxes to match -omega for the
        # adjoint calculation
        if self.adjoint == True:
            angle_locs = h5reader.location_generator(self,self.angles)
            new_flux = h5reader.sort_by_reverse_angles(self,self.angular_flux,
                    self.angles, angle_locs)
            self.angular_flux = new_flux


    def location_generator(self,data):
        location_dict = {}
        for d in range(len(data)):
            location_dict[str(data[d])] = d
        return location_dict

    def sort_by_reverse_angles(self,data,angles,angle_dict):
        reverse_data = np.zeros(np.shape(data))
        for angle in angles:
            reverse_data[:,:,:,:,angle_dict[str(angle)]] = \
                    data[:,:,:,:,angle_dict[str(-angle)]]
        return reverse_data


class Integrator(object):
    def __init__(self, forwarddata, adjointdata):
        self.forwarddata = forwarddata
        self.adjointdata = adjointdata
        self.integrated_numerator = []
        self.integrated_denominator = []
        self.integrated_fluxes = []
        self.mesh_g = adjointdata.mesh_g
        self.mesh_z = adjointdata.mesh_z
        self.mesh_y = adjointdata.mesh_y
        self.mesh_x = adjointdata.mesh_x
        self.group_bounds_n = adjointdata.group_bounds_n

        # anisotropy metric variables. Used in the case of anisotropy
        # quantification for omega-method analysis. See
        # quantify_anisotropy
        # function for descriptions of each metric.
        self.forward_anisotropy = np.array([])
        self.adjoint_anisotropy = np.array([])
        self.contributon_anisotropy = np.array([])
        self.metric_one = np.array([])
        self.metric_two = np.array([])
        self.metric_three = np.array([])
        self.metric_four = np.array([])
        self.metric_five = np.array([])
        self.metric_six = np.array([])
        self.metric_seven = np.array([])
        pass

    def calculate_weighted_fluxes(self):
		# First unpack the relevant data from object created in
        # filereader
        forward_flux = self.forwarddata.angular_flux
        adjoint_flux = self.adjointdata.angular_flux
        quadrature_weights = self.forwarddata.quadrature_weights

        # Create numerator and denominator arrays
        numerator = forward_flux[:,:,:,:]*\
                adjoint_flux[:,:,:,:]*quadrature_weights
        denominator = forward_flux[:,:,:,:]*quadrature_weights

        # Integrate the denominator and numerator separately,
        # then divide the
        # values to obtain a weighted adjoint scalar flux
        integrated_numerator = 4.*np.pi*np.sum(numerator, axis=4)
        integrated_denominator = np.sum(denominator, axis=4)
        try:
            weighted_scalar_flux = \
                    np.divide(integrated_numerator,\
                    integrated_denominator)
        except RuntimeWarning:
            pass
            print('You have a 0 division error, \
                    replacing first element with 0')
            weighted_scalar_flux[0,0,0,0] = 0.0


        self.integrated_fluxes = weighted_scalar_flux
        self.integrated_numerator = integrated_numerator
        self.integrated_denominator = integrated_denominator
        pass

    def quantify_anisotropy(self):
        # First unpack the relevant data from object
        # created in filereader
        forward_flux = self.forwarddata.angular_flux
        adjoint_flux = self.adjointdata.angular_flux
        omega_fluxes = self.integrated_fluxes
        contributon_fluxes = self.integrated_numerator
        fwd_quadrature_weights = self.forwarddata.quadrature_weights
        adj_quadrature_weights = self.adjointdata.quadrature_weights

        # Create forward info
        forward_mat = forward_flux[:,:,:,:]*fwd_quadrature_weights
        fwd_scalars = np.sum(forward_mat, axis=4)
        fwd_max_val = forward_mat.max(axis=4)
        fwd_min_val = forward_mat.min(axis=4)
        fwd_quad_sum = np.sum(fwd_quadrature_weights)

        # Create adjoint info
        adjoint_mat = adjoint_flux[:,:,:,:]*adj_quadrature_weights
        adj_scalars = np.sum(adjoint_mat, axis=4)
        adj_max_val = adjoint_mat.max(axis=4)
        adj_min_val = adjoint_mat.min(axis=4)
        adj_quad_sum = np.sum(adj_quadrature_weights)

        # Create contributon info
        contributon_mat = 4.*np.pi*adjoint_flux[:,:,:,:]*\
                forward_flux[:,:,:,:]*fwd_quadrature_weights
        cont_scalars = contributon_fluxes
        # cont_scalars = np.sum(contributon_mat, axis =4)
        cont_max_val = contributon_mat.max(axis=4)
        cont_min_val = contributon_mat.min(axis=4)

        # now quantify forward anisotropy
        avg_flux = fwd_scalars/fwd_quad_sum
        fwd_ratio = fwd_max_val/avg_flux

        # now quantify adjoint anisotropy
        avg_flux = adj_scalars/adj_quad_sum
        adj_ratio = adj_max_val/avg_flux
        adj_ratio_min = np.divide(adj_max_val,adj_min_val)

        # calculate the contributon ratio (advantg does this already)
        scalar_cont_product = adj_scalars*fwd_scalars

        # quantify contributon ratio (Metric No. 1)
        cont_ratio_one = scalar_cont_product/cont_scalars

        # calculate the ratio between omega and adjoint
        # fluxes (Metric No. 2)
        cont_ratio_two = omega_fluxes/adj_scalars

        # quantify max to avg contributon anisotropy
        # (Metric No. 3)
        avg_flux = cont_scalars/fwd_quad_sum
        cont_ratio_three = cont_max_val/avg_flux

        # quantify the ratio between omega and adjoint fluxes
        # (Metric No. 4)
        cont_ratio_four = cont_ratio_three/adj_ratio

        # quantify max to min contributon anisotropy
        # (Metric No. 5)
        cont_ratio_five = np.divide(cont_max_val,cont_min_val)

        # quantify the ratio between omega and adjoint fluxes
        # (Metric No. 6)
        cont_ratio_six = cont_ratio_five/adj_ratio_min

        # load the anisotropy ratios into object
        self.forward_anisotropy = fwd_ratio
        self.adjoint_anisotropy = adj_ratio
        self.metric_one = cont_ratio_one
        self.metric_two = cont_ratio_two
        self.metric_three = cont_ratio_three
        self.metric_four = cont_ratio_four
        self.metric_five = cont_ratio_five
        self.metric_six = cont_ratio_six

class SaveData(object):
    def __init__(self, data):
        self.data = data
        self.mesh_x = data.mesh_x
        self.mesh_y = data.mesh_y
        self.mesh_z = data.mesh_z
        self.mesh_g = data.mesh_g
        self.integrated_fluxes = data.integrated_fluxes
        self.forward_anisotropy = data.forward_anisotropy
        self.adjoint_anisotropy = data.adjoint_anisotropy
        self.contributon_flux = data.integrated_numerator
        self.contributon_anisotropy = data.contributon_anisotropy

        # convert the mesh vectors to cell-centerd values
        x = self.midpoint_finder(self.mesh_x)
        y = self.midpoint_finder(self.mesh_y)
        z = self.midpoint_finder(self.mesh_z)
        (self.Z,self.Y,self.X) = np.meshgrid(z,y,x, indexing='ij')
        pass

    def omega_by_group(self, filename):
        ''' This function saves the integrated angular fluxes
        into the silo file by
        group. '''
        # first delete the file if it already exists
        filename = str(filename)
        os.system('rm %s' %(filename))

        # write the data by group into a silo file with the
        # filename specified by
        # the user.
        with SiloMeshFile('%s' %filename) as f:
            f.write_mesh(*map(const_View_Field_Dbl.fromarray, (self.mesh_x,
                self.mesh_y, self.mesh_z)))
            f.write("x", self.X)
            f.write("y", self.Y)
            f.write("z", self.Z)
            for group in self.mesh_g:
                f.write("omega_flux_%03d" %(group), \
                        self.integrated_fluxes[group])

    def anisotropies_to_hdf5(self, filename):
        '''Saves quantified anisotropies to an hdf5 file for
        postprocessing.

        If all anisotropies are calculated, then the file
        will include metrics one through six (see
        Integrator.quantify_anisotropy for a description
        of each metric), the forward, adjoint, and contributon
        anisotropies, and the contributon scalar flux.'''
        filename = str(filename)
        os.system('rm %s' %(filename))

        metricnames = {"one": self.data.metric_one,
                "two": self.data.metric_two,
                "three": self.data.metric_three,
                "four": self.data.metric_four,
                "five": self.data.metric_five,
                "six": self.data.metric_six}
        for name, variable in metricnames.iteritems():
            assert variable.size, \
                    "metric "+str(name)+" contains no data"

        # write the data by group into a silo file with the
        # filename specified by
        # the user.
        with h5py.File('%s' %filename, 'w') as f:
            fname = f.create_group('forward_anisotropy')
            aname = f.create_group('adjoint_anisotropy')
            cname = f.create_group('contributon_flux')
            for name, variable in metricnames.iteritems():
                mname = f.create_group('metric_%s' %name)
                for group in self.mesh_g:
                    mname.create_dataset('group_%03d' %group,\
                            data=variable[group])
            for group in self.mesh_g:
                fname.create_dataset('group_%03d' %group,
                        data=self.forward_anisotropy[group])
                aname.create_dataset('group_%03d' %group,
                        data=self.adjoint_anisotropy[group])
                cname.create_dataset('group_%03d' %group,
                        data=self.contributon_flux[group])

    def anisotropies_to_silo(self, filename):
        ''' This function saves all of the anisotropies in
        the problem used for
        problem diagnostics by group to a silo file for
        visualization purposes.

        If all anisotropies are calculated, then the file
        will include metrics one through six (see
        Integrator.quantify_anisotropy for a description of
        each metric), the
        forward, adjoint, and contributon anisotropies,
        and the contributon
        scalar flux.'''
        filename = str(filename)
        os.system('rm %s' %(filename))

        metricnames = {"one": self.data.metric_one,
                "two": self.data.metric_two,
                "three": self.data.metric_three,
                "four": self.data.metric_four,
                "five": self.data.metric_five,
                "six": self.data.metric_six}
        for name, variable in metricnames.iteritems():
            assert variable.size, \
                    "metric "+str(name)+" contains no data"

        # write the data by group into a silo file with the
        # filename specified by the user.
        with SiloMeshFile('%s' %filename) as f:
            f.write_mesh(*map(const_View_Field_Dbl.fromarray, \
                    (self.mesh_x,
                self.mesh_y, self.mesh_z)))
            f.write("x", self.X)
            f.write("y", self.Y)
            f.write("z", self.Z)
            for group in self.mesh_g:
                for name, variable in metricnames.iteritems():
                    f.write("metric_%s_group_%03d" %(name, group),
                            variable[group])

        # if the forward anisotropy has been quantified, also write
                # them to the file
                if self.forward_anisotropy.size:
                    f.write("F_anis_group_%03d" %(group),
                            self.forward_anisotropy[group])

               # if the adjoint anisotropy has been quantified,
               # write it to file too
                if self.adjoint_anisotropy.size:
                    f.write("A_anis_group_%03d" %(group),
                            self.adjoint_anisotropy[group])

                # if contributon anisotropy quantified,
                # write it to file too.
                if self.contributon_anisotropy.size:
                    f.write("C_anis_group%03d" %(group),
                            self.contributon_anisotropy[group])

                # if contributon flux quantified, write
                # it to file.
                if self.contributon_flux.size:
                    f.write("contributon_flux_group%03d" %(group),
                            self.contributon_flux[group])

    def midpoint_finder(self, mesh_vector):
        new_mesh = np.zeros(len(mesh_vector)-1)
        new_mesh = (mesh_vector[0:-1]+mesh_vector[1:])/2
        return new_mesh

#-------------------------------------------------------------------------#
if __name__ == '__main__':
    main()

############################################################################
# end of Denovo/tools/integrator.py
############################################################################
