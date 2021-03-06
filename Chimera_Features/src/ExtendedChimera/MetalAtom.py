ionic_radii = dict(
    {
        "CA": 1.00,
        "CO": 0.65,
        "CU": 0.73,
        "FE": 0.61,
        "K": 1.38,
        "MG": 0.72,
        "MN": 0.83,
        "MO": 0.65,
        "NA": 1.02,
        "NI": 0.69,
        "ZN": 0.74,
    }
)


class MetalAtom:
    """ Represents a metal atom within a protein structure
    """

    def __init__(self, metal_type, nearby_residues, location, site_number):
        """
        nearby_residues: A list of strings in the format:
        residuenumber ("C208", "H271", etc.)
        """

        if metal_type in ionic_radii:
            self.radius = ionic_radii[metal_type]
        else:
            raise ValueError("Unsupported metal type: {}".format(metal_type))

        self.type = metal_type
        self.nearby_residues = nearby_residues
        self.location = location
        self.site_number = site_number

    def __repr__(self):
        return str(self.__dict__)

        # def __str__(self):
        #     return "A {} atom at location {}".format(
        #         self.type, self.location)
