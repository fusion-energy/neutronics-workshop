
"""
.. moduleauthor:: Chris Bowman <chris.bowman@york.ac.uk>
"""

from numpy import exp, log, dot, sqrt, std, argmin, diag, nonzero, ndarray
from numpy import zeros, ones, array, where, pi
from scipy.special import erf
from numpy.linalg import inv, slogdet, solve
from scipy.optimize import minimize, differential_evolution
from multiprocessing import Pool, cpu_count
from itertools import product



class GpRegressor(object):
    """
    A class for performing Gaussian-process regression in one or more dimensions.

    :param x: \
        The spatial coordinates of the y-data values. For the 1-dimensional case, \
        this should be a list or array of floats. For greater than 1 dimension, \
        a list of coordinate arrays or tuples should be given.

    :param y: The y-data values as a list or array of floats.

    :param y_err: \
        The error on the y-data values supplied as a list or array of floats. \
        This technique explicitly assumes that errors are Gaussian, so the supplied \
        error values represent normal distribution standard deviations. If this \
        argument is not specified the errors are taken to be small but non-zero.

    :param scale_lengths: \
        The default behaviour of GpRegressor is to determine an appropriate \
        scale-length for each dimension separately, such that for a problem \
        with N dimensions, there are N+1 total hyperparameters. Alternatively, \
        this can be reduced to only 2 hyperparameters regardless of the number \
        of dimensions by specifying the scale_lengths argument. In this case, \
        the hyperparameters become and amplitude and a scalar multiplier for \
        the provided scale-lengths. The specified lengths must be given as an \
        iterable of length equal to the number of dimensions.

    :param hyperpars: \
        The amplitude and scale-length parameters for the normal prior distribution. \
        If a single global scale length should be used, the hyperparameters should be \
        specified as a two element list, i.e. [amplitude, length]. Alternatively, a \
        separate length-scale for each dimension can be specified by passing an \
        amplitude followed by iterable of lengths, i.e. [amplitude, (L1, L2, ...)].
    """
    def __init__(self, x, y, y_err = None, scale_lengths = None, hyperpars = None):

        # data to fit
        self.x = x
        self.y = array(y)

        # data errors covariance matrix
        self.sig = zeros([len(self.y), len(self.y)])
        if y_err is not None:
            if len(y) == len(y_err):
                for i in range(len(self.y)):
                    self.sig[i,i] = y_err[i]**2
            else:
                raise ValueError('y_err must be the same length as y')
        else:
            err = ((self.y.max()-self.y.min()) * 1e-5)**2
            for i in range(len(self.y)):
                self.sig[i,i] = err

        # number of spatial dimensions
        if hasattr(self.x[0], '__len__'):  # multi-dimensional case
            self.N = len(self.x[0])
        else:  # 1D case
            self.N = 1
            self.x = [ (k,) for k in self.x ]


        # checks or builds scale_lengths
        if scale_lengths is None:
            self.scale_lengths = ones(self.N)
        elif len(scale_lengths)==self.N:
            self.scale_lengths = array(scale_lengths)
        else:
            raise ValueError('exactly one scale length per dimension is required')

        # pre-calculates hyperparameter-independent part of the
        # data covariance matrix as an optimisation
        self.distances = []
        for i in range(self.N):
            D = [[ (a[i]-b[i])**2 for b in self.x] for a in self.x]
            self.distances.append( -0.5*array(D) )

        # selects optimal values for covariance function parameters
        if hyperpars is not None:
            self.a, self.s = hyperpars
        elif scale_lengths is None:
            self.optimize_hyperparameters_free_lengths()
        else:
            self.optimize_hyperparameters_fixed_lengths()

        # build the covariance matrix
        self.K_xx = self.build_covariance(self.a, self.s*self.scale_lengths)
        self.H = solve(self.K_xx, self.y)

    def __call__(self, q, threads = None):
        """
        Calculate the mean and standard deviation of the regression estimate at a series
        of specified spatial points.

        :param q: \
            A list containing the spatial locations where the mean and standard \
            deviation of the estimate is to be calculated. In the 1D case this \
            would be a list of floats, or a list of coordinate tuples in the \
            multi-dimensional case.

        :param threads: \
            An integer indicating the number of threads to use in evaluating \
            the regression estimate at the provided coordinates. If a value \
            of -1 is given, the number of available threads of the current \
            machine will be used.

        :return: Two 1D arrays, the first containing the means and the second containing \
                 the sigma values.
        """
        if threads is -1: threads = cpu_count()

        if threads is None:
            results = [self.evaluate(v) for v in q]
        elif type(threads) is int and threads > 0:
            workers = Pool(threads)
            results = workers.map(self.evaluate, q)
        else:
            raise ValueError('threads keyword must be either -1 or an integer greater than zero')

        mu  = [ t[0] for t in results ]
        sig = [ t[1] for t in results ]
        return array(mu), array(sig)

    def evaluate(self, v):
        lengths = self.s * self.scale_lengths
        if hasattr(v, '__iter__'):
            K_qx = array([self.covariance(v, j, lengths) for j in self.x]).reshape([1, len(self.x)])
        else:
            K_qx = array([self.covariance((v,), j, lengths) for j in self.x]).reshape([1, len(self.x)])

        mu = dot(K_qx, self.H)[0]
        var = (self.a**2 - diag(dot(K_qx, solve(self.K_xx, K_qx.T))))[0]
        return mu, sqrt(var)

    def build_posterior(self, q):
        """
        Generates the full mean vector and covariance matrix for the GP fit at
        a set of specified points 'q'.

        :param q: A list containing the spatial locations which will be used to construct \
                  the Gaussian process. In the 1D case this would be a list of floats, or \
                  a list of coordinate tuples in the multi-dimensional case.

        :return: The mean vector as a 1D array, followed by covariance matrix as a 2D array.
        """
        v = q
        if hasattr(q, '__iter__'):
            if hasattr(q[0], '__iter__'):
                if len(q[0]) is not self.N:
                    raise ValueError('Specified coordinates have incorrect dimensionality')
            elif self.N is 1:
                v = [(k,) for k in q]
            else:
                raise ValueError('The number of specified points must be greater than 1')
        else:
            raise ValueError('The number of specified points must be greater than 1')


        lengths = self.s * self.scale_lengths
        K_qx = self.matrix(v, self.x, lengths)
        K_qq = self.matrix(v, v, lengths)
        self.mu = dot(K_qx, self.H)
        self.sigma = K_qq - dot( K_qx, solve( self.K_xx, K_qx.T ) )
        return self.mu, self.sigma

    def dist(self, a, b, l):
        """
        Calculates the effective squared-distance between any two
        points in the space by normalising the change in each
        dimension to the corresponding value in self.scale_lengths
        """
        # works for non-arrays
        return sum( ((i-j)/k)**2 for i,j,k in zip(a, b, l) )

    def covariance(self, x1, x2, lengths):
        """
        Evaluates the covariance function K(x1, x2) which is
        used to construct the covariance matrix for the data.

        In this case K(x1, x2) is taken to be Gaussian, and may
        be tuned to the data provided using the hyperparameters
        self.s and self.a
        """
        z = self.dist(x1, x2, lengths)
        return (self.a**2) * exp(-0.5*z)

    def matrix(self, v1, v2, lengths):
        """
        Given two vectors of points on the x axis v1 & v2,
        this function returns the covariance matrix for those
        vectors as a numpy array of size [len(v1), len(v2)]
        """
        M = [[self.covariance(i, j, lengths) for j in v2] for i in v1]
        return array(M)

    def build_covariance(self, a, lengths):
        """
        Optimized version of self.matrix() specifically for the data
        covariance matrix where the vectors v1 & v2 are both self.x.
        """
        D = sum( d/l**2 for d,l in zip(self.distances, lengths) )
        return (a**2) * exp(D) + self.sig

    def LML(self, theta):
        """
        returns the negative log marginal likelihood for the
        supplied hyperparameter values.
        Used by the scipy.optimize.minimize function to maximise
        the log marginal likelihood.
        """
        t = [exp(h) for h in theta]
        a = t[0]
        s = array(t[1:])
        K_xx = self.build_covariance(a, s*self.scale_lengths)

        try: # protection against singular matrix error crash
            sgn, ldet = slogdet(K_xx)
            if sgn is -1: print(' # WARNING # - negative determinant')
            L = dot( self.y.T, solve( K_xx, self.y ) ) + ldet
        except:
            L = 1e50
        return L

    def optimize_hyperparameters_fixed_lengths(self):
        a_std = log(std(self.y)) # rough guess for amplitude value

        D = -2*sum(d / l**2 for d, l in zip(self.distances, self.scale_lengths))
        # generate optimisation bounds
        D_lwr = log( sqrt( D[nonzero(D)].min() ) ) - 1
        D_upr = log( sqrt( D.max() ) ) + 1
        bnds = [(a_std-4, a_std+4), (D_lwr, D_upr)]

        opt_result = differential_evolution(self.LML, bnds) # optimise the hyperparameters

        # parameters are selected in log-space, so taking exp() here yields desired values.
        self.a, self.s = [exp(h) for h in opt_result.x]

    def optimize_hyperparameters_free_lengths(self):
        a_std = log(std(self.y)) # rough guess for amplitude value
        bnds = [(a_std - 4, a_std + 4)]

        for d in self.distances:
            L = sqrt(-2*d)
            lwr = log(L[nonzero(L)].min()) - 1
            upr = log(L.max()) + 1
            bnds.append( (lwr, upr) )

        opt_result = differential_evolution(self.LML, bnds) # optimise the hyperparameters

        # parameters are selected in log-space, so taking exp() here yields desired values.
        t = [exp(h) for h in opt_result.x]
        self.a = t[0]
        self.s = array(t[1:])






class GpInverter(object):
    """
    Solves linear inverse problems of the form y = Gb, using a Gaussian-process
    prior which imposes spatial regularity on the solution.

    The solution vector 'b' must describe the value of a quantity everywhere
    on a grid, as the GP prior imposes covariance between these grid-points
    based on the 'distance' between them. The grid need not be a spatial one,
    only one over which regularity is desired, e.g. time, wavelength ect.

    > arguments

        x 	- array of position values/vectors for the model parameters

        y 	- array of data values

        cov	- covariance matrix for the data

        G	- the linearisation matrix


    > [more documentation here!]
    """
    def __init__(self, x, y, cov, G, scale_length = None, mean = None, amplitude = None, selector = 'evidence'):
        self.x = x  # spatial location of the parameters, *not* the y data
        self.y = y  # data values
        self.S_y = cov  # data covariance matrix
        self.G = G  # geometry matrix

        self.selector = selector
        self.hyperpar_settings = (amplitude, scale_length, mean)

        # check inputs for compatability
        self.parse_inputs()

        self.I = ones([G.shape[1],1])
        self.f = dot( self.G, self.I )
        self.iS_y = inv(self.S_y)

        # generate square-distance matrix from self.x
        if hasattr(self.x[0], '__iter__'): # multi-dimensional case
            self.D = [ [ self.dist(i,j) for j in self.x] for i in self.x ]
        else: # 1D case
            self.D = [ [ (i-j)**2 for j in self.x] for i in self.x ]
        self.D = -0.5*array(self.D)

        self.A, self.L, self.mu_val = self.optimize_hyperparameters()

        # now we have determined the hyperparameters, generate the prior
        # mean and covariance matrices
        self.mu_p = self.mu_val * ones([len(x), 1])
        self.S_p = (self.A**2)*exp(self.D/(self.L**2))

        # we may now also generate the posterior mean and covariance.
        # To improve the numerical stability of calculating the posterior
        # covariance, we use the woodbury matrix identity:
        K = dot(self.G, self.S_p)

        V = self.S_y + dot(K, self.G.T)
        iVK = solve(V,K)
        self.S_b = self.S_p - dot( K.T, iVK )

        # posterior mean involves no further inversions so is stable
        self.mu_b = self.mu_p + dot( self.S_b, dot( self.G.T, dot( self.iS_y, (self.y - self.mu_val*self.f) ) ) )

    def parse_inputs(self):
        # first check input types
        if type(self.y) is not ndarray: self.y = array(self.y)
        if type(self.S_y) is not ndarray: self.S_y = array(self.S_y)
        if type(self.G) is not ndarray: self.G = array(self.G)

        # now check shapes / sizes are compatible
        if len(self.y.shape) is not 2: self.y = self.y.reshape([self.y.size,1])
        if self.S_y.shape[0] != self.S_y.shape[0]:
            raise ValueError('Data covariance matrix must be square')
        if self.S_y.shape[0] != self.y.shape[0]:
            raise ValueError('Dimensions of the data covariance matrix must equal the number of data points')
        if (self.G.shape[0] != self.y.shape[0]) or  (self.G.shape[1] != len(self.x)):
            raise ValueError('The operator matrix must have dimensions [# data points, # spatial points]')

    def dist(self, a, b):
        return sum( (i-j)**2 for i, j in zip(a, b) )

    def log_ev(self, h):
        # extract hyperparameters
        A, L, mu_p = [exp(v) for v in h]
        # first make the prior covariance
        S_p = (A**2)*exp(self.D/(L**2))
        # now the marginal likelihood covariance
        S_m = dot( self.G, dot(S_p, self.G.T) ) + self.S_y
        # and the marginal likelihood mean
        mu_m = mu_p * self.f
        # now calculate negative log marginal likelihood
        u = self.y - mu_m
        iSu = solve(S_m, u)
        L = dot( u.T, iSu ) + slogdet(S_m)[1]
        return L[0][0]

    def nn_maximum_likelihood(self, h):
        A, L, mu_p = [exp(v) for v in h]

        S_p = (A**2)*exp(self.D/(L**2))

        K = dot(self.G, S_p)
        V = self.S_y + dot(K, self.G.T)
        iVK = solve(V,K)
        S_b = S_p - dot( K.T, iVK )

        # posterior mean involves no further inversions so is stable
        mu_b = mu_p + dot( S_b, dot( self.G.T, dot( self.iS_y, (self.y - mu_p*self.f) ) ) )
        mu_b[where(mu_b < 0)] = 0.
        # find the residual
        res = self.y - self.G.dot(mu_b)
        LL = dot(res.T, self.iS_y.dot(res))
        return LL[0,0]

    def optimize_hyperparameters(self):
        # choose the selection criterion for the hyperparameters
        if self.selector is 'evidence':
            criterion = self.log_ev
        elif self.selector is 'NNML':
            criterion = self.nn_maximum_likelihood
        else:
            raise ValueError('The selector keyword must be given as either `evidence` or `NNML`')

        # Choose the correct inputs for the criterion based on which
        # hyperparameters have been given fixed values
        code = tuple([ x is None for x in self.hyperpar_settings ])
        log_vals = []
        for x in self.hyperpar_settings:
            if x is None:
                log_vals.append(None)
            else:
                log_vals.append(log(x))

        selection_functions = {
            (1,1,1) : lambda x : criterion(x),
            (1,1,0) : lambda x : criterion([x[0],x[1],log_vals[2]]),
            (1,0,1) : lambda x : criterion([x[0],log_vals[1],x[1]]),
            (0,1,1) : lambda x : criterion([log_vals[0],x[0],x[1]]),
            (1,0,0) : lambda x : criterion([x[0],log_vals[1],log_vals[2]]),
            (0,1,0) : lambda x : criterion([log_vals[0],x[0],log_vals[2]]),
            (0,0,1) : lambda x : criterion([log_vals[0],log_vals[1],x[0]]),
            (0,0,0) : None
        }

        minfunc = selection_functions[code]

        # if all the hyperparameters have been fixed, just return the fixed values
        if minfunc is None: return self.hyperpar_settings


        # make some guesses for the hyperparameters
        A_guess  = [-6,-4,-2, 0]
        L_guess  = [-6,-5,-4,-3,-2] # NOTE - should be data-determined in future
        mu_guess = [-8,-6,-4,-2, 0]

        # build a list of initial guesses again depending on what parameters are fixed
        guess_components = []
        if code[0]: guess_components.append(A_guess)
        if code[1]: guess_components.append(L_guess)
        if code[2]: guess_components.append(mu_guess)
        guesses = [ g for g in product(*guess_components) ]

        # sort the guesses by best score
        guesses = sorted(guesses, key = minfunc)

        LML_list   = []
        theta_list = []

        for g in guesses[:3]: # minimize the LML for the best guesses
            min_obj = minimize( minfunc, g, method = 'L-BFGS-B' )
            LML_list.append( min_obj['fun'] )
            theta_list.append( min_obj['x'] )

        # pick the solution the best score
        opt_params = theta_list[ argmin(array(LML_list)) ]
        paras = []
        k = 0
        for i in range(3):
            if code[i]:
                paras.append(opt_params[k])
                k += 1
            else:
                paras.append(log_vals[i])

        return [exp(v) for v in paras]






class GpOptimiser(object):
    """
    A class for performing Gaussian-process optimisation in one or more dimensions.

    GpOptimiser extends the functionality of GpRegressor to perform Gaussian-process \
    optimisation, often also referred to as 'Bayesian optimisation'. This technique \
    is suited to problems for which a single evaluation of the function being explored \
    is expensive, such that the total number of function evaluations must be made as \
    small as possible.

    In order to construct the gaussian-process regression estimate which is used to \
    search for the global maximum, on initialisation GpOptimiser must be provided with \
    at least two evaluations of the function which is to be maximised.

    :param x: \
        The spatial coordinates of the y-data values. For the 1-dimensional case, \
        this should be a list or array of floats. For greater than 1 dimension, \
        a list of coordinate arrays or tuples should be given.

    :param y: The y-data values as a list or array of floats.

    :param y_err: \
        The error on the y-data values supplied as a list or array of floats. \
        This technique explicitly assumes that errors are Gaussian, so the supplied \
        error values represent normal distribution standard deviations. If this \
        argument is not specified the errors are taken to be small but non-zero.

    :param bounds: \
        A iterable containing tuples which specify for the upper and lower bounds \
        for the optimisation in each dimension in the format (lower_bound, upper_bound).
    """
    def __init__(self, x, y, y_err = None, bounds = None):
        self.x = list(x)
        self.y = list(y)
        self.y_err = y_err

        if y_err is not None: self.y = list(self.y)
        self.bounds = bounds
        self.gp = GpRegressor(x, y, y_err=y_err)

        self.ir2pi = 1 / sqrt(2*pi)
        self.mu_max = max(self.y)

    def __call__(self, x):
        return self.gp(x)

    def add_evaluation(self, new_x, new_y, new_y_err=None):
        """
        Add the latest evaluation to the data set and re-build the \
        Gaussian process so a new proposed evaluation can be made.

        :param new_x: location of the new evaluation
        :param new_y: function value of the new evaluation
        :param new_y_err: Error of the new evaluation.
        """
        # update the data arrays
        self.x.append(new_x)
        self.y.append(new_y)
        if self.y_err is not None:
            if new_y_err is not None:
                self.y_err.append(new_y_err)
            else:
                raise ValueError('y_err must be specified for new evaluations if y_err was specified during __init__')

        # re-train the GP
        self.gp = GpRegressor(self.x, self.y, y_err=self.y_err)
        self.mu_max = max(self.y)

    def variance_aq(self,x):
        _, sig = self.gp(x)
        return -sig**2

    def maximise_aquisition(self, aq_func):
        opt_result = differential_evolution(aq_func, self.bounds)
        return opt_result.x

    def learn_function(self):
        return self.maximise_aquisition(self.variance_aq)

    def search_for_maximum(self):
        """
        Request a proposed location for the next evaluation. This proposal is \
        selected in order to maximise the "expected improvement" criteria which \
        searches for the global maximum value of the function.

        :return: location of the next proposed evaluation.
        """
        return self.maximise_aquisition(self.expected_improvement)

    def expected_improvement(self,x):
        mu, sig = self.gp([x])
        Z  = (mu - self.mu_max) / sig
        pdf = self.normal_pdf(Z)
        cdf = self.normal_cdf(Z)
        return -(mu-self.mu_max)*cdf - sig*pdf

    def normal_pdf(self,z):
       return exp(-0.5*z**2)*self.ir2pi

    def normal_cdf(self,z):
        return 0.5*(1 + erf(z/sqrt(2)))