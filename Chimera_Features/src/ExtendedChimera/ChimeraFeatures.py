import re
from ChimeraUtils import read_reply_log, save_and_clear_reply_log
from chimera import selection
from chimera import runCommand as rc
from ExtendedAtom import ExtendedAtom
from Utils import median
import math

# All of the features that we care about
features = [
    "AAindCodonDiv",
    "AAindMolVol",
    "AAindPolarity",
    "AAindSS",
    "AAindElecCharge",
    "netCharge",
    "posCharge",
    "negCharge",
    "sumMetals",
    "CO",
    "CU",
    "FE",
    "K",
    "MN",
    "MO",
    "NA",
    "NI",
    "ZN",
    "contacts",
    "RKPT",
    "Arg",
    "Lys",
    "Pro",
    "Thr",
    "surfMC",
    "surfM",
    "surfC",
    "hydro",
    "OHRxnConst",
    "SS",
    "helix",
    "sheet",
    "disord",
    "disordScore",
    "protBindSPPIDER",
    "protBindDISOPRED",
    "protBindDISOPREDscore",
    "areaSAS",
    "reactivity",
    "circularVariance",
    "depth",
]


def get_atom_features(eAtom):
    """ Get the features associated with this ExtendedAtom
    """
    atom_features = {
        "AA": eAtom.residue_1_letter,
        "Position": eAtom.number,
        "AAindCodonDiv": eAtom.aaind_codon_diversity,
        "AAindMolVol": eAtom.aaind_molecular_volume,
        "AAindPolarity": eAtom.aaind_polarity,
        "AAindSS": eAtom.aaind_secondary_structure,
        "AAindElecCharge": eAtom.aaind_charge,
        "netCharge": eAtom.charge,
        "posCharge": (1 if eAtom.charge == 1 else 0),
        "negCharge": (-1 if eAtom.charge == -1 else 0),
        # Keep sumMetals as NaN, since metals sum isn't strictly addative
        "sumMetals": len(
            list(set([metal.site_number for metal in eAtom.metal_contacts]))
        ),
        "CA": eAtom.metal_contacts.count("CA"),
        "CO": eAtom.metal_contacts.count("CO"),
        "CU": eAtom.metal_contacts.count("CU"),
        "FE": eAtom.metal_contacts.count("FE"),
        "K": eAtom.metal_contacts.count("K"),
        "MG": eAtom.metal_contacts.count("MG"),
        "MN": eAtom.metal_contacts.count("MN"),
        "MO": eAtom.metal_contacts.count("MO"),
        "NA": eAtom.metal_contacts.count("NA"),
        "NI": eAtom.metal_contacts.count("NI"),
        "ZN": eAtom.metal_contacts.count("ZN"),
        "RKPT": (1 if eAtom.residue_1_letter in ["R", "K", "P", "T"] else 0),
        "Arg": (1 if eAtom.residue_1_letter == "R" else 0),
        "Lys": (1 if eAtom.residue_1_letter == "K" else 0),
        "Pro": (1 if eAtom.residue_1_letter == "P" else 0),
        "Thr": (1 if eAtom.residue_1_letter == "T" else 0),
        "surfMC": eAtom.residue_1_letter in ["M", "C"] and (eAtom.depth - 1.782) < 0.01,
        "surfM": eAtom.residue_1_letter == "M" and (eAtom.depth - 1.782) < 0.01,
        "surfC": eAtom.residue_1_letter == "C" and (eAtom.depth - 1.782) < 0.01,
        "hydro": eAtom.hydrophobicity,
        "OHRxnConst": eAtom.hydroxyl_constant,
        "SS": (1 if eAtom.isSheet or eAtom.isHelix else 0),
        "helix": (1 if eAtom.isHelix else 0),
        "sheet": (1 if eAtom.isSheet else 0),
        "disord": eAtom.disorder_call,
        "disordScore": eAtom.disorder_score,
        "protBindSPPIDER": eAtom.sppider_binding_call,
        "protBindDISOPRED": eAtom.disopred_binding_call,
        "protBindDISOPREDscore": eAtom.disopred_binding_score,
        "areaSAS": eAtom.area_sas,
        "reactivity": eAtom.reactivity,
        "circularVariance": eAtom.get_circular_variance(),
        "depth": eAtom.depth,
        "contacts": 1,
    }

    # Make sure that we get all of the features
    for feature_name in features:
        if feature_name not in atom_features:
            raise Exception("Feature missing: {}".format(feature_name))

    return atom_features


def get_residue_features(eResidue):
    """ Get the features associated with this ExtendedResidue.
    """
    residue_features = {
        "AA": eResidue.residue_1_letter,
        "Position": eResidue.number,
        "AAindCodonDiv_res": eResidue.aaind_codon_diversity,
        "AAindMolVol_res": eResidue.aaind_molecular_volume,
        "AAindPolarity_res": eResidue.aaind_polarity,
        "AAindSS_res": eResidue.aaind_secondary_structure,
        "AAindElecCharge_res": eResidue.aaind_charge,
        "netCharge_res": eResidue.charge,
        "posCharge_res": (1 if eResidue.charge == 1 else 0),
        "negCharge_res": (-1 if eResidue.charge == -1 else 0),
        # Keep sumMetals as NaN, since metals sum isn't strictly addative
        "sumMetals_res": len(
            list(set([metal.site_number for metal in eResidue.metal_contacts]))
        ),
        "CA_res": eResidue.metal_contacts.count("CA"),
        "CO_res": eResidue.metal_contacts.count("CO"),
        "CU_res": eResidue.metal_contacts.count("CU"),
        "FE_res": eResidue.metal_contacts.count("FE"),
        "K_res": eResidue.metal_contacts.count("K"),
        "MG_res": eResidue.metal_contacts.count("MG"),
        "MN_res": eResidue.metal_contacts.count("MN"),
        "MO_res": eResidue.metal_contacts.count("MO"),
        "NA_res": eResidue.metal_contacts.count("NA"),
        "NI_res": eResidue.metal_contacts.count("NI"),
        "ZN_res": eResidue.metal_contacts.count("ZN"),
        "RKPT_res": (1 if eResidue.residue_1_letter in ["R", "K", "P", "T"] else 0),
        "Arg_res": (1 if eResidue.residue_1_letter == "R" else 0),
        "Lys_res": (1 if eResidue.residue_1_letter == "K" else 0),
        "Pro_res": (1 if eResidue.residue_1_letter == "P" else 0),
        "Thr_res": (1 if eResidue.residue_1_letter == "T" else 0),
        "surfMC_res": eResidue.residue_1_letter in ["M", "C"]
        and (eResidue.depth - 1.782) < 0.01,
        "surfM_res": (eResidue.residue_1_letter == "M")
        and (eResidue.depth - 1.782) < 0.01,
        "surfC_res": (eResidue.residue_1_letter == "C")
        and (eResidue.depth - 1.782) < 0.01,
        "hydro_res": eResidue.hydrophobicity,
        "OHRxnConst_res": eResidue.hydroxyl_constant,
        "SS_res": (1 if eResidue.isSheet or eResidue.isHelix else 0),
        "helix_res": (1 if eResidue.isHelix else 0),
        "sheet_res": (1 if eResidue.isSheet else 0),
        "disord_res": eResidue.disorder_call,
        "disordScore_res": eResidue.disorder_score,
        "protBindSPPIDER_res": eResidue.sppider_binding_call,
        "protBindDISOPRED_res": eResidue.disopred_binding_call,
        "protBindDISOPREDscore_res": eResidue.disopred_binding_score,
        "areaSAS_res": eResidue.area_sas,
        "reactivity_res": eResidue.reactivity,
        # Computed later on
        "circularVariance_res": float("NaN"),
        "depth_res": eResidue.depth,
        "contacts_res": 1,
    }

    # Make sure that we get all of the features
    for feature_name in features:
        res_feature_name = "{}_res".format(feature_name)
        if res_feature_name not in residue_features:
            raise Exception("Feature missing: {}".format(res_feature_name))

    return residue_features


def get_residues_features_sums(eResidues):
    """ Get the sum of all the features for the residues in the given
    list of ExtendedResidues.
    """
    residues_features = dict.fromkeys(features, 0)
    residues_features_copy = dict.fromkeys(features, 0)

    # Initalize features to found "None"s found in each feature
    for feature in residues_features_copy:
        none_feature = "{}_None".format(feature)
        residues_features[none_feature] = 0
        

    for residue in eResidues:
        # Get the features for this single residue
        single_residue_features = get_residue_features(residue)
        # Add this residue's features to the accumulating features
        for feature in residues_features_copy:
            single_feature = "{}_res".format(feature)
            if single_residue_features[single_feature] is not None:
                residues_features[feature] += single_residue_features[single_feature]
            else:
                # If this feature doesn't exist for this residue, then it will be None.
                # We should keep track of features like this in a seperate feature.
                none_feature = "{}_None".format(feature)
                residues_features[none_feature] += 1

    return residues_features


def compute_global_attributes_residues(eResidues):
    """ Computes various residue-level attributes on the given residues

    Arguments:
        eResidues ([List of Extended Residues) A list of the residues
        on which to compute characteristics
    Requires:
        None
    Returns:
        0. sum_global_secondary_structure (int) How many residues have
        secondary structure?
        1. sum_global_helicies (int) How many residues are part of a helix?
        2. sum_global_sheets (int) How many residues are part of a sheet?
        3. sum_global_SAS (int)  How much solvent accessible surface area
        do all of the residues have in aggregate?
    Effect:
        None
    """

    features = get_residues_features_sums(eResidues)

    # Overwrite metal binding features
    # Metal binding features at a global level will not vary residue-to-residue,
    # so just get all of the metals infinite distance from one of the residues
    eResidue = eResidues[0]
    eResidue.set_metal_contacts(float("Inf"))
    metal_types = [metal.type for metal in eResidue.metal_contacts]

    # Update the features dictionary with contacts from this residue
    features.update(
        {
            "sumMetals": len(
                list(set([metal.site_number for metal in eResidue.metal_contacts]))
            ),
            "CA": metal_types.count("CA"),
            "CO": metal_types.count("CO"),
            "CU": metal_types.count("CU"),
            "FE": metal_types.count("FE"),
            "K": metal_types.count("K"),
            "MG": metal_types.count("MG"),
            "MN": metal_types.count("MN"),
            "MO": metal_types.count("MO"),
            "NA": metal_types.count("NA"),
            "NI": metal_types.count("NI"),
            "ZN": metal_types.count("ZN"),
        }
    )

    # Overwrite circular variance features

    return features


def compute_global_circular_variance(base_atom, compared_atoms):
    # Get all contacts in the protein
    base_atom.set_atom_contacts(compared_atoms, float("Inf"))
    return {"circularVariance_global": base_atom.get_circular_variance()}


def compute_bubble_attributes_residues(
    base_atom, compared_residues, compared_atoms, radius
):
    base_atom.set_residue_contacts(compared_residues, radius)
    base_atom.set_metal_contacts(radius)

    # We'll need atom contacts if we're at a radius of 0, but just get all compared atoms
    if radius < 1e-20:
        base_atom.set_atom_contacts(compared_atoms, float("Inf"))
    else:
        base_atom.set_atom_contacts(compared_atoms, radius)

    bubble_features = get_residues_features_sums(base_atom.residue_contacts)

    # Add the base features to the bubble features, if we're at a radius of 0
    if radius < 1e-20:
        base_features = get_atom_features(base_atom)
        for key in bubble_features:
            # Don't include self in measurement of RPKT and contacts
            if key in base_features and key not in [
                "R",
                "K",
                "P",
                "T",
                "RPKT",
                "contacts",
            ]:
                if base_features[key] is not None:
                    bubble_features[key] = bubble_features[key] + base_features[key]

    # Overwrite metal binding features
    # Metal binding features at a bubble level does not depend on compared residues,
    # just the base atom
    metal_types = [metal.type for metal in base_atom.metal_contacts]

    # Update the features dictionary with contacts from this residue
    bubble_features.update(
        {
            "sumMetals": len(
                list(set([metal.site_number for metal in base_atom.metal_contacts]))
            ),
            "CA": metal_types.count("CA"),
            "CO": metal_types.count("CO"),
            "CU": metal_types.count("CU"),
            "FE": metal_types.count("FE"),
            "K": metal_types.count("K"),
            "MG": metal_types.count("MG"),
            "MN": metal_types.count("MN"),
            "MO": metal_types.count("MO"),
            "NA": metal_types.count("NA"),
            "NI": metal_types.count("NI"),
            "ZN": metal_types.count("ZN"),
        }
    )

    # Update the features dictionary with the circular variance from this atom
    bubble_features.update({"circularVariance": base_atom.get_circular_variance()})

    return bubble_features


def get_depths(times=1):
    depths_lists = {}
    depths_return = {}
    for time in range(times):
        current_depths = get_depth()
        for atom_name, depth in current_depths.items():
            if atom_name in depths_lists:
                depths_lists[atom_name].append(depth)
            else:
                depths_lists[atom_name] = [depth]

    for atom_name, depths_list in depths_lists.items():
        depths_return[atom_name] = median([float(depth) for depth in depths_list])

    return depths_return


def get_depth():
    """ Gets the depth of all atoms in the currently-loaded protein.

    The following atoms are used for depth calculations:
    RPKT: arg, lys, mly, kxc @ ce, pro @ cd, thr @ cb
    MC: met @ sd, cys @ sg
    All other residues: atom at lowest depth, excluding hydrogens.

    For atoms that can be carbonylated (RPKT), we select the atom at which that
    residue could be carbonylated. For MC, we select the oxidizable sulfur.

    All other atoms would not be expected to be carbonylated, so their depth values
    are used as an additional feature describing the relative solvent-accessibility
    at a certain residue.

    Arguments:
    Requires:
    Returns:
    Effect:
    Note: This contains some repeated code, but it is probably necessary,
    as this collect distance data via runCommand instead of directly from
    atom objects. This is because I don't know how to measure the distance
    between an atom and the surface without runCommand.
    """
    # Read and clear the reply log before measuring distance
    # save_and_clear_reply_log(logfile_name)

    # Select all RPKT/MC atoms at the correct location
    rc("~select")
    rc("select :arg@cd|:lys@ce|:mly@ce|:kcx@ce|:pro@cd|:thr@cb|:cys@sg|:met@sd")
    rpktmc_depths = get_depth_minimum()

    # Select all non-RPKTMC atoms that aren't hydrogen
    rc("~select")
    rc("select protein")
    rc("~select :arg|:lys|:mly|:kcx|:pro|:thr|:cys|:met")
    rc("~select element.H")
    atoms_all_except_hydrogen_depths = get_depth_minimum()

    residue_to_depth = rpktmc_depths
    residue_to_depth.update(atoms_all_except_hydrogen_depths)

    return residue_to_depth


def get_depth_minimum():
    """ Gets the depth of all RPKT to the surface

    Arguments:
    Requires:
    Returns:
    Effect:
    Note: This contains some repeated code, but it is probably necessary,
    as this collect distance data via runCommand instead of directly from
    atom objects. This is because I don't know how to measure the distance
    between an atom and the surface without runCommand.
    """
    # Read and clear the reply log before measuring distance
    # Note: requires a selection to be made before calling
    # Measures distance between current selection and the surface
    save_and_clear_reply_log("clear_depth.log")
    rc(("measure distance selection" " #0&~@* multiple true show true"))
    r, distances = read_reply_log()

    all_atoms = []
    for atom in selection.currentAtoms():
        all_atoms.append(ExtendedAtom(atom))

    # Map between atom number and atom residue
    atom_to_aa = {}
    for atom in all_atoms:
        atom_to_aa[atom.number] = atom.residue_1_letter

    # Initalize the return depth dictionary
    residue_to_depth = {}

    # Loop through each line that Chimera outputs
    for line in distances.splitlines():
        line = line.rstrip()
        if "minimum distance from" in line:
            # Delete 'minmum distance from'
            line = line.replace("minimum distance from ", "")

            # Seperate the residue and depth by a tab
            line = re.sub(r" to #0:\? = ", "\t", line)

            # Get the atom and depth from the line
            atom, depth = line.split("\t")

            residue_name, atom_type = atom.split("@")
            residue_name = re.sub(r"#.+:", "", residue_name)
            residue_number = residue_name.split(".")[0]

            # Get the minimum depth
            depth_key = "{},{}".format(residue_number, atom_to_aa[residue_name])

            # Only put this depth in the dictionary if this depth is:
            # (1) the first depth seen for this key, or
            # (2) smaller than the last depth seen for this key
            if depth_key in residue_to_depth:
                old_depth = residue_to_depth[depth_key]
                if old_depth > depth:
                    residue_to_depth[depth_key] = depth
            else:
                residue_to_depth[depth_key] = depth

    return residue_to_depth
