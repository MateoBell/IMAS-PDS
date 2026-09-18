"""TORAX config file with default inner sources activated and ECRH set to zero to be coupled with ECRH model such as TORBEAM."""
import numpy as np 
imas_uri = "imas:hdf5?path=${SCENARIOS_REPO}/${SHOT}/data/in"

# Add gaussian anomalous ad-hoc transport in the core similar to what is used in HFPS. See Theo's paper.
def gaussian_profile(x, maximum, center, width):
    return maximum * np.exp(-((x - center) ** 2) / (2 * width**2))


def get_t_values(imas_uri):
    import imas
    import numpy as np
    with imas.DBEntry(imas_uri, 'r') as db:
        eq = db.get('equilibrium')
        # t_initial = eq.time[0]
        t_initial = eq.time[1] # Caused issue with initial plasma composition
        t_final = eq.time[-1]
    return t_initial, t_final

t_initial, t_final = get_t_values(imas_uri)

rhon = np.linspace(0, 1, 25)

# Setting a higher time resolution between 0 and 20s.
epsilon = 1e-5
fixed_dt= {0.0: 1, 10 - epsilon: 1e-1, 20.0 - epsilon: 1e-1, 30.0 - epsilon: 1}

CONFIG = {
    'profile_conditions': {},
    'plasma_composition': {
        'main_ion': {'H': 1},
        "impurity": { # Dummy impurities and z_eff replaced by M3 actor 
            "species": {
                "Ne": None,
                "W": 4e-5,
            },
            "impurity_mode": "n_e_ratios_Z_eff",
        },
        "Z_eff": 1.6,
    },
    'numerics': {
        't_initial': t_initial,
        't_final': t_final,
        'exact_t_final': True,
        # 'fixed_dt': fixed_dt,
        'fixed_dt': 1.,
        'adaptive_dt': True,
        'resistivity_multiplier': 1,
        'evolve_current': True,
        # 'evolve_current': False,
        'evolve_ion_heat': True,
        'evolve_electron_heat': True,
        'evolve_density': True,
    },
    # circular geometry is only for testing and prototyping
    'geometry': {
        'geometry_type': 'circular',
        'n_rho': 50,
    },
    'pedestal': {},
    'sources': {
        # Physics-based sources
        'ohmic': {},
        'fusion': {},
        'ei_exchange': {},
        'bremsstrahlung': {},
        'impurity_radiation': {
             'model_name': 'mavrin_fit',
             'radiation_multiplier': 3.0,
            # 'model_name': 'P_in_scaled_flat_profile',
            # 'fraction_P_heating': 0.3,
        },
        # Actuators
        'ecrh': {'mode': 'ZERO'},
    },
    # "transport": {
    #     'model_name': 'qlknn',
    #     "DV_effective": True,
    #     "smooth_everywhere": True, #Try to avoid discontinuity in the transport coeffs leading to hollowing of the profiles
    #     # set inner core transport coefficients (ad-hoc MHD/EM transport)
    #     'apply_inner_patch': True,
    #     'D_e_inner': 0.25,
    #     'V_e_inner': 0.0,
    #     'chi_i_inner': 1.0,
    #     'chi_e_inner': 1.0,
    #     'rho_inner': 0.15,  # radius below which patch transport is applied
    #     # set outer core transport coefficients (L-mode near edge region)
    #     'apply_outer_patch': True,
    #     'D_e_outer': 0.1,
    #     'V_e_outer': -0.3,
    #     'chi_i_outer': 2.0,
    #     'chi_e_outer': 2.0,
    #     'rho_outer': 0.9,  # radius above which patch transport is applied
    # },
    "transport": {
        'model_name': 'combined',
        'transport_models': [
            {
            'model_name': 'qlknn',
            "DV_effective": False, # True gives large increase in core T. Can create sharper density transport when False
            # "rho_min": 0.15, 
            # "rho_max": 0.93, 
        },
        {
            # Gaussian ad-hoc anomalous transport in the edge (L-mode near edge patch)
            "model_name": "constant",
            # "chi_e": (rhon, gaussian_profile(rhon, 2.0, 1.0, 0.1)),
            # "chi_i": (rhon, gaussian_profile(rhon, 2.0, 1.0, 0.1)),
            # "D_e": (rhon, gaussian_profile(rhon, 0.2, 1.0, 0.1)),
            "chi_e": 2.0,
            "chi_i": 2.0,
            "D_e": 0.2,
            "V_e": -0.2,
            'merge_mode': 'overwrite',
            # 'disable_chi_i': True,
            # 'disable_chi_e': True,
            "rho_min": 0.9,
        },
        {
            # Gaussian ad-hoc anomalous transport in the core (ad-hoc MHD/EM transport)
            "model_name": "constant",
            # "chi_e": (rhon, gaussian_profile(rhon, 1.5, 0.0, 0.15)),
            # "chi_i": (rhon, gaussian_profile(rhon, 1.5, 0.0, 0.15)),
            "chi_e": 1.5,
            "chi_i": 1.5,
            "D_e": 0.1,
            "V_e": 0.0,
            'merge_mode': 'add',
            # 'disable_chi_i': True,
            # 'disable_chi_e': True,
            # 'disable_D_e': True,
            "rho_max": 0.3,
        },
    ],
    #  Smoothing
    "smoothing_width": 0.1,
    "smooth_everywhere": False,
    # Clipping
    "chi_min": 0.05,
    "chi_max": 100,
    "D_e_min": 0.05,
    },
    'solver': {
        'solver_type': 'newton_raphson',
        'use_predictor_corrector': True,
        'n_corrector_steps': 10,
        'use_pereverzev': True,
    },
    'time_step_calculator': {
        'calculator_type': 'fixed',
    },
    'neoclassical': {
        'bootstrap_current': {'model_name': 'sauter'},
        # 'transport': {"model_name": "angioni_sauter",
        #               "use_shaing_ion_correction": True,
        #               "shaing_ion_multiplier": 1.,
        # }
    },
}
